#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def read_scan_chunked(e57, scan_index, max_points, seed, chunk_size=200000):
    """Read and optionally sample a scan without one very large native buffer.

    Some pye57/libE57 combinations stall when ``read_scan`` allocates a buffer
    for the complete scan. Repeated reads with a bounded buffer avoid that
    issue and keep memory usage predictable.
    """
    from pye57.e57 import (
        COORDINATE_SYSTEMS,
        convert_spherical_to_cartesian,
    )

    header = e57.get_header(scan_index)
    coordinate_system = header.get_coordinate_system(COORDINATE_SYSTEMS)
    if coordinate_system is COORDINATE_SYSTEMS.CARTESIAN:
        coordinate_fields = ["cartesianX", "cartesianY", "cartesianZ"]
        invalid_field = "cartesianInvalidState"
    elif coordinate_system is COORDINATE_SYSTEMS.SPHERICAL:
        coordinate_fields = [
            "sphericalRange",
            "sphericalAzimuth",
            "sphericalElevation",
        ]
        invalid_field = "sphericalInvalidState"
    else:
        raise RuntimeError(f"Unsupported E57 coordinate system: {coordinate_system}")

    fields = list(coordinate_fields)
    if invalid_field in header.point_fields:
        fields.append(invalid_field)
    if "intensity" in header.point_fields:
        fields.append("intensity")
    color_fields = ["colorRed", "colorGreen", "colorBlue"]
    has_colors = all(field in header.point_fields for field in color_fields)
    if has_colors:
        fields.extend(color_fields)

    point_count = int(header.point_count)
    selected = None
    if max_points and point_count > max_points:
        selected = np.sort(
            np.random.default_rng(seed).choice(
                point_count,
                int(max_points),
                replace=False,
            )
        )

    buffer_size = max(1, min(int(chunk_size), point_count))
    data, buffers = e57.make_buffers(fields, buffer_size)
    reader = header.points.reader(buffers)
    xyz_parts = []
    rgb_parts = []
    intensity_parts = []
    offset = 0
    try:
        while True:
            count = int(reader.read())
            if count <= 0:
                break

            if selected is None:
                indices = np.arange(count)
            else:
                lo = np.searchsorted(selected, offset, side="left")
                hi = np.searchsorted(selected, offset + count, side="left")
                indices = selected[lo:hi] - offset

            if invalid_field in data and indices.size:
                valid = ~data[invalid_field][indices].astype(bool)
                indices = indices[valid]

            if indices.size:
                coordinates = np.column_stack(
                    [data[field][indices] for field in coordinate_fields]
                ).astype(np.float64)
                if coordinate_system is COORDINATE_SYSTEMS.SPHERICAL:
                    coordinates = convert_spherical_to_cartesian(coordinates)
                if header.has_pose():
                    coordinates = e57.to_global(
                        coordinates,
                        header.rotation,
                        header.translation,
                    )
                xyz_parts.append(coordinates)

                if has_colors:
                    rgb_parts.append(
                        np.column_stack(
                            [data[field][indices] for field in color_fields]
                        ).astype(np.uint8)
                    )
                if "intensity" in data:
                    intensity_parts.append(
                        np.asarray(data["intensity"][indices]).copy()
                    )
            offset += count
    finally:
        reader.close()

    xyz = (
        np.concatenate(xyz_parts)
        if xyz_parts
        else np.empty((0, 3), dtype=np.float64)
    )
    rgb = np.concatenate(rgb_parts) if rgb_parts else None
    intensity = np.concatenate(intensity_parts) if intensity_parts else None
    return xyz, rgb, intensity


def q2r(q):
    q = np.asarray(q, dtype=float)
    n = np.linalg.norm(q)
    if n == 0:
        return np.eye(3)
    w, x, y, z = q / n
    return np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ],
        dtype=float,
    )


def apply_scan_pose(xyz, metadata, scan_index):
    if not metadata or not metadata.exists():
        raise RuntimeError("--apply-scan-pose requires --metadata prepared_dataset/cameras.json")
    meta = json.loads(metadata.read_text(encoding="utf-8"))
    scans = meta.get("data3d", [])
    if scan_index >= len(scans):
        return xyz
    s = scans[scan_index]
    R = q2r(s.get("rotation_wxyz", [1, 0, 0, 0]))
    t = np.asarray(s.get("translation_xyz", [0, 0, 0]), dtype=float)
    return xyz @ R.T + t[None, :]


def save_points(out_path: Path, xyz, rgb, inten):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"xyz": xyz}
    if rgb is not None:
        payload["rgb"] = rgb
    if inten is not None:
        payload["intensity"] = inten
    np.savez_compressed(out_path, **payload)
    print(f"Saved {xyz.shape[0]} points to {out_path}")


def per_scan_out_path(out_path: Path, scan_index: int) -> Path:
    return out_path.with_name(f"{out_path.stem}_scan_{scan_index:03d}{out_path.suffix}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e57", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--scan-index", type=int, default=0)
    ap.add_argument(
        "--all-scans",
        action="store_true",
        help="Write one points_scan_XXX.npz file for every data3D scan.",
    )
    ap.add_argument("--max-points", type=int, default=500000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--metadata", type=Path)
    ap.add_argument(
        "--apply-scan-pose",
        action="store_true",
        help=(
            "Apply data3D pose from cameras.json. For the provided Pentax sample, "
            "leave this OFF because pye57 already returns coordinates in the same frame used by images2D."
        ),
    )
    args = ap.parse_args()

    try:
        import pye57
    except ImportError as exc:
        raise SystemExit("pye57 is not installed. Install with: pip install pye57") from exc

    e57 = pye57.E57(str(args.e57))
    try:
        scan_indexes = range(e57.scan_count) if args.all_scans else [args.scan_index]
        for scan_index in scan_indexes:
            xyz, rgb, inten = read_scan_chunked(
                e57,
                scan_index,
                max_points=args.max_points,
                seed=args.seed + int(scan_index),
            )

            if args.apply_scan_pose:
                xyz = apply_scan_pose(xyz, args.metadata, scan_index)

            out_path = (
                per_scan_out_path(args.out, scan_index)
                if args.all_scans
                else args.out
            )
            save_points(out_path, xyz, rgb, inten)
            if args.all_scans and e57.scan_count == 1:
                save_points(args.out, xyz, rgb, inten)

        if args.apply_scan_pose:
            print("Applied data3D scan pose.")
        else:
            print("Did not apply data3D scan pose. This is the default for the provided Pentax E57 sample.")
    finally:
        e57.close()


if __name__ == "__main__":
    main()

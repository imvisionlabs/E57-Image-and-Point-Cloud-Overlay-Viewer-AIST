#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import struct
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {"e57": "http://www.astm.org/COMMIT/E57/2010-e57-v1.0"}


def val(node, default=""):
    if node is None or node.text is None or node.text.strip() == "":
        return default
    return node.text.strip()


def f(node, default=0.0):
    return float(val(node, default))


def i(node, default=0):
    return int(float(val(node, default)))


def safe(name):
    return re.sub(r"[^A-Za-z0-9_.\-]+", "_", name.replace("/", "_").replace("\\", "_"))


def read_header(e57_path: Path):
    """Read the fixed 48-byte E57 header.

    E57 stores data in pages. Each physical page contains a 4-byte checksum at
    the end, so logical byte ranges must skip those checksum bytes.
    """
    with e57_path.open("rb") as fh:
        header = fh.read(48)
    if len(header) != 48:
        raise RuntimeError("E57 header is too short")
    magic, major, minor, file_len, xml_offset, xml_len, page_size = struct.unpack(
        "<8sIIQQQQ", header
    )
    if magic != b"ASTM-E57":
        raise RuntimeError(f"Not an ASTM E57 file: magic={magic!r}")
    return {
        "major": major,
        "minor": minor,
        "file_len": file_len,
        "xml_offset": xml_offset,
        "xml_len": xml_len,
        "page_size": page_size,
    }


def read_logical_bytes(e57_path: Path, offset: int, length: int) -> bytes:
    """Read a logical byte range from an E57 file, skipping page checksums."""
    h = read_header(e57_path)
    page_size = int(h["page_size"])
    if page_size <= 4:
        raise RuntimeError(f"Invalid E57 page size: {page_size}")

    out = bytearray()
    pos = int(offset)
    with e57_path.open("rb") as fh:
        while len(out) < length:
            in_page = pos % page_size
            # Last 4 bytes of each physical page are checksum bytes.
            if in_page >= page_size - 4:
                pos += page_size - in_page
                continue
            take = min((page_size - 4) - in_page, length - len(out))
            fh.seek(pos)
            chunk = fh.read(take)
            if len(chunk) != take:
                raise EOFError("Unexpected EOF while reading E57 logical bytes")
            out += chunk
            pos += take
    return bytes(out)


def advance_logical_offset(offset: int, length: int, page_size: int) -> int:
    """Advance a physical E57 offset by logical bytes, skipping checksums."""
    pos = int(offset)
    remaining = int(length)
    while remaining > 0:
        in_page = pos % page_size
        if in_page >= page_size - 4:
            pos += page_size - in_page
            continue
        take = min((page_size - 4) - in_page, remaining)
        pos += take
        remaining -= take
    return pos


def dump_xml(e57_path: Path, xml_path: Path):
    """Extract the XML section directly from the E57 file.

    This version does not require e57xmldump or libE57Format command-line tools.
    """
    h = read_header(e57_path)
    xml = read_logical_bytes(e57_path, int(h["xml_offset"]), int(h["xml_len"]))
    xml_path.write_bytes(xml)


def blob(e57_path: Path, out_path: Path, offset: int, length: int):
    """Extract an E57 Blob.

    The Blob section starts with a 16-byte section header. The XML length refers
    to the actual blob payload, so the JPEG/PNG bytes begin at fileOffset + 16.
    """
    header = read_header(e57_path)
    payload_offset = advance_logical_offset(
        int(offset),
        16,
        int(header["page_size"]),
    )
    data = read_logical_bytes(e57_path, payload_offset, int(length))
    if not (data.startswith(b"\xff\xd8") or data.startswith(b"\x89PNG")):
        print(f"warning: {out_path.name} does not look like JPEG/PNG bytes", file=sys.stderr)
    out_path.write_bytes(data)


def parse(xml_path: Path, e57_path: Path, out_dir: Path):
    root = ET.parse(xml_path).getroot()
    images = out_dir / "images"
    images.mkdir(parents=True, exist_ok=True)
    result = {
        # Keep prepared datasets portable and avoid recording user-specific
        # absolute paths in cameras.json.
        "source_e57": e57_path.name,
        "source_xml": xml_path.name,
        "data3d": [],
        "cameras": [],
    }

    scan_guid_to_index = {}
    for scan_index, scan in enumerate(root.findall("./e57:data3D/e57:vectorChild", NS)):
        pose = scan.find("e57:pose", NS)
        rot = pose.find("e57:rotation", NS) if pose is not None else None
        tr = pose.find("e57:translation", NS) if pose is not None else None
        scan_guid = val(scan.find("e57:guid", NS))
        if scan_guid:
            scan_guid_to_index[scan_guid] = scan_index
        result["data3d"].append(
            {
                "scan_index": scan_index,
                "guid": scan_guid,
                "name": val(scan.find("e57:name", NS)),
                "rotation_wxyz": [
                    f(rot.find("e57:w", NS), 1) if rot is not None else 1,
                    f(rot.find("e57:x", NS), 0) if rot is not None else 0,
                    f(rot.find("e57:y", NS), 0) if rot is not None else 0,
                    f(rot.find("e57:z", NS), 0) if rot is not None else 0,
                ],
                "translation_xyz": [
                    f(tr.find("e57:x", NS), 0) if tr is not None else 0,
                    f(tr.find("e57:y", NS), 0) if tr is not None else 0,
                    f(tr.find("e57:z", NS), 0) if tr is not None else 0,
                ],
            }
        )

    for image_index, im in enumerate(root.findall("./e57:images2D/e57:vectorChild", NS)):
        pin = im.find("e57:pinholeRepresentation", NS)
        pose = im.find("e57:pose", NS)
        if pin is None or pose is None:
            continue

        jpg = pin.find("e57:jpegImage", NS)
        png = pin.find("e57:pngImage", NS)
        img_node = jpg if jpg is not None else png
        if img_node is None:
            continue

        guid = val(im.find("e57:guid", NS))
        name = val(im.find("e57:name", NS), guid + (".jpg" if jpg is not None else ".png"))
        associated_guid = val(im.find("e57:associatedData3DGuid", NS))
        scan_index = scan_guid_to_index.get(associated_guid)
        camera_id_source = guid if guid and guid != "0000000000000000" else associated_guid
        camera_id = f"image_{image_index:04d}_{safe(camera_id_source or name)}"
        fname = f"{image_index:04d}_{safe(name)}"
        if jpg is not None and not fname.lower().endswith((".jpg", ".jpeg")):
            fname += ".jpg"
        if png is not None and not fname.lower().endswith(".png"):
            fname += ".png"

        offset = int(img_node.attrib["fileOffset"])
        length = int(img_node.attrib["length"])
        blob(e57_path, images / fname, offset, length)

        rot = pose.find("e57:rotation", NS)
        tr = pose.find("e57:translation", NS)
        focal = f(pin.find("e57:focalLength", NS))
        pw = f(pin.find("e57:pixelWidth", NS))
        ph = f(pin.find("e57:pixelHeight", NS))
        result["cameras"].append(
            {
                "camera_id": camera_id,
                "image_index": image_index,
                "guid": guid,
                "name": name,
                "image_path": str(Path("images") / fname),
                "associated_data3d_guid": associated_guid,
                "scan_index": scan_index,
                "points_path": (
                    f"points_scan_{scan_index:03d}.npz"
                    if scan_index is not None
                    else "points.npz"
                ),
                "width": i(pin.find("e57:imageWidth", NS)),
                "height": i(pin.find("e57:imageHeight", NS)),
                "focal_length_mm": focal,
                "pixel_width_mm": pw,
                "pixel_height_mm": ph,
                "fx": focal / pw if pw else None,
                "fy": focal / ph if ph else None,
                "cx": f(pin.find("e57:principalPointX", NS)),
                "cy": f(pin.find("e57:principalPointY", NS)),
                "rotation_wxyz": [
                    f(rot.find("e57:w", NS), 1),
                    f(rot.find("e57:x", NS), 0),
                    f(rot.find("e57:y", NS), 0),
                    f(rot.find("e57:z", NS), 0),
                ],
                "translation_xyz": [
                    f(tr.find("e57:x", NS), 0),
                    f(tr.find("e57:y", NS), 0),
                    f(tr.find("e57:z", NS), 0),
                ],
                "blob": {"fileOffset": offset, "length": length},
            }
        )
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e57", required=True, type=Path)
    ap.add_argument("--xml", type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    xml = args.xml or args.out / "e57.xml"
    if args.xml is None:
        print("Extracting XML directly from E57...", file=sys.stderr)
        dump_xml(args.e57, xml)

    meta = parse(xml, args.e57, args.out)
    (args.out / "cameras.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Extracted {len(meta['cameras'])} images to {args.out}")
    print(f"Wrote: {args.out / 'cameras.json'}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET

try:
    from extract_images_from_e57_xml import NS, read_header, read_logical_bytes, val
except ImportError:
    from tools.extract_images_from_e57_xml import (
        NS,
        read_header,
        read_logical_bytes,
        val,
    )


UNKNOWN_COORDINATE_SYSTEM = "UNKNOWN／UNSUPPORTED"


@dataclass
class ScanResult:
    index: int
    name: str
    guid: str
    coordinate_system: str
    coordinate_fields: list[str]
    point_fields: list[str]
    point_count: int
    has_pose: bool
    associated_images: int
    classification_error: str = ""


@dataclass
class FileResult:
    path: Path
    scans: list[ScanResult]
    image_count: int
    representation_counts: Counter[str]
    image_format_counts: Counter[str]
    associations_matched: int
    associations_missing: int
    associations_unknown: int


def xml_root(e57_path: Path) -> ET.Element:
    header = read_header(e57_path)
    xml = read_logical_bytes(
        e57_path,
        int(header["xml_offset"]),
        int(header["xml_len"]),
    )
    return ET.fromstring(xml)


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def display_representation(name: str) -> str:
    if name.endswith("Representation"):
        name = name[: -len("Representation")]
    return name.upper() or "UNKNOWN"


def inspect_xml(e57_path: Path):
    root = xml_root(e57_path)
    scan_rows = root.findall("./e57:data3D/e57:vectorChild", NS)
    scan_metadata = []
    guid_to_index = {}
    for index, scan in enumerate(scan_rows):
        guid = val(scan.find("e57:guid", NS))
        name = val(scan.find("e57:name", NS))
        scan_metadata.append((name, guid))
        if guid:
            guid_to_index[guid] = index

    image_rows = root.findall("./e57:images2D/e57:vectorChild", NS)
    representation_counts: Counter[str] = Counter()
    image_format_counts: Counter[str] = Counter()
    associated_by_scan: dict[int, int] = defaultdict(int)
    associations_matched = 0
    associations_missing = 0
    associations_unknown = 0

    for image in image_rows:
        representations = [
            child
            for child in list(image)
            if local_name(child.tag).endswith("Representation")
        ]
        if not representations:
            representation_counts["UNKNOWN"] += 1
        for representation in representations:
            representation_name = display_representation(local_name(representation.tag))
            representation_counts[representation_name] += 1
            if representation.find("e57:jpegImage", NS) is not None:
                image_format_counts[f"{representation_name}/JPEG"] += 1
            if representation.find("e57:pngImage", NS) is not None:
                image_format_counts[f"{representation_name}/PNG"] += 1

        associated_guid = val(image.find("e57:associatedData3DGuid", NS))
        if not associated_guid:
            associations_missing += 1
        elif associated_guid in guid_to_index:
            associations_matched += 1
            associated_by_scan[guid_to_index[associated_guid]] += 1
        else:
            associations_unknown += 1

    return (
        scan_metadata,
        len(image_rows),
        representation_counts,
        image_format_counts,
        associated_by_scan,
        associations_matched,
        associations_missing,
        associations_unknown,
    )


def classify_coordinate_system(header, coordinate_systems):
    try:
        system = header.get_coordinate_system(coordinate_systems)
        if system is coordinate_systems.CARTESIAN:
            return "CARTESIAN", ""
        if system is coordinate_systems.SPHERICAL:
            return "SPHERICAL", ""
        return UNKNOWN_COORDINATE_SYSTEM, f"Unexpected value: {system!r}"
    except Exception as exc:
        return UNKNOWN_COORDINATE_SYSTEM, f"{type(exc).__name__}: {exc}"


def inspect_file(e57_path: Path) -> FileResult:
    import pye57
    from pye57.e57 import COORDINATE_SYSTEMS

    (
        scan_metadata,
        image_count,
        representation_counts,
        image_format_counts,
        associated_by_scan,
        associations_matched,
        associations_missing,
        associations_unknown,
    ) = inspect_xml(e57_path)

    e57 = pye57.E57(str(e57_path))
    scans = []
    try:
        for index in range(e57.scan_count):
            header = e57.get_header(index)
            point_fields = list(header.point_fields)
            coordinate_fields = [
                field
                for field in point_fields
                if field.startswith("cartesian") or field.startswith("spherical")
            ]
            coordinate_system, classification_error = classify_coordinate_system(
                header,
                COORDINATE_SYSTEMS,
            )
            name, guid = (
                scan_metadata[index]
                if index < len(scan_metadata)
                else ("", str(getattr(header, "guid", "")))
            )
            scans.append(
                ScanResult(
                    index=index,
                    name=name,
                    guid=guid,
                    coordinate_system=coordinate_system,
                    coordinate_fields=coordinate_fields,
                    point_fields=point_fields,
                    point_count=int(header.point_count),
                    has_pose=bool(header.has_pose()),
                    associated_images=int(associated_by_scan.get(index, 0)),
                    classification_error=classification_error,
                )
            )
    finally:
        e57.close()

    return FileResult(
        path=e57_path,
        scans=scans,
        image_count=image_count,
        representation_counts=representation_counts,
        image_format_counts=image_format_counts,
        associations_matched=associations_matched,
        associations_missing=associations_missing,
        associations_unknown=associations_unknown,
    )


def markdown_list(items) -> str:
    values = list(items)
    return ", ".join(str(value) for value in values) if values else "—"


def counter_text(counter: Counter[str]) -> str:
    if not counter:
        return "—"
    return ", ".join(f"{key}: {counter[key]}" for key in sorted(counter))


def escape_cell(value) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def consistency_text(scans: list[ScanResult]) -> str:
    if len(scans) <= 1:
        return "N/A（単一スキャン）"
    systems = {scan.coordinate_system for scan in scans}
    return "一致" if len(systems) == 1 else "不一致"


def association_text(result: FileResult) -> str:
    if result.image_count == 0:
        return "画像なし"
    return (
        f"一致: {result.associations_matched}, "
        f"GUIDなし: {result.associations_missing}, "
        f"不明GUID: {result.associations_unknown}"
    )


def render_markdown(results: list[FileResult], source_label: str) -> str:
    lines = [
        "# 入力E57データ一覧",
        "",
        f"対象: `{source_label}` 内のE57ファイル",
        "",
        "座標系は各スキャンを `pye57` で開き、"
        "`header.get_coordinate_system(COORDINATE_SYSTEMS)` の結果で分類しています。",
        "",
        "## ファイル別概要",
        "",
        "| E57ファイル | サイズ | スキャン数 | 座標系 | 複数スキャン内の一致 | 画像数 | 画像表現 | 画像とスキャンの関連付け |",
        "| --- | ---: | ---: | --- | --- | ---: | --- | --- |",
    ]

    for result in results:
        systems = sorted({scan.coordinate_system for scan in result.scans})
        lines.append(
            "| "
            + " | ".join(
                escape_cell(value)
                for value in (
                    result.path.name,
                    f"{result.path.stat().st_size / (1024 ** 3):.3f} GiB",
                    len(result.scans),
                    markdown_list(systems),
                    consistency_text(result.scans),
                    result.image_count,
                    counter_text(result.representation_counts),
                    association_text(result),
                )
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## スキャン別詳細",
            "",
            "| E57ファイル | Scan | 名前 | GUID | 座標系 | 実在する座標フィールド | 全点フィールド | 点数 | 姿勢 | 関連画像数 |",
            "| --- | ---: | --- | --- | --- | --- | --- | ---: | --- | ---: |",
        ]
    )

    for result in results:
        for scan in result.scans:
            lines.append(
                "| "
                + " | ".join(
                    escape_cell(value)
                    for value in (
                        result.path.name,
                        scan.index,
                        scan.name or "—",
                        scan.guid or "—",
                        scan.coordinate_system,
                        markdown_list(f"`{field}`" for field in scan.coordinate_fields),
                        markdown_list(f"`{field}`" for field in scan.point_fields),
                        f"{scan.point_count:,}",
                        "あり" if scan.has_pose else "なし",
                        scan.associated_images,
                    )
                )
                + " |"
            )

    lines.extend(
        [
            "",
            "## 画像表現の詳細",
            "",
            "| E57ファイル | 画像表現 | 画像データ形式 | 関連付け結果 |",
            "| --- | --- | --- | --- |",
        ]
    )
    for result in results:
        lines.append(
            "| "
            + " | ".join(
                escape_cell(value)
                for value in (
                    result.path.name,
                    counter_text(result.representation_counts),
                    counter_text(result.image_format_counts),
                    association_text(result),
                )
            )
            + " |"
        )

    multi_scan = [result for result in results if len(result.scans) > 1]
    inconsistent = [
        result
        for result in multi_scan
        if len({scan.coordinate_system for scan in result.scans}) > 1
    ]
    unknown = [
        (result.path.name, scan.index, scan.classification_error)
        for result in results
        for scan in result.scans
        if scan.coordinate_system == UNKNOWN_COORDINATE_SYSTEM
    ]
    all_scans = [scan for result in results for scan in result.scans]
    system_counts = Counter(scan.coordinate_system for scan in all_scans)
    scans_with_pose = sum(scan.has_pose for scan in all_scans)
    spherical_image_files = [
        result.path.name
        for result in results
        if result.representation_counts.get("SPHERICAL", 0)
    ]
    unassociated_images = sum(result.associations_missing for result in results)
    unknown_associations = sum(result.associations_unknown for result in results)

    lines.extend(["", "## 確認結果", ""])
    lines.append(
        f"- 全{len(all_scans)}スキャンの座標系内訳: {counter_text(system_counts)}。"
    )
    lines.append(
        f"- 姿勢情報があるスキャンは{scans_with_pose}/{len(all_scans)}件でした。"
    )
    if multi_scan:
        if inconsistent:
            lines.append(
                "- 複数スキャン内で座標系が一致しないファイル: "
                + markdown_list(result.path.name for result in inconsistent)
            )
        else:
            lines.append("- 複数スキャンを含む全ファイルで、スキャン間の座標系は一致しました。")
    else:
        lines.append("- 複数スキャンを含むファイルはありませんでした。")

    if unknown:
        lines.append(f"- `{UNKNOWN_COORDINATE_SYSTEM}` に分類されたスキャンがあります。")
        for file_name, scan_index, error in unknown:
            lines.append(f"  - `{file_name}` scan {scan_index}: {error}")
    else:
        lines.append(
            f"- `{UNKNOWN_COORDINATE_SYSTEM}` に分類されたスキャンはありませんでした。"
        )

    if spherical_image_files:
        lines.append(
            "- `SPHERICAL` 画像表現を含むファイル: "
            + markdown_list(f"`{name}`" for name in spherical_image_files)
            + "。これはパノラマ画像の表現形式であり、点群の座標系分類とは別です。"
        )
    lines.append(f"- `associatedData3DGuid` がない画像は合計{unassociated_images}件でした。")
    lines.append(f"- 存在しないスキャンGUIDを参照する画像は合計{unknown_associations}件でした。")
    lines.extend(
        [
            "",
            "## 判定上の注意",
            "",
            "- `CARTESIAN` は `cartesianX`、`cartesianY`、`cartesianZ` の組を持つスキャンです。",
            "- `SPHERICAL` は `sphericalRange`、`sphericalAzimuth`、`sphericalElevation` の組を持つスキャンです。",
            f"- `{UNKNOWN_COORDINATE_SYSTEM}` は `get_coordinate_system()` が上記の完全な組を判定できなかった場合です。",
            "- 画像とスキャンの関連付けは、画像の `associatedData3DGuid` と `data3D` のGUIDが一致するかで判定しています。",
        ]
    )
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Inspect coordinate systems and image associations in E57 files."
    )
    parser.add_argument("data_dir", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--source-label", default="data/")
    args = parser.parse_args()

    e57_files = sorted(args.data_dir.glob("*.e57"), key=lambda path: path.name.lower())
    if not e57_files:
        raise SystemExit(f"No E57 files found in: {args.data_dir}")

    results = []
    for e57_path in e57_files:
        print(f"Inspecting: {e57_path.name}")
        results.append(inspect_file(e57_path))

    markdown = render_markdown(results, args.source_label)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(markdown, encoding="utf-8")
        print(f"Wrote: {args.output}")
    else:
        print(markdown)


if __name__ == "__main__":
    main()

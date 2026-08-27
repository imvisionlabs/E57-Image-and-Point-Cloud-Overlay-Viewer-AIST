# 入力E57データ一覧

対象: `data/` 内のE57ファイル

座標系は各スキャンを `pye57` で開き、`header.get_coordinate_system(COORDINATE_SYSTEMS)` の結果で分類しています。

## ファイル別概要

| E57ファイル | サイズ | スキャン数 | 座標系 | 複数スキャン内の一致 | 画像数 | 画像表現 | 画像とスキャンの関連付け |
| --- | ---: | ---: | --- | --- | ---: | --- | --- |
| 1102_202109110828_S16_000002.e57 | 0.043 GiB | 1 | CARTESIAN | N/A（単一スキャン） | 48 | PINHOLE: 48 | 一致: 0, GUIDなし: 48, 不明GUID: 0 |
| 7701_202402130837_S21_000003.e57 | 1.162 GiB | 4 | CARTESIAN | 一致 | 441 | PINHOLE: 392, SPHERICAL: 49 | 一致: 0, GUIDなし: 441, 不明GUID: 0 |
| 7701_202402131317_S20_000001.e57 | 1.329 GiB | 2 | CARTESIAN | 一致 | 504 | PINHOLE: 448, SPHERICAL: 56 | 一致: 0, GUIDなし: 504, 不明GUID: 0 |
| EdoCastle_ShimizuGate_RIEGLE_EightScan.e57 | 3.014 GiB | 11 | CARTESIAN | 一致 | 70 | PINHOLE: 70 | 一致: 70, GUIDなし: 0, 不明GUID: 0 |
| EdoCastle_ShimizuGate_RIEGLE_SingleScan.e57 | 0.307 GiB | 1 | CARTESIAN | N/A（単一スキャン） | 7 | PINHOLE: 7 | 一致: 7, GUIDなし: 0, 不明GUID: 0 |
| job53.e57 | 0.099 GiB | 1 | CARTESIAN | N/A（単一スキャン） | 6 | PINHOLE: 6 | 一致: 6, GUIDなし: 0, 不明GUID: 0 |
| openpitmine.e57 | 0.574 GiB | 10 | CARTESIAN | 一致 | 21 | PINHOLE: 21 | 一致: 0, GUIDなし: 21, 不明GUID: 0 |
| sample.e57 | 0.043 GiB | 1 | CARTESIAN | N/A（単一スキャン） | 48 | PINHOLE: 48 | 一致: 0, GUIDなし: 48, 不明GUID: 0 |

## スキャン別詳細

| E57ファイル | Scan | 名前 | GUID | 座標系 | 実在する座標フィールド | 全点フィールド | 点数 | 姿勢 | 関連画像数 |
| --- | ---: | --- | --- | --- | --- | --- | ---: | --- | ---: |
| 1102_202109110828_S16_000002.e57 | 0 | L01_000001 | 74d773d2-a041-4e10-97d6-b2595dc86c57 | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `cartesianX`, `cartesianY`, `cartesianZ`, `intensity`, `colorRed`, `colorGreen`, `colorBlue` | 2,048,592 | あり | 0 |
| 7701_202402130837_S21_000003.e57 | 0 | L01_000001 | 7093a9e9-4d05-40db-8c53-3f219b28417d | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `cartesianX`, `cartesianY`, `cartesianZ`, `intensity`, `colorRed`, `colorGreen`, `colorBlue` | 2,354,132 | あり | 0 |
| 7701_202402130837_S21_000003.e57 | 1 | L02_000000 | d440a9e5-43f9-458b-a504-7adde77270ee | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `cartesianX`, `cartesianY`, `cartesianZ`, `intensity`, `colorRed`, `colorGreen`, `colorBlue` | 19,482,126 | あり | 0 |
| 7701_202402130837_S21_000003.e57 | 2 | L01_000000 | c1c58930-3a68-41b6-a295-3fc12783b3f3 | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `cartesianX`, `cartesianY`, `cartesianZ`, `intensity`, `colorRed`, `colorGreen`, `colorBlue` | 19,013,596 | あり | 0 |
| 7701_202402130837_S21_000003.e57 | 3 | L02_000001 | a6cb1a0b-d3e6-49f3-b3c5-958efe10daca | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `cartesianX`, `cartesianY`, `cartesianZ`, `intensity`, `colorRed`, `colorGreen`, `colorBlue` | 1,727,154 | あり | 0 |
| 7701_202402131317_S20_000001.e57 | 0 | L01_000000 | 91990de7-e95d-4ffa-99f2-1fa2ccf44541 | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `cartesianX`, `cartesianY`, `cartesianZ`, `intensity`, `colorRed`, `colorGreen`, `colorBlue` | 22,075,008 | あり | 0 |
| 7701_202402131317_S20_000001.e57 | 1 | L02_000000 | 5119244b-af13-45c8-8dd4-f322266074c3 | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `cartesianX`, `cartesianY`, `cartesianZ`, `intensity`, `colorRed`, `colorGreen`, `colorBlue` | 21,186,196 | あり | 0 |
| EdoCastle_ShimizuGate_RIEGLE_EightScan.e57 | 0 | 250201_101535 | /20250201EdojoShimizumon/SCANS/ScanPos001/SINGLESCANS/250201_101535 | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `rlms:amplitude`, `intensity`, `rlms:reflectance`, `colorRed`, `colorGreen`, `colorBlue`, `nor:normalX`, `nor:normalY`, `nor:normalZ`, `cartesianX`, `cartesianY`, `cartesianZ` | 14,573,642 | あり | 7 |
| EdoCastle_ShimizuGate_RIEGLE_EightScan.e57 | 1 | 250201_101855 | /20250201EdojoShimizumon/SCANS/ScanPos002/SINGLESCANS/250201_101855 | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `rlms:amplitude`, `intensity`, `rlms:reflectance`, `colorRed`, `colorGreen`, `colorBlue`, `nor:normalX`, `nor:normalY`, `nor:normalZ`, `cartesianX`, `cartesianY`, `cartesianZ` | 13,127,681 | あり | 7 |
| EdoCastle_ShimizuGate_RIEGLE_EightScan.e57 | 2 | 250201_102110 | /20250201EdojoShimizumon/SCANS/ScanPos003/SINGLESCANS/250201_102110 | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `rlms:amplitude`, `intensity`, `rlms:reflectance`, `colorRed`, `colorGreen`, `colorBlue`, `nor:normalX`, `nor:normalY`, `nor:normalZ`, `cartesianX`, `cartesianY`, `cartesianZ` | 15,410,923 | あり | 7 |
| EdoCastle_ShimizuGate_RIEGLE_EightScan.e57 | 3 | 250201_102403 | /20250201EdojoShimizumon/SCANS/ScanPos004/SINGLESCANS/250201_102403 | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `rlms:amplitude`, `intensity`, `rlms:reflectance`, `colorRed`, `colorGreen`, `colorBlue`, `nor:normalX`, `nor:normalY`, `nor:normalZ`, `cartesianX`, `cartesianY`, `cartesianZ` | 14,560,199 | あり | 7 |
| EdoCastle_ShimizuGate_RIEGLE_EightScan.e57 | 4 | 250201_102828 | /20250201EdojoShimizumon/SCANS/ScanPos005/SINGLESCANS/250201_102828 | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `rlms:amplitude`, `intensity`, `rlms:reflectance`, `colorRed`, `colorGreen`, `colorBlue`, `nor:normalX`, `nor:normalY`, `nor:normalZ`, `cartesianX`, `cartesianY`, `cartesianZ` | 10,667,717 | あり | 7 |
| EdoCastle_ShimizuGate_RIEGLE_EightScan.e57 | 5 | 250201_103155 | /20250201EdojoShimizumon/SCANS/ScanPos006/SINGLESCANS/250201_103155 | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `rlms:amplitude`, `intensity`, `rlms:reflectance`, `colorRed`, `colorGreen`, `colorBlue`, `nor:normalX`, `nor:normalY`, `nor:normalZ`, `cartesianX`, `cartesianY`, `cartesianZ` | 11,188,238 | あり | 7 |
| EdoCastle_ShimizuGate_RIEGLE_EightScan.e57 | 6 | 250201_103406 | /20250201EdojoShimizumon/SCANS/ScanPos007/SINGLESCANS/250201_103406 | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `rlms:amplitude`, `intensity`, `rlms:reflectance`, `colorRed`, `colorGreen`, `colorBlue`, `nor:normalX`, `nor:normalY`, `nor:normalZ`, `cartesianX`, `cartesianY`, `cartesianZ` | 11,026,506 | あり | 7 |
| EdoCastle_ShimizuGate_RIEGLE_EightScan.e57 | 7 | 250201_103629 | /20250201EdojoShimizumon/SCANS/ScanPos008/SINGLESCANS/250201_103629 | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `rlms:amplitude`, `intensity`, `rlms:reflectance`, `colorRed`, `colorGreen`, `colorBlue`, `nor:normalX`, `nor:normalY`, `nor:normalZ`, `cartesianX`, `cartesianY`, `cartesianZ` | 11,638,216 | あり | 7 |
| EdoCastle_ShimizuGate_RIEGLE_EightScan.e57 | 8 | 250201_105139 | /20250201EdojoShimizumon/SCANS/ScanPos009/SINGLESCANS/250201_105139 | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `rlms:amplitude`, `intensity`, `rlms:reflectance`, `colorRed`, `colorGreen`, `colorBlue`, `nor:normalX`, `nor:normalY`, `nor:normalZ`, `cartesianX`, `cartesianY`, `cartesianZ` | 12,216,690 | あり | 0 |
| EdoCastle_ShimizuGate_RIEGLE_EightScan.e57 | 9 | 250201_105817 | /20250201EdojoShimizumon/SCANS/ScanPos009/SINGLESCANS/250201_105817 | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `rlms:amplitude`, `intensity`, `rlms:reflectance`, `colorRed`, `colorGreen`, `colorBlue`, `nor:normalX`, `nor:normalY`, `nor:normalZ`, `rowIndex`, `columnIndex`, `cartesianX`, `cartesianY`, `cartesianZ` | 904,068 | あり | 7 |
| EdoCastle_ShimizuGate_RIEGLE_EightScan.e57 | 10 | 250201_111924 | /20250201EdojoShimizumon/SCANS/ScanPos010/SINGLESCANS/250201_111924 | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `rlms:amplitude`, `intensity`, `rlms:reflectance`, `colorRed`, `colorGreen`, `colorBlue`, `nor:normalX`, `nor:normalY`, `nor:normalZ`, `rowIndex`, `columnIndex`, `cartesianX`, `cartesianY`, `cartesianZ` | 11,221,272 | あり | 7 |
| EdoCastle_ShimizuGate_RIEGLE_SingleScan.e57 | 0 | 250201_101855 | /20250201EdojoShimizumon/SCANS/ScanPos002/SINGLESCANS/250201_101855 | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `rlms:amplitude`, `intensity`, `rlms:reflectance`, `colorRed`, `colorGreen`, `colorBlue`, `nor:normalX`, `nor:normalY`, `nor:normalZ`, `cartesianX`, `cartesianY`, `cartesianZ` | 13,127,681 | あり | 7 |
| job53.e57 | 0 | ジョブ 053- Setup 068 | 0000000000000001 | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ`, `cartesianInvalidState` | `cartesianX`, `cartesianY`, `cartesianZ`, `intensity`, `colorRed`, `colorGreen`, `colorBlue`, `rowIndex`, `columnIndex`, `cartesianInvalidState` | 4,657,819 | あり | 6 |
| openpitmine.e57 | 0 | 110613_165007 | /OpenPitMine2/SCANS/ScanPos001/SINGLESCANS/110613_165007 | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `cartesianX`, `cartesianY`, `cartesianZ`, `rlms:amplitude`, `rlms:reflectance`, `colorRed`, `colorGreen`, `colorBlue` | 4,438,419 | あり | 0 |
| openpitmine.e57 | 1 | 110613_165955 | /OpenPitMine2/SCANS/ScanPos001/SINGLESCANS/110613_165955 | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `cartesianX`, `cartesianY`, `cartesianZ`, `rlms:amplitude`, `rlms:reflectance`, `colorRed`, `colorGreen`, `colorBlue` | 2,478 | あり | 0 |
| openpitmine.e57 | 2 | 110613_171059 | /OpenPitMine2/SCANS/ScanPos002/SINGLESCANS/110613_171059 | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `cartesianX`, `cartesianY`, `cartesianZ`, `rlms:amplitude`, `rlms:reflectance`, `colorRed`, `colorGreen`, `colorBlue` | 4,114,758 | あり | 0 |
| openpitmine.e57 | 3 | 110613_173251 | /OpenPitMine2/SCANS/ScanPos003/SINGLESCANS/110613_173251 | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `cartesianX`, `cartesianY`, `cartesianZ`, `rlms:amplitude`, `rlms:reflectance`, `colorRed`, `colorGreen`, `colorBlue` | 5,367,979 | あり | 0 |
| openpitmine.e57 | 4 | 110613_174259 | /OpenPitMine2/SCANS/ScanPos003/SINGLESCANS/110613_174259 | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `cartesianX`, `cartesianY`, `cartesianZ`, `rlms:amplitude`, `rlms:reflectance`, `colorRed`, `colorGreen`, `colorBlue` | 2,526 | あり | 0 |
| openpitmine.e57 | 5 | 110613_175510 | /OpenPitMine2/SCANS/ScanPos004/SINGLESCANS/110613_175510 | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `cartesianX`, `cartesianY`, `cartesianZ`, `rlms:amplitude`, `rlms:reflectance`, `colorRed`, `colorGreen`, `colorBlue` | 4,032,245 | あり | 0 |
| openpitmine.e57 | 6 | 110613_180332 | /OpenPitMine2/SCANS/ScanPos004/SINGLESCANS/110613_180332 | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `cartesianX`, `cartesianY`, `cartesianZ`, `rlms:amplitude`, `rlms:reflectance`, `colorRed`, `colorGreen`, `colorBlue` | 2,534 | あり | 0 |
| openpitmine.e57 | 7 | 110613_181622 | /OpenPitMine2/SCANS/ScanPos005/SINGLESCANS/110613_181622 | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `cartesianX`, `cartesianY`, `cartesianZ`, `rlms:amplitude`, `rlms:reflectance`, `colorRed`, `colorGreen`, `colorBlue` | 4,023,614 | あり | 0 |
| openpitmine.e57 | 8 | 110613_184058 | /OpenPitMine2/SCANS/ScanPos006/SINGLESCANS/110613_184058 | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `cartesianX`, `cartesianY`, `cartesianZ`, `rlms:amplitude`, `rlms:reflectance`, `colorRed`, `colorGreen`, `colorBlue` | 4,923,710 | あり | 0 |
| openpitmine.e57 | 9 | 110613_185050 | /OpenPitMine2/SCANS/ScanPos006/SINGLESCANS/110613_185050 | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `cartesianX`, `cartesianY`, `cartesianZ`, `rlms:amplitude`, `rlms:reflectance`, `colorRed`, `colorGreen`, `colorBlue` | 2,508 | あり | 0 |
| sample.e57 | 0 | L01_000001 | 74d773d2-a041-4e10-97d6-b2595dc86c57 | CARTESIAN | `cartesianX`, `cartesianY`, `cartesianZ` | `cartesianX`, `cartesianY`, `cartesianZ`, `intensity`, `colorRed`, `colorGreen`, `colorBlue` | 2,048,592 | あり | 0 |

## 画像表現の詳細

| E57ファイル | 画像表現 | 画像データ形式 | 関連付け結果 |
| --- | --- | --- | --- |
| 1102_202109110828_S16_000002.e57 | PINHOLE: 48 | PINHOLE/JPEG: 48 | 一致: 0, GUIDなし: 48, 不明GUID: 0 |
| 7701_202402130837_S21_000003.e57 | PINHOLE: 392, SPHERICAL: 49 | PINHOLE/JPEG: 392, SPHERICAL/JPEG: 49 | 一致: 0, GUIDなし: 441, 不明GUID: 0 |
| 7701_202402131317_S20_000001.e57 | PINHOLE: 448, SPHERICAL: 56 | PINHOLE/JPEG: 448, SPHERICAL/JPEG: 56 | 一致: 0, GUIDなし: 504, 不明GUID: 0 |
| EdoCastle_ShimizuGate_RIEGLE_EightScan.e57 | PINHOLE: 70 | PINHOLE/JPEG: 70 | 一致: 70, GUIDなし: 0, 不明GUID: 0 |
| EdoCastle_ShimizuGate_RIEGLE_SingleScan.e57 | PINHOLE: 7 | PINHOLE/JPEG: 7 | 一致: 7, GUIDなし: 0, 不明GUID: 0 |
| job53.e57 | PINHOLE: 6 | PINHOLE/JPEG: 6 | 一致: 6, GUIDなし: 0, 不明GUID: 0 |
| openpitmine.e57 | PINHOLE: 21 | PINHOLE/JPEG: 21 | 一致: 0, GUIDなし: 21, 不明GUID: 0 |
| sample.e57 | PINHOLE: 48 | PINHOLE/JPEG: 48 | 一致: 0, GUIDなし: 48, 不明GUID: 0 |

## 確認結果

- 全31スキャンの座標系内訳: CARTESIAN: 31。
- 姿勢情報があるスキャンは31/31件でした。
- 複数スキャンを含む全ファイルで、スキャン間の座標系は一致しました。
- `UNKNOWN／UNSUPPORTED` に分類されたスキャンはありませんでした。
- `SPHERICAL` 画像表現を含むファイル: `7701_202402130837_S21_000003.e57`, `7701_202402131317_S20_000001.e57`。これはパノラマ画像の表現形式であり、点群の座標系分類とは別です。
- `associatedData3DGuid` がない画像は合計1062件でした。
- 存在しないスキャンGUIDを参照する画像は合計0件でした。

## 判定上の注意

- `CARTESIAN` は `cartesianX`、`cartesianY`、`cartesianZ` の組を持つスキャンです。
- `SPHERICAL` は `sphericalRange`、`sphericalAzimuth`、`sphericalElevation` の組を持つスキャンです。
- `UNKNOWN／UNSUPPORTED` は `get_coordinate_system()` が上記の完全な組を判定できなかった場合です。
- 画像とスキャンの関連付けは、画像の `associatedData3DGuid` と `data3D` のGUIDが一致するかで判定しています。

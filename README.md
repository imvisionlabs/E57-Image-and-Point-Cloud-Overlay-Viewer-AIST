# E57 Fusion Viewer MVP v8

E57内の点群・画像・pinhole camera情報を展開し、画像上に点群を投影して重畳表示する簡易ソフトウェアです。


主な機能:

- `Open E57 and prepare` からE57を選択し、Viewer内で前処理を実行
- 点群と画像の重畳表示
- `point alpha` と `image alpha` の独立制御
- `Corrected CX`, `Corrected CY` を入力して主点ずれをViewer上で補正
- 補正値を `corrections.json` に保存
- 補正後のカメラメタデータを `corrected_cameras.json` として出力
- PyInstallerによるWindows exe配布用設定

## Setup with Anaconda

既に `e57-fusion-viewer` 環境を作成済みなら、v8フォルダで以下を実行してください。

```bat
conda activate e57-fusion-viewer
pip install -e .
```

または、

```bat
install_v8.bat
```

## Run

```bat
run_viewer.bat
```

Viewerが起動したら、`Open E57 and prepare` から `.e57` を選択できます。

## Principal point correction

右側の `Principal point correction` で、E57内の元のCX/CYを確認しながら、補正後のCX/CYを入力できます。

- `Corrected CX`: 補正後の principalPointX [px]
- `Corrected CY`: 補正後の principalPointY [px]
- `Delta CX/CY`: E57元値からの差分 [px]

`Save corrections.json + settings` で補正値と表示設定を保存します。

`Export corrected_cameras.json` を押すと、補正後のCX/CYを反映した `corrected_cameras.json` を出力します。これはE57本体の書き換えではなく、補正値確認用・次段階のE57再書き出し用メタデータです。

## Build Windows exe

```bat
build_exe.bat
```

成功すると、以下に配布用フォルダが作成されます。

```text
dist\E57FusionViewer\
  E57FusionViewer.exe
  _internal\
```

配布時は `dist\E57FusionViewer` フォルダ全体をZIP化してください。

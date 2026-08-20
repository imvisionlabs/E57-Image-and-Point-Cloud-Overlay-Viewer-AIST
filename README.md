# E57 Fusion Viewer

E57ファイルに含まれる点群・画像・pinhole camera情報を読み出し、画像上に点群を重ねて確認するWindows向けViewerです。

## 主な機能

- `.e57` をGUIから選択して、そのまま前処理・表示
- 画像と点群の重畳表示
- 画像ごとに関連するスキャンの点群を自動選択
- 点群・画像の透明度、点サイズ、表示点数を調整
- 画像上をクリックして、最寄り投影点のXYZ座標を表示
- 前処理済みデータセットの再読み込み
- PyInstallerによるWindows実行ファイルの作成

## 動作環境

- Windows 10 / 11
- Anaconda または Miniconda
- E57ファイルと前処理結果を保存できる空き容量

## リポジトリを取得する

GitHubの `Code` ボタンから `Download ZIP` を選んで展開するか、Gitが使える場合は表示されたURLをコピーして次を実行します。

```bat
git clone <コピーしたリポジトリURL>
```

以降の操作は、リポジトリのルート（このREADMEがあるフォルダ）で行います。初めて使う場合は **Anaconda Prompt** を開き、`cd` でこのフォルダへ移動してください。

```bat
cd C:\path\to\e57-fusion-viewer-AIST
```

## クイックスタート（初回のみ）

### 1. Conda環境を作成する

初回セットアップには、必要なパッケージだけを定義した `environment-minimal.yml` を使用します。

```bat
conda env create -f environment-minimal.yml
```

### 2. Conda環境を有効化する

```bat
conda activate e57-fusion-viewer
```

### 3. Viewerをインストールする

```bat
pip install -e .
```

### 4. Viewerを起動する

```bat
run_viewer.bat
```

2回目以降は、リポジトリのルートで `run_viewer.bat` を実行するだけです。このbatファイルが `e57-fusion-viewer` 環境を有効化してViewerを起動します。

## E57ファイルを表示する

1. Viewer右側の `Open E57 and prepare` を押します。
2. 表示したい `.e57` ファイルを選択します。
3. 前処理が完了するまで待ちます。大きいE57では時間がかかることがあります。
4. 前処理が完了すると、最初の画像と点群が自動的に表示されます。
5. `Image` のプルダウンから別の画像へ切り替えます。

前処理結果は、元のE57ファイルと同じ場所に次の名前で作成されます。

```text
<E57ファイル名>_prepared_dataset\
  cameras.json
  images\
  points.npz
  points_scan_000.npz  （複数スキャンの場合）
  points_scan_001.npz
  ...
```

同じE57を再度確認するときは `Open prepared dataset` を押し、上記の `_prepared_dataset` フォルダを選択すると、前処理を省略できます。

## 画面の設定項目

| 項目 | 説明 |
| --- | --- |
| `point alpha` | 点群の透明度を変更します。 |
| `image alpha` | 背景画像の透明度を変更します。 |
| `point size` | 描画する点の大きさを変更します。 |
| `max overlay points` | 画像に重ねて描画する点数の上限です。値を増やすと密になりますが、描画が重くなります。 |
| `prepare max points` | E57の各スキャンから前処理時に保存する点数の上限です。値を増やすと精細になりますが、処理時間と使用メモリが増えます。 |

画像上をクリックすると、クリック位置から15 px以内にある最寄り投影点のXYZ座標が右側に表示されます。

## 別の起動方法

Pythonモジュールとして直接起動することもできます。

```bat
conda activate e57-fusion-viewer
set PYTHONPATH=%CD%\src
python -m e57_fusion_viewer.main
```

前処理済みデータセットを起動時に開く場合は、フォルダのパスを引数に指定します。

```bat
python -m e57_fusion_viewer.main "C:\path\to\sample_prepared_dataset"
```

## 既存環境を更新する

依存パッケージの定義が更新された場合は、次を実行します。

```bat
conda env update -f environment-minimal.yml --prune
conda activate e57-fusion-viewer
pip install -e .
```

`install_v8.bat` でもViewerを再インストールできます。ただし、先に `e57-fusion-viewer` 環境を作成しておく必要があります。

## トラブルシューティング

### `conda` が認識されない

通常のコマンドプロンプトではなく **Anaconda Prompt** を使用してください。それでも認識されない場合は、AnacondaまたはMinicondaがインストールされているか確認してください。

### `EnvironmentNameNotFound: Could not find conda environment: e57-fusion-viewer` と表示される

Conda環境がまだ作成されていません。リポジトリのルートで次を実行してください。

```bat
conda env create -f environment-minimal.yml
```

### `ModuleNotFoundError` が表示される

環境を有効化してViewerを再インストールします。

```bat
conda activate e57-fusion-viewer
pip install -e .
```

### E57の前処理に失敗する

- E57ファイルが他のアプリで使用中でないか確認してください。
- 元のE57と同じフォルダに書き込み権限と十分な空き容量があるか確認してください。
- 大きいE57でメモリ不足になる場合は、GUIの `prepare max points` を小さくして再実行してください。
- 同名の `_prepared_dataset` フォルダが壊れている可能性がある場合は、必要に応じて退避してから再実行してください。

### 点群が表示されない、または画像と位置が合わない

画面右下のステータスで、投影点数と使用中の `points*.npz` を確認してください。E57の出力元によって、カメラ姿勢・座標軸・画像とスキャンの関連付けの記録方法が異なる場合があります。その場合、ファイルは読み込めても正しく重ならないことがあります。

このViewerの投影は、検証済みのPentax E57サンプルに合わせて次の規約を使用します。

- カメラ姿勢: camera-to-world
- カメラ前方: `-Z`
- カメラ座標の上方向: `+Y`
- 画像座標の下方向: `+V`
- 主点: E57に記録された `principalPointX` / `principalPointY` を保持

手動で投影規約や主点を補正する機能はありません。別の規約で出力されたE57では、出力元の仕様確認または変換処理が必要です。

## Windows実行ファイルを作成する

```bat
build_exe.bat
```

成功すると、次の配布用フォルダが作成されます。

```text
dist\E57FusionViewer\
  E57FusionViewer.exe
  _internal\
```

配布時は `dist\E57FusionViewer` フォルダ全体をZIP化してください。

## 完全固定した環境を使う場合

`environment-win64-explicit.txt` には、Win64向けのCondaパッケージが固定されています。再現性を優先する場合は次を使用します。

```bat
conda create -n e57-fusion-viewer --file environment-win64-explicit.txt
conda activate e57-fusion-viewer
pip install -r requirements.txt
pip install -e .
```

`pye57` などのpipパッケージは明示的ロックファイルに含まれないため、`pip install -r requirements.txt` を省略しないでください。

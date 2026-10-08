# ソース版のセットアップ

ソースコードからViewerを起動するための手順です。配布されたWindows実行ファイルを使用する場合は、[README](../README.md)を参照してください。

## 必要な環境

- 64-bit版Windows 10 / 11
- Anaconda または Miniconda
- 初回セットアップ時にパッケージを取得できるインターネット接続
- E57ファイルと前処理結果を保存できる空き容量

## リポジトリの準備

GitHubの `Code` ボタンから `Download ZIP` を選んで展開するか、Gitが使える場合は表示されたURLをコピーして次を実行します。

```bat
git clone <コピーしたリポジトリURL>
```

以降のコマンドは、すべてリポジトリのルート（`README.md` があるフォルダ）で実行します。**Anaconda Prompt** を開き、取得したフォルダへ移動してください。

```bat
cd /d C:\path\to\E57-Image-and-Point-Cloud-Overlay-Viewer-AIST
```

環境構築用の設定ファイルとスクリプトは `env/` にまとめています。コマンドを実行するために `env/` へ移動する必要はありません。

## 初回セットアップ

Win64向けのCondaパッケージを固定した `env/environment-win64-explicit.txt` から環境を作成します。

### 1. Conda環境を作成する

```bat
conda create -n e57-fusion-viewer --file env\environment-win64-explicit.txt
```

### 2. Conda環境を有効化する

```bat
conda activate e57-fusion-viewer
```

### 3. pip依存パッケージをインストールする

`pye57` など、Condaの明示的ロックファイルに含まれないパッケージをインストールします。この手順は省略しないでください。

```bat
python -m pip install -r env\requirements.txt
```

### 4. Viewerをインストールする

```bat
python -m pip install -e .
```

手順2〜4は、次のスクリプトでも実行できます。先に手順1で `e57-fusion-viewer` 環境を作成してください。

```bat
env\install.bat
```

`env/install.bat` は既存のConda環境を有効化し、pip依存パッケージとViewerをインストールします。

### 5. Viewerを起動する

```bat
run_viewer.bat
```

2回目以降も、リポジトリのルートで `run_viewer.bat` を実行します。このスクリプトが `e57-fusion-viewer` 環境を有効化してViewerを起動します。E57の表示手順と画面操作は[README](../README.md)を参照してください。

## Pythonモジュールとして起動する

```bat
conda activate e57-fusion-viewer
set PYTHONPATH=%CD%\src
python -m e57_fusion_viewer.main
```

前処理済みデータセットを起動時に開く場合は、フォルダのパスを引数に指定します。

```bat
python -m e57_fusion_viewer.main "C:\path\to\sample_prepared_dataset"
```

## 既存環境の更新

ソースコードまたはpip依存パッケージが更新された場合は、次を実行します。

```bat
env\install.bat
```

個別に実行する場合は、初回セットアップの手順2〜4と同じコマンドを使用します。

`env/environment-win64-explicit.txt` が更新された場合や環境が壊れた場合は、既存環境を削除して作り直してください。環境内に独自に追加したパッケージも削除されるため、必要な場合は事前に記録してください。

```bat
conda deactivate
conda env remove -n e57-fusion-viewer
conda create -n e57-fusion-viewer --file env\environment-win64-explicit.txt
env\install.bat
```

## 依存関係ファイルの役割

| ファイル | 用途 |
| --- | --- |
| `env/environment-win64-explicit.txt` | 初回セットアップで使用するWin64向けConda明示的ロックファイル。 |
| `env/requirements.txt` | Conda環境の作成後にインストールするpip依存パッケージ。 |
| `env/environment.yml` | 依存関係の保守・参照用。初回セットアップには使用しません。 |
| `pyproject.toml` | Viewerのパッケージ情報と依存関係を定義します。`pip install -e .` で使用します。 |

配布用EXEの作成方法は[ビルド手順](build.md)を参照してください。

## トラブルシューティング

### `conda` が認識されない

通常のコマンドプロンプトではなく **Anaconda Prompt** を使用してください。それでも認識されない場合は、AnacondaまたはMinicondaがインストールされているか確認してください。

### `EnvironmentNameNotFound: Could not find conda environment: e57-fusion-viewer` と表示される

Conda環境がまだ作成されていません。リポジトリのルートで次を実行してください。

```bat
conda create -n e57-fusion-viewer --file env\environment-win64-explicit.txt
env\install.bat
```

### `ModuleNotFoundError` が表示される

依存パッケージとViewerを再インストールします。

```bat
env\install.bat
```

E57の前処理や表示に関するトラブルは[README](../README.md)を参照してください。

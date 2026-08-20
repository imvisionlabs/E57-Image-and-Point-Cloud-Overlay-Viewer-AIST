# E57 Fusion Viewer MVP v8

E57内の点群・画像・pinhole camera情報を展開し、画像上に点群を投影して重畳表示する簡易ソフトウェアです。


主な機能:

- `Open E57 and prepare` からE57を選択し、Viewer内で前処理を実行
- 点群と画像の重畳表示
- `point alpha` と `image alpha` の独立制御
- 画像上のクリックで最寄り投影点のXYZを表示
- PyInstallerによるWindows exe配布用設定

投影規約はPentax E57サンプルで検証した組み合わせ（pose=cam→world、front=-Z、V軸反転あり）に固定しています。

## Setup with Anaconda

### 新規に環境を作成する場合

方法A: `environment.yml` で conda依存 + pip依存(pye57, pyinstaller等)をまとめて構築（推奨・簡単）

```bat
conda env create -n e57-fusion-viewer -f environment.yml
conda activate e57-fusion-viewer
pip install -e .
```

既に同名環境がある場合は `conda env create` の代わりに以下で更新できます。

```bat
conda env update -n e57-fusion-viewer -f environment.yml --prune
```

方法B: `environment-win64-explicit.txt` でconda側バイナリを完全固定してから、pipで残りを補完

```bat
conda create -n e57-fusion-viewer --file environment-win64-explicit.txt
conda activate e57-fusion-viewer
pip install -r requirements.txt
pip install -e .
```

`environment-win64-explicit.txt` はWin64向けのconda-forgeバイナリのみを固定したロックファイルで、`pye57` などのpip専用パッケージは含まれていません。`requirements.txt` で必ず補ってください。

### 既に `e57-fusion-viewer` 環境を作成済みの場合

v8フォルダで以下を実行してください。

```bat
conda activate e57-fusion-viewer
pip install -e .
```

または、

```bat
install_v8.bat
```

> `install_v8.bat` / `run_viewer.bat` は環境名 `e57-fusion-viewer` を前提にしています。別名の環境を使う場合は、上記コマンドを手動で実行するか、環境名を `e57-fusion-viewer` に合わせてください。

## Run

```bat
run_viewer.bat
```

Viewerが起動したら、`Open E57 and prepare` から `.e57` を選択できます。

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

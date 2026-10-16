# Windows実行ファイルのビルド

ソースコードから配布用フォルダを作成するための手順です。生成物の起動方法とViewerの操作は[README](../README.md)を参照してください。

## 必要な環境

- 64-bit版Python 3.11を利用できるWindows PC
- 初回ビルド時にパッケージを取得できるインターネット接続

以降のコマンドは、すべてリポジトリのルート（`README.md` があるフォルダ）で実行します。

## ビルドする

```bat
env\build_exe.bat
```

`env/build_exe.bat` は利用可能なPythonを自動検出し、通常はリポジトリのルートにビルド専用の `.build-venv/` を作成します。必要なパッケージをインストールし、PyInstallerを実行します。2回目以降は正常な `.build-venv/` を再利用します。

ビルド用の中間ファイルはルートの `build/`、配布用ファイルはルートの `dist/` に作成されます。

ビルド完了時には、Viewer本体、QtのWindows用プラグイン、E57前処理ツール、pye57のネイティブモジュール、アプリケーションアイコンが含まれていることを確認します。これらのファイル確認に失敗した場合、ビルドはエラーとして終了します。

## 生成したEXEの依存関係を確認する

生成したEXEを起動する依存関係テストは、次のように明示的に有効化できます。

```bat
set E57_RUN_EXE_SMOKE_TEST=1
env\build_exe.bat
```

このテストでは、画面を開かずにパッケージ内の依存関係を読み込みます。通常のビルドでは、生成したEXEを実行するテストは省略されます。

組織のDevice Guardなどが未署名EXEの実行を制限しているPCでは、このテストを有効にしないでください。実行をブロックされた場合は、組織のサポート担当者へコード署名や利用許可について確認してください。

設定を解除する場合は、次を実行します。

```bat
set E57_RUN_EXE_SMOKE_TEST=
```

## 配布するファイル

成功すると、次のフォルダが作成されます。

```text
dist\E57-Image-and-Point-Cloud-Overlay-Viewer\
  E57-Image-and-Point-Cloud-Overlay-Viewer.exe
  _internal\
  LICENSE
  THIRD_PARTY_NOTICES.md
  third_party_licenses\
```

`E57-Image-and-Point-Cloud-Overlay-Viewer` フォルダ全体を配布してください。EXEと `_internal` フォルダは同じ場所に置く必要があります。配布先PCにPython、Conda、pipをインストールする必要はありません。

## ビルド関連ファイル

| ファイル | 用途 |
| --- | --- |
| `env/build_exe.bat` | ビルド環境の準備、PyInstallerの実行、生成物の確認。 |
| `env/viewer.spec` | 同梱するツール・画像・依存ライブラリなどのPyInstaller設定。 |
| `env/run_viewer_packaged.py` | 配布用EXEの起動処理と依存関係テスト。 |
| `env/requirements.txt` | ビルド環境にインストールする依存パッケージ。 |

ソースコードからViewerを直接起動する場合は[セットアップ手順](setup.md)を参照してください。

## ライセンス文書と対応ソース

ビルド時に `env/collect_licenses.py` がライセンス文書を収集します。
Qt／PySide6／Shiboken6 6.11.1、pye57 0.4.19に対応する文書を同梱しており、
新規環境にはこのバージョンをインストールします。既存環境でバージョンが異なる場合は
停止します。更新する際は、対応する文書とソースも準備してください。
OpenSSLはビルド環境のバージョンに対応する `OpenSSL-<バージョン>-NOTICES.txt` が必要です。

不要なQt PDF・仮想キーボードのプラグインを除外し、他のアプリのDLLが混入しないよう
DLL探索用PATHを限定しています。想定外のQtモジュールが含まれる場合は停止します。
ビルド完了後、`third_party_licenses/INDEX.md` でバージョン・ライセンス文書・DLL配置を
確認してください。収集に失敗した出力は配布せず、不足を解消して再ビルドしてください。

公開するZIPにはライセンス文書も含め、LGPL対象部品の対応ソースと必要なビルド情報を
同じRelease等で提供します。詳細は[第三者ソフトウェアの説明](../THIRD_PARTY_NOTICES.md)を
参照し、ソースの取得とライブラリの差し替え、実データでの操作を確認してから公開してください。

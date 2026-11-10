# コード

[English](README.md)

| パス | 内容 |
|---|---|
| `verify/v0_inputs.py` | ハッシュ、メタデータ、全行列ファイルの形状、各 Gram 行列の基本事項。標準ライブラリのみ |
| `verify/v1_action.py` | 生成元が各形式を保つこと。GAP とそのパッケージ SmallGrp で、S が −1 を含み SL(2,29) と同型であること、生成する群が記載の位数であること。GAP ありで約 7 分。`--no-gap` は終了コード 2 |
| `verify/v2_construction.py` | `data/Wb2/` から L112.03-14 を組み立て直す。`data/U112/` の L112.15 の構造。約 30 秒 |
| `verify/quick.sh` | 上の 3 つを実行。すべて実行して通ったときだけ 0、失敗で 1、GAP が無く群の構造を検査しなかったときは 2 |
| `verify/preflight.sh` | Python が古いか、ツリーが `SHA256SUMS` と違うときに、長い実行をすぐ止める |
| `lib/report.py` | `require` と記録 `out/<step>.json`（コードと入力のハッシュ、ソフトウェアの版、判定） |
| `lib/data.py` | 行列（形状も検査）、entry、`SHA256SUMS` の読み込み |
| `lib/exact.py` | 整数の厳密な線形代数。形状の合わない行列はエラー |
| `lib/__init__.py` | パッケージの印 |
| `tests/` | `conftest.py`, `test_docs.py`, `test_layout.py`, `test_v0.py`, `test_v1_v2.py`, `test_quick.py`。`python3 -m pytest code/tests` で実行（pytest が必要） |

スクリプトは失敗を非ゼロの終了コードで伝えます。`out/` のファイルはその判定の記録です。段の開始時に古いファイルを消すので、途中で止まった実行が以前の結果を残すことはなく、`"passed": false` が残ります。検査を省いた実行は `"incomplete": true` となり、合格とは記録されません。

`verify/` は `lib/` だけを使い、`lib/` は `code/` の他の部分を使いません。`tests/test_layout.py` で確かめます。

CI（`.github/workflows/checks.yml`）は Python 3.11, 3.12, 3.13 で `verify/v0_inputs.py`, `verify/v2_construction.py` と試験を実行し、GAP を入れて `verify/quick.sh` を実行します。

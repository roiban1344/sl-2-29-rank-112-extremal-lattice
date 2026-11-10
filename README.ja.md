# SL₂(29) 作用をもつ112次元格子

[English](README.md)

112次元の14個の極値偶ユニモジュラー格子として提示する L112.01–L112.14 と、最小値が未決の候補 L112.15 の Gram 行列と構造化データを収録する、作業中のリポジトリです。**この版には証明を掲載していません。** 極値性・相異性・分類を確かめるための材料は順次追加し、それぞれどこまで確かめられているかを明記します（[STATUS.ja.md](STATUS.ja.md)）。このリポジトリの内容について、独立した人間によるレビューは受けていません。

L112.01 には[別リポジトリの公開版 v2026-10-19.1](https://github.com/roiban1344/112-dimensional-extremal-even-unimodular-lattice/tree/v2026-10-19.1)に計算機援用証明のパッケージがあります。L112.02–L112.14 の極値性は研究計算の結果を記録したもので、確かめるための材料はこの版に含めていません。L112.02 に使った方法は監査を受けていません。L112.03–L112.14 では、列挙が短いベクトルを見落とさないという論証の一部が未解決です。L112.15 の極値性は主張しません。

Ivan Gauvin 氏が、L112.02 の最小値が 10 であることの[独立な計算機援用検証](https://github.com/Katabolanga/l112-02-independent-verification/tree/a78893f59d532f9da1b6cb192b8336ceb8acfd45)を公開しています。L112.01 のパッケージの方法を拡張し、その区間演算の列挙器を使っています。そのうえで、この列挙以外の主な検査の第 2 の実装、同じ凍結データからの別の機械での検証器の再実行、最後の演繹の Lean による検査を加えています。査読は受けておらず、AI アシスタントを使ったと明記されています。

15件の整数 Gram 行列、各格子に作用する群の生成元、L112.01–14 のノルム 10 のベクトル、構造データ、構造化データを収録します。L112.01–L112.15 は各行列を識別する固定 ID です。全項目は [lattices/index.json](lattices/index.json)、形式と状態ラベルは [docs/schema.md](docs/schema.md) に記載します。

整数係数の行ベクトル x のノルム（長さの2乗）は x G xᵀ です。112次元の極値偶ユニモジュラー格子の最小ノルムは10です。Gram ファイルは `#` で始まるコメント行を除くと112行×112列で、空白区切りの10進整数です。

## 検査

Python 3.11 以上（標準ライブラリのみ）と、パッケージ SmallGrp を入れた [GAP](https://www.gap-system.org/) で `bash code/verify/quick.sh` を実行します（約 8 分）。GAP 4.12.1 と SmallGrp 1.5.3（Ubuntu 24.04 のパッケージ `gap-core`, `gap-libs`, `gap-smallgrp`）、および GAP 4.15.1 と SmallGrp 1.5.4 で実行を確かめています。GAP が無いと終了コード 2 で終わり、実行しなかった検査を表示します。SmallGrp が無いと失敗し、その旨を表示します。使った版は `out/v1_action.json` に記録されます。

| スクリプト | 厳密に検査する内容 |
|---|---|
| `code/verify/v0_inputs.py` | ファイルのハッシュ、メタデータ、全行列ファイルの形状。各 Gram 行列が対称、正定値、偶、行列式 1 であること。L112.01–14 にノルム 10 のベクトルがあること |
| `code/verify/v1_action.py` | 生成元が各形式を保つこと。うち 2 つが −1 を含み SL₂(29) と同型な群を生成し、作用が PSL₂(29) を経由しないこと。全体が記載の位数の群を生成すること |
| `code/verify/v2_construction.py` | L112.03–14 を `data/Wb2/` の基礎の格子から組み立て、公開行列と一致すること。`data/U112/` の L112.15 の構造 |

**これらの検査は、最小値の下界・相異性・分類を確かめるものではありません。** 全自己同型群や kissing number の主張はこの版には含めません。

## ファイル

| パス | 内容 |
|---|---|
| `lattices/` | `index.json` と、格子ごとの `gram.txt`, `entry.toml`, `generators.txt`, `norm10.txt`（L112.01–14） |
| `data/` | 構造を定める行列。[data/README.ja.md](data/README.ja.md) を参照 |
| `docs/schema.md` | データの形式と状態の欄 |
| `docs/construction.md`, `docs/construction.ja.md` | 検査から主張を導く議論 |
| `code/` | 検査のコードとその試験。[code/README.ja.md](code/README.ja.md) を参照 |
| `SHA256SUMS` | 自身を除く全ファイルのハッシュ |
| `STATUS.md`, `STATUS.ja.md` | 各主張をどこまで確かめたか |
| `CONTRIBUTING.md`, `CONTRIBUTING.ja.md`, `.github/ISSUE_TEMPLATE/*.yml` | 誤りの報告の仕方 |
| `CHANGELOG.md`, `CHANGELOG.ja.md` | 読み手に関わる変更 |
| `CITATION.cff`, `LICENSE` | 引用とライセンス |
| `.github/workflows/checks.yml`, `.gitignore` | CI、git の管理から外すファイル |

## クレジット

roiban1344 が作業を指揮しました。研究計算と草稿は Claude（Anthropic）と進め、このデータ版の組み立てと検査器は OpenAI Codex と Claude で作成しました。データ・文書は CC BY 4.0、コードは MIT です。[LICENSE](LICENSE)、[CITATION.cff](CITATION.cff) を参照し、利用時にはコミットまたは公開タグを指定してください。

# 変更履歴

読み手に関わる変更を記します。[English](CHANGELOG.md)

## 未公開

- 検査器を `check/check.py` から `code/verify/v0_inputs.py` に移しました。検査の内容は同じで、記録を `out/v0_inputs.json` に書くようになりました。`SHA256SUMS` に載せればファイルを追加できます。
- メタデータの形式を第 2 版にしました（`docs/schema.md`）。`proof_in_this_release` と `extremality_status` を、表 `extremality` の `method`, `package`, `review` に置き換えました。Gram 行列のパスとハッシュは変わりません。
- 各格子に作用する群の生成元（`generators.txt`）、L112.01–14 のノルム 10 のベクトル（`norm10.txt`）、`data/` のデータ、検査 `code/verify/v1_action.py`, `code/verify/v2_construction.py`, `code/verify/quick.sh` を追加しました。
- `STATUS.ja.md`（各主張をどこまで確かめたか）、`docs/construction.ja.md`（検査から主張を導く議論）、`CONTRIBUTING.ja.md`、issue テンプレートを追加しました。
- L112.02 の entry に Ivan Gauvin 氏の独立な検証を引用しました（`independent_check`）。

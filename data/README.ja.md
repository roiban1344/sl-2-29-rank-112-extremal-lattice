# データ

[English](README.md)

格子の構造を定める共有の行列です。ベクトルは整数の行ベクトルで、行列は右から作用します。`#` で始まる行はコメントです。

| ファイル | 内容 |
|---|---|
| `Wb2/base-gram.txt` | 56 次元の格子 B0 の Gram 行列 b。行列式 29⁴⁸。スケールした双対 (B0^#, 29 b) は Nebe の L_{56,6}（*Some cyclo-quaternionic lattices*, 1998） |
| `Wb2/base-S.txt` | B0 上の S = SL₂(29) の 2 つの生成元 |
| `Wb2/base-order.txt` | S の交換子環（3 と ∞ で分岐する ℚ 上の四元数環）の極大整環の ℤ 基底 |
| `Wb2/L112.<j>-basis.txt` | 29·Bz。Bz の行は B0 ⊥ B0 の座標での L112.j（j = 03–14）の基底 |
| `Wb2/L112.<j>-lll.txt` | U。`gram.txt` = Uᵀ (Bz bb Bzᵀ) U で、bb は b ⊥ b |
| `U112/sqrt5.txt` | L112.15 への √5 の作用 |
| `U112/b0-gram.txt` | S 不変な形式 G0。`gram.txt` = T_s G0 で、T_s は s = 1/348 − √5/1740 による乗法の行列 |

`code/verify/v2_construction.py` がこれらを `lattices/` と照合します。B0 のスケールした双対が L_{56,6} であること、`base-order.txt` の行列がその四元数環の極大整環の ℤ 基底であることは検査しません。検査するのは、行列が 4 つあり S と可換であることだけです。この 2 つの主張の根拠となる論証と計算はこの版に含めていません。

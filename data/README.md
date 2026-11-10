# Data

[日本語](README.ja.md)

Shared matrices that define the structures of the lattices. Vectors are integer row vectors and matrices act on the right. Lines beginning with `#` are comments.

| File | Contents |
|---|---|
| `Wb2/base-gram.txt` | Gram matrix b of the 56-dimensional lattice B0, of determinant 29⁴⁸. The rescaled dual (B0^#, 29 b) is Nebe's L_{56,6} (*Some cyclo-quaternionic lattices*, 1998) |
| `Wb2/base-S.txt` | Two generators of S = SL₂(29) on B0 |
| `Wb2/base-order.txt` | A ℤ-basis of the maximal order of the commutant of S, a quaternion algebra over ℚ ramified at 3 and ∞ |
| `Wb2/L112.<j>-basis.txt` | 29·Bz, where the rows of Bz are a basis of L112.j (j = 03–14) in the coordinates of B0 ⊥ B0 |
| `Wb2/L112.<j>-lll.txt` | U, with `gram.txt` = Uᵀ (Bz bb Bzᵀ) U, where bb is b ⊥ b |
| `U112/sqrt5.txt` | The action of √5 on L112.15 |
| `U112/b0-gram.txt` | The S-invariant form G0 with `gram.txt` = T_s G0, where T_s is the matrix of multiplication by s = 1/348 − √5/1740 |

`code/verify/v2_construction.py` checks these against `lattices/`. It does not check that the rescaled dual of B0 is L_{56,6}, or that the matrices of `base-order.txt` are a ℤ-basis of a maximal order of that quaternion algebra; it checks only that there are four of them and that they commute with S. These two statements rest on arguments and computations that are not in this release.

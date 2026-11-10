# Status of each statement

[日本語](STATUS.ja.md)

This repository is being prepared to support the following statement.

> There are 14 or 15 isometry classes of positive definite even unimodular lattices of rank 112 and minimum norm 10 whose automorphism group contains a subgroup isomorphic to SL₂(29). Fourteen are given explicitly (L112.01–14), and the only further possibility is L112.15.

**This statement is not established by the current contents.** No step has had independent human review. The tables below give the status of each statement.

Notation: S is a group isomorphic to SL₂(29), and −1 is its central element of order 2. W_a, W_b and U_112 are three rational irreducible S-modules on which −1 acts as −1, determined by their characters:

- W_a, of dimension 56, has character 2(ψ + ψ′), where ψ and ψ′ are the two complex irreducible characters of degree 14. Its endomorphism algebra is a totally definite quaternion algebra over ℚ(√29).
- W_b, of dimension 56, has character 2χ, where χ is the rational-valued irreducible character of degree 28 with Frobenius–Schur indicator −1. Its endomorphism algebra is the quaternion algebra over ℚ ramified at 3 and ∞.
- U_112, of dimension 112, has character 2(χ′ + χ″), where χ′ and χ″ are the two irreducible characters of degree 28 with character field ℚ(√5) and indicator −1.

W_a², W_b² and U_112 are the module types of the [next section](#module-types). The arguments behind the rows marked "checked here" are in [docs/construction.md](docs/construction.md).

| Label | Meaning |
|---|---|
| checked here | Exact computation that you can run from this repository: in integers, or in GAP on the reduction modulo 3, which is injective on these groups |
| computer-assisted proof | A written reduction and an exhaustive computation with error control, which can be re-run from its package |
| computed | A research computation whose result is recorded. It is not a proof in the sense above, and the material for checking it is not here unless stated |
| written, not complete | An argument exists, but it has not been checked in full. The table names the main steps still open |
| open | Undecided |

## Properties of the distributed matrices

| Statement | Label | Evidence |
|---|---|---|
| The 15 Gram matrices are symmetric, positive definite, even and of determinant 1 | checked here | `code/verify/v0_inputs.py` |
| Two of the listed generators of each lattice generate a group isomorphic to SL₂(29) that contains −1 and preserves the form, so the action does not factor through PSL₂(29). This concerns the 15 distributed lattices only | checked here | `code/verify/v1_action.py` (GAP and its package SmallGrp, on the reduction modulo 3) |
| All listed generators of each lattice generate a group of the order in its entry. This does not say that the group is the full automorphism group | checked here | `code/verify/v1_action.py` (GAP) |
| L112.01–14 have a vector of norm 10, so their minima are at most 10 | checked here | `code/verify/v0_inputs.py` |
| From the distributed bases, L112.03–14 are computed in B0 ⊥ B0 and equal the published matrices. For L112.15, √5 acts integrally and compatibly with S and the form, I + √5 is even, and G = T_s G0 for a symmetric form G0, where T_s is the matrix of multiplication by s = 1/348 − √5/1740 ([data/README.md](data/README.md)) | checked here | `code/verify/v2_construction.py`. Not checked: that the rescaled dual of B0 is Nebe's L_{56,6}, and that the four commuting matrices are a basis of a maximal order |

## Module types

| Statement | Label | Evidence and limits |
|---|---|---|
| If S acts faithfully on an extremal even unimodular lattice L of rank 112, then L ⊗ ℚ is isomorphic, as a ℚS-module, to W_a², W_b² or U_112. In particular −1 acts on L as −1 | written, not complete | Not included here. An automorphism of order 29 of such a lattice has no non-zero fixed vector (Nebe 2013, §4, with Blichfeldt's bound for the Hermite constant). By the character table this leaves twelve module types, including those on which −1 acts trivially or with a fixed space of dimension 56. Nine are excluded: in five, L is the orthogonal sum of two even unimodular lattices of rank 56, so its minimum is at most 6; in three, L has a vector of norm at most 8; and the irreducible module of dimension 112 on which −1 acts trivially carries no unimodular lattice. The exclusions use computations not published here, among them composition factors and images of the group ring modulo primes (MeatAxe) and explicit short vectors. For W_a ⊕ W_b, one step (that the 3-adic image of the group ring on W_a is a maximal order) rests on a theorem of Reiner whose fit to this case has not been checked. No human review |
| L112.01–02 lie in W_a², L112.03–14 in W_b² and L112.15 in U_112 | computed | Not checked here: the type follows from how each lattice was constructed, and that construction is not published here. The check that −1 ∈ S for the distributed lattices (above) is consistent with these types but does not determine them |

## Minimum norms

| Statement | Label | Evidence and limits |
|---|---|---|
| L112.01 has minimum 10 | computer-assisted proof | [Separate package, release v2026-10-19.1](https://github.com/roiban1344/112-dimensional-extremal-even-unimodular-lattice/tree/v2026-10-19.1). Not reviewed by a person. The package's `data/R112_gram_LLL.txt` has the same integer rows as `lattices/L112.01/gram.txt`; no script here checks this |
| L112.02 has minimum 10 | computed | Not included here. The method of the research computation has not been audited. Ivan Gauvin has published an [independent computer-assisted verification](https://github.com/Katabolanga/l112-02-independent-verification/tree/a78893f59d532f9da1b6cb192b8336ceb8acfd45). It extends the method of the L112.01 package and shares its interval enumerator, and it is not peer-reviewed. It states that AI assistants were used and that its only review was within its team. Its code has not been run for this repository. The argument for the statement at the top of this page does not use this verification; it uses the research computation of this row |
| L112.03–14 have minimum 10 | computed | Not included here. The computation uses a floating-point enumerator with a written error bound. Whether the enumerator visits every short vector is still open: the argument from the code has not been reviewed or machine-checked, and the re-run with the corrected enumerator has not been published here |
| The minimum of L112.15 | open | The statement at the top of this page does not need it |

## The count

| Statement | Label | Evidence and limits |
|---|---|---|
| L112.01–14 are pairwise non-isometric. With the minimum norms in the table above, this would give at least 14 classes | written, not complete | Not included here. The argument determines the automorphism groups using the classification of finite simple groups, through the tables of Hiss and Malle (2001; corrigenda 2002), together with exact enumerations of isometries. No human has read it, and the correspondence with the literature and the public re-run of the enumerations are not finished |
| Any further lattice is isometric to L112.15, so there are at most 15 classes | written, not complete | Not included here, including the computations that exclude the other candidates. No part has had human review. The argument starts from the module types above. The main steps still open are how the mass formula of Gan, Hanke and Yu (2001, Prop. 9.4) applies to W_a² and that the eight classes exhaust the genus, and the correspondence between invariant lattices and maximal isotropic subspaces of the 29-adic discriminant module for W_b² |

## References

These are the works on which the steps above that are not complete depend. [docs/construction.md](docs/construction.md) has its own list.

- H. F. Blichfeldt, *The minimum value of quadratic forms, and the closest packing of spheres*, Math. Ann. 101 (1929), 605–608. <https://doi.org/10.1007/BF01454863>
- W. T. Gan, J. P. Hanke, J.-K. Yu, *On an exact mass formula of Shimura*, Duke Math. J. 107 (2001), 103–133, Prop. 9.4. <https://doi.org/10.1215/S0012-7094-01-10716-3>
- G. Hiss, G. Malle, *Low-dimensional representations of quasi-simple groups*, LMS J. Comput. Math. 4 (2001), 22–63. <https://doi.org/10.1112/S1461157000000796>
- G. Hiss, G. Malle, *Corrigenda: Low-dimensional representations of quasi-simple groups*, LMS J. Comput. Math. 5 (2002), 95–126. <https://doi.org/10.1112/S1461157000000711>
- G. Nebe, *On automorphisms of extremal even unimodular lattices*, Int. J. Number Theory 9 (2013), 1933–1959, §4, Definition 4.1 and Lemma 4.3. <https://doi.org/10.1142/S179304211350067X>
- I. Reiner, *Maximal Orders*, London Math. Soc. Monographs, New Series 28, Oxford University Press, 2003, Theorem 39.14. <https://doi.org/10.1093/oso/9780198526735.001.0001>

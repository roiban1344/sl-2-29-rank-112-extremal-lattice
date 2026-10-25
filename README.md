# Rank 112 lattices with an SL₂(29) action

[日本語](README.ja.md)

This repository is a work in progress. It contains Gram matrices and structured metadata for L112.01–L112.14, presented as fourteen extremal even unimodular lattices of rank 112, and L112.15, a further candidate whose minimum is open. **Proofs are not included in this release.** Proofs of extremality, non-isometry and classification, together with verification code, will be added in stages. No independent human review has been completed.

For L112.01, a computer-assisted proof package is already available in the [separate repository, release v2026-10-19.1](https://github.com/roiban1344/112-dimensional-extremal-even-unimodular-lattice/tree/v2026-10-19.1). For L112.02–L112.14, extremality is recorded from research computations; their proof packages are not included here. L112.15 is not asserted to be extremal.

The release contains 15 integer Gram matrices and structured metadata. IDs L112.01–L112.15 identify the distributed matrices and will remain stable. [lattices/index.json](lattices/index.json) contains all entries. See [docs/schema.md](docs/schema.md) for formats and status labels.

For a row vector of integer coefficients x, the norm (squared length) is x G xᵀ. An extremal even unimodular lattice of rank 112 has minimum norm 10. After ignoring lines beginning with `#`, each Gram file has 112 rows of 112 whitespace-separated decimal integers.

Run `python3 check/check.py` with Python 3.11 or later (standard library only). It checks all file hashes, metadata consistency, symmetry, positive definiteness, evenness and determinant 1 using exact integer arithmetic. **These checks do not establish the minimum, non-isometry, the group action or classification.** No claim about the full automorphism groups or kissing numbers is part of this data release.

The work was directed by roiban1344. Research computations and drafts were developed with Claude (Anthropic); this data packaging and checker were prepared with OpenAI Codex. Data and text: CC BY 4.0; code: MIT. See [LICENSE](LICENSE) and [CITATION.cff](CITATION.cff). Cite a specific commit or release tag when using the data.

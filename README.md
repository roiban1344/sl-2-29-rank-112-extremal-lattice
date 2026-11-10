# Rank 112 lattices with an SL₂(29) action

[日本語](README.ja.md)

This repository is a work in progress. It contains Gram matrices and structured metadata for L112.01–L112.14, presented as fourteen extremal even unimodular lattices of rank 112, and L112.15, a further candidate whose minimum is open. **Proofs are not included in this release.** Material for checking extremality, non-isometry and classification will be added in stages, each labelled with how far it has been checked ([STATUS.md](STATUS.md)). The contents of this repository have not had independent human review.

For L112.01, a computer-assisted proof package is already available in the [separate repository, release v2026-10-19.1](https://github.com/roiban1344/112-dimensional-extremal-even-unimodular-lattice/tree/v2026-10-19.1). For L112.02–L112.14, extremality is recorded from research computations and the material for checking it is not included here. The method used for L112.02 has not been audited. For L112.03–L112.14, the argument that the enumeration misses no short vector is still open in part. L112.15 is not asserted to be extremal.

Ivan Gauvin has published an [independent computer-assisted verification](https://github.com/Katabolanga/l112-02-independent-verification/tree/a78893f59d532f9da1b6cb192b8336ceb8acfd45) that L112.02 has minimum 10. It extends the method and uses the interval enumerator of the L112.01 package. It adds a second implementation of the main checks other than that enumeration, a re-run of the verifiers on a second machine from the same frozen data, and a Lean check of the final deduction. It is not peer-reviewed, and it states that AI assistants were used.

The release contains 15 integer Gram matrices, generators of a group acting on each, vectors of norm 10 for L112.01–14, structure data and structured metadata. IDs L112.01–L112.15 identify the distributed matrices and will remain stable. [lattices/index.json](lattices/index.json) contains all entries. See [docs/schema.md](docs/schema.md) for formats and status labels.

For a row vector of integer coefficients x, the norm (squared length) is x G xᵀ. An extremal even unimodular lattice of rank 112 has minimum norm 10. After ignoring lines beginning with `#`, each Gram file has 112 rows of 112 whitespace-separated decimal integers.

## Checks

Run `bash code/verify/quick.sh` with Python 3.11 or later (standard library only) and [GAP](https://www.gap-system.org/) with its package SmallGrp (about 8 minutes). It has been run with GAP 4.12.1 and SmallGrp 1.5.3 (the Ubuntu 24.04 packages `gap-core`, `gap-libs` and `gap-smallgrp`), and with GAP 4.15.1 and SmallGrp 1.5.4. Without GAP it ends with status 2 and says what was not run; without SmallGrp it fails and says so. The versions used are written to `out/v1_action.json`.

| Script | What it checks, exactly |
|---|---|
| `code/verify/v0_inputs.py` | File hashes, metadata and the shape of every matrix file. Each Gram matrix is symmetric, positive definite, even, of determinant 1. L112.01–14 have a vector of norm 10 |
| `code/verify/v1_action.py` | The generators preserve each form. Two of them generate a group isomorphic to SL₂(29) containing −1, so the action does not factor through PSL₂(29). All of them generate a group of the stated order |
| `code/verify/v2_construction.py` | L112.03–14 are rebuilt from the base lattice in `data/Wb2/` and equal the published matrices. The structure of L112.15 in `data/U112/` |

**These checks do not establish a lower bound on any minimum, non-isometry or the classification.** No claim about the full automorphism groups or kissing numbers is part of this release.

## Files

| Path | Contents |
|---|---|
| `lattices/` | `index.json` and, for each lattice, `gram.txt`, `entry.toml`, `generators.txt` and `norm10.txt` (L112.01–14) |
| `data/` | Matrices that define the structures; see [data/README.md](data/README.md) |
| `docs/schema.md` | Data format and status fields |
| `docs/construction.md`, `docs/construction.ja.md` | The arguments that turn the checks into statements |
| `code/` | Verification code and its tests; see [code/README.md](code/README.md) |
| `SHA256SUMS` | Hashes of every file in the release except itself |
| `STATUS.md`, `STATUS.ja.md` | How far each statement has been checked |
| `CONTRIBUTING.md`, `CONTRIBUTING.ja.md`, `.github/ISSUE_TEMPLATE/*.yml` | How to report an error |
| `CHANGELOG.md`, `CHANGELOG.ja.md` | Changes that affect readers of this repository |
| `CITATION.cff`, `LICENSE` | Citation and license |
| `.github/workflows/checks.yml`, `.gitignore` | Continuous integration; files left out of git |

## Credits

The work was directed by roiban1344. Research computations and drafts were developed with Claude (Anthropic); this data packaging and checker were prepared with OpenAI Codex and Claude. Data and text: CC BY 4.0; code: MIT. See [LICENSE](LICENSE) and [CITATION.cff](CITATION.cff). Cite a specific commit or release tag when using the data.

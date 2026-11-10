# Changelog

Changes that affect readers of this repository. [日本語](CHANGELOG.ja.md)

## Unreleased

- The checker moved from `check/check.py` to `code/verify/v0_inputs.py`. It checks the same facts, and also writes a record to `out/v0_inputs.json`. Files may now be added if `SHA256SUMS` lists them.
- Metadata format version 2 (see `docs/schema.md`). The fields `proof_in_this_release` and `extremality_status` are replaced by the table `extremality`, with the fields `method`, `package` and `review`. The paths of the Gram matrices and their hashes do not change.
- Added generators of a group acting on each lattice (`generators.txt`), vectors of norm 10 for L112.01–14 (`norm10.txt`), the data in `data/`, and the checks `code/verify/v1_action.py`, `code/verify/v2_construction.py` and `code/verify/quick.sh`.
- Added `STATUS.md` (how far each statement has been checked), `docs/construction.md` (the arguments that turn the checks into statements), `CONTRIBUTING.md` and issue templates.
- The entry of L112.02 cites the independent verification by Ivan Gauvin (`independent_check`).

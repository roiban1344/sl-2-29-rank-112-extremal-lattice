# Code

[日本語](README.ja.md)

| Path | Contents |
|---|---|
| `verify/v0_inputs.py` | Hashes, metadata, the shape of every matrix file and basic facts about each Gram matrix. Standard library only |
| `verify/v1_action.py` | The generators preserve each form; with GAP and its package SmallGrp, S is SL(2,29) with -1 in S, and the generated group has the stated order. About 7 minutes with GAP. `--no-gap` ends with status 2 |
| `verify/v2_construction.py` | Rebuilds L112.03-14 from `data/Wb2/`; the structure of L112.15 in `data/U112/`. About 30 seconds |
| `verify/quick.sh` | Runs the three above. Status 0 only if all ran and passed, 1 on a failure, 2 if GAP is missing and the group structure was not checked |
| `verify/preflight.sh` | Stops a long run at once if Python is too old or the tree differs from `SHA256SUMS` |
| `lib/report.py` | `require`, and the record `out/<step>.json` with the hashes of code and inputs, the software versions and the verdict |
| `lib/data.py` | Reads matrices, checking their shape, entries and `SHA256SUMS` |
| `lib/exact.py` | Exact integer linear algebra; a matrix of the wrong shape is an error |
| `lib/__init__.py` | Marks the package |
| `tests/` | `conftest.py`, `test_docs.py`, `test_layout.py`, `test_v0.py`, `test_v1_v2.py`, `test_quick.py`. Run with `python3 -m pytest code/tests` (needs pytest) |

A script reports failure by a non-zero exit status. The file in `out/` is the record of that verdict: an old file is deleted when a step starts, so a run that stops early leaves `"passed": false`, not an earlier result. A run that skipped checks has `"incomplete": true` and does not say passed.

`verify/` imports only `lib/`, and `lib/` imports nothing else from `code/`. `tests/test_layout.py` checks this.

CI (`.github/workflows/checks.yml`) runs `verify/v0_inputs.py`, `verify/v2_construction.py` and the tests on Python 3.11, 3.12 and 3.13, and `verify/quick.sh` with GAP.

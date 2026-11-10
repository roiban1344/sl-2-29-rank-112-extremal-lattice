# Reporting errors

[日本語](CONTRIBUTING.ja.md)

Reports of errors and of failed reproductions are very welcome, in English or Japanese.

## How to report

Open an [issue](https://github.com/roiban1344/sl-2-29-rank-112-extremal-lattice/issues/new/choose) and choose a template:

- **Mathematical error**: an error in a statement, a label or a computation. Give the commit or tag you read, the location, and why it fails.
- **Verification fails or cannot be run**: a check that fails, or instructions that do not work. Include the command, its full output, `out/<step>.json` if one was written, and your environment.
- **Text or documentation**: unclear wording, a wrong citation, a missing explanation, or a difference between the English and Japanese versions.

## What happens after a report

1. The report is acknowledged in the issue, and its effect on the statements in [STATUS.md](STATUS.md) is assessed there.
2. A correction is made in a pull request that refers to the issue.
3. [CHANGELOG.md](CHANGELOG.md) records the correction, and whether a statement or a label changed. Earlier commits and tags are kept, so every cited version stays available.

## Pull requests

Pull requests are welcome for documentation and code. For a change that affects a statement or a label, please open an issue first. The IDs L112.01–L112.15 identify the distributed matrices and do not change. Update `SHA256SUMS` for any file you change or add, or the checks fail:

```
git ls-files | grep -v '^SHA256SUMS$' | LC_ALL=C sort | xargs sha256sum > SHA256SUMS
```

CI runs `v0_inputs.py`, `v2_construction.py` and the tests on Python 3.11–3.13, and `quick.sh` with GAP, on pull requests.

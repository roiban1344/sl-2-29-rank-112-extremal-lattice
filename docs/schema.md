# Data format (schema version 1)

`lattices/L112.XX/entry.toml` is the canonical metadata entry. `lattices/index.json` is an ordered array of the same entries, without loss of fields. Text is UTF-8. Gram matrices use row coefficients: the norm is x G xᵀ. Ignore `#` comment lines; the remaining 112 lines each contain 112 decimal integers.

- `schema_version`, `id`, `dimension`, `gram`: format version, stable ID, rank and local Gram filename.
- `gram_sha256`: hash of the distributed Gram file.
- `properties`: exact checks of positive definiteness, evenness and determinant. The checker verifies these against the distributed integers.
- `proof_in_this_release`: false for all entries.
- `extremality_status`: `external-computer-assisted-proof` for L112.01 (see README link); `computed-proof-not-included` for L112.02–14; `open` for L112.15.
- `claims.minimal_norm`: 10 for L112.01–14, a research claim rather than an output of the included checker. Omitted for L112.15, whose minimum is unknown. Its `claims` table is empty (an empty object in JSON).

Distinct IDs do not certify pairwise non-isometry. `SHA256SUMS` covers every distributed file except itself. The checker also enforces the complete file inventory; extra files are errors. This release does not distribute group generators or certify the SL₂(29) action.

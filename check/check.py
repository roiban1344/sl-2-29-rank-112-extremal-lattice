#!/usr/bin/env python3
"""Verify the data release using Python 3.11+ and exact integer arithmetic."""
import hashlib
import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDS = [f'L112.{i:02d}' for i in range(1, 16)]
FIXED = {'README.md', 'README.ja.md', 'LICENSE', 'CITATION.cff', 'docs/schema.md',
         'lattices/index.json', 'check/check.py', 'SHA256SUMS'}
EXPECTED = FIXED | {f'lattices/{i}/{f}' for i in IDS for f in ('gram.txt', 'entry.toml')}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify():
    files = set()
    for p in ROOT.rglob('*'):
        rel = p.relative_to(ROOT)
        if rel.parts[0] == '.git':
            continue
        require(not p.is_symlink(), f'symlink forbidden: {rel}')
        if p.is_file():
            files.add(rel.as_posix())
    require(files == EXPECTED, f'file inventory mismatch: {files ^ EXPECTED}')
    sums = {}
    for line in (ROOT / 'SHA256SUMS').read_text().splitlines():
        digest, name = line.split('  ', 1)
        require(name not in sums, f'duplicate checksum: {name}')
        sums[name] = digest
    require(set(sums) == EXPECTED - {'SHA256SUMS'}, 'checksum inventory mismatch')
    for name, digest in sums.items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, f'hash: {name}')
    index = json.loads((ROOT / 'lattices/index.json').read_text())
    require([e['id'] for e in index] == IDS, 'index IDs')
    for number, ident in enumerate(IDS, 1):
        directory = ROOT / 'lattices' / ident
        e = tomllib.loads((directory / 'entry.toml').read_text())
        require(e == index[number - 1], f'entry/index mismatch: {ident}')
        require(set(e) == {'schema_version', 'id', 'dimension', 'gram', 'gram_sha256',
                          'proof_in_this_release', 'extremality_status', 'properties', 'claims'}, 'entry keys')
        require(e['id'] == ident and e['schema_version'] == 1 and e['dimension'] == 112, 'identity')
        require(e['gram'] == 'gram.txt' and e['proof_in_this_release'] is False, 'release status')
        require(e['properties'] == {'positive_definite': True, 'even': True, 'determinant': 1}, 'properties')
        expected_status = ('external-computer-assisted-proof' if number == 1 else
                           'computed-proof-not-included' if number < 15 else 'open')
        require(e['extremality_status'] == expected_status, 'extremality status')
        require(e['claims'] == ({'minimal_norm': 10} if number < 15 else {}), 'minimum claim')
        require(e['gram_sha256'] == sums[f'lattices/{ident}/gram.txt'], 'Gram hash metadata')
        lines = (directory / 'gram.txt').read_text().splitlines()
        G = [[int(t) for t in line.split()] for line in lines if line and not line.startswith('#')]
        require(len(G) == 112 and all(len(r) == 112 for r in G), 'matrix dimensions')
        require(all(G[i][j] == G[j][i] for i in range(112) for j in range(i)), 'symmetry')
        require(all(G[i][i] % 2 == 0 for i in range(112)), 'even diagonal')
        # Fraction-free elimination without pivoting: each pivot is a leading principal minor.
        M = [row[:] for row in G]
        previous = 1
        for k in range(112):
            pivot = M[k][k]
            require(pivot > 0, f'positive definiteness: {ident}, pivot {k}')
            for i in range(k + 1, 112):
                for j in range(k + 1, 112):
                    value, remainder = divmod(M[i][j] * pivot - M[i][k] * M[k][j], previous)
                    require(remainder == 0, 'nonexact Bareiss division')
                    M[i][j] = value
            previous = pivot
        require(previous == 1, f'determinant: {ident}')
        print(f'{ident}: hashes, metadata, symmetric 112 x 112, positive definite, even, determinant 1: PASS', flush=True)
    print('ALL PASSED. Minimum, non-isometry, group structure and classification are not checked.')


if __name__ == '__main__':
    try:
        verify()
    except (ValueError, KeyError, OSError, TypeError) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        sys.exit(1)

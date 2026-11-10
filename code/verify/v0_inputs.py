#!/usr/bin/env python3
"""Basic facts about the distributed data, using Python 3.11+ and exact integer arithmetic.

Checks all file hashes, the metadata, the shape of every matrix file, and for each Gram matrix: symmetric,
112 x 112, positive definite, even, determinant 1. For L112.01-14 it checks a vector of norm 10, which bounds the minimum
from above only. It does not check the lower bound, non-isometry, the group action or the classification.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.data import IDS, LATTICES, check_sums, read_entry, read_index, read_matrices, read_matrix  # noqa: E402
from lib.exact import is_even_unimodular_positive  # noqa: E402
from lib.report import REPO, CheckFailed, Report, require  # noqa: E402

KEYS = {'schema_version', 'id', 'dimension', 'gram', 'generators', 'gram_sha256', 'properties', 'claims', 'extremality', 'group'}
# The status of each lattice in this release. A change of status has to be made here as well as in the
# entry, so that it cannot happen by accident.
STATUS = {'L112.01': {'method': 'computer-assisted', 'package': 'external', 'review': 'none',
                      'package_url': 'https://github.com/roiban1344/112-dimensional-extremal-even-unimodular-lattice/tree/v2026-10-19.1'},
          'L112.02': {'method': 'computed', 'package': 'not-included', 'review': 'none'},
          **{f'L112.{k:02d}': {'method': 'computed', 'package': 'not-included', 'review': 'internal-ai'} for k in range(3, 15)},
          'L112.15': {'method': 'open', 'package': 'none', 'review': 'none'}}
INDEPENDENT_CHECK = {'L112.02': {
    'author': 'Ivan Gauvin',
    'repository': 'https://github.com/Katabolanga/l112-02-independent-verification',
    'commit': 'a78893f59d532f9da1b6cb192b8336ceb8acfd45',
    'result': 'minimal norm 10',
}}


# The shape of each matrix file of data/: rows x columns, or a list of n x n matrices.
SHAPES = {'data/Wb2/base-gram.txt': (56, 56), 'data/Wb2/base-S.txt': (2, 56), 'data/Wb2/base-order.txt': (4, 56),
          'data/U112/sqrt5.txt': (112, 112), 'data/U112/b0-gram.txt': (112, 112),
          **{f'data/Wb2/{i}-{name}.txt': (112, 112) for i in IDS[2:14] for name in ('basis', 'lll')}}
LISTS = {'data/Wb2/base-S.txt', 'data/Wb2/base-order.txt'}


def check_shapes():
    for name, (rows, columns) in SHAPES.items():
        if name in LISTS:
            require(len(read_matrices(REPO / name, columns)) == rows, f'{name}: {rows} matrices')
        else:
            read_matrix(REPO / name, rows, columns)
    for ident in IDS:
        read_matrices(LATTICES / ident / 'generators.txt', 112)


def check_entry(ident, entry, sums):
    keys = KEYS | ({'independent_check'} if ident in INDEPENDENT_CHECK else set())
    keys |= {'witness_norm10'} if ident != 'L112.15' else set()
    require(set(entry) == keys, f'{ident}: entry keys')
    require(entry.get('independent_check') == INDEPENDENT_CHECK.get(ident), f'{ident}: independent check')
    require(entry['id'] == ident and entry['schema_version'] == 2 and entry['dimension'] == 112, f'{ident}: identity')
    require(entry['gram'] == 'gram.txt' and entry['generators'] == 'generators.txt', f'{ident}: file names')
    require(entry.get('witness_norm10') == (None if ident == 'L112.15' else 'norm10.txt'), f'{ident}: witness file name')
    require(set(entry['group']) == {'generated_order'} and entry['group']['generated_order'] > 0, f'{ident}: group')
    require(entry['gram_sha256'] == sums[f'lattices/{ident}/gram.txt'], f'{ident}: Gram hash metadata')
    require(entry['properties'] == {'positive_definite': True, 'even': True, 'determinant': 1}, f'{ident}: properties')
    require(entry['extremality'] == STATUS[ident], f'{ident}: extremality status')
    # A minimum is claimed exactly when the method is not open.
    claims = {} if STATUS[ident]['method'] == 'open' else {'minimal_norm': 10}
    require(entry['claims'] == claims, f'{ident}: minimum claim')


def check_gram(ident):
    matrix = read_matrix(LATTICES / ident / 'gram.txt', 112, 112)
    size = len(matrix)
    require(all(matrix[i][j] == matrix[j][i] for i in range(size) for j in range(i)), f'{ident}: symmetry')
    require(is_even_unimodular_positive(matrix), f'{ident}: positive definite, even, determinant 1')
    if ident != 'L112.15':
        vector = read_matrix(LATTICES / ident / 'norm10.txt', 1, size)
        w = vector[0]
        norm = sum(w[i] * matrix[i][j] * w[j] for i in range(size) for j in range(size))
        require(norm == 10, f'{ident}: the witness has norm {norm}')


def run(report):
    sums = check_sums(REPO)
    report.check(True, f'SHA256SUMS: {len(sums)} files, inventory and hashes')
    check_shapes()
    report.check(True, f'the shape of {len(SHAPES)} matrix files in data/ and of {len(IDS)} generator files')
    index = read_index()
    require([entry['id'] for entry in index] == IDS, 'index IDs')
    for ident, indexed in zip(IDS, index):
        entry = read_entry(ident)
        require(entry == indexed, f'{ident}: entry differs from the index')
        check_entry(ident, entry, sums)
        check_gram(ident)
        report.check(True, f'{ident}: metadata; symmetric 112 x 112, positive definite, even, determinant 1' + ('' if ident == 'L112.15' else '; a vector of norm 10'))


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out', help='directory of the JSON record (default: out/)')
    args = parser.parse_args()
    # SHA256SUMS fixes every other input.
    report = Report('v0_inputs', [__file__], [REPO / 'SHA256SUMS'], args.out)
    try:
        run(report)
    except (CheckFailed, ArithmeticError, KeyError, ValueError, OSError, TypeError) as error:
        return report.fail(error)
    status = report.finish()
    print('ALL PASSED. The lower bound on the minimum, non-isometry, the group action and the classification are not checked.')
    return status


if __name__ == '__main__':
    sys.exit(main())

"""Read the distributed data."""
import json
import tomllib
from pathlib import Path

from lib.report import REPO, require, sha256_file

LATTICES = REPO / 'lattices'
IDS = [f'L112.{i:02d}' for i in range(1, 16)]
# Generated or local directories at the top of the tree, which are not distributed.
NOT_DISTRIBUTED = {'.git', 'out', '.pytest_cache', '.venv'}
# Files without which the tree is not this release.
REQUIRED = {'README.md', 'README.ja.md', 'LICENSE', 'CITATION.cff', 'CHANGELOG.md', 'CHANGELOG.ja.md',
            'docs/schema.md', 'lattices/index.json', 'data/README.md', 'data/README.ja.md',
            'data/U112/sqrt5.txt', 'data/U112/b0-gram.txt',
            'data/Wb2/base-gram.txt', 'data/Wb2/base-S.txt', 'data/Wb2/base-order.txt',
            'code/verify/v0_inputs.py', 'code/verify/v1_action.py', 'code/verify/v2_construction.py',
            'code/verify/quick.sh', 'code/verify/preflight.sh',
            'code/lib/data.py', 'code/lib/exact.py', 'code/lib/report.py'}
REQUIRED |= {f'lattices/{i}/{name}' for i in IDS for name in ('gram.txt', 'entry.toml', 'generators.txt')}
REQUIRED |= {f'lattices/{i}/norm10.txt' for i in IDS[:14]}
REQUIRED |= {f'data/Wb2/{i}-{name}.txt' for i in IDS[2:14] for name in ('basis', 'lll')}


def read_matrix(path, rows=None, columns=None):
    """An integer matrix from a text file, one row per line, ignoring empty lines and lines beginning with #.

    All rows have one length; with rows and columns given, the matrix has that shape.
    """
    matrix = []
    for line in Path(path).read_text().splitlines():
        if line and not line.startswith('#'):
            matrix.append([int(token) for token in line.split()])
    name = display_name(path)
    lengths = sorted({len(row) for row in matrix})
    require(len(lengths) <= 1, f'{name}: rows of lengths {lengths}')
    if rows is not None:
        found = (len(matrix), lengths[0] if lengths else 0)
        require(found == (rows, columns), f'{name}: shape {found[0]} x {found[1]}, expected {rows} x {columns}')
    return matrix


def display_name(path):
    """The path relative to the tree, for messages."""
    path = Path(path)
    return path.relative_to(REPO).as_posix() if path.is_relative_to(REPO) else path.name


def read_entry(ident):
    return tomllib.loads((LATTICES / ident / 'entry.toml').read_text())


def read_index():
    return json.loads((LATTICES / 'index.json').read_text())


def distributed_files(root=REPO):
    """Every distributed file, as a path relative to the root. Symbolic links are refused."""
    files = set()
    for path in Path(root).rglob('*'):
        relative = path.relative_to(root)
        if relative.parts[0] in NOT_DISTRIBUTED:
            continue
        require(not path.is_symlink(), f'symbolic link in the tree: {relative}')
        if relative.parts[0] == 'code' and '__pycache__' in relative.parts:
            continue
        if path.is_file():
            files.add(relative.as_posix())
    return files


def read_sums(path):
    """The name -> hash table of a SHA256SUMS file; a repeated name is an error."""
    sums = {}
    for line in Path(path).read_text().splitlines():
        digest, name = line.split('  ', 1)
        require(name not in sums, f'duplicate checksum: {name}')
        sums[name] = digest
    return sums


def check_sums(root=REPO):
    """SHA256SUMS lists every distributed file but itself, each with the right hash."""
    sums = read_sums(Path(root) / 'SHA256SUMS')
    expected = distributed_files(root) - {'SHA256SUMS'}
    require(set(sums) == expected, f'file inventory differs from SHA256SUMS: {sorted(set(sums) ^ expected)}')
    require(REQUIRED <= expected, f'file inventory lacks required files: {sorted(REQUIRED - expected)}')
    lattices = {name.split('/')[1] for name in expected if name.startswith('lattices/') and name.count('/') > 1}
    require(lattices == set(IDS), f'file inventory: unexpected lattices {sorted(lattices ^ set(IDS))}')
    for name, digest in sums.items():
        require(sha256_file(Path(root) / name) == digest, f'hash: {name}')
    return sums


def read_matrices(path, size):
    """All the size x size matrices of a text file, one row per line, in order."""
    rows = read_matrix(path)
    require(all(len(row) == size for row in rows) and len(rows) % size == 0,
            f'{display_name(path)}: not a list of {size} x {size} matrices')
    return [rows[k:k + size] for k in range(0, len(rows), size)]


def read_generators(ident):
    """The (label, matrix) pairs of lattices/<id>/generators.txt."""
    path = LATTICES / ident / 'generators.txt'
    labels = [line[len('# generator:'):].strip() for line in path.read_text().splitlines()
              if line.startswith('# generator:')]
    matrices = read_matrices(path, 112)
    require(len(labels) == len(matrices), f'{ident}: one label for each generator')
    require(len(matrices) >= 2, f'{ident}: at least the two generators of S')
    return list(zip(labels, matrices))

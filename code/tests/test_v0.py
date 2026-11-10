"""v0_inputs passes on the tree and fails, with status 1 and the right reason, when anything is changed."""
import json
import shutil
import subprocess
import sys

import pytest

from conftest import REPO
from lib.exact import determinant, inverse, is_even_unimodular_positive, leading_minors, multiply, transpose
from lib.report import sha256_file


def copy_tree(target):
    ignore = shutil.ignore_patterns('.git', 'out', '__pycache__', '.pytest_cache', '.venv')
    shutil.copytree(REPO, target, ignore=ignore)
    return target


def run_v0(root):
    return subprocess.run([sys.executable, '-I', str(root / 'code/verify/v0_inputs.py')],
                          capture_output=True, text=True)


def rehash(root, *names):
    path = root / 'SHA256SUMS'
    lines = []
    for line in path.read_text().splitlines():
        digest, listed = line.split('  ', 1)
        lines.append(f'{sha256_file(root / listed) if listed in names else digest}  {listed}')
    path.write_text('\n'.join(lines) + '\n')


def add_to_sums(root, name):
    with (root / 'SHA256SUMS').open('a') as stream:
        stream.write(f'{sha256_file(root / name)}  {name}\n')


def assert_fails(root, message):
    result = run_v0(root)
    assert result.returncode == 1 and message in result.stderr, result.stderr
    assert json.loads((root / 'out/v0_inputs.json').read_text())['passed'] is False


@pytest.fixture
def root(tmp_path):
    return copy_tree(tmp_path / 'repo')


def test_v0_passes_and_records(root):
    result = run_v0(root)
    assert result.returncode == 0, result.stderr
    record = json.loads((root / 'out/v0_inputs.json').read_text())
    assert record['passed'] and len(record['checks']) == 17
    assert 'code/lib/report.py' in record['code']


def test_changed_file_is_rejected(root):
    with (root / 'lattices/L112.03/gram.txt').open('a') as stream:
        stream.write('# comment\n')
    assert_fails(root, 'hash: lattices/L112.03/gram.txt')


def test_unlisted_file_is_rejected(root):
    (root / 'extra.txt').write_text('x')
    assert_fails(root, 'file inventory differs')


@pytest.mark.parametrize('name', ['README.md', 'LICENSE', 'docs/schema.md', 'lattices/L112.07/gram.txt', 'lattices/L112.15/generators.txt', 'data/U112/sqrt5.txt', 'data/Wb2/L112.09-basis.txt', 'code/verify/quick.sh', 'code/verify/v1_action.py'])
def test_required_file_cannot_be_removed_even_from_the_sums(root, name):
    (root / name).unlink()
    sums = root / 'SHA256SUMS'
    sums.write_text(''.join(line for line in sums.read_text().splitlines(True) if not line.endswith(f'  {name}\n')))
    assert_fails(root, 'lacks required files')


def test_listed_extra_lattice_is_rejected(root):
    (root / 'lattices/L112.16').mkdir()
    (root / 'lattices/L112.16/gram.txt').write_text('x')
    add_to_sums(root, 'lattices/L112.16/gram.txt')
    assert_fails(root, 'unexpected lattices')


@pytest.mark.parametrize('directory', ['lattices/L112.03/out', 'lattices/.venv', 'docs/__pycache__'])
def test_generated_names_are_only_excused_where_they_belong(root, directory):
    (root / directory).mkdir()
    (root / directory / 'gram.txt').write_text('x')
    assert_fails(root, 'file inventory differs')


def test_symbolic_link_is_rejected(root):
    (root / 'lattices/out').mkdir()
    (root / 'lattices/out/link').symlink_to(root / 'README.md')
    assert_fails(root, 'symbolic link')


def test_missing_sums_leaves_a_failure_record(root):
    (root / 'SHA256SUMS').unlink()
    assert_fails(root, 'SHA256SUMS')


def edit_entry(root, ident, old, new):
    """Change an entry and the index in the same way and fix the hashes, so that only the check of the value can fail."""
    entry = root / 'lattices' / ident / 'entry.toml'
    text = entry.read_text()
    assert old in text
    entry.write_text(text.replace(old, new))
    index = root / 'lattices/index.json'
    data = json.loads(index.read_text())
    position = int(ident[-2:]) - 1
    key, old_value = (part.strip().strip('"') for part in old.split('='))
    _, new_value = (part.strip().strip('"') for part in new.split('='))
    table = data[position]
    for section in ('extremality', 'independent_check'):
        if section in table and key in table[section]:
            assert table[section][key].startswith(old_value)
            table[section][key] = table[section][key].replace(old_value, new_value)
    index.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    rehash(root, f'lattices/{ident}/entry.toml', 'lattices/index.json')


@pytest.mark.parametrize('ident, old, new, message', [
    ('L112.15', 'method = "open"', 'method = "computed"', 'L112.15: extremality status'),
    ('L112.03', 'method = "computed"', 'method = "computer-assisted"', 'L112.03: extremality status'),
    ('L112.03', 'package = "not-included"', 'package = "included"', 'L112.03: extremality status'),
    ('L112.02', 'review = "none"', 'review = "internal-ai"', 'L112.02: extremality status'),
    ('L112.01', 'review = "none"', 'review = "internal-ai"', 'L112.01: extremality status'),
    ('L112.02', 'commit = "a78893f', 'commit = "b78893f', 'L112.02: independent check'),
])
def test_status_values_are_pinned(root, ident, old, new, message):
    edit_entry(root, ident, old, new)
    assert_fails(root, message)


def edit_table(root, ident, old, new, change):
    """Change one line of an entry, apply `change` to the same value in the index, and fix the hashes."""
    entry = root / 'lattices' / ident / 'entry.toml'
    text = entry.read_text()
    assert old in text
    entry.write_text(text.replace(old, new))
    index = root / 'lattices/index.json'
    data = json.loads(index.read_text())
    change(data[int(ident[-2:]) - 1])
    index.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    rehash(root, f'lattices/{ident}/entry.toml', 'lattices/index.json')


@pytest.mark.parametrize('old, new, change, message', [
    ('gram = "gram.txt"', 'gram = "g.txt"', lambda e: e.update(gram='g.txt'), 'file names'),
    ('generators = "generators.txt"', 'generators = "g.txt"', lambda e: e.update(generators='g.txt'), 'file names'),
    ('witness_norm10 = "norm10.txt"', 'witness_norm10 = "w.txt"', lambda e: e.update(witness_norm10='w.txt'), 'witness file name'),
    ('generated_order = 48720', 'generated_order = 0', lambda e: e['group'].update(generated_order=0), ': group'),
    ('minimal_norm = 10', 'minimal_norm = 8', lambda e: e['claims'].update(minimal_norm=8), 'minimum claim'),
])
def test_other_entry_fields_are_checked(root, old, new, change, message):
    edit_table(root, 'L112.03', old, new, change)
    assert_fails(root, message)


@pytest.mark.parametrize('old, new, change, message', [
    ('schema_version = 2', 'schema_version = 1', lambda e: e.update(schema_version=1), ': identity'),
    ('dimension = 112', 'dimension = 111', lambda e: e.update(dimension=111), ': identity'),
    ('id = "L112.03"', 'id = "L112.04"', lambda e: e.update(id='L112.04'), 'index IDs'),
    ('determinant = 1', 'determinant = 2', lambda e: e['properties'].update(determinant=2), ': properties'),
    ('dimension = 112', 'dimension = 112\nextra = 1', lambda e: e.update(extra=1), ': entry keys'),
])
def test_identity_fields_are_checked(root, old, new, change, message):
    edit_table(root, 'L112.03', old, new, change)
    assert_fails(root, message)


def test_gram_hash_metadata_is_checked(root):
    entry = root / 'lattices/L112.03/entry.toml'
    old = next(line for line in entry.read_text().splitlines() if line.startswith('gram_sha256'))
    edit_table(root, 'L112.03', old, 'gram_sha256 = "' + 64 * '0' + '"', lambda e: e.update(gram_sha256=64 * '0'))
    assert_fails(root, 'Gram hash metadata')


def test_index_order_is_checked(root):
    index = root / 'lattices/index.json'
    data = json.loads(index.read_text())
    data[2], data[3] = data[3], data[2]
    index.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    rehash(root, 'lattices/index.json')
    assert_fails(root, 'index IDs')


def test_wrong_witness_is_rejected(root):
    path = root / 'lattices/L112.06/norm10.txt'
    lines = path.read_text().splitlines()
    k = next(i for i, line in enumerate(lines) if not line.startswith('#'))
    tokens = lines[k].split()
    tokens[0] = str(int(tokens[0]) + 1)
    lines[k] = ' '.join(tokens)
    path.write_text('\n'.join(lines) + '\n')
    rehash(root, 'lattices/L112.06/norm10.txt')
    assert_fails(root, 'L112.06: the witness has norm')


def test_short_witness_is_rejected(root):
    path = root / 'lattices/L112.06/norm10.txt'
    path.write_text('1 0 0\n')
    rehash(root, 'lattices/L112.06/norm10.txt')
    assert_fails(root, 'lattices/L112.06/norm10.txt: shape 1 x 3, expected 1 x 112')


def edit_first_row(path, change):
    lines = path.read_text().splitlines()
    k = next(i for i, line in enumerate(lines) if line and not line.startswith('#'))
    lines[k] = change(lines[k])
    path.write_text('\n'.join(lines) + '\n')


@pytest.mark.parametrize('name, change, message', [
    ('data/Wb2/L112.03-basis.txt', lambda line: line + ' 987654321', 'data/Wb2/L112.03-basis.txt: rows of lengths [112, 113]'),
    ('data/Wb2/L112.09-lll.txt', lambda line: line.rsplit(' ', 1)[0], 'data/Wb2/L112.09-lll.txt: rows of lengths [111, 112]'),
    ('data/U112/sqrt5.txt', lambda line: '', 'data/U112/sqrt5.txt: shape 111 x 112, expected 112 x 112'),
    ('data/Wb2/base-gram.txt', lambda line: '', 'data/Wb2/base-gram.txt: shape 55 x 56, expected 56 x 56'),
    ('data/Wb2/base-S.txt', lambda line: '', 'data/Wb2/base-S.txt: not a list of 56 x 56 matrices'),
    ('lattices/L112.07/generators.txt', lambda line: line + ' 0', 'lattices/L112.07/generators.txt: rows of lengths [112, 113]'),
])
def test_matrix_file_of_the_wrong_shape_is_rejected(root, name, change, message):
    edit_first_row(root / name, change)
    rehash(root, name)
    assert_fails(root, message)


def test_entry_differing_from_the_index_is_rejected(root):
    entry = root / 'lattices/L112.03/entry.toml'
    entry.write_text(entry.read_text().replace('review = "internal-ai"', 'review = "none"'))
    rehash(root, 'lattices/L112.03/entry.toml')
    assert_fails(root, 'entry differs from the index')


def edit_gram(root, ident, change):
    path = root / 'lattices' / ident / 'gram.txt'
    head = [line for line in path.read_text().splitlines() if line.startswith('#')]
    rows = [[int(t) for t in line.split()] for line in path.read_text().splitlines() if line and not line.startswith('#')]
    change(rows)
    path.write_text('\n'.join(head + [' '.join(map(str, row)) for row in rows]) + '\n')
    digest = sha256_file(path)
    edit = root / 'lattices' / ident / 'entry.toml'
    old = next(line for line in edit.read_text().splitlines() if line.startswith('gram_sha256'))
    edit.write_text(edit.read_text().replace(old, f'gram_sha256 = "{digest}"'))
    index = root / 'lattices/index.json'
    data = json.loads(index.read_text())
    data[int(ident[-2:]) - 1]['gram_sha256'] = digest
    index.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    rehash(root, f'lattices/{ident}/gram.txt', f'lattices/{ident}/entry.toml', 'lattices/index.json')


def _asymmetric(rows):
    rows[0][1] += 1


def _wrong_size(rows):
    rows.pop()


def _long_row(rows):
    rows[0].append(987654321)


def _short_row(rows):
    rows[5].pop()


def _odd_diagonal(rows):
    rows[3][3] += 1


def _determinant(rows):
    rows[0][0] += 2


@pytest.mark.parametrize('change, message', [
    (_asymmetric, 'L112.04: symmetry'),
    (_wrong_size, 'lattices/L112.04/gram.txt: shape 111 x 112, expected 112 x 112'),
    (_long_row, 'lattices/L112.04/gram.txt: rows of lengths [112, 113]'),
    (_short_row, 'lattices/L112.04/gram.txt: rows of lengths [111, 112]'),
    (_odd_diagonal, 'L112.04: positive definite, even, determinant 1'),
    (_determinant, 'L112.04: positive definite, even, determinant 1'),
])
def test_bad_gram_is_rejected(root, change, message):
    edit_gram(root, 'L112.04', change)
    assert_fails(root, message)


def test_a_stale_record_does_not_survive(root):
    (root / 'out').mkdir()
    (root / 'out/v0_inputs.json').write_text('{"passed": true}')
    (root / 'extra.txt').write_text('x')
    assert_fails(root, 'file inventory')


def test_preflight_accepts_the_tree(root):
    result = subprocess.run(['bash', '-c', f'. "{root}/code/verify/preflight.sh"; preflight "{sys.executable}"; echo reached'],
                            capture_output=True, text=True)
    assert result.returncode == 0 and 'reached' in result.stdout, result.stderr


def test_preflight_stops_on_a_changed_tree(root):
    (root / 'extra.txt').write_text('x')
    result = subprocess.run(['bash', '-c', f'. "{root}/code/verify/preflight.sh"; preflight "{sys.executable}"; echo reached'],
                            capture_output=True, text=True)
    assert result.returncode == 1 and 'reached' not in result.stdout


@pytest.mark.parametrize('matrix, expected', [
    ([[2, 1], [1, 2]], False),            # determinant 3
    ([[1]], False),                       # odd
    ([[2, 3], [3, 4]], False),            # indefinite, determinant -1
    ([[0, 1], [1, 0]], False),            # even unimodular but indefinite
])
def test_gram_test_on_small_matrices(matrix, expected):
    assert is_even_unimodular_positive(matrix) is expected


def test_gram_test_accepts_e8():
    e8 = [[0] * 8 for _ in range(8)]
    for i in range(8):
        e8[i][i] = 2
    for i, j in [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (4, 7)]:
        e8[i][j] = e8[j][i] = -1
    assert is_even_unimodular_positive(e8)
    assert leading_minors(e8)[-1] == 1


@pytest.mark.parametrize('function, arguments', [
    (multiply, ([[1, 2, 3]], [[1], [2]])),               # 1 x 3 by 2 x 1
    (multiply, ([[1, 2]], [[1], [2, 3]])),               # rows of the right factor of different lengths
    (multiply, ([[1, 2], [3]], [[1], [2]])),             # rows of the left factor of different lengths
    (transpose, ([[1, 2], [3]],)),
    (determinant, ([[1, 2]],)),
    (determinant, ([[1, 2], [3, 4, 5]],)),
    (leading_minors, ([[2, 1, 0], [1, 2, 0]],)),
    (is_even_unimodular_positive, ([[2, 1], [1, 2], [0, 0]],)),
    (inverse, ([[1, 0, 0], [0, 1, 0]],)),
])
def test_matrix_functions_refuse_wrong_shapes(function, arguments):
    with pytest.raises(ValueError):
        function(*arguments)

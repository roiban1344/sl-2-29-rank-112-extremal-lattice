"""The checks of v1_action and v2_construction, on the real data with one thing changed.

Some conditions of v2_construction follow from others, so no input can fail them alone. They stay as written
checks of the statements in the docstring: C is even and det C = 29^8 (given that b is even and det b = 29^48, and
that C is integral); the Gram matrix is even and [L : B0 _|_ B0] = 29^48 (given determinant 1); det G0 = 151380^56
(given G = T_s G0, det G = 1 and det T_s^-1).
"""
import copy
import json
import re
import shutil
import stat
import subprocess
import sys

import pytest

from conftest import CODE, REPO
from lib.data import read_generators, read_matrices, read_matrix
from lib.exact import determinant, inverse, multiply, transpose
from lib.report import CheckFailed

sys.path.insert(0, str(CODE / 'verify'))
import v1_action  # noqa: E402
import v2_construction as v2  # noqa: E402

WB2 = REPO / 'data/Wb2'
U112 = REPO / 'data/U112'


def copy_tree(target):
    ignore = shutil.ignore_patterns('.git', 'out', '__pycache__', '.pytest_cache', '.venv')
    shutil.copytree(REPO, target, ignore=ignore)
    return target


def run(root, script, *args, **kwargs):
    return subprocess.run([sys.executable, '-I', str(root / 'code/verify' / script), *args],
                          capture_output=True, text=True, **kwargs)


def change_first_integer(path):
    lines = path.read_text().splitlines()
    k = next(i for i, line in enumerate(lines) if not line.startswith('#'))
    tokens = lines[k].split()
    tokens[0] = str(int(tokens[0]) + 1)
    lines[k] = ' '.join(tokens)
    path.write_text('\n'.join(lines) + '\n')


# ---- v1_action

def test_v1_without_gap_is_incomplete_and_not_passed(tmp_path):
    root = copy_tree(tmp_path / 'repo')
    result = run(root, 'v1_action.py', '--no-gap')
    assert result.returncode == 2 and 'INCOMPLETE' in result.stdout
    record = json.loads((root / 'out/v1_action.json').read_text())
    assert record['gap'] == 'not run' and record['incomplete'] is True and record['passed'] is False


def test_v1_without_gap_binary_fails(tmp_path):
    root = copy_tree(tmp_path / 'repo')
    result = run(root, 'v1_action.py', env={'GAP': '/nonexistent/gap'})
    assert result.returncode == 1 and 'GAP not found' in result.stderr


def test_v1_rejects_a_changed_generator(tmp_path):
    root = copy_tree(tmp_path / 'repo')
    change_first_integer(root / 'lattices/L112.05/generators.txt')
    result = run(root, 'v1_action.py', '--no-gap')
    assert result.returncode == 1 and 'L112.05' in result.stderr and 'does not preserve the form' in result.stderr


def test_v1_rejects_mislabelled_generators(tmp_path):
    root = copy_tree(tmp_path / 'repo')
    path = root / 'lattices/L112.05/generators.txt'
    path.write_text(path.read_text().replace('# generator: SL_2(29), g2', '# generator: other'))
    result = run(root, 'v1_action.py', '--no-gap')
    assert result.returncode == 1 and 'the first two generators' in result.stderr


def test_empty_generators_are_rejected(tmp_path):
    root = copy_tree(tmp_path / 'repo')
    (root / 'lattices/L112.03/generators.txt').write_text('# nothing\n')
    result = run(root, 'v1_action.py', '--no-gap')
    assert result.returncode == 1 and 'L112.03: at least the two generators' in result.stderr
    result = run(root, 'v2_construction.py')
    assert result.returncode == 1 and 'L112.03: at least the two generators' in result.stderr


GOOD = {'GAP_VERSION': '4.14', 'SMALLGRP': '1.5.4', 'ORDER': '24360', 'SIZE_S': '24360', 'FAITHFUL_ON_ORBIT': 'true', 'MINUS_ONE': 'true', 'ISO_SL229': 'true'}


def fake_gap(tmp_path, values, status=0, errors=''):
    """A stand-in for GAP that prints the given values, and the given errors to standard error."""
    path = tmp_path / 'gap'
    printed = '\n'.join(f'{key} {value}' for key, value in values.items())
    path.write_text(f"#!/bin/sh\ncat <<EOF\n{printed}\nEOF\nprintf '%s' '{errors}' >&2\nexit {status}\n")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return [str(path)]


GENERATORS = [('SL_2(29), g1', [[1]]), ('SL_2(29), g2', [[1]])]


def test_gap_results_are_read(tmp_path):
    versions = v1_action.check_with_gap('L112.13', GENERATORS, fake_gap(tmp_path, GOOD))
    assert versions == {'gap_version': '4.14', 'smallgrp_version': '1.5.4'}


def test_missing_smallgrp_is_named(tmp_path):
    with pytest.raises(CheckFailed, match='lacks its package SmallGrp'):
        v1_action.check_with_gap('L112.13', GENERATORS, fake_gap(tmp_path, {'MISSING_PACKAGE': 'smallgrp'}, status=3))


def test_the_first_gap_error_line_is_kept(tmp_path):
    errors = 'Error, the Small Groups identification is required but not installed\n' + 'x' * 1000
    with pytest.raises(CheckFailed, match='Error, the Small Groups identification'):
        v1_action.check_with_gap('L112.13', GENERATORS, fake_gap(tmp_path, {'ORDER': '24360'}, status=1, errors=errors))


@pytest.mark.parametrize('key, value, message', [
    ('ORDER', '48720', 'generated order'),
    ('SIZE_S', '12180', '|S|'),
    ('FAITHFUL_ON_ORBIT', 'false', 'not faithful'),
    ('MINUS_ONE', 'false', '-1 is not in S'),
    ('ISO_SL229', 'false', 'not isomorphic'),
])
def test_each_gap_result_is_required(tmp_path, key, value, message):
    with pytest.raises(CheckFailed, match=message.replace('|', r'\|')):
        v1_action.check_with_gap('L112.13', GENERATORS, fake_gap(tmp_path, {**GOOD, key: value}))


def test_gap_failure_and_missing_output_are_failures(tmp_path):
    with pytest.raises(CheckFailed, match='GAP failed'):
        v1_action.check_with_gap('L112.13', GENERATORS, fake_gap(tmp_path, GOOD, status=1))
    with pytest.raises(CheckFailed, match='GAP failed'):
        v1_action.check_with_gap('L112.13', GENERATORS, fake_gap(tmp_path, {'ORDER': '24360'}))


def test_gap_program_takes_s_from_the_first_two_generators():
    program = v1_action.gap_program(GENERATORS)
    assert 'S := Group(gens{[1, 2]});' in program and 'IsomorphismGroups(P, SL(2, 29))' in program
    assert program.index('LoadPackage("smallgrp", false)') < program.index('gens :=')


# ---- v2_construction, on a copy of the tree with one file of the wrong shape

def edit_rows(path, change):
    lines = path.read_text().splitlines()
    head = [line for line in lines if line.startswith('#')]
    rows = [line.split() for line in lines if line and not line.startswith('#')]
    change(rows)
    path.write_text('\n'.join(head + [' '.join(row) for row in rows]) + '\n')


def _long_first_row(rows):
    rows[0].append('987654321')


def _short_last_row(rows):
    rows[-1].pop()


def _drop_last_row(rows):
    rows.pop()


@pytest.mark.parametrize('name, change, message', [
    ('data/Wb2/L112.03-basis.txt', _long_first_row, 'data/Wb2/L112.03-basis.txt: rows of lengths [112, 113]'),
    ('data/Wb2/L112.03-basis.txt', _short_last_row, 'data/Wb2/L112.03-basis.txt: rows of lengths [111, 112]'),
    ('data/Wb2/L112.03-lll.txt', _drop_last_row, 'data/Wb2/L112.03-lll.txt: shape 111 x 112, expected 112 x 112'),
    ('data/Wb2/base-gram.txt', _long_first_row, 'data/Wb2/base-gram.txt: rows of lengths [56, 57]'),
    ('data/Wb2/base-S.txt', _drop_last_row, 'data/Wb2/base-S.txt: not a list of 56 x 56 matrices'),
    ('data/Wb2/base-order.txt', _short_last_row, 'data/Wb2/base-order.txt: rows of lengths [55, 56]'),
])
def test_v2_refuses_a_matrix_of_the_wrong_shape(tmp_path, name, change, message):
    root = copy_tree(tmp_path / 'repo')
    edit_rows(root / name, change)
    result = run(root, 'v2_construction.py')
    assert result.returncode == 1 and message in result.stderr, result.stderr


@pytest.mark.parametrize('name, change, message', [
    ('sqrt5.txt', _drop_last_row, 'sqrt5.txt: shape 111 x 112, expected 112 x 112'),
    ('b0-gram.txt', _long_first_row, 'b0-gram.txt: rows of lengths [112, 113]'),
])
def test_u112_refuses_a_matrix_of_the_wrong_shape(monkeypatch, tmp_path, name, change, message):
    shutil.copytree(U112, tmp_path / 'U112')
    edit_rows(tmp_path / 'U112' / name, change)
    monkeypatch.setattr(v2, 'U112', tmp_path / 'U112')
    with pytest.raises(CheckFailed, match=re.escape(message)):
        v2.check_u112()


# ---- v2_construction, in process: each case replaces one matrix read by the check

@pytest.fixture
def base():
    return read_matrix(WB2 / 'base-gram.txt'), read_matrices(WB2 / 'base-S.txt', 56)


def patch_reads(monkeypatch, name, change):
    """Make v2 read a changed copy of the file with this name."""
    def read_one(path, *shape):
        matrix = read_matrix(path, *shape)
        if path.name == name:
            matrix = copy.deepcopy(matrix)
            change(matrix)
        return matrix

    def read_many(path, size):
        matrices = read_matrices(path, size)
        if path.name == name:
            matrices = copy.deepcopy(matrices)
            change(matrices)
        return matrices
    monkeypatch.setattr(v2, 'read_matrix', read_one)
    monkeypatch.setattr(v2, 'read_matrices', read_many)


def _add(i, j, value=1):
    def change(matrix):
        matrix[i][j] += value
    return change


def _double_row(matrix):
    matrix[0] = [2 * x for x in matrix[0]]


def _swap_rows(matrix):
    matrix[0], matrix[1] = matrix[1], matrix[0]


def _bump_first_matrix(matrices):
    matrices[0][0][0] += 1


def _three_matrices(matrices):
    matrices.pop()


@pytest.mark.parametrize('name, change, message', [
    ('base-gram.txt', _add(0, 1), 'symmetric, even'),
    ('base-gram.txt', _add(0, 0), 'symmetric, even'),
    ('base-gram.txt', _add(0, 0, 2), 'det b'),
    ('base-S.txt', _bump_first_matrix, 'S preserves b'),
    ('base-order.txt', _bump_first_matrix, 'O commutes with S'),
    ('base-order.txt', _three_matrices, 'four basis elements'),
])
def test_base_checks(monkeypatch, name, change, message):
    patch_reads(monkeypatch, name, change)
    with pytest.raises(CheckFailed, match=message):
        v2.check_base()


def _leave_dual_pairing(matrix):
    """Add to a row a vector of 29 (B0 _|_ B0)^#: L stays in the dual, but its form stops being integral.

    The vector is 29 b^-1 e_k, and it pairs with row j to z_j[k] / 29, so k is chosen with some z_j[k] prime to 29.
    """
    dual = inverse(read_matrix(WB2 / 'base-gram.txt'))
    k = next(k for k in range(56) if any(row[k] % 29 for row in matrix[1:]))
    vector = [int(29 * x) for x in dual[k]] + [0] * 56
    matrix[0] = [x + y for x, y in zip(matrix[0], vector)]


@pytest.mark.parametrize('name, change, message', [
    ('L112.03-basis.txt', _add(0, 0), 'in the dual'),
    ('L112.03-basis.txt', _leave_dual_pairing, 'the Gram matrix is integral'),
    ('L112.03-basis.txt', _double_row, 'determinant 1'),
    ('L112.03-lll.txt', _double_row, 'det U'),
    ('L112.03-lll.txt', _swap_rows, 'the published Gram'),
])
def test_lattice_checks(monkeypatch, base, name, change, message):
    patch_reads(monkeypatch, name, change)
    with pytest.raises(CheckFailed, match=message):
        v2.check_wb2('L112.03', *base)


def test_generators_must_be_s_acting_diagonally(base):
    b, s = base
    with pytest.raises(CheckFailed, match='S acting diagonally'):
        v2.check_wb2('L112.03', b, [s[1], s[0]])


def _negate(matrix):
    for row in matrix:
        row[:] = [-x for x in row]


def _double_all(matrix):
    for row in matrix:
        row[:] = [2 * x for x in row]


@pytest.mark.parametrize('name, change, message', [
    ('sqrt5.txt', _double_all, 'sigma\\^2'),
    ('sqrt5.txt', _negate, 'G = T_s G0'),
    ('b0-gram.txt', _add(0, 1), 'G0 is symmetric'),
])
def test_u112_checks(monkeypatch, name, change, message):
    patch_reads(monkeypatch, name, change)
    with pytest.raises(CheckFailed, match=message):
        v2.check_u112()


def _symmetric_change(matrix):
    matrix[0][1] += 1
    matrix[1][0] += 1


def test_u112_form_must_scale_under_sigma(monkeypatch):
    patch_reads(monkeypatch, 'gram.txt', _symmetric_change)
    with pytest.raises(CheckFailed, match='sigma G sigma'):
        v2.check_u112()


def test_u112_sigma_must_commute_with_s(monkeypatch):
    monkeypatch.setattr(v2, 'read_generators', lambda ident: read_generators('L112.03'))
    with pytest.raises(CheckFailed, match='sigma commutes'):
        v2.check_u112()


def small_u112(monkeypatch, sigma, gram, g0):
    """Run the check of L112.15 on 2 x 2 matrices, which can reach conditions the real data satisfies by nature."""
    files = {'sqrt5.txt': sigma, 'gram.txt': gram, 'b0-gram.txt': g0}
    monkeypatch.setattr(v2, 'read_matrix', lambda path, *shape: files[path.name])
    monkeypatch.setattr(v2, 'read_generators', lambda ident: [('g', [[1, 0], [0, 1]])])


SIGMA = [[1, 2], [2, -1]]            # sigma^2 = 5, and I + sigma is even


def g0_for(gram):
    return multiply([[435 + 87, 174], [174, 435 - 87]], gram)        # (435 I + 87 sigma) G


def test_u112_i_plus_sigma_must_be_even(monkeypatch):
    sigma = [[2, 1], [1, -2]]
    gram = [[1, 0], [0, 1]]
    small_u112(monkeypatch, sigma, gram, gram)
    with pytest.raises(CheckFailed, match='I \\+ sigma'):
        v2.check_u112()


def test_u112_gram_must_have_determinant_1(monkeypatch):
    gram = [[2, 0], [0, 2]]
    small_u112(monkeypatch, SIGMA, gram, g0_for(gram))
    with pytest.raises(CheckFailed, match='det G = 1'):
        v2.check_u112()


def test_u112_determinant_of_s_inverse_is_checked(monkeypatch):
    gram = [[1, 0], [0, 1]]
    small_u112(monkeypatch, SIGMA, gram, g0_for(gram))
    with pytest.raises(CheckFailed, match='det T_s\\^-1'):
        v2.check_u112()


def test_rescaled_dual_must_be_integral(monkeypatch):
    # 2 I is even, and the determinant is stubbed so that the check of C is reached: 29 (2 I)^-1 is not integral.
    b = [[2 * int(i == j) for j in range(56)] for i in range(56)]
    monkeypatch.setattr(v2, 'read_matrix', lambda path, *shape: b)
    monkeypatch.setattr(v2, 'determinant', lambda matrix: 29 ** 48)
    with pytest.raises(CheckFailed, match='C is integral'):
        v2.check_base()


def test_is_symmetric_even():
    assert v2.is_symmetric_even([[2, 1], [1, 2]])
    assert not v2.is_symmetric_even([[2, 1], [0, 2]])
    assert not v2.is_symmetric_even([[1, 1], [1, 2]])


def test_a_missing_directory_leaves_a_failure_record(tmp_path):
    root = copy_tree(tmp_path / 'repo')
    (root / 'out').mkdir()
    (root / 'out/v2_construction.json').write_text('{"passed": true}')
    shutil.rmtree(root / 'data/U112')
    assert run(root, 'v2_construction.py').returncode == 1
    assert json.loads((root / 'out/v2_construction.json').read_text())['passed'] is False


def test_changed_data_fails_the_script(tmp_path):
    root = copy_tree(tmp_path / 'repo')
    change_first_integer(root / 'data/Wb2/L112.07-lll.txt')
    result = run(root, 'v2_construction.py')
    assert result.returncode == 1 and 'L112.07' in result.stderr
    assert json.loads((root / 'out/v2_construction.json').read_text())['passed'] is False


def test_exact_helpers_on_a_small_matrix():
    a = [[0, 2], [3, 1]]
    assert determinant(a) == -6
    assert multiply(a, transpose(a)) == [[4, 2], [2, 10]]
    assert multiply(inverse(a), a) == [[1, 0], [0, 1]]

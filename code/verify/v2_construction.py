#!/usr/bin/env python3
"""The structure data of the lattices, using Python 3.11+ and exact arithmetic (about 30 seconds).

The base lattice B0, on data/Wb2: b is symmetric, even, of determinant 29^48; C = (B0^#, 29 b) is integral,
even, of determinant 29^8; the two generators of S preserve b; the four matrices of base-order.txt commute
with S. Not checked here: that C is Nebe's L_{56,6}, and that these four matrices are a Z-basis of a maximal
order of the commutant, a quaternion algebra ramified at 3 and infinity.

Each of L112.03-14, rebuilt from B0: L lies in the dual of B0 _|_ B0; its Gram matrix is integral, even, of
determinant 1, so B0 _|_ B0 lies in L; [L : B0 _|_ B0] = 29^48; det U = +-1 and U^T (Bz bb Bz^T) U is the
published gram.txt; S acting diagonally on B0 _|_ B0 is the pair of the first two generators in generators.txt.

L112.15, on data/U112: sigma^2 = 5, sigma G sigma^T = 5 G, sigma commutes with S, and I + sigma is even; with
s = 1/348 - sqrt5/1740 and T_s its matrix, the Gram matrix is G = T_s G0 with G0 symmetric. So the form is b0(x s, y)
and the lattice satisfies X^# = X s for b0, while X^# = X s^-1 fails: det(T_s^-1) det(G0) is not 1.
"""
import argparse
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.data import LATTICES, read_generators, read_matrices, read_matrix  # noqa: E402
from lib.exact import determinant, identity, inverse, multiply, transpose  # noqa: E402
from lib.report import REPO, CheckFailed, Report, require  # noqa: E402

WB2 = REPO / 'data' / 'Wb2'
U112 = REPO / 'data' / 'U112'
IDS_WB2 = [f'L112.{k:02d}' for k in range(3, 15)]


def block_diagonal(a, b):
    n, m = len(a), len(b)
    return [row + [0] * m for row in a] + [[0] * n + row for row in b]


def is_symmetric_even(matrix):
    return matrix == transpose(matrix) and all(matrix[i][i] % 2 == 0 for i in range(len(matrix)))


def check_base():
    b = read_matrix(WB2 / 'base-gram.txt', 56, 56)
    require(is_symmetric_even(b), 'b: symmetric, even')
    require(determinant(b) == 29 ** 48, 'det b = 29^48')
    dual = [[29 * x for x in row] for row in inverse(b)]
    require(all(x.denominator == 1 for row in dual for x in row), 'C is integral')
    c = [[int(x) for x in row] for row in dual]
    require(all(c[i][i] % 2 == 0 for i in range(56)), 'C is even')
    require(determinant(c) == 29 ** 8, 'det C = 29^8')
    s = read_matrices(WB2 / 'base-S.txt', 56)
    require(len(s) == 2 and all(multiply(multiply(g, b), transpose(g)) == b for g in s), 'S preserves b')
    order = read_matrices(WB2 / 'base-order.txt', 56)
    require(len(order) == 4, 'four basis elements of O')
    require(all(multiply(o, g) == multiply(g, o) for o in order for g in s), 'O commutes with S')
    return b, s, len(order)


def check_wb2(ident, b, s):
    bb = block_diagonal(b, b)
    z = read_matrix(WB2 / f'{ident}-basis.txt', 112, 112)              # z = 29 Bz
    u = read_matrix(WB2 / f'{ident}-lll.txt', 112, 112)
    zbb = multiply(z, bb)
    require(all(x % 29 == 0 for row in zbb for x in row), f'{ident}: L is in the dual of B0 _|_ B0')
    scaled = multiply(zbb, transpose(z))
    require(all(x % 841 == 0 for row in scaled for x in row), f'{ident}: the Gram matrix is integral')
    gram = [[x // 841 for x in row] for row in scaled]
    require(is_symmetric_even(gram), f'{ident}: the Gram matrix is even')
    require(determinant(gram) == 1, f'{ident}: determinant 1')
    require(abs(determinant(z)) == 29 ** 64, f'{ident}: [L : B0 _|_ B0] = 29^48')
    require(abs(determinant(u)) == 1, f'{ident}: det U = +-1')
    ut = transpose(u)
    require(multiply(multiply(ut, gram), u) == read_matrix(LATTICES / ident / 'gram.txt', 112, 112), f'{ident}: the published Gram matrix')
    utz = multiply(ut, z)
    published = read_generators(ident)
    for (label, g), base in zip(published[:2], s):
        require(multiply(g, utz) == multiply(utz, block_diagonal(base, base)), f'{ident}: {label} is S acting diagonally')


def check_u112():
    ident = 'L112.15'
    gram = read_matrix(LATTICES / ident / 'gram.txt', 112, 112)
    g0 = read_matrix(U112 / 'b0-gram.txt', 112, 112)
    sigma = read_matrix(U112 / 'sqrt5.txt', 112, 112)
    size = len(gram)
    require(multiply(sigma, sigma) == [[5 * x for x in row] for row in identity(size)], 'sigma^2 = 5')
    require(multiply(multiply(sigma, gram), transpose(sigma)) == [[5 * x for x in row] for row in gram], 'sigma G sigma^T = 5 G')
    for label, g in read_generators(ident)[:2]:
        require(multiply(sigma, g) == multiply(g, sigma), f'sigma commutes with {label}')
    require(all((int(i == j) + sigma[i][j]) % 2 == 0 for i in range(size) for j in range(size)), 'I + sigma is even')
    require(g0 == transpose(g0), 'G0 is symmetric')
    t_s = [[Fraction(int(i == j), 348) - Fraction(sigma[i][j], 1740) for j in range(size)] for i in range(size)]
    require(multiply(t_s, g0) == gram, 'G = T_s G0')
    require(determinant(gram) == 1, 'X^# = X s: det G = 1')
    t_s_inverse = [[435 * int(i == j) + 87 * sigma[i][j] for j in range(size)] for i in range(size)]
    require(determinant(t_s_inverse) == 151380 ** 56, 'det T_s^-1 = 151380^56')
    require(determinant(g0) == 151380 ** 56, 'det G0 = 151380^56, so X^# differs from X s^-1')


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out', help='directory of the JSON record (default: out/)')
    args = parser.parse_args()
    inputs = [WB2 / f'{name}.txt' for name in ('base-gram', 'base-S', 'base-order')]
    inputs += [WB2 / f'{ident}-{name}.txt' for ident in IDS_WB2 for name in ('basis', 'lll')]
    inputs += [U112 / 'sqrt5.txt', U112 / 'b0-gram.txt']
    inputs += [LATTICES / ident / name for ident in [*IDS_WB2, 'L112.15'] for name in ('gram.txt', 'generators.txt')]
    report = Report('v2_construction', [__file__], inputs, args.out)
    try:
        b, s, count = check_base()
        report.check(True, f'B0: determinant, the rescaled dual, S on B0, {count} matrices commuting with S')
        for ident in IDS_WB2:
            check_wb2(ident, b, s)
            report.check(True, f'{ident}: rebuilt from B0 _|_ B0 and equal to the published Gram matrix')
        check_u112()
        report.check(True, 'L112.15: sqrt5, the form b0 and the self-duality condition')
    except (CheckFailed, ArithmeticError, OSError, ValueError, StopIteration) as error:
        return report.fail(error)
    return report.finish()


if __name__ == '__main__':
    sys.exit(main())

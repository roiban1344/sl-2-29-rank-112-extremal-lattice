"""Exact integer linear algebra. Every function refuses a matrix of the wrong shape with ValueError."""


def shape(matrix):
    """The (rows, columns) of a list of rows of one length."""
    columns = len(matrix[0]) if matrix else 0
    if any(len(row) != columns for row in matrix):
        raise ValueError('rows of different lengths')
    return len(matrix), columns


def require_square(matrix):
    rows, columns = shape(matrix)
    if rows != columns:
        raise ValueError(f'not square: {rows} x {columns}')
    return rows


def leading_minors(matrix):
    """The leading principal minors of a square integer matrix, by fraction-free elimination.

    Elimination stops after the first minor that vanishes. Bareiss division is checked to be exact.
    """
    size = require_square(matrix)
    work = [row[:] for row in matrix]
    previous = 1
    minors = []
    for k in range(size):
        pivot = work[k][k]
        minors.append(pivot)
        if pivot == 0:
            break
        for i in range(k + 1, size):
            for j in range(k + 1, size):
                value, remainder = divmod(work[i][j] * pivot - work[i][k] * work[k][j], previous)
                if remainder:
                    raise ArithmeticError('inexact Bareiss division')
                work[i][j] = value
        previous = pivot
    return minors


def is_even_unimodular_positive(matrix):
    """Whether a symmetric integer matrix is positive definite, even and of determinant 1."""
    size = require_square(matrix)
    if any(matrix[i][i] % 2 for i in range(size)):
        return False
    minors = leading_minors(matrix)
    return len(minors) == size and all(m > 0 for m in minors) and minors[-1] == 1


def determinant(matrix):
    """The determinant of a square integer matrix, by fraction-free elimination with row exchanges."""
    size = require_square(matrix)
    work = [row[:] for row in matrix]
    sign = 1
    previous = 1
    for k in range(size - 1):
        if work[k][k] == 0:
            pivot_row = next((i for i in range(k + 1, size) if work[i][k]), None)
            if pivot_row is None:
                return 0
            work[k], work[pivot_row] = work[pivot_row], work[k]
            sign = -sign
        for i in range(k + 1, size):
            for j in range(k + 1, size):
                value, remainder = divmod(work[i][j] * work[k][k] - work[i][k] * work[k][j], previous)
                if remainder:
                    raise ArithmeticError('inexact Bareiss division')
                work[i][j] = value
        previous = work[k][k]
    return sign * work[-1][-1]


def transpose(matrix):
    shape(matrix)
    return [list(row) for row in zip(*matrix)]


def multiply(left, right):
    inner, outer = shape(right)
    if shape(left)[1] != inner:
        raise ValueError(f'cannot multiply: {shape(left)} by {inner, outer}')
    columns = list(zip(*right))
    return [[sum(a * b for a, b in zip(row, column)) for column in columns] for row in left]


def identity(size):
    return [[int(i == j) for j in range(size)] for i in range(size)]


def inverse(matrix):
    """The exact inverse of a square integer matrix, with Fraction entries."""
    from fractions import Fraction
    size = require_square(matrix)
    work = [[Fraction(x) for x in row] + [Fraction(int(i == j)) for j in range(size)] for i, row in enumerate(matrix)]
    for k in range(size):
        pivot_row = next(i for i in range(k, size) if work[i][k])
        work[k], work[pivot_row] = work[pivot_row], work[k]
        pivot = work[k][k]
        work[k] = [x / pivot for x in work[k]]
        for i in range(size):
            if i != k and work[i][k]:
                factor = work[i][k]
                work[i] = [x - factor * y for x, y in zip(work[i], work[k])]
    return [row[size:] for row in work]

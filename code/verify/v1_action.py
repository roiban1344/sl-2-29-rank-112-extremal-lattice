#!/usr/bin/env python3
"""The group action on each lattice, using Python 3.11+ and, for the second part, GAP.

Exact integer check: every generator g is an integer matrix with g G g^T = G. As det G = 1, this gives det g = +-1.
With GAP and its package SmallGrp, which IsomorphismGroups needs here (about 7 minutes for all lattices): the first two generators generate a group S isomorphic to
SL(2,29) and containing -1, so S acts faithfully and not through PSL(2,29); all the generators generate
a group of the order stated in entry.toml. These generators preserve a positive definite form, so the
group is finite and its reduction modulo 3 is injective (Minkowski); GAP works on the reduction.

It does not check that the generated group is the full automorphism group. With --no-gap the second part
is not run, the record does not say passed, and the exit status is 2.
"""
import argparse
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.data import IDS, LATTICES, read_entry, read_generators, read_matrix  # noqa: E402
from lib.exact import multiply, transpose  # noqa: E402
from lib.report import CheckFailed, Report, require  # noqa: E402

SL229_ORDER = 24360
KEYS = ('GAP_VERSION', 'SMALLGRP', 'ORDER', 'SIZE_S', 'FAITHFUL_ON_ORBIT', 'MINUS_ONE', 'ISO_SL229')


def check_isometries(ident, generators):
    gram = read_matrix(LATTICES / ident / 'gram.txt', 112, 112)
    for label, g in generators:
        require(multiply(multiply(g, gram), transpose(g)) == gram, f'{ident}: {label} does not preserve the form')
    require(all(label.startswith('SL_2(29)') for label, _ in generators[:2]), f'{ident}: the first two generators')


def gap_matrix(matrix):
    return '[' + ','.join('[' + ','.join(str(x % 3) for x in row) + ']' for row in matrix) + '] * Z(3)^0'


def gap_program(generators):
    matrices = ',\n'.join(gap_matrix(g) for _, g in generators)
    return f"""if LoadPackage("smallgrp", false) <> true then
  Print("MISSING_PACKAGE smallgrp\\n");
  QuitGap(3);
fi;
Print("SMALLGRP ", GAPInfo.PackagesLoaded.smallgrp[2], "\\n");
gens := [{matrices}];
G := Group(gens);
S := Group(gens{{[1, 2]}});
orbit := Orbit(S, gens[1][1], OnRight);
P := Image(ActionHomomorphism(S, orbit, OnRight));
Print("GAP_VERSION ", GAPInfo.Version, "\\n");
Print("ORDER ", Size(G), "\\n");
Print("SIZE_S ", Size(S), "\\n");
Print("FAITHFUL_ON_ORBIT ", Size(P) = Size(S), "\\n");
Print("MINUS_ONE ", -One(S) in S, "\\n");
Print("ISO_SL229 ", IsomorphismGroups(P, SL(2, 29)) <> fail, "\\n");
QUIT;
"""


def check_with_gap(ident, generators, gap):
    with tempfile.TemporaryDirectory() as directory:
        program = Path(directory) / 'action.g'
        program.write_text(gap_program(generators))
        result = subprocess.run([*gap, '-q', str(program)], capture_output=True, text=True, stdin=subprocess.DEVNULL)
    require('MISSING_PACKAGE smallgrp' not in result.stdout,
            'GAP lacks its package SmallGrp, which IsomorphismGroups needs here (on Debian and Ubuntu, gap-libs provides it)')
    values = dict(re.findall(rf'^({"|".join(KEYS)}) (\S+)$', result.stdout, re.M))
    require(result.returncode == 0 and len(values) == len(KEYS), f'{ident}: GAP failed: {gap_error(result)}')
    expected = read_entry(ident)['group']['generated_order']
    require(values['ORDER'] == str(expected), f"{ident}: generated order {values['ORDER']}, expected {expected}")
    require(values['SIZE_S'] == str(SL229_ORDER), f"{ident}: |S| = {values['SIZE_S']}")
    require(values['FAITHFUL_ON_ORBIT'] == 'true', f'{ident}: the action on the orbit is not faithful')
    require(values['MINUS_ONE'] == 'true', f'{ident}: -1 is not in S')
    require(values['ISO_SL229'] == 'true', f'{ident}: S is not isomorphic to SL(2,29)')
    return {'gap_version': values['GAP_VERSION'], 'smallgrp_version': values['SMALLGRP']}


def gap_error(result):
    """The first error line of GAP, if any, and the end of its output."""
    output = result.stderr + result.stdout
    first = next((line for line in output.splitlines() if line.startswith(('Error', 'Syntax error'))), None)
    tail = output[-300:]
    return f'status {result.returncode}; ' + (f'{first}; ...{tail}' if first and first not in tail else f'...{tail}')


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out', help='directory of the JSON record (default: out/)')
    parser.add_argument('--no-gap', action='store_true', help='only the integer checks; exit status 2')
    args = parser.parse_args()
    inputs = [LATTICES / i / name for i in IDS for name in ('generators.txt', 'gram.txt', 'entry.toml')]
    report = Report('v1_action', [__file__], inputs, args.out)
    gap = shlex.split(os.environ.get('GAP', 'gap'))
    try:
        require(args.no_gap or shutil.which(gap[0]), f"GAP not found ('{gap[0]}'): set GAP, or use --no-gap")
        for ident in IDS:
            generators = read_generators(ident)
            check_isometries(ident, generators)
            report.check(True, f'{ident}: {len(generators)} generators preserve the form')
            if not args.no_gap:
                report.record.update(check_with_gap(ident, generators, gap))
                report.check(True, f'{ident}: S is SL(2,29) with -1 in S; order of the generated group as stated')
    except (CheckFailed, ArithmeticError, OSError, ValueError, KeyError) as error:
        return report.fail(error)
    report.record['gap'] = 'not run' if args.no_gap else 'run'
    status = report.finish(complete=not args.no_gap)
    if status:
        return status
    if args.no_gap:
        print('INCOMPLETE: the isometries are checked; the group structure was not checked (--no-gap).')
        return 2
    print('ALL PASSED. S = SL(2,29) acts faithfully on every lattice. Whether the generated group is the full automorphism group is not checked.')
    return 0


if __name__ == '__main__':
    sys.exit(main())

"""The dependency rule of code/README.md: verify/ imports only lib/, lib/ nothing else from code/."""
import ast

import pytest

from conftest import CODE

ALLOWED = {'lib': {'lib'}, 'verify': {'lib'}}
AREAS = {path.name for path in CODE.iterdir() if path.is_dir() and not path.name.startswith('__')} - {'tests'}
SOURCES = sorted(p for area in AREAS for p in (CODE / area).rglob('*.py'))


def imported_areas(path):
    areas = set()
    for node in ast.walk(ast.parse(path.read_text())):
        names = []
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            names = [node.module]
        areas |= {name.split('.')[0] for name in names} & AREAS
    return areas


@pytest.mark.parametrize('path', SOURCES, ids=lambda p: str(p.relative_to(CODE)))
def test_imports_follow_the_layout(path):
    area = path.relative_to(CODE).parts[0]
    assert imported_areas(path) <= ALLOWED.get(area, AREAS)


def test_the_rule_sees_each_area():
    assert {'lib', 'verify'} <= AREAS

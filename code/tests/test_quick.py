"""The exit status of quick.sh, with the checks replaced by stand-ins that exit as told."""
import shutil
import stat
import subprocess

import pytest

from conftest import REPO
from test_v0 import rehash

STEPS = ['v0_inputs', 'v1_action', 'v2_construction']


def tree(tmp_path, statuses):
    root = tmp_path / 'repo'
    shutil.copytree(REPO, root, ignore=shutil.ignore_patterns('.git', 'out', '__pycache__', '.pytest_cache', '.venv'))
    for step, status in statuses.items():
        (root / f'code/verify/{step}.py').write_text(f'import sys\nsys.exit({status})\n')
    rehash(root, *[f'code/verify/{step}.py' for step in STEPS])
    return root


def fake_gap(tmp_path):
    path = tmp_path / 'gap'
    path.write_text('#!/bin/sh\nexit 0\n')
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return str(path)


def run(root, gap):
    return subprocess.run(['bash', str(root / 'code/verify/quick.sh')], capture_output=True, text=True, env={'GAP': gap, 'PATH': '/usr/bin:/bin'})


@pytest.mark.parametrize('statuses, has_gap, status, last', [
    ({'v0_inputs': 0, 'v1_action': 0, 'v2_construction': 0}, True, 0, 'QUICK CHECKS PASSED'),
    ({'v0_inputs': 1, 'v1_action': 0, 'v2_construction': 0}, True, 1, 'QUICK CHECKS FAILED: v0_inputs'),
    ({'v0_inputs': 0, 'v1_action': 1, 'v2_construction': 0}, True, 1, 'QUICK CHECKS FAILED: v1_action'),
    ({'v0_inputs': 0, 'v1_action': 0, 'v2_construction': 1}, True, 1, 'QUICK CHECKS FAILED: v2_construction'),
    ({'v0_inputs': 0, 'v1_action': 2, 'v2_construction': 0}, False, 2, 'QUICK CHECKS INCOMPLETE'),
    ({'v0_inputs': 0, 'v1_action': 1, 'v2_construction': 0}, False, 1, 'QUICK CHECKS FAILED: v1_action'),
    ({'v0_inputs': 0, 'v1_action': 0, 'v2_construction': 0}, False, 1, 'QUICK CHECKS FAILED: v1_action'),
])
def test_status(tmp_path, statuses, has_gap, status, last):
    root = tree(tmp_path, statuses)
    result = run(root, fake_gap(tmp_path) if has_gap else '/nonexistent/gap')
    assert result.returncode == status, result.stdout + result.stderr
    assert result.stdout.strip().splitlines()[-1].startswith(last)


def test_gap_with_arguments_counts_as_present(tmp_path):
    root = tree(tmp_path, dict.fromkeys(STEPS, 0))
    result = run(root, fake_gap(tmp_path) + ' -l /somewhere')
    assert result.returncode == 0, result.stdout


def test_a_changed_tree_stops_before_any_check(tmp_path):
    root = tree(tmp_path, dict.fromkeys(STEPS, 0))
    (root / 'extra.txt').write_text('x')
    result = run(root, fake_gap(tmp_path))
    assert result.returncode == 1 and '== v0_inputs' not in result.stdout

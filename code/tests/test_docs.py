"""Every tracked file is described in a README, and text for readers keeps to the current state."""
import re
import shutil
import subprocess

import pytest

from conftest import REPO

DOC_NAMES = {'README.md', 'README.ja.md', 'MANIFEST.md', 'MANIFEST.ja.md'}
# Dates in these files are the record itself or part of a name.
DATED = {'CHANGELOG.md', 'CHANGELOG.ja.md', 'CITATION.cff', 'SHA256SUMS'}
TEXT_SUFFIXES = {'.md', '.typ', '.py', '.sh', '.toml', '.json', '.cff', '.yml', '.tsv', '.g'}
LOCAL_PATH = re.compile(r'/home/[a-z]|/Users/[a-z]')
PROGRESS_DATE = re.compile(r'(?<![\w.-])20\d\d-\d\d-\d\d(?![\w.-])')


def tracked():
    if shutil.which('git') is None or not (REPO / '.git').exists():
        pytest.skip('git or .git is not available')
    return subprocess.run(['git', 'ls-files'], cwd=REPO, capture_output=True, text=True, check=True).stdout.split()


def names_in(text):
    """The file names in a text (words with a dot, or anything in backticks), as regular expressions."""
    patterns = []
    words = re.findall(r'[\w.<>*/-]*\.[\w<>*]+', text) + re.findall(r'`([\w.<>*/-]+)`', text)
    for word in set(words):
        word = word.rstrip('.').removeprefix('./')
        if len(re.sub(r'\W', '', word)) < 3:
            continue
        pattern = re.sub(r'<\w+>', r'\\d+', re.escape(word).replace(r'\*', '.*'))
        patterns.append(re.compile(r'(?:.*/)?' + pattern + r'\Z'))
    return patterns


def reader_text():
    for name in tracked():
        path = REPO / name
        if path.suffix in TEXT_SUFFIXES and not name.startswith('code/tests/'):
            yield name, path.read_text(encoding='utf-8')
        elif path.suffix == '.txt':     # data: only the comment lines are text
            lines = path.read_text(encoding='utf-8').splitlines()
            yield name, '\n'.join(line for line in lines if line.startswith('#'))


def test_every_tracked_file_is_described():
    files = tracked()
    patterns = []
    for name in files:
        if name.rsplit('/', 1)[-1] in DOC_NAMES:
            patterns += names_in((REPO / name).read_text(encoding='utf-8'))
    missing = [f for f in files if f.rsplit('/', 1)[-1] not in DOC_NAMES and not any(p.match(f) for p in patterns)]
    assert not missing, 'files not described in any README:\n  ' + '\n  '.join(missing)


def test_no_local_paths():
    bad = [name for name, text in reader_text() if LOCAL_PATH.search(text)]
    assert not bad, f'local paths: {bad}'


def test_no_dated_progress_notes():
    bad = {name: PROGRESS_DATE.findall(text) for name, text in reader_text()
           if name.rsplit('/', 1)[-1] not in DATED and PROGRESS_DATE.search(text)}
    assert not bad, f'dates outside the changelog: {bad}'

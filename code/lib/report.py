"""Uniform reporting: every check is printed and collected into out/<step>.json.

The exit status is the verdict and the JSON file is its record. An existing out/<step>.json is
deleted when the report is created, so a run that dies never leaves an old result behind: if the
script ends without calling finish(), the file is written at exit with "passed": false.
"""
import atexit
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO / 'out'


class CheckFailed(Exception):
    """A required condition does not hold."""


def require(condition, message):
    """Stop the check with a message unless the condition holds."""
    if not condition:
        raise CheckFailed(message)


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


class Report:
    """Collect the checks of one step. `code`, `code/lib` and `inputs` are hashed into the record.

    A missing input is recorded as null; the step itself decides that this is a failure.
    """

    def __init__(self, step, code, inputs=(), out_dir=None):
        self.step = step
        self.path = Path(out_dir or DEFAULT_OUT) / f'{step}.json'
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.unlink(missing_ok=True)
        self.start = time.monotonic()
        self.checks = []
        self.record = {
            'step': step,
            'code': {str(Path(c).resolve().relative_to(REPO)): sha256_file(c)
                     for c in [*code, *sorted(Path(__file__).parent.glob('*.py'))]},
            'inputs': {str(Path(i).resolve().relative_to(REPO)): sha256_file(i) if Path(i).exists() else None
                       for i in inputs},
            'python': platform.python_version(),
            'platform': platform.platform(),
        }
        self.finished = False
        atexit.register(self._write_if_unfinished)

    def check(self, condition, message):
        """Record one check and print it. A failure is reported at finish()."""
        self.checks.append({'check': message, 'passed': bool(condition)})
        print(f"[{'ok' if condition else 'FAIL'}] {message}", flush=True)

    def _write(self, passed, error=None):
        self.record.update(passed=passed, checks=self.checks,
                           seconds=round(time.monotonic() - self.start, 3))
        if error:
            self.record['error'] = error
        temporary = self.path.with_suffix('.tmp')
        temporary.write_text(json.dumps(self.record, indent=1, sort_keys=True) + '\n')
        temporary.replace(self.path)

    def _write_if_unfinished(self):
        if not self.finished:
            kind, value, _ = sys.exc_info()
            self._write(False, repr(value) if kind else 'the script stopped before finish()')

    def fail(self, error):
        """Record a fatal error and return the failing exit status."""
        self.finished = True
        self._write(False, str(error))
        print(f'FAIL: {error}', file=sys.stderr)
        return 1

    def finish(self, complete=True):
        """Write the record and return the exit status of the checks that ran.

        With complete=False some checks did not run: the record does not say passed, and has "incomplete": true.
        """
        self.finished = True
        passed = bool(self.checks) and all(c['passed'] for c in self.checks)
        if not complete:
            self.record['incomplete'] = True
        self._write(passed and complete)
        return 0 if passed else 1

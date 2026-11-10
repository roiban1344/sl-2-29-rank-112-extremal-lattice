"""Make code/ importable from the tests."""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CODE = REPO / 'code'
sys.path.insert(0, str(CODE))
sys.path.insert(0, str(Path(__file__).resolve().parent))

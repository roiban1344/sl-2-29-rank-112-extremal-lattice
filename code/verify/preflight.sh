#!/usr/bin/env bash
# To be sourced by a script that runs long checks. `preflight PY` stops at once if PY is older than Python 3.11 or
# SHA256SUMS does not match the tree, before any long computation starts.
preflight() {
  local py="$1" root
  root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
  if ! "$py" -I -c 'import sys; sys.exit(sys.version_info < (3, 11))'; then
    echo "'$py' does not run, or is older than Python 3.11" >&2
    exit 1
  fi
  if ! "$py" -I -c "
import sys
sys.path.insert(0, '$root/code')
from lib.data import check_sums
check_sums()"; then
    echo "the tree does not match SHA256SUMS" >&2
    exit 1
  fi
}

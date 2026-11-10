#!/usr/bin/env bash
# All the checks that run in minutes. Status 0 only if all of them ran and passed, 1 on a failure, 2 if GAP
# is missing and the group structure was not checked. The last line says the result. Set GAP=... if gap is
# not on PATH.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
PY=${PYTHON:-python3}
# shellcheck source=code/verify/preflight.sh
. code/verify/preflight.sh
preflight "$PY"
failed=(); notrun=()
for step in v0_inputs v2_construction; do
  echo "== $step"
  "$PY" -I "code/verify/$step.py" || failed+=("$step")
done
echo "== v1_action"
GAPCMD=${GAP:-gap}
if command -v "${GAPCMD%% *}" >/dev/null 2>&1; then
  "$PY" -I code/verify/v1_action.py || failed+=(v1_action)
else
  "$PY" -I code/verify/v1_action.py --no-gap
  [ $? -eq 2 ] && notrun+=("v1_action (GAP)") || failed+=(v1_action)
fi
echo
if [ ${#failed[@]} -gt 0 ]; then echo "QUICK CHECKS FAILED: ${failed[*]}"; exit 1; fi
if [ ${#notrun[@]} -gt 0 ]; then echo "QUICK CHECKS INCOMPLETE, not run: ${notrun[*]}"; exit 2; fi
echo "QUICK CHECKS PASSED. They do not establish a lower bound on any minimum, or the classification."

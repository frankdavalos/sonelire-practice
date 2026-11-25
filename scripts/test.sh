#!/usr/bin/env bash
# Run the full test suite: node unit tests, then every tests/browser_*.py.
# Exits non-zero if any suite fails, or if Python Playwright is missing.
#
#   PYTHON    Python interpreter for the browser tests
#             (default: .venv/bin/python if present, else python3)
#   CHROMIUM  Chromium executable for Playwright (default: /usr/bin/chromium)
set -u

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root" || exit 1

if [ -z "${PYTHON:-}" ]; then
  if [ -x .venv/bin/python ]; then PYTHON=.venv/bin/python; else PYTHON=python3; fi
fi
export CHROMIUM="${CHROMIUM:-/usr/bin/chromium}"

failed=0

echo "==> node --test tests/"
node --test tests/ || failed=1

echo "==> browser tests ($PYTHON)"
if ! "$PYTHON" -c 'import playwright.sync_api' 2>/dev/null; then
  echo "FAIL: Python Playwright is not importable by '$PYTHON'." >&2
  echo "  Install the dev dependencies into a virtualenv:" >&2
  echo "    python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt" >&2
  echo "  or point PYTHON at an interpreter that has them." >&2
  failed=1
elif [ ! -x "$CHROMIUM" ]; then
  echo "FAIL: Chromium not found at '$CHROMIUM'. Set CHROMIUM to its path." >&2
  failed=1
else
  for test in tests/browser_*.py; do
    echo "--> $test"
    "$PYTHON" "$test" || { echo "FAIL: $test" >&2; failed=1; }
  done
fi

if [ "$failed" -ne 0 ]; then
  echo "==> TESTS FAILED" >&2
  exit 1
fi
echo "==> all tests passed"

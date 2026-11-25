#!/usr/bin/env bash
# Run the full test suite: node unit tests, then the browser scenarios in tests/browser/.
# Exits non-zero if any suite fails, or if pytest or Python Playwright is missing.
# Extra arguments go to pytest, e.g. scripts/test.sh -k companion
#
#   PYTHON    Python interpreter for the browser tests
#             (default: .venv/bin/python if present, else python3)
#   CHROMIUM  Chromium executable for Playwright (default: /usr/bin/chromium)
#   SONELIRE_COVERAGE=1  also report how much of each page's inline script ran
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
if ! "$PYTHON" -c 'import playwright.sync_api, pytest' 2>/dev/null; then
  echo "FAIL: pytest or Python Playwright is not importable by '$PYTHON'." >&2
  echo "  Install the dev dependencies into a virtualenv:" >&2
  echo "    python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt" >&2
  echo "  or point PYTHON at an interpreter that has them." >&2
  failed=1
elif [ ! -x "$CHROMIUM" ]; then
  echo "FAIL: Chromium not found at '$CHROMIUM'. Set CHROMIUM to its path." >&2
  failed=1
else
  "$PYTHON" -m pytest -q tests/browser "$@" || failed=1
fi

if [ "$failed" -ne 0 ]; then
  echo "==> TESTS FAILED" >&2
  exit 1
fi
echo "==> all tests passed"

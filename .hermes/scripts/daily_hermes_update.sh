#!/usr/bin/env bash
set -u

started_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "# Daily Hermes update"
echo "- Started: ${started_at} UTC"

run_step() {
  local label="$1"
  shift
  echo
  echo "## ${label}"
  echo '```text'
  "$@"
  local status=$?
  echo '```'
  echo "- Exit code: ${status}"
  return "${status}"
}

if ! command -v hermes >/dev/null 2>&1; then
  echo "ERROR: hermes CLI not found on PATH"
  exit 127
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "ERROR: npm not found on PATH"
  exit 127
fi

run_step "hermes update" hermes update
update_status=$?
if [ "${update_status}" -ne 0 ]; then
  echo
  echo "FAILED: hermes update exited ${update_status}; npm install was not run."
  exit "${update_status}"
fi

repo="/home/alfred/.hermes/hermes-agent"
if [ ! -d "${repo}" ]; then
  echo "ERROR: Hermes repo not found at ${repo}"
  exit 2
fi

(
  cd "${repo}" || exit 2
  run_step "npm install (${repo})" npm install
)
npm_status=$?
if [ "${npm_status}" -ne 0 ]; then
  echo
  echo "FAILED: npm install exited ${npm_status}."
  exit "${npm_status}"
fi

finished_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo
echo "OK: Hermes update and npm install completed."
echo "- Finished: ${finished_at} UTC"

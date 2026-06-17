#!/usr/bin/env bash
# monthly_docker_cleanup.sh
# Conservative monthly Docker cleanup.
# - Runs only if Docker is installed.
# - Uses docker system prune -f and docker image prune -f for dangling images.
# - Logs Docker disk usage before/after so reclaimed space is visible.

set -uo pipefail

LOG_DIR="/home/alfred/maintenance/logs"
LOG_FILE="$LOG_DIR/monthly_docker_cleanup.log"
LOCK_FILE="/tmp/monthly_docker_cleanup.lock"
DATE="/usr/bin/date"
MKDIR="/usr/bin/mkdir"
FLOCK="/usr/bin/flock"
DOCKER_BIN="$(/usr/bin/command -v docker 2>/dev/null || true)"

$MKDIR -p "$LOG_DIR"
exec 9>"$LOCK_FILE"
if ! $FLOCK -n 9; then
  printf '[%s] another Docker cleanup is already running; exiting.\n' "$($DATE -Iseconds)" >> "$LOG_FILE"
  exit 0
fi

log() {
  printf '[%s] %s\n' "$($DATE -Iseconds)" "$*" >> "$LOG_FILE"
}

log "=== monthly Docker cleanup started ==="

if [ -z "$DOCKER_BIN" ]; then
  log "Docker is not installed; cleanup skipped."
  exit 0
fi

if ! "$DOCKER_BIN" info >/dev/null 2>&1; then
  log "Docker is installed but daemon is unavailable or current user lacks permission; cleanup skipped safely."
  exit 0
fi

log "Docker disk usage before cleanup:"
"$DOCKER_BIN" system df >> "$LOG_FILE" 2>&1 || log "WARNING: docker system df before cleanup failed."

log "Running docker system prune -f"
"$DOCKER_BIN" system prune -f >> "$LOG_FILE" 2>&1 || log "WARNING: docker system prune failed."

log "Removing dangling images, if any."
"$DOCKER_BIN" image prune -f >> "$LOG_FILE" 2>&1 || log "WARNING: docker image prune failed."

log "Docker disk usage after cleanup:"
"$DOCKER_BIN" system df >> "$LOG_FILE" 2>&1 || log "WARNING: docker system df after cleanup failed."

log "=== monthly Docker cleanup completed ==="

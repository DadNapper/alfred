#!/usr/bin/env bash
# weekly_log_cleanup.sh
# Conservative log maintenance.
# - Rotates/compresses oversized maintenance logs instead of deleting active files.
# - Deletes old maintenance logs older than 30 days.
# - Flushes PM2 logs safely only if PM2 is installed.

set -uo pipefail

LOG_DIR="/home/alfred/maintenance/logs"
LOG_FILE="$LOG_DIR/weekly_log_cleanup.log"
LOCK_FILE="/tmp/weekly_log_cleanup.lock"
DATE="/usr/bin/date"
MKDIR="/usr/bin/mkdir"
FIND="/usr/bin/find"
GZIP="/usr/bin/gzip"
MV="/usr/bin/mv"
TOUCH="/usr/bin/touch"
TRUNCATE="/usr/bin/truncate"
FLOCK="/usr/bin/flock"
PM2_BIN="$(/usr/bin/command -v pm2 2>/dev/null || true)"
MAX_LOG_SIZE_BYTES=$((50 * 1024 * 1024))

$MKDIR -p "$LOG_DIR"
exec 9>"$LOCK_FILE"
if ! $FLOCK -n 9; then
  printf '[%s] another log cleanup is already running; exiting.\n' "$($DATE -Iseconds)" >> "$LOG_FILE"
  exit 0
fi

log() {
  printf '[%s] %s\n' "$($DATE -Iseconds)" "$*" >> "$LOG_FILE"
}

log "=== weekly log cleanup started ==="

# Rotate oversized current logs. This is rollback/log-friendly: the old content is kept compressed.
for file in "$LOG_DIR"/*.log; do
  [ -f "$file" ] || continue
  size="$(/usr/bin/stat -c '%s' "$file" 2>/dev/null || printf '0')"
  if [ "$size" -gt "$MAX_LOG_SIZE_BYTES" ]; then
    stamp="$($DATE +%Y%m%d_%H%M%S)"
    rotated="${file}.${stamp}"
    log "Rotating oversized log $file (${size} bytes) -> $rotated.gz"
    $MV -- "$file" "$rotated" && $TOUCH "$file" && $GZIP -f "$rotated"
  fi
done

# Remove old compressed/rotated maintenance logs. Active *.log files are not deleted here.
$FIND "$LOG_DIR" -type f \( -name '*.gz' -o -name '*.old' -o -name '*.rotated' -o -name '*.log.*' \) -mtime +30 -print -delete >> "$LOG_FILE" 2>&1 || \
  log "WARNING: old log cleanup encountered an error."

# Safety valve: ensure no active maintenance log remains absurdly large if rotation failed.
for file in "$LOG_DIR"/*.log; do
  [ -f "$file" ] || continue
  size="$(/usr/bin/stat -c '%s' "$file" 2>/dev/null || printf '0')"
  if [ "$size" -gt $((MAX_LOG_SIZE_BYTES * 2)) ]; then
    log "WARNING: truncating still-oversized active log $file to 10MB."
    $TRUNCATE -s 10M "$file"
  fi
done

if [ -n "$PM2_BIN" ]; then
  log "Flushing PM2 logs."
  "$PM2_BIN" flush >> "$LOG_FILE" 2>&1 || log "WARNING: pm2 flush failed."
else
  log "PM2 is not installed; PM2 log flush skipped."
fi

log "=== weekly log cleanup completed ==="

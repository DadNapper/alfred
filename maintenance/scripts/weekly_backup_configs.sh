#!/usr/bin/env bash
# weekly_backup_configs.sh
# Weekly timestamped backup of important Hermes and maintenance configuration.
# - Never overwrites backups; archive names include timestamp and PID.
# - Uses umask 077 because backups may contain secrets such as ~/.hermes/.env/auth.json.
# - Backs up current user crontab and relevant package manifests.

set -uo pipefail
umask 077

LOG_DIR="/home/alfred/maintenance/logs"
BACKUP_DIR="/home/alfred/maintenance/backups"
LOG_FILE="$LOG_DIR/weekly_backup_configs.log"
LOCK_FILE="/tmp/weekly_backup_configs.lock"
DATE="/usr/bin/date"
MKDIR="/usr/bin/mkdir"
TAR="/usr/bin/tar"
CP="/usr/bin/cp"
FLOCK="/usr/bin/flock"
CRONTAB="/usr/bin/crontab"

$MKDIR -p "$LOG_DIR" "$BACKUP_DIR"
exec 9>"$LOCK_FILE"
if ! $FLOCK -n 9; then
  printf '[%s] another config backup is already running; exiting.\n' "$($DATE -Iseconds)" >> "$LOG_FILE"
  exit 0
fi

log() {
  printf '[%s] %s\n' "$($DATE -Iseconds)" "$*" >> "$LOG_FILE"
}

add_if_exists() {
  local src="$1"
  local dst_root="$2"
  if [ -e "$src" ]; then
    local rel="${src#/}"
    /usr/bin/mkdir -p "$dst_root/$(/usr/bin/dirname "$rel")"
    $CP -a -- "$src" "$dst_root/$rel"
    log "Included: $src"
  else
    log "Skipped missing: $src"
  fi
}

stamp="$($DATE +%Y%m%d_%H%M%S)"
workdir="$BACKUP_DIR/.work_${stamp}_$$"
archive="$BACKUP_DIR/hermes_config_backup_${stamp}_$$.tar.gz"

log "=== weekly config backup started ==="

if [ -e "$archive" ]; then
  log "ERROR: archive already exists unexpectedly: $archive"
  exit 1
fi

$MKDIR -p "$workdir"

# Hermes config/secrets/state pointers. Kept narrow for rollback friendliness without copying bulky sessions/logs.
add_if_exists "/home/alfred/.hermes/config.yaml" "$workdir"
add_if_exists "/home/alfred/.hermes/.env" "$workdir"
add_if_exists "/home/alfred/.hermes/auth.json" "$workdir"
add_if_exists "/home/alfred/.hermes/shell-hooks-allowlist.json" "$workdir"

# Hermes source/package manifests if present.
add_if_exists "/home/alfred/.hermes/hermes-agent/package.json" "$workdir"
add_if_exists "/home/alfred/.hermes/hermes-agent/package-lock.json" "$workdir"

# Maintenance scripts and user crontab for rollback.
add_if_exists "/home/alfred/maintenance/scripts" "$workdir"
$MKDIR -p "$workdir/crontab"
if $CRONTAB -l > "$workdir/crontab/alfred.crontab" 2>> "$LOG_FILE"; then
  log "Included: current user crontab"
else
  printf '# no user crontab at backup time\n' > "$workdir/crontab/alfred.crontab"
  log "No user crontab found; recorded placeholder."
fi

# Include root-visible system cron text only if readable by this user.
for src in /etc/crontab /etc/cron.d; do
  if [ -r "$src" ]; then
    add_if_exists "$src" "$workdir"
  else
    log "Skipped unreadable: $src"
  fi
done

if $TAR -C "$workdir" -czf "$archive" . >> "$LOG_FILE" 2>&1; then
  log "Created archive: $archive"
  /usr/bin/rm -rf -- "$workdir"
  log "=== weekly config backup completed successfully ==="
else
  rc=$?
  log "ERROR: tar failed with exit code $rc; leaving workdir for inspection: $workdir"
  exit "$rc"
fi

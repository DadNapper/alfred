#!/usr/bin/env bash
# weekly_ubuntu_update.sh
# Conservative weekly Ubuntu package maintenance for this workstation/server.
# - Does NOT run release upgrades or change Ubuntu major versions.
# - Uses sudo non-interactively; if passwordless sudo is not available, logs and exits.
# - Appends timestamped output to ~/maintenance/logs/weekly_ubuntu_update.log.

set -uo pipefail

LOG_DIR="/home/alfred/maintenance/logs"
LOG_FILE="$LOG_DIR/weekly_ubuntu_update.log"
LOCK_FILE="/tmp/weekly_ubuntu_update.lock"
APT="/usr/bin/apt"
SUDO="/usr/bin/sudo"
DATE="/usr/bin/date"
MKDIR="/usr/bin/mkdir"
FLOCK="/usr/bin/flock"

$MKDIR -p "$LOG_DIR"
exec 9>"$LOCK_FILE"
if ! $FLOCK -n 9; then
  printf '[%s] another weekly Ubuntu update is already running; exiting.\n' "$($DATE -Iseconds)" >> "$LOG_FILE"
  exit 0
fi

log() {
  printf '[%s] %s\n' "$($DATE -Iseconds)" "$*" >> "$LOG_FILE"
}

run_logged() {
  log "RUN: $*"
  "$@" >> "$LOG_FILE" 2>&1
  local rc=$?
  log "EXIT($rc): $*"
  return $rc
}

log "=== weekly Ubuntu update started ==="

if [ ! -x "$SUDO" ] || [ ! -x "$APT" ]; then
  log "ERROR: sudo or apt not found; aborting."
  exit 1
fi

if ! $SUDO -n true >> "$LOG_FILE" 2>&1; then
  log "ERROR: passwordless sudo is not available for this cron context; apt maintenance skipped safely."
  log "Recommendation: run this script manually or configure a limited sudoers rule if you want unattended apt updates."
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive

run_logged $SUDO -n $APT update || exit 1
run_logged $SUDO -n $APT upgrade -y || exit 1
run_logged $SUDO -n $APT autoremove -y || exit 1

log "=== weekly Ubuntu update completed successfully ==="

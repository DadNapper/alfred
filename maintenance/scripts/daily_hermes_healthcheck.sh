#!/usr/bin/env bash
# daily_hermes_healthcheck.sh
# Frequent Hermes runtime health check using systemd as the single source of truth.
# Checks:
# - hermes-gateway.service is active via `systemctl is-active hermes-gateway`.
# - a Hermes gateway process is running.
# - configured local health/webhook port responds, if such a port is configured.
# Recovery:
# - If unhealthy, attempt `sudo systemctl restart hermes-gateway` only when
#   passwordless sudo is available; otherwise log a warning and never hang.
# - No PM2 checks or PM2 restarts are used.

set -uo pipefail

LOG_DIR="/home/alfred/maintenance/logs"
LOG_FILE="$LOG_DIR/daily_hermes_healthcheck.log"
LOCK_FILE="/tmp/daily_hermes_healthcheck.lock"
HERMES_HOME="/home/alfred/.hermes"
ENV_FILE="$HERMES_HOME/.env"
SERVICE_NAME="hermes-gateway"
DATE="/usr/bin/date"
MKDIR="/usr/bin/mkdir"
FLOCK="/usr/bin/flock"
PGREP="/usr/bin/pgrep"
CURL="/usr/bin/curl"
SYSTEMCTL="/usr/bin/systemctl"
SUDO="/usr/bin/sudo"

$MKDIR -p "$LOG_DIR"
exec 9>"$LOCK_FILE"
if ! $FLOCK -n 9; then
  printf '[%s] another Hermes healthcheck is already running; exiting.\n' "$($DATE -Iseconds)" >> "$LOG_FILE"
  exit 0
fi

log() {
  printf '[%s] %s\n' "$($DATE -Iseconds)" "$*" >> "$LOG_FILE"
}

hermes_process_running() {
  $PGREP -af 'hermes_cli\.main gateway run|hermes .*gateway run' >/dev/null 2>&1
}

service_active() {
  $SYSTEMCTL is-active --quiet "$SERVICE_NAME"
}

configured_ports() {
  if [ -n "${HERMES_HEALTH_PORT:-}" ]; then
    printf '%s\n' "$HERMES_HEALTH_PORT"
    return 0
  fi

  if [ -r "$ENV_FILE" ]; then
    /usr/bin/awk -F= '
      /^[[:space:]]*(TELEGRAM_WEBHOOK_PORT|TEAMS_PORT|API_SERVER_PORT|HERMES_PORT|PORT)=/ {
        v=$2; gsub(/[[:space:]"'"'"']/, "", v); if (v ~ /^[0-9]+$/) print v
      }
    ' "$ENV_FILE" | /usr/bin/sort -u
  fi
}

port_responds() {
  local port="$1"
  [ -x "$CURL" ] || return 1
  $CURL --silent --show-error --fail --max-time 5 "http://127.0.0.1:${port}/health" >/dev/null 2>&1 \
    || $CURL --silent --show-error --fail --max-time 5 "http://127.0.0.1:${port}/" >/dev/null 2>&1
}

sudo_available() {
  [ -x "$SUDO" ] && $SUDO -n -l "$SYSTEMCTL" restart "$SERVICE_NAME" >/dev/null 2>&1
}

restart_systemd_service() {
  local reason="$1"

  if ! sudo_available; then
    log "WARNING: $SERVICE_NAME is unhealthy but passwordless sudo is unavailable; restart skipped to avoid hanging. Reason: $reason"
    log "Recommendation: add the minimum sudoers rule: alfred ALL=(root) NOPASSWD: /usr/bin/systemctl restart hermes-gateway"
    return 1
  fi

  log "Restarting systemd service '$SERVICE_NAME'. Reason: $reason"
  $SUDO -n $SYSTEMCTL restart "$SERVICE_NAME" >> "$LOG_FILE" 2>&1
  local rc=$?
  log "systemctl restart '$SERVICE_NAME' exit code: $rc"

  if [ "$rc" -eq 0 ]; then
    /bin/sleep 5
    if service_active; then
      log "OK: $SERVICE_NAME is active after restart."
    else
      status="$($SYSTEMCTL is-active "$SERVICE_NAME" 2>&1 || true)"
      log "ERROR: $SERVICE_NAME is still not active after restart; status=$status"
    fi
  fi

  return "$rc"
}

unhealthy=0
reasons=""
mark_unhealthy() {
  unhealthy=1
  reasons="${reasons}${reasons:+; }$*"
}

log "=== Hermes healthcheck started ==="

service_status="$($SYSTEMCTL is-active "$SERVICE_NAME" 2>&1 || true)"
if [ "$service_status" = "active" ]; then
  log "OK: $SERVICE_NAME service is active."
else
  log "ERROR: $SERVICE_NAME service is not active; status=$service_status"
  mark_unhealthy "$SERVICE_NAME status=$service_status"
fi

if hermes_process_running; then
  log "OK: Hermes gateway process is running."
else
  log "ERROR: Hermes gateway process not found."
  mark_unhealthy "Hermes gateway process missing"
fi

ports="$(configured_ports || true)"
if [ -z "$ports" ]; then
  log "WARNING: No active configured Hermes/webhook port found in $ENV_FILE and HERMES_HEALTH_PORT is unset; port check skipped."
else
  for port in $ports; do
    if port_responds "$port"; then
      log "OK: localhost port $port responded."
    else
      log "ERROR: configured localhost port $port did not respond to HTTP /health or /."
      mark_unhealthy "port $port did not respond"
    fi
  done
fi

if [ "$unhealthy" -eq 1 ]; then
  restart_systemd_service "$reasons" || true
fi

log "=== Hermes healthcheck completed ==="

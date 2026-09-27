#!/usr/bin/env bash

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    printf 'Carrega aquest fitxer amb: source %s\n' "$0" >&2
    exit 1
fi

export SMTP_HOST="smtp.serviciodecorreo.es"
export SMTP_PORT="465"
export SMTP_USER="noreply@trackio.es"
export SMTP_FROM="noreply@trackio.es"
export SMTP_USE_SSL="true"
export SMTP_TIMEOUT_SECONDS="20"

export APP_PUBLIC_URL="https://trackio.es/api"
export REDIS_URL="redis://redis:6379/0"
export MBTILES_DIR="/app/mbtiles"
export PLANETILER_SCHEMA="/opt/planetiler/planetiler.yaml"
export PLANETILER_JAR="/opt/planetiler/planetiler.jar"
export PBF_MAX_DOWNLOAD_BYTES="21474836480"
export MBTILES_TTL_SECONDS="86400"
export MBTILES_CLEANUP_INTERVAL_SECONDS="3600"

if [[ -z "${SMTP_PASSWORD:-}" ]]; then
    read -r -s -p "Contrasenya SMTP de ${SMTP_USER}: " SMTP_PASSWORD
    printf '\n'
    if [[ -z "$SMTP_PASSWORD" ]]; then
        printf 'Cal indicar la contrasenya SMTP.\n' >&2
        return 1
    fi
    export SMTP_PASSWORD
fi

APP_SECRET_FILE="${APP_SECRET_FILE:-$HOME/.config/strackrec-backend/.confirmation_secret}"
if [[ -z "${CONFIRMATION_SECRET:-}" ]]; then
    if [[ ! -s "$APP_SECRET_FILE" ]]; then
        if ! command -v openssl >/dev/null 2>&1; then
            printf 'Cal openssl per generar el secret: %s\n' "$APP_SECRET_FILE" >&2
            return 1
        fi
        umask 077
        mkdir -p "$(dirname "$APP_SECRET_FILE")" || return 1
        openssl rand -hex 32 > "$APP_SECRET_FILE" || return 1
        chmod 600 "$APP_SECRET_FILE"
    fi
    CONFIRMATION_SECRET="$(<"$APP_SECRET_FILE")"
fi
export CONFIRMATION_SECRET
unset APP_SECRET_FILE
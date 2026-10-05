#!/bin/sh
set -eu
umask 077

case "${LOG_RETENTION_DAYS:-30}" in
    30|90) retention_days="${LOG_RETENTION_DAYS:-30}" ;;
    *) echo 'LOG_RETENTION_DAYS must be 30 or 90' >&2; exit 1 ;;
esac

# Keep the installed configuration immutable; the runtime copy lives in tmpfs.
sed -e "s/rotate 30/rotate $retention_days/" \
    -e "s/maxage 30/maxage $retention_days/" \
    /etc/logrotate.d/nginx-private > /tmp/nginx-logrotate.conf

maintain_logs() {
    logrotate --state /var/log/nginx/private/logrotate.status /tmp/nginx-logrotate.conf
    # Enforce time expiry even when an archive receives no subsequent rotations.
    find /var/log/nginx/private -maxdepth 1 -type f -name '*.log-*' \
        -mmin "+$((retention_days * 1440))" -delete
}

nginx -t
nginx -g 'daemon off;' &
nginx_pid=$!

(
    while kill -0 "$nginx_pid" 2>/dev/null; do
        if ! maintain_logs; then
            echo 'Log retention maintenance failed' >&2
            kill -QUIT "$nginx_pid"
            exit 1
        fi
        sleep 60 &
        sleeper=$!
        trap 'kill "$sleeper" 2>/dev/null || true; exit 0' TERM INT
        wait "$sleeper" || true
    done
) &
maintenance_pid=$!

stop() {
    kill -TERM "$maintenance_pid" 2>/dev/null || true
    kill -QUIT "$nginx_pid" 2>/dev/null || true
}
trap stop TERM INT QUIT
status=0
wait "$nginx_pid" || status=$?
stop
wait "$nginx_pid" 2>/dev/null || true
wait "$maintenance_pid" 2>/dev/null || true
exit "$status"

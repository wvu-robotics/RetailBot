#!/bin/bash

# This is run when the container starts. 
# Should be idempotent because the container may restart using same ephemeral filesystem.

echo "Running entrypoint.sh..."

# Start an SSH server
SSHD_PORT="${SSHD_PORT:-2222}"
AUTHORIZED_KEYS="${AUTHORIZED_KEYS:-/home/rb/.ssh/authorized_keys}"
RUN_SSHD="${RUN_SSHD:-1}"


sudo mkdir -p /run/sshd
# Generate host keys if missing
if ! ls /etc/ssh/ssh_host_*key >/dev/null 2>&1; then
echo "[entrypoint] generating ssh host keys..."
sudo ssh-keygen -A
fi

# Start sshd in background.
echo "[entrypoint] starting sshd on :$SSHD_PORT"
sudo /usr/sbin/sshd -D -e -p "$SSHD_PORT" -o MaxAuthTries=20 -o PasswordAuthentication=no -o PermitEmptyPasswords=no &

if [[ $# -gt 0 ]]; then
  echo "[entrypoint] exec: $*"
  exec "$@"
else
  echo "[entrypoint] no CMD given; sleeping."
  exec sleep infinity
fi
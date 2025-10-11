#!/usr/bin/env bash
set -euo pipefail

POLICY_USER_DIR="$HOME/.config/containers"
POLICY_SYSTEM_FILE="/etc/containers/policy.json"

mkdir -p "$POLICY_USER_DIR"

cat > "$POLICY_USER_DIR/policy.json" <<'JSON'
{
  "default": [
    {
      "type": "insecureAcceptAnything"
    }
  ]
}
JSON

echo "Wrote $POLICY_USER_DIR/policy.json"

if [ "$EUID" -ne 0 ]; then
  echo "To write system-wide policy.json, run: sudo mkdir -p /etc/containers && sudo tee /etc/containers/policy.json >/dev/null <<'JSON'
{ "default": [ { "type": "insecureAcceptAnything" } ] }
JSON"
else
  mkdir -p /etc/containers
  cat > /etc/containers/policy.json <<'JSON'
{ "default": [ { "type": "insecureAcceptAnything" } ] }
JSON
  echo "Wrote /etc/containers/policy.json"
fi

echo "podman/buildah policy.json helper: done"

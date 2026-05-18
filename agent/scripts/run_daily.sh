#!/usr/bin/env bash
# ai-seo-agent daily runner. Cron-installable.
#
# Called by /etc/cron.d/ai-seo-daily (or systemd timer). Runs the
# platform-agnostic pipeline across every enrolled site.
#
# Log location: /var/log/ai-seo/daily.log (caller's responsibility
# to create + rotate; fallback: stderr).
#
# Never mutates Shopify / GitHub / user-facing state. Only reads from
# Google APIs and writes to SeoReport + on-disk snapshots.

set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT/agent"

# Prefer uv run if available; fall back to .venv; fall back to PATH.
if command -v uv >/dev/null 2>&1; then
    exec uv run --frozen ai-seo-agent report --all
elif [ -x ".venv/bin/ai-seo-agent" ]; then
    exec ".venv/bin/ai-seo-agent" report --all
else
    exec ai-seo-agent report --all
fi

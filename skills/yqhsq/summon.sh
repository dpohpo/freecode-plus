#!/usr/bin/env bash
set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/scripts" && pwd)"
WORK_DIR="${1:-$(pwd)}"

bash "$SCRIPTS_DIR/launch.sh" --work-dir "$WORK_DIR"

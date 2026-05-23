#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="$HOME/.freecode-plus/backups/$STAMP"

mkdir -p "$BACKUP_DIR" "$HOME/.config/free-code" "$HOME/.claude/agents" "$HOME/.claude/commands" "$HOME/bin" "$HOME/.freecode-plus"

backup_path() {
  local path="$1"
  if [[ -e "$path" || -L "$path" ]]; then
    local name
    name="$(echo "$path" | sed 's#^/##; s#/#__#g')"
    cp -R "$path" "$BACKUP_DIR/$name"
  fi
}

backup_path "$HOME/bin/free-code"
backup_path "$HOME/.config/free-code"
backup_path "$HOME/.claude/agents"
backup_path "$HOME/.claude/commands/yqhsq.md"
backup_path "$HOME/.agent-shared-skills/current"

if ! command -v rsync >/dev/null 2>&1; then
  echo "rsync is required." >&2
  exit 1
fi

if ! command -v bun >/dev/null 2>&1; then
  echo "bun is required. Install Bun first, then rerun this installer." >&2
  exit 1
fi

cd "$ROOT"
bun install
bun run build

if [[ -x "$ROOT/cli" ]]; then
  ln -sfn "$ROOT/cli" "$HOME/bin/free-code"
else
  ln -sfn "$ROOT/scripts/freecode-source-cli.sh" "$HOME/bin/free-code"
fi

RELEASE_DIR="$HOME/.agent-shared-skills/releases/freecode-plus"
rm -rf "$RELEASE_DIR"
mkdir -p "$RELEASE_DIR"
rsync -a --delete "$ROOT/skills/" "$RELEASE_DIR/skills/"
ln -sfn "$RELEASE_DIR" "$HOME/.agent-shared-skills/current"
ln -sfn "$HOME/.agent-shared-skills/current/skills" "$HOME/.claude/skills"

rsync -a "$ROOT/plus/claude/agents/" "$HOME/.claude/agents/"
rsync -a "$ROOT/plus/claude/commands/" "$HOME/.claude/commands/"

if [[ ! -f "$HOME/.config/free-code/freeds.settings.json" ]]; then
  cp "$ROOT/plus/config/freeds.settings.example.json" "$HOME/.config/free-code/freeds.settings.json"
fi

if [[ ! -f "$HOME/.config/free-code/freeglm.settings.json" ]]; then
  cp "$ROOT/plus/config/freeglm.settings.example.json" "$HOME/.config/free-code/freeglm.settings.json"
fi

if [[ ! -f "$HOME/.config/free-code/agent-team-model-profiles.json" ]]; then
  cp "$ROOT/plus/config/agent-team-model-profiles.example.json" "$HOME/.config/free-code/agent-team-model-profiles.json"
fi

chmod 700 "$HOME/.config/free-code" "$HOME/.freecode-plus" "$HOME/.freecode-plus/backups" "$BACKUP_DIR" 2>/dev/null || true
chmod 600 "$HOME/.config/free-code/"*.json 2>/dev/null || true

sed "s#__FREECODE_PLUS_ROOT__#$ROOT#g" "$ROOT/plus/shell/freecode-plus.zsh.template" > "$HOME/.freecode-plus/freecode-plus.zsh"

if ! grep -q 'freecode-plus/freecode-plus.zsh' "$HOME/.zshrc" 2>/dev/null; then
  {
    echo ''
    echo '# freecode-plus'
    echo 'source "$HOME/.freecode-plus/freecode-plus.zsh"'
  } >> "$HOME/.zshrc"
fi

"$HOME/bin/free-code" --version
find "$HOME/.agent-shared-skills/current/skills" -name SKILL.md | wc -l | awk '{print "installed_skills=" $1}'

echo "Installed freecode-plus from $ROOT"
echo "Local backup: $BACKUP_DIR"
echo "Open a new shell, then run: freeglm or freeds"

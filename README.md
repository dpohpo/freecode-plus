# freecode-plus

`freecode-plus` is the local Free Code distribution used for the GLM, DeepSeek,
and Claude lanes on this machine. It contains:

- the patched Free Code source tree
- `freeglm` and `freeds` launch helpers
- official Agent Teams support for `/yqhsq`
- the shared skill snapshot under `skills/`
- install, rollback, and security notes under `plus/`

This repository intentionally does **not** contain API keys, generated settings,
local caches, `node_modules`, virtual environments, or compiled binaries.

## Quick Install

```bash
git clone https://github.com/dpohpo/freecode-plus.git
cd freecode-plus
./plus/install/install-freecode-plus.sh
```

Then add this to `~/.zshrc` if the installer did not add it for you:

```bash
source "$HOME/.freecode-plus/freecode-plus.zsh"
```

Run:

```bash
freeglm
freeds
```

Inside Free Code, use `/yqhsq` to create the six teammate agents through the
official Agent Teams tools. The teammates use `model: inherit`, so a GLM session
spawns GLM teammates, a DeepSeek session spawns DeepSeek teammates, and a Claude
session keeps Claude teammates.

## Required Secrets

Store provider keys on each employee machine. Do not commit them.

```bash
security add-generic-password -a "$USER" -s freecode-zai-api-key -w '<glm-or-zai-key>' -U
security add-generic-password -a "$USER" -s freecode-deepseek-api-key -w '<deepseek-key>' -U
security add-generic-password -a "$USER" -s freecode-anthropic-api-key -w '<anthropic-key>' -U
```

Environment variables also work:

```bash
export ZAI_API_KEY='...'
export DEEPSEEK_API_KEY='...'
export ANTHROPIC_API_KEY='...'
```

## Repository Layout

- `src/`, `scripts/`, `package.json`: patched Free Code source
- `scripts/glm-agent-team`: GLM launcher
- `scripts/deepseek-agent-team`: DeepSeek launcher
- `scripts/ensure-agent-team-profiles`: creates local model profile config
- `skills/`: shared skill snapshot
- `plus/claude/agents/`: teammate role files
- `plus/claude/commands/yqhsq.md`: `/yqhsq` command
- `plus/config/`: safe example config, no keys
- `plus/install/`: installer
- `plus/docs/`: rollback and security docs

## Build

Install Bun, then:

```bash
bun install
bun run build
```

The source launchers can also run without a compiled binary through
`scripts/freecode-source-cli.sh`, which executes `src/entrypoints/cli.tsx`.

## Rollback

Before this repository was created, a local backup was written on the source
machine. See `plus/docs/ROLLBACK.md` for the rollback procedure.

## Upstream README

The original Free Code README is preserved at `UPSTREAM_README.md`.

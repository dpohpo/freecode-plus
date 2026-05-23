# Rollback

## Source Machine Backup

Before `freecode-plus` was prepared, a local backup was created at:

```text
/Volumes/金阳/backups/freecode-plus-prepublish-20260523-080147
```

It contains:

- `free-code/`: source tree snapshot
- `free-code-all-refs.bundle`: git bundle of all local refs
- `free-code-working-tree.diff`: current working tree patch
- `home/config-free-code/`: local Free Code config, including private generated settings
- `home/claude-agents/`: local agent definitions
- `home/claude-commands/yqhsq.md`: current `/yqhsq` command
- `agent-shared-skills-release/`: shared skill release snapshot

That backup is local-only and may contain private keys. Do not upload it.

## Restore Source Tree

```bash
rsync -a --delete /Volumes/金阳/backups/freecode-plus-prepublish-20260523-080147/free-code/ /Volumes/金阳/projects/free-code/
```

## Restore Home Config

```bash
rsync -a --delete /Volumes/金阳/backups/freecode-plus-prepublish-20260523-080147/home/config-free-code/ "$HOME/.config/free-code/"
rsync -a --delete /Volumes/金阳/backups/freecode-plus-prepublish-20260523-080147/home/claude-agents/ "$HOME/.claude/agents/"
rsync -a /Volumes/金阳/backups/freecode-plus-prepublish-20260523-080147/home/claude-commands/yqhsq.md "$HOME/.claude/commands/yqhsq.md"
```

## Restore Git Refs From Bundle

```bash
mkdir -p /tmp/free-code-restore
git clone /Volumes/金阳/backups/freecode-plus-prepublish-20260523-080147/free-code-all-refs.bundle /tmp/free-code-restore
```

## Installer Backups On Employee Machines

The installer writes per-machine backups to:

```text
~/.freecode-plus/backups/<timestamp>
```

Restore files from there if an installation overwrites local config unexpectedly.

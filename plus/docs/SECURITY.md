# Security Notes

This repository is designed to be cloneable by employees without sharing the
owner machine's credentials.

Do not commit:

- `~/.config/free-code/agent-team-model-profiles.json`
- `~/.config/free-code/agent-team-generated-settings/`
- provider keys
- keychain exports
- `.env` files
- `node_modules/`
- Python virtual environments
- compiled binaries with local paths baked in

The checked-in files under `plus/config/` are examples only. They use
`apiKeyHelper` commands so every machine reads its own provider keys from
Keychain.

The launchers intentionally avoid `--bare` for normal `freeds` and `freeglm`
sessions because `--bare` disables default skill and custom-agent discovery.
That behavior was the source of previous DeepSeek teammate isolation failures.

Before pushing, run:

```bash
rg -n --hidden 'sk-[A-Za-z0-9_-]{20,}|gh[opsu]_[A-Za-z0-9_]{20,}|authToken\"\\s*:\\s*\"[^\"$]|apiKey\"\\s*:\\s*\"sk-' .
```

Investigate every hit before publishing.

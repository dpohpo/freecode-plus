# Teammate Model Isolation

The intended architecture is provider-local inheritance.

1. The entry lane (`freeglm`, `freeds`, or Claude) sets the active model and
   provider environment.
2. Agent role files use `model: inherit`.
3. The Agent Teams spawn path resolves `inherit` to the current model.
4. If the resolved model name is provider-specific, the spawn path detects the
   profile alias and writes a generated local settings file.
5. The teammate starts with that model and settings file.

Expected examples:

- `glm-5.1` parent -> `glm-5.1` teammates with GLM base URL and token
- `deepseek-v4-pro` parent -> `deepseek-v4-pro` teammates with DeepSeek base URL and key
- `opus` parent -> `opus` teammates with normal Claude settings

The `/yqhsq` command should create the team through official Free Code Agent
Teams tools only:

- `TeamCreate`
- `Agent`
- `SendMessage`

It should not use `hcom`, manual tmux roster files, or the old `launch.sh`.

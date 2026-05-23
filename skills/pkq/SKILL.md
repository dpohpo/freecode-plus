# /pkq - Pokemon Mascot Customizer

Replace the Free Code CLI mascot with any Pokemon (or custom image) using Unicode block art.

## Quick Usage

```bash
# Default: Pikachu 20x40 (auto-install, download, patch, build)
python3 ~/.claude/skills/pkq/scripts/generate_art.py

# Bigger/smaller
python3 ~/.claude/skills/pkq/scripts/generate_art.py --height 30 --width 60

# Different Pokemon (by Pokedex ID)
python3 ~/.claude/skills/pkq/scripts/generate_art.py --pokemon 6    # Charizard
python3 ~/.claude/skills/pkq/scripts/generate_art.py --pokemon 150  # Mewtwo
python3 ~/.claude/skills/pkq/scripts/generate_art.py --pokemon 133  # Eevee

# Custom image
python3 ~/.claude/skills/pkq/scripts/generate_art.py --image ~/my_logo.png

# Preview without patching
python3 ~/.claude/skills/pkq/scripts/generate_art.py --preview

# Save to file
python3 ~/.claude/skills/pkq/scripts/generate_art.py --output ~/pikachu_art.txt
```

## What it does

1. Auto-installs `img2unicode` in `/tmp/img2u-env` (one-time)
2. Downloads official Pokemon sprite from PokeAPI
3. Converts to Unicode quad-block art (▛▜▟▙) with full RGB color
4. Patches `~/projects/free-code/src/components/LogoV2/Clawd.tsx`
5. Rebuilds `cli-dev` binary

## Dependencies

- Python 3.11+ (system)
- Bun (for building free-code)
- Internet (for downloading sprites)
- img2unicode (auto-installed)

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--pokemon, -p` | 25 | Pokedex ID |
| `--image, -i` | - | Custom image path |
| `--height` | 20 | Art height (rows) |
| `--width` | 40 | Art width (columns) |
| `--output, -o` | - | Save art file only |
| `--no-build` | false | Skip rebuild |
| `--preview` | false | Preview in terminal |

#!/usr/bin/env python3
"""
Imagen API Image Generator
Generate product lifestyle images for Amazon using Google Imagen API
"""

import os
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def get_access_token():
    """Get OAuth access token from Gemini credentials"""
    creds_path = Path.home() / ".gemini" / "oauth_creds.json"
    if not creds_path.exists():
        return None

    try:
        with open(creds_path) as f:
            data = json.load(f)
            return data.get("access_token") or data.get("token")
    except:
        return None

def generate_imagen_image(prompt, output_dir=None, aspect_ratio="1:1"):
    """
    Generate image using Imagen API

    Args:
        prompt: Text prompt for image generation
        output_dir: Directory to save image (default: ~/Desktop/scene-images)
        aspect_ratio: Image aspect ratio (default: "1:1" for Amazon)

    Returns:
        Path to generated image or None if failed
    """
    token = get_access_token()
    if not token:
        print("Error: Could not get access token", file=sys.stderr)
        return None

    if output_dir is None:
        output_dir = Path.home() / "Desktop" / "scene-images"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Use gemini CLI to generate image via its tool
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_prompt_file = Path(f"/tmp/imagen_prompt_{timestamp}.txt")

    try:
        # Write prompt to file
        temp_prompt_file.write_text(prompt)

        # Call gemini with Imagen capability
        cmd = [
            "gemini",
            "-y",  # yolo mode
            "-p",
            f"Create a professional product lifestyle image using your image generation capability. Here is the detailed prompt:\n\n{prompt}\n\nPlease save the image and output the exact file path."
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(output_dir)
        )

        # Look for generated image files
        image_files = []
        for ext in [".png", ".jpg", ".jpeg", ".webp"]:
            image_files.extend(output_dir.glob(f"*{ext}"))

        if image_files:
            # Get the most recently modified file
            latest = max(image_files, key=lambda p: p.stat().st_mtime)
            return str(latest)

        # If gemini didn't create file, try to parse output
        output = result.stdout + result.stderr
        for line in output.split("\n"):
            for ext in [".png", ".jpg", ".jpeg", ".webp"]:
                if ext in line and "/" in line:
                    # Extract potential file path
                    parts = line.split(ext)
                    if parts:
                        potential_path = parts[0].split()[-1] + ext
                        if Path(potential_path).exists():
                            return potential_path

        return None

    except subprocess.TimeoutExpired:
        print("Error: Image generation timed out", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None
    finally:
        if temp_prompt_file.exists():
            temp_prompt_file.unlink()

def main():
    if len(sys.argv) < 2:
        print("Usage: gen_image.py '<prompt>' [output_dir]", file=sys.stderr)
        sys.exit(1)

    prompt = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    result = generate_imagen_image(prompt, output_dir)

    if result:
        print(result)
        sys.exit(0)
    else:
        print("Error: Failed to generate image", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

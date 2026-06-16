"""
Download game sprites from the official TBH wiki CDN.
These images are used as visual templates for chest detection.

Usage:
    python scripts/download_assets.py
"""

import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

try:
    import requests
    import cv2
    import numpy as np
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Run: pip install requests opencv-python numpy")
    sys.exit(1)

CDN_BASE = "https://taskbarhero.net/TBH_%20Task%20Bar%20Hero%20Wiki%20%26%20Database_files/"

# Mapeamento: destino local → nome no CDN
ASSETS: dict[str, list[str]] = {
    "ui": [
        ("blue_chest_icon",       "Item_910011"),    # Stage Box (baú azul)
        ("gold_icon",             "Icon_Gold"),
        ("gold_icon_3",           "Icon_Gold_3_0"),
        ("soulstone_normal",      "Item_190001"),    # Soulstone Normal
        ("soulstone_nightmare",   "Item_190002"),    # Soulstone Nightmare
        ("soulstone_hell",        "Item_190003"),    # Soulstone Hell
        ("soulstone_torment",     "Item_190004"),    # Soulstone Torment
        ("menu_stat_active",      "MenuButton_Stat_Active"),
    ],
    "items": [
        # Gems por raridade (para reconhecimento de drops)
        ("gem_ruby",      "Item_110001"),
        ("gem_sapphire",  "Item_110002"),
        ("gem_topaz",     "Item_110003"),
        ("gem_emerald",   "Item_110004"),
        ("gem_amethyst",  "Item_110005"),
    ],
    "heroes": [
        ("hero_knight",    "HeroArt_101"),
        ("hero_ranger",    "HeroArt_201"),
        ("hero_sorcerer",  "HeroArt_301"),
        ("hero_priest",    "HeroArt_401"),
        ("hero_hunter",    "HeroArt_501"),
        ("hero_slayer",    "HeroArt_601"),
    ],
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def download_image(cdn_name: str, dest_path: Path) -> bool:
    url = CDN_BASE + cdn_name + ".png"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 200 and len(resp.content) > 100:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dest_path, "wb") as f:
                f.write(resp.content)
            return True
        print(f"  [{resp.status_code}] {cdn_name}")
        return False
    except Exception as e:
        print(f"  [ERRO] {cdn_name}: {e}")
        return False


def verify_image(path: Path) -> bool:
    try:
        img = cv2.imread(str(path))
        return img is not None and img.size > 0
    except Exception:
        return False


def main():
    templates_dir = ROOT / "templates"
    print("=" * 55)
    print("  TBH Bot — Download de Assets do Jogo")
    print("=" * 55)
    print(f"  Destino: {templates_dir}")
    print()

    total = sum(len(v) for v in ASSETS.values())
    downloaded = 0
    skipped = 0
    failed = 0

    for subfolder, items in ASSETS.items():
        dest_dir = templates_dir / subfolder
        dest_dir.mkdir(parents=True, exist_ok=True)
        print(f"  [{subfolder.upper()}]")

        for local_name, cdn_name in items:
            dest = dest_dir / f"{local_name}.png"

            if dest.exists() and verify_image(dest):
                print(f"    ✓  {local_name:<30} (já existe)")
                skipped += 1
                continue

            print(f"    ↓  {local_name:<30}", end="", flush=True)
            ok = download_image(cdn_name, dest)
            if ok and verify_image(dest):
                print(f" ✅")
                downloaded += 1
            else:
                print(f" ❌ falhou")
                failed += 1
                if dest.exists():
                    dest.unlink()

            time.sleep(0.3)  # Rate limiting

        print()

    print("=" * 55)
    print(f"  Baixados: {downloaded}   Já existiam: {skipped}   Falhas: {failed}")
    if failed > 0:
        print()
        print("  ⚠ Alguns assets falharam. O bot pode não detectar")
        print("    esses elementos visualmente.")
    else:
        print()
        print("  ✅ Todos os assets foram baixados com sucesso!")
    print("=" * 55)


if __name__ == "__main__":
    main()

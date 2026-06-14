"""
Debug tool: captures the game window and draws bounding boxes for every
template that matches, then saves an annotated image.

Usage:
    python scripts/debug_vision.py [--threshold 0.75]
"""

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

try:
    import cv2
    import numpy as np
except ImportError:
    print("Missing: pip install opencv-python numpy")
    sys.exit(1)

from tbh.config import Config
from tbh.window import GameWindow
from tbh.capture import ScreenCapture
from tbh.vision import TemplateMatcher


def main():
    parser = argparse.ArgumentParser(description="TBH Vision Debugger")
    parser.add_argument("--threshold", type=float, default=0.75, help="Match threshold (default 0.75)")
    args = parser.parse_args()

    config = Config.load()
    window = GameWindow(
        process_name=config.settings.window.process_name,
        title_fragment=config.settings.window.window_title_fragment,
    )
    window.find()
    capture = ScreenCapture(window)
    matcher = TemplateMatcher(threshold=args.threshold, dpi_scale=config.settings.window.dpi_scale)

    print(f"Capturando janela do jogo (threshold={args.threshold})...")
    try:
        frame = capture.grab_window()
    except RuntimeError as e:
        print(f"Erro: {e}")
        print("O jogo está aberto?")
        sys.exit(1)

    annotated = frame.copy()
    templates_dir = ROOT / "templates"
    found_any = False

    for png in sorted(templates_dir.rglob("*.png")):
        name = png.stem
        matches = matcher.find_all(frame, name)
        for match in matches:
            found_any = True
            x, y, w, h = match.rect
            cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 255, 0), 2)
            label = f"{name} ({match.confidence:.2f})"
            cv2.putText(
                annotated, label, (x, max(y - 4, 12)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1
            )
            print(f"  FOUND  {name:<30} conf={match.confidence:.3f}  center={match.center}")

    if not found_any:
        print("Nenhum template encontrado. Verifique se os templates foram capturados.")

    output_dir = ROOT / "debug_output"
    output_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = output_dir / f"debug_{ts}.png"
    cv2.imwrite(str(out_path), annotated)
    print(f"\nImagem de debug salva: {out_path}")

    try:
        from PIL import Image
        Image.fromarray(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)).show()
    except ImportError:
        pass


if __name__ == "__main__":
    main()

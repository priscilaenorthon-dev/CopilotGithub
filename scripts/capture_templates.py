"""
Interactive template capture tool.

Usage:
    python scripts/capture_templates.py

Controls:
    F9      → take screenshot and open region selector
    Escape  → quit

With the region selector open:
    Click and drag to draw a rectangle around the UI element.
    Release mouse → you will be prompted for a name → saved to templates/
"""

import sys
import time
import tkinter as tk
from pathlib import Path

ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = ROOT / "templates"

try:
    import cv2
    import numpy as np
    import mss
    import pyautogui
    from PIL import Image, ImageTk
    import keyboard
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Run: pip install opencv-python mss pyautogui pillow keyboard")
    sys.exit(1)


class RegionSelector(tk.Toplevel):
    def __init__(self, screenshot: np.ndarray):
        super().__init__()
        self.screenshot = screenshot
        self.result: tuple[int, int, int, int] | None = None
        self._start: tuple[int, int] | None = None
        self._rect_id = None

        self.attributes("-fullscreen", True)
        self.attributes("-alpha", 0.4)
        self.config(bg="black", cursor="crosshair")

        h, w = screenshot.shape[:2]
        img = Image.fromarray(cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB))
        self._photo = ImageTk.PhotoImage(img)

        self.canvas = tk.Canvas(self, width=w, height=h, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self._photo)

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Escape>", lambda _: self.destroy())

        label = tk.Label(
            self,
            text="Selecione a região da UI. Pressione Esc para cancelar.",
            bg="#222",
            fg="white",
            font=("Arial", 12),
        )
        label.place(x=10, y=10)

    def _on_press(self, event):
        self._start = (event.x, event.y)
        if self._rect_id:
            self.canvas.delete(self._rect_id)

    def _on_drag(self, event):
        if self._start:
            self._rect_id = self.canvas.create_rectangle(
                *self._start, event.x, event.y,
                outline="lime", width=2,
            )

    def _on_release(self, event):
        if self._start:
            x1, y1 = self._start
            x2, y2 = event.x, event.y
            self.result = (min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
            self.destroy()


def prompt_save_name(crop: np.ndarray) -> str | None:
    root = tk.Tk()
    root.title("Salvar template")
    root.resizable(False, False)

    h, w = crop.shape[:2]
    preview = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
    if w > 300 or h > 200:
        preview.thumbnail((300, 200))
    photo = ImageTk.PhotoImage(preview)

    tk.Label(root, image=photo).pack(padx=8, pady=8)
    tk.Label(root, text="Nome do template (sem extensão):").pack(padx=8)

    name_var = tk.StringVar()
    entry = tk.Entry(root, textvariable=name_var, width=30)
    entry.pack(padx=8, pady=4)
    entry.focus()

    result = [None]

    def _save():
        result[0] = name_var.get().strip()
        root.destroy()

    def _cancel():
        root.destroy()

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=6)
    tk.Button(btn_frame, text="Salvar", command=_save).pack(side="left", padx=4)
    tk.Button(btn_frame, text="Cancelar", command=_cancel).pack(side="left", padx=4)

    entry.bind("<Return>", lambda _: _save())
    root.mainloop()
    return result[0]


def determine_subfolder(name: str) -> str:
    """Auto-detect template subfolder based on name prefix."""
    if name.startswith("stage_"):
        return "stages"
    if any(name.startswith(p) for p in ("act1_", "act2_", "act3_", "stage_selected", "stage_button")):
        return "portal_menu"
    return "ui"


def capture_and_save():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        raw = sct.grab(monitor)
        screenshot = np.array(raw)[:, :, :3]

    root = tk.Tk()
    root.withdraw()
    selector = RegionSelector(screenshot)
    root.wait_window(selector)
    root.destroy()

    if selector.result is None:
        print("Captura cancelada.")
        return

    x, y, w, h = selector.result
    if w < 4 or h < 4:
        print("Região muito pequena, tente novamente.")
        return

    crop = screenshot[y:y+h, x:x+w]
    name = prompt_save_name(crop)
    if not name:
        print("Nenhum nome fornecido.")
        return

    subfolder = determine_subfolder(name)
    save_dir = TEMPLATES_DIR / subfolder
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / f"{name}.png"
    cv2.imwrite(str(save_path), crop)
    print(f"Template salvo: {save_path}")


def main():
    print("=" * 50)
    print("TBH Template Capture Tool")
    print("=" * 50)
    print("Pressione F9 para capturar um template.")
    print("Pressione Esc para sair.\n")

    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    for sub in ("ui", "portal_menu", "stages"):
        (TEMPLATES_DIR / sub).mkdir(exist_ok=True)

    keyboard.add_hotkey("F9", capture_and_save)
    keyboard.wait("esc")
    print("Saindo.")


if __name__ == "__main__":
    main()

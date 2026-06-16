import logging
import numpy as np
from pathlib import Path
from .utils import Rect
from .window import GameWindow

logger = logging.getLogger("tbh.capture")


class ScreenCapture:
    """Captures the game window region using mss for low-latency grabs."""

    def __init__(self, window: GameWindow, monitor_index: int = 1):
        self.window = window
        self.monitor_index = monitor_index
        self._sct = None

    def _get_sct(self):
        if self._sct is None:
            import mss
            self._sct = mss.mss()
        return self._sct

    def grab_window(self) -> np.ndarray:
        rect = self.window.get_rect()
        if rect is None:
            raise RuntimeError("Game window not found — cannot capture")
        return self.grab_region(rect)

    def grab_region(self, rect: Rect) -> np.ndarray:
        sct = self._get_sct()
        monitor = {
            "left": rect.left,
            "top": rect.top,
            "width": rect.width,
            "height": rect.height,
        }
        screenshot = sct.grab(monitor)
        frame = np.array(screenshot)
        # mss returns BGRA — drop alpha channel
        return frame[:, :, :3]

    def save_debug(self, frame: np.ndarray, path: str | Path) -> None:
        import cv2
        cv2.imwrite(str(path), frame)
        logger.debug(f"Saved debug frame: {path}")

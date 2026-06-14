import logging
import time
from .utils import Rect
from .window import GameWindow

logger = logging.getLogger("tbh.controller")


class MouseController:
    """Translates window-relative coordinates to screen-absolute and drives mouse/keyboard."""

    def __init__(self, window: GameWindow, click_delay_ms: int = 150, hover_delay_ms: int = 300):
        self.window = window
        self.click_delay_ms = click_delay_ms
        self.hover_delay_ms = hover_delay_ms

    def _to_screen(self, x: int, y: int) -> tuple[int, int]:
        rect = self.window.get_rect()
        if rect is None:
            raise RuntimeError("Cannot resolve screen coordinates — window not found")
        return rect.left + x, rect.top + y

    def click(self, x: int, y: int, relative: bool = True) -> None:
        import pyautogui
        sx, sy = self._to_screen(x, y) if relative else (x, y)
        logger.debug(f"Click ({sx}, {sy})")
        pyautogui.click(sx, sy)
        time.sleep(self.click_delay_ms / 1000)

    def right_click(self, x: int, y: int, relative: bool = True) -> None:
        import pyautogui
        sx, sy = self._to_screen(x, y) if relative else (x, y)
        logger.debug(f"Right-click ({sx}, {sy})")
        pyautogui.rightClick(sx, sy)
        time.sleep(self.click_delay_ms / 1000)

    def hover(self, x: int, y: int, relative: bool = True) -> None:
        import pyautogui
        sx, sy = self._to_screen(x, y) if relative else (x, y)
        logger.debug(f"Hover ({sx}, {sy})")
        pyautogui.moveTo(sx, sy)
        time.sleep(self.hover_delay_ms / 1000)

    def double_click(self, x: int, y: int, relative: bool = True) -> None:
        import pyautogui
        sx, sy = self._to_screen(x, y) if relative else (x, y)
        logger.debug(f"Double-click ({sx}, {sy})")
        pyautogui.doubleClick(sx, sy)
        time.sleep(self.click_delay_ms / 1000)

    def scroll(self, x: int, y: int, clicks: int, relative: bool = True) -> None:
        import pyautogui
        sx, sy = self._to_screen(x, y) if relative else (x, y)
        logger.debug(f"Scroll ({sx}, {sy}) by {clicks}")
        pyautogui.scroll(clicks, x=sx, y=sy)
        time.sleep(self.click_delay_ms / 1000)

    def press_escape(self) -> None:
        import pyautogui
        pyautogui.press("escape")
        time.sleep(self.click_delay_ms / 1000)

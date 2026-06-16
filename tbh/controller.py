import logging
import time
from .window import GameWindow

logger = logging.getLogger("tbh.controller")


class MouseController:
    """Traduz coordenadas relativas à janela para absolutas na tela e controla o mouse.

    Usa pydirectinput para cliques (melhor compatibilidade com jogos via DirectInput).
    Mantém pyautogui para scroll e teclado, que pydirectinput não suporta completamente.
    """

    def __init__(self, window: GameWindow, click_delay_ms: int = 150, hover_delay_ms: int = 300):
        self.window = window
        self.click_delay_ms = click_delay_ms
        self.hover_delay_ms = hover_delay_ms

    def _to_screen(self, x: int, y: int) -> tuple[int, int]:
        rect = self.window.get_rect()
        if rect is None:
            raise RuntimeError("Não foi possível resolver coordenadas — janela não encontrada")
        return rect.left + x, rect.top + y

    # ── Cliques (pydirectinput) ───────────────────────────────────────────────

    def click(self, x: int, y: int, relative: bool = True) -> None:
        sx, sy = self._to_screen(x, y) if relative else (x, y)
        logger.debug(f"Click ({sx}, {sy})")
        try:
            import pydirectinput
            pydirectinput.click(sx, sy)
        except ImportError:
            import pyautogui
            pyautogui.click(sx, sy)
        time.sleep(self.click_delay_ms / 1000)

    def right_click(self, x: int, y: int, relative: bool = True) -> None:
        sx, sy = self._to_screen(x, y) if relative else (x, y)
        logger.debug(f"Right-click ({sx}, {sy})")
        try:
            import pydirectinput
            pydirectinput.rightClick(sx, sy)
        except ImportError:
            import pyautogui
            pyautogui.rightClick(sx, sy)
        time.sleep(self.click_delay_ms / 1000)

    def double_click(self, x: int, y: int, relative: bool = True) -> None:
        sx, sy = self._to_screen(x, y) if relative else (x, y)
        logger.debug(f"Double-click ({sx}, {sy})")
        try:
            import pydirectinput
            pydirectinput.doubleClick(sx, sy)
        except ImportError:
            import pyautogui
            pyautogui.doubleClick(sx, sy)
        time.sleep(self.click_delay_ms / 1000)

    def hover(self, x: int, y: int, relative: bool = True) -> None:
        sx, sy = self._to_screen(x, y) if relative else (x, y)
        logger.debug(f"Hover ({sx}, {sy})")
        try:
            import pydirectinput
            pydirectinput.moveTo(sx, sy)
        except ImportError:
            import pyautogui
            pyautogui.moveTo(sx, sy)
        time.sleep(self.hover_delay_ms / 1000)

    # ── Scroll e teclado (pyautogui — pydirectinput não suporta) ─────────────

    def scroll(self, x: int, y: int, clicks: int, relative: bool = True) -> None:
        import pyautogui
        sx, sy = self._to_screen(x, y) if relative else (x, y)
        logger.debug(f"Scroll ({sx}, {sy}) clicks={clicks}")
        pyautogui.scroll(clicks, x=sx, y=sy)
        time.sleep(self.click_delay_ms / 1000)

    def press_escape(self) -> None:
        try:
            import pydirectinput
            pydirectinput.press("escape")
        except ImportError:
            import pyautogui
            pyautogui.press("escape")
        time.sleep(self.click_delay_ms / 1000)

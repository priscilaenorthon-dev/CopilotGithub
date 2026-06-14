import logging
import time
from typing import Optional
from .utils import Rect

logger = logging.getLogger("tbh.window")

# Title fragments that identify TBH game panel windows
_PANEL_TITLES = ["HERO", "PORTAL", "STASH", "Task Bar Hero", "TBH"]
# Process executable names to try (Steam may rename)
_PROCESS_NAMES = ["TBH.exe", "TaskBarHero.exe", "tbh.exe"]


class WindowNotFoundError(Exception):
    pass


class GameWindow:
    """Detects and manages the TBH game window using pywin32.

    TBH runs as three separate floating panels (STASH, HERO, PORTAL).
    get_rect() returns the COMBINED bounding box of all visible panels so that
    a single mss capture covers every UI element the bot needs.
    """

    def __init__(self, process_name: str = "TBH.exe", title_fragment: str = "Task Bar Hero"):
        self.process_name = process_name
        self.title_fragment = title_fragment
        self._hwnd: Optional[int] = None
        self._game_pid: Optional[int] = None

    # ── Public API ────────────────────────────────────────────────────────────

    def find(self) -> Optional[int]:
        """Find the primary game window (prefers HERO panel)."""
        try:
            import win32gui
            import win32process
            import psutil

            candidates: list[tuple[int, str]] = []

            def _cb(hwnd, _):
                if not win32gui.IsWindowVisible(hwnd):
                    return True
                title = win32gui.GetWindowText(hwnd)
                if not title:
                    return True
                title_up = title.upper()
                for frag in _PANEL_TITLES:
                    if frag.upper() in title_up:
                        try:
                            _, pid = win32process.GetWindowThreadProcessId(hwnd)
                            proc = psutil.Process(pid)
                            name = proc.name().lower()
                            if any(p.lower() in name for p in _PROCESS_NAMES):
                                candidates.append((hwnd, title))
                                return True
                        except Exception:
                            candidates.append((hwnd, title))
                        return True
                return True

            win32gui.EnumWindows(_cb, None)

            if not candidates:
                self._hwnd = None
                return None

            # Prefer HERO panel as primary anchor window
            for hwnd, title in candidates:
                if "HERO" in title.upper():
                    self._hwnd = hwnd
                    self._game_pid = self._get_pid(hwnd)
                    logger.debug(f"Found HERO panel hwnd={hwnd}, pid={self._game_pid}")
                    return hwnd

            # Fallback: any found panel
            self._hwnd, title = candidates[0]
            self._game_pid = self._get_pid(self._hwnd)
            logger.debug(f"Found game panel hwnd={self._hwnd}, title='{title}'")
            return self._hwnd

        except ImportError:
            logger.warning("pywin32 not available — falling back to mock window")
            return self._mock_find()

    def is_open(self) -> bool:
        if self._hwnd is None:
            return self.find() is not None
        try:
            import win32gui
            return win32gui.IsWindow(self._hwnd) and win32gui.IsWindowVisible(self._hwnd)
        except ImportError:
            return self._hwnd is not None

    def is_expanded(self) -> bool:
        rect = self.get_rect()
        if rect is None:
            return False
        return rect.height > 80

    def bring_to_front(self) -> bool:
        """Bring the primary panel (HERO) to front."""
        if self._hwnd is None:
            return False
        try:
            import win32gui
            import win32con
            win32gui.ShowWindow(self._hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(self._hwnd)
            time.sleep(0.1)
            return True
        except ImportError:
            return True
        except Exception as e:
            logger.warning(f"Could not bring window to front: {e}")
            return False

    def get_rect(self) -> Optional[Rect]:
        """Return the COMBINED bounding box of all visible game panels.

        Since TBH shows three separate windows (STASH, HERO, PORTAL) side by
        side, this combined rect lets a single mss capture cover all of them so
        template matching works across every panel without additional logic.
        """
        try:
            import win32gui

            hwnds = self._find_all_panel_hwnds()
            if not hwnds:
                return None

            lefts, tops, rights, bottoms = [], [], [], []
            for hwnd in hwnds:
                try:
                    l, t, r, b = win32gui.GetWindowRect(hwnd)
                    if r - l > 10 and b - t > 10:  # skip zero/tiny helper windows
                        lefts.append(l)
                        tops.append(t)
                        rights.append(r)
                        bottoms.append(b)
                except Exception:
                    continue

            if not lefts:
                return None

            combined = Rect(
                left=min(lefts),
                top=min(tops),
                width=max(rights) - min(lefts),
                height=max(bottoms) - min(tops),
            )
            logger.debug(f"Combined game area: {combined}")
            return combined

        except ImportError:
            return Rect(left=0, top=0, width=1280, height=300)
        except Exception as e:
            logger.warning(f"Could not get window rect: {e}")
            return None

    def expand(self) -> bool:
        """Click on game to expand from taskbar strip to main window."""
        rect = self.get_rect()
        if rect is None:
            return False
        try:
            import pyautogui
            pyautogui.click(rect.left + rect.width // 2, rect.top + rect.height // 2)
            time.sleep(0.5)
            return True
        except ImportError:
            logger.warning("pyautogui not available")
            return False

    def get_process_id(self) -> Optional[int]:
        if self._hwnd is None:
            return None
        return self._game_pid

    # ── Internal ──────────────────────────────────────────────────────────────

    def _find_all_panel_hwnds(self) -> list[int]:
        """Return hwnds for all visible windows belonging to the game process."""
        try:
            import win32gui
            import win32process

            result: list[int] = []

            def _cb(hwnd, _):
                if not win32gui.IsWindowVisible(hwnd):
                    return True
                title = win32gui.GetWindowText(hwnd)
                if not title:
                    return True
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    # Include any window from the same process PID
                    if self._game_pid and pid == self._game_pid:
                        result.append(hwnd)
                        return True
                except Exception:
                    pass
                # Fallback: title-fragment match
                title_up = title.upper()
                for frag in _PANEL_TITLES:
                    if frag.upper() in title_up:
                        result.append(hwnd)
                        return True
                return True

            win32gui.EnumWindows(_cb, None)
            return result if result else ([self._hwnd] if self._hwnd else [])

        except ImportError:
            return [self._hwnd] if self._hwnd else []

    def _get_pid(self, hwnd: int) -> Optional[int]:
        try:
            import win32process
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            return pid
        except Exception:
            return None

    def _mock_find(self) -> Optional[int]:
        logger.info("Mock window mode: returning fake hwnd=1")
        self._hwnd = 1
        return self._hwnd

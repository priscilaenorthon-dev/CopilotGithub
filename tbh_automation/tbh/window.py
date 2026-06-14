import logging
import time
from typing import Optional
from .utils import Rect

logger = logging.getLogger("tbh.window")


class WindowNotFoundError(Exception):
    pass


class GameWindow:
    """Detects and manages the TBH game window using pywin32."""

    def __init__(self, process_name: str = "TBH.exe", title_fragment: str = "Task Bar Hero"):
        self.process_name = process_name
        self.title_fragment = title_fragment
        self._hwnd: Optional[int] = None

    def find(self) -> Optional[int]:
        try:
            import win32gui
            import win32process
            import psutil

            def callback(hwnd, hwnds):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if self.title_fragment.lower() in title.lower():
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        try:
                            proc = psutil.Process(pid)
                            if self.process_name.lower() in proc.name().lower():
                                hwnds.append(hwnd)
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            hwnds.append(hwnd)
                return True

            hwnds = []
            win32gui.EnumWindows(callback, hwnds)

            if not hwnds:
                # Fallback: find by title fragment only
                def title_callback(hwnd, hwnds):
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if self.title_fragment.lower() in title.lower():
                            hwnds.append(hwnd)
                    return True
                win32gui.EnumWindows(title_callback, hwnds)

            self._hwnd = hwnds[0] if hwnds else None
            if self._hwnd:
                logger.debug(f"Found game window: hwnd={self._hwnd}")
            return self._hwnd

        except ImportError:
            logger.warning("pywin32 not available — falling back to mock window")
            return self._mock_find()

    def _mock_find(self) -> Optional[int]:
        """Fallback for non-Windows environments (dev/testing)."""
        logger.info("Mock window mode: returning fake hwnd=1")
        self._hwnd = 1
        return self._hwnd

    def is_open(self) -> bool:
        if self._hwnd is None:
            return self.find() is not None
        try:
            import win32gui
            return win32gui.IsWindow(self._hwnd) and win32gui.IsWindowVisible(self._hwnd)
        except ImportError:
            return self._hwnd is not None

    def is_expanded(self) -> bool:
        """Check if the main game window is expanded (not just taskbar strip)."""
        rect = self.get_rect()
        if rect is None:
            return False
        return rect.height > 80

    def bring_to_front(self) -> bool:
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
        if self._hwnd is None:
            return None
        try:
            import win32gui
            left, top, right, bottom = win32gui.GetWindowRect(self._hwnd)
            return Rect(left=left, top=top, width=right - left, height=bottom - top)
        except ImportError:
            # Mock rect for dev/testing
            return Rect(left=0, top=1040, width=400, height=200)
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
            center_x = rect.left + rect.width // 2
            center_y = rect.top + rect.height // 2
            pyautogui.click(center_x, center_y)
            time.sleep(0.5)
            return True
        except ImportError:
            logger.warning("pyautogui not available")
            return False

    def get_process_id(self) -> Optional[int]:
        if self._hwnd is None:
            return None
        try:
            import win32process
            _, pid = win32process.GetWindowThreadProcessId(self._hwnd)
            return pid
        except ImportError:
            return None

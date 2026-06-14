import logging
import threading
import time
from typing import Callable, Optional

from .capture import ScreenCapture
from .config import Config, Stage
from .controller import MouseController
from .state import GameState, GameStateDetector
from .vision import TemplateMatcher, TemplateNotFoundError
from .window import GameWindow

logger = logging.getLogger("tbh.navigator")


class NavigationError(Exception):
    pass


class StageNavigator:
    """Orchestrates the full navigation flow through portal → stage selection."""

    def __init__(
        self,
        window: GameWindow,
        capture: ScreenCapture,
        matcher: TemplateMatcher,
        controller: MouseController,
        state_detector: GameStateDetector,
        config: Config,
    ):
        self.window = window
        self.capture = capture
        self.matcher = matcher
        self.controller = controller
        self.state_detector = state_detector
        self.config = config
        self._timing = config.settings.timing
        self._on_status: Optional[Callable[[str], None]] = None

    def set_status_callback(self, callback: Callable[[str], None]) -> None:
        self._on_status = callback

    def _status(self, msg: str) -> None:
        logger.info(msg)
        if self._on_status:
            self._on_status(msg)

    # ── Public API ──────────────────────────────────────────────────────────

    def navigate_to(self, stage_id: str) -> bool:
        """Navigate to a specific stage via the portal menu. Returns True on success."""
        stage = self.config.get_stage(stage_id)
        if stage is None:
            raise NavigationError(f"Stage '{stage_id}' not found in config")

        self._status(f"Navigating to {stage.label}...")

        if not self.ensure_window_open():
            raise NavigationError("Could not open game window")

        for attempt in range(self._timing.retry_attempts):
            try:
                if not self.open_portal_menu():
                    raise NavigationError("Failed to open portal menu")

                if not self._select_stage_in_portal(stage):
                    raise NavigationError(f"Stage {stage_id} not found in portal menu")

                self._status(f"Stage {stage.label} selected successfully")
                return True
            except NavigationError as e:
                logger.warning(f"Navigation attempt {attempt + 1} failed: {e}")
                self._recover()
                if attempt < self._timing.retry_attempts - 1:
                    time.sleep(self._timing.retry_delay_ms / 1000)

        raise NavigationError(f"Navigation to {stage_id} failed after {self._timing.retry_attempts} attempts")

    def farm_loop(
        self,
        stage_ids: list[str],
        iterations: Optional[int] = None,
        stop_event: Optional[threading.Event] = None,
    ) -> None:
        """Loop through stage_ids, navigating to each one repeatedly."""
        if not stage_ids:
            raise NavigationError("No stages specified for farm loop")

        current = 0
        while True:
            if stop_event and stop_event.is_set():
                self._status("Farm loop stopped by user")
                break
            if iterations is not None and current >= iterations:
                self._status(f"Farm loop completed {iterations} iteration(s)")
                break

            for stage_id in stage_ids:
                if stop_event and stop_event.is_set():
                    break
                try:
                    self.navigate_to(stage_id)
                    self.wait_for_stage_completion()
                except NavigationError as e:
                    logger.error(f"Navigation error during farm loop: {e}")
                    self._recover()

            current += 1

    def wait_for_stage_completion(self) -> bool:
        """Wait until the game returns to the main window after combat ends."""
        timeout = self._timing.stage_completion_timeout_ms
        self._status("Waiting for stage to complete...")
        result = self.state_detector.wait_for_state(
            GameState.MAIN_WINDOW_OPEN, timeout_ms=timeout, poll_interval_ms=1000
        )
        if result:
            self._status("Stage complete")
        else:
            logger.warning("Stage completion timeout reached")
        return result

    # ── Internal steps ───────────────────────────────────────────────────────

    def ensure_window_open(self) -> bool:
        if self.window.find() is None:
            raise NavigationError("Game window not found — is TBH running?")
        self.window.bring_to_front()

        state = self.state_detector.detect()
        if state == GameState.MAIN_WINDOW_OPEN:
            return True

        if state == GameState.MAIN_WINDOW_CLOSED:
            self._status("Expanding game window...")
            self.window.expand()
            return self.state_detector.wait_for_state(
                GameState.MAIN_WINDOW_OPEN, timeout_ms=3000
            )

        # For UNKNOWN / other states, just wait a bit and check again
        time.sleep(1.0)
        return self.state_detector.wait_for_state(
            GameState.MAIN_WINDOW_OPEN, timeout_ms=3000
        )

    def open_portal_menu(self) -> bool:
        frame = self.capture.grab_window()
        match = self.matcher.find(frame, "portal_icon")
        if not match:
            raise NavigationError("Portal icon not found in game window")

        self.controller.click(*match.center)
        time.sleep(self._timing.portal_open_wait_ms / 1000)

        reached = self.state_detector.wait_for_state(
            GameState.PORTAL_MENU_OPEN, timeout_ms=3000
        )
        if not reached:
            raise NavigationError("Portal menu did not open after clicking icon")
        return True

    def _select_stage_in_portal(self, stage: Stage) -> bool:
        act_key = f"act{stage.act_number}_header"
        frame = self.capture.grab_window()

        # Scroll to find the correct act header
        if not self._scroll_to_act(frame, act_key):
            logger.warning(f"Act header '{act_key}' not found after scrolling")

        # Refresh frame after scrolling
        frame = self.capture.grab_window()
        match = self.matcher.find(frame, stage.template)
        if not match:
            raise NavigationError(
                f"Stage template '{stage.template}' not found in portal menu. "
                f"Ensure templates/stages/{stage.template}.png exists."
            )

        self.controller.click(*match.center)
        time.sleep(self._timing.stage_click_wait_ms / 1000)

        arrived = self.state_detector.wait_for_any_state(
            [GameState.IN_COMBAT, GameState.LOADING, GameState.MAIN_WINDOW_OPEN],
            timeout_ms=5000,
        )
        return arrived is not None

    def _scroll_to_act(self, frame, act_key: str, max_scrolls: int = 4) -> bool:
        """Scroll the portal menu until the act header is visible."""
        if self.matcher.find(frame, act_key):
            return True

        rect = self.window.get_rect()
        if rect is None:
            return False

        mid_x = rect.width // 2
        mid_y = rect.height // 2

        for _ in range(max_scrolls):
            self.controller.scroll(mid_x, mid_y, clicks=-3)
            time.sleep(0.3)
            frame = self.capture.grab_window()
            if self.matcher.find(frame, act_key):
                return True

        return False

    def _recover(self) -> None:
        """Best-effort recovery: close overlays and re-establish main window."""
        logger.info("Attempting recovery...")
        try:
            self.controller.press_escape()
            time.sleep(0.3)
            self.ensure_window_open()
        except Exception as e:
            logger.warning(f"Recovery failed: {e}")

import logging
import time
from enum import Enum
from typing import Callable
import numpy as np
from .capture import ScreenCapture
from .vision import TemplateMatcher

logger = logging.getLogger("tbh.state")


class GameState(Enum):
    UNKNOWN = "unknown"
    MAIN_WINDOW_CLOSED = "strip_only"
    MAIN_WINDOW_OPEN = "main_window"
    PORTAL_MENU_OPEN = "portal_menu"
    IN_COMBAT = "in_combat"
    LOADING = "loading"


class GameStateDetector:
    """Classifies current game state by detecting known UI templates."""

    # Presence of these templates implies a particular state
    _STATE_SIGNALS: list[tuple[list[str], GameState]] = [
        (["act1_header", "act2_header", "act3_header"], GameState.PORTAL_MENU_OPEN),
        (["portal_icon"], GameState.MAIN_WINDOW_OPEN),
    ]

    def __init__(self, capture: ScreenCapture, matcher: TemplateMatcher):
        self.capture = capture
        self.matcher = matcher

    def detect(self) -> GameState:
        try:
            frame = self.capture.grab_window()
        except Exception as e:
            logger.debug(f"State detection failed to capture: {e}")
            return GameState.UNKNOWN

        # Check portal menu first (more specific)
        for any_of in ["act1_header", "act2_header", "act3_header"]:
            if self.matcher.find(frame, any_of):
                return GameState.PORTAL_MENU_OPEN

        if self.matcher.find(frame, "portal_icon"):
            return GameState.MAIN_WINDOW_OPEN

        # No UI chrome visible — likely loading or strip-only
        rect = self.capture.window.get_rect()
        if rect and rect.height <= 80:
            return GameState.MAIN_WINDOW_CLOSED

        return GameState.UNKNOWN

    def wait_for_state(
        self,
        target: GameState,
        timeout_ms: int = 5000,
        poll_interval_ms: int = 300,
    ) -> bool:
        deadline = time.time() + timeout_ms / 1000
        while time.time() < deadline:
            current = self.detect()
            if current == target:
                logger.debug(f"Reached state: {target.value}")
                return True
            time.sleep(poll_interval_ms / 1000)
        logger.warning(f"Timeout waiting for state '{target.value}'")
        return False

    def wait_for_any_state(
        self,
        targets: list[GameState],
        timeout_ms: int = 5000,
        poll_interval_ms: int = 300,
    ) -> GameState | None:
        deadline = time.time() + timeout_ms / 1000
        while time.time() < deadline:
            current = self.detect()
            if current in targets:
                return current
            time.sleep(poll_interval_ms / 1000)
        return None

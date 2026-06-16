import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional
import cv2
import numpy as np

logger = logging.getLogger("tbh.vision")

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


@dataclass
class Match:
    template_name: str
    confidence: float
    center: tuple[int, int]
    rect: tuple[int, int, int, int]  # x, y, w, h


class TemplateNotFoundError(Exception):
    pass


class TemplateMatcher:
    """Template matching engine using OpenCV TM_CCOEFF_NORMED."""

    def __init__(self, threshold: float = 0.80, debug: bool = False, dpi_scale: float = 1.0):
        self.threshold = threshold
        self.debug = debug
        self.dpi_scale = dpi_scale
        self._cache: dict[str, np.ndarray] = {}

    def load_template(self, name: str) -> np.ndarray:
        if name in self._cache:
            return self._cache[name]

        candidates = [
            TEMPLATES_DIR / "ui" / f"{name}.png",
            TEMPLATES_DIR / "portal_menu" / f"{name}.png",
            TEMPLATES_DIR / "stages" / f"{name}.png",
            TEMPLATES_DIR / f"{name}.png",
        ]
        for path in candidates:
            if path.exists():
                tmpl = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
                if tmpl is None:
                    raise TemplateNotFoundError(f"Could not read template: {path}")
                if self.dpi_scale != 1.0:
                    h, w = tmpl.shape
                    new_w = int(w * self.dpi_scale)
                    new_h = int(h * self.dpi_scale)
                    tmpl = cv2.resize(tmpl, (new_w, new_h))
                self._cache[name] = tmpl
                logger.debug(f"Loaded template '{name}' from {path}")
                return tmpl

        raise TemplateNotFoundError(
            f"Template '{name}' not found in {TEMPLATES_DIR}. "
            f"Run scripts/capture_templates.py to create it."
        )

    def _to_gray(self, frame: np.ndarray) -> np.ndarray:
        if len(frame.shape) == 3:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return frame

    def find(self, frame: np.ndarray, template_name: str) -> Optional[Match]:
        """Find best single match above threshold."""
        try:
            tmpl = self.load_template(template_name)
        except TemplateNotFoundError as e:
            logger.warning(str(e))
            return None

        gray = self._to_gray(frame)
        th, tw = tmpl.shape[:2]

        best_match: Optional[Match] = None

        for scale in (1.0, 0.9, 1.1):
            scaled_tmpl = tmpl
            if scale != 1.0:
                new_w = int(tw * scale)
                new_h = int(th * scale)
                if new_w < 5 or new_h < 5:
                    continue
                scaled_tmpl = cv2.resize(tmpl, (new_w, new_h))

            if scaled_tmpl.shape[0] > gray.shape[0] or scaled_tmpl.shape[1] > gray.shape[1]:
                continue

            result = cv2.matchTemplate(gray, scaled_tmpl, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val >= self.threshold:
                sh, sw = scaled_tmpl.shape[:2]
                cx = max_loc[0] + sw // 2
                cy = max_loc[1] + sh // 2
                match = Match(
                    template_name=template_name,
                    confidence=float(max_val),
                    center=(cx, cy),
                    rect=(max_loc[0], max_loc[1], sw, sh),
                )
                if best_match is None or match.confidence > best_match.confidence:
                    best_match = match

        if best_match:
            logger.debug(f"Found '{template_name}' at {best_match.center} (conf={best_match.confidence:.3f})")
        return best_match

    def find_all(self, frame: np.ndarray, template_name: str) -> list[Match]:
        """Find all matches above threshold (with NMS)."""
        try:
            tmpl = self.load_template(template_name)
        except TemplateNotFoundError as e:
            logger.warning(str(e))
            return []

        gray = self._to_gray(frame)
        th, tw = tmpl.shape[:2]

        result = cv2.matchTemplate(gray, tmpl, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= self.threshold)

        matches = []
        for pt in zip(*locations[::-1]):
            cx = pt[0] + tw // 2
            cy = pt[1] + th // 2
            matches.append(Match(
                template_name=template_name,
                confidence=float(result[pt[1], pt[0]]),
                center=(cx, cy),
                rect=(pt[0], pt[1], tw, th),
            ))

        return self._nms(matches, overlap_threshold=0.3)

    def _nms(self, matches: list[Match], overlap_threshold: float) -> list[Match]:
        if not matches:
            return []
        matches.sort(key=lambda m: m.confidence, reverse=True)
        kept = []
        for match in matches:
            x, y, w, h = match.rect
            dominated = False
            for kept_match in kept:
                kx, ky, kw, kh = kept_match.rect
                ix = max(x, kx)
                iy = max(y, ky)
                ix2 = min(x + w, kx + kw)
                iy2 = min(y + h, ky + kh)
                if ix2 > ix and iy2 > iy:
                    intersection = (ix2 - ix) * (iy2 - iy)
                    union = w * h + kw * kh - intersection
                    if intersection / union > overlap_threshold:
                        dominated = True
                        break
            if not dominated:
                kept.append(match)
        return kept

    def wait_for(
        self,
        capture_fn: Callable[[], np.ndarray],
        template_name: str,
        timeout_ms: int = 5000,
        poll_interval_ms: int = 200,
    ) -> Optional[Match]:
        deadline = time.time() + timeout_ms / 1000
        while time.time() < deadline:
            frame = capture_fn()
            match = self.find(frame, template_name)
            if match:
                return match
            time.sleep(poll_interval_ms / 1000)
        logger.debug(f"Timeout waiting for template '{template_name}'")
        return None

    def template_exists(self, name: str) -> bool:
        try:
            self.load_template(name)
            return True
        except TemplateNotFoundError:
            return False

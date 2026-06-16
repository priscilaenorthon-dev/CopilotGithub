from .config import Config
from .window import GameWindow
from .capture import ScreenCapture
from .vision import TemplateMatcher
from .controller import MouseController
from .state import GameStateDetector
from .navigator import StageNavigator


def build_navigator(config: Config) -> StageNavigator:
    """Wire up all components and return a ready-to-use StageNavigator."""
    s = config.settings
    window = GameWindow(
        process_name=s.window.process_name,
        title_fragment=s.window.window_title_fragment,
    )
    window.find()
    capture = ScreenCapture(window, monitor_index=s.capture.monitor_index)
    matcher = TemplateMatcher(
        threshold=s.vision.match_threshold,
        debug=s.vision.debug_mode,
        dpi_scale=s.window.dpi_scale,
    )
    controller = MouseController(
        window,
        click_delay_ms=s.timing.click_delay_ms,
        hover_delay_ms=s.timing.hover_delay_ms,
    )
    state_detector = GameStateDetector(capture, matcher)
    return StageNavigator(window, capture, matcher, controller, state_detector, config)

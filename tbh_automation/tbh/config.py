import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


@dataclass
class Stage:
    id: str
    label: str
    template: str

    @property
    def act_number(self) -> int:
        return int(self.id.split("-")[0])


@dataclass
class Act:
    label: str
    stages: list[Stage] = field(default_factory=list)


@dataclass
class CaptureSettings:
    monitor_index: int = 1


@dataclass
class VisionSettings:
    match_threshold: float = 0.80
    debug_mode: bool = False


@dataclass
class TimingSettings:
    click_delay_ms: int = 150
    hover_delay_ms: int = 300
    portal_open_wait_ms: int = 600
    stage_click_wait_ms: int = 800
    retry_attempts: int = 5
    retry_delay_ms: int = 500
    stage_completion_timeout_ms: int = 300000


@dataclass
class WindowSettings:
    process_name: str = "TBH.exe"
    window_title_fragment: str = "Task Bar Hero"
    expand_on_start: bool = True
    dpi_scale: float = 1.0


@dataclass
class Settings:
    capture: CaptureSettings = field(default_factory=CaptureSettings)
    vision: VisionSettings = field(default_factory=VisionSettings)
    timing: TimingSettings = field(default_factory=TimingSettings)
    window: WindowSettings = field(default_factory=WindowSettings)


class Config:
    def __init__(self, settings: Settings, acts: dict[str, Act], farm_presets: dict[str, list[str]]):
        self.settings = settings
        self.acts = acts
        self.farm_presets = farm_presets
        self._stage_index: dict[str, Stage] = {
            stage.id: stage
            for act in acts.values()
            for stage in act.stages
        }

    @classmethod
    def load(
        cls,
        settings_path: Path | None = None,
        maps_path: Path | None = None,
        base_dir: Path | None = None,
    ) -> "Config":
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        if settings_path is None:
            settings_path = base_dir / "config" / "settings.toml"
        if maps_path is None:
            maps_path = base_dir / "config" / "maps.toml"

        with open(settings_path, "rb") as f:
            raw_settings = tomllib.load(f)

        with open(maps_path, "rb") as f:
            raw_maps = tomllib.load(f)

        settings = cls._parse_settings(raw_settings)
        acts, farm_presets = cls._parse_maps(raw_maps)
        return cls(settings, acts, farm_presets)

    @classmethod
    def _parse_settings(cls, raw: dict) -> Settings:
        capture = CaptureSettings(**raw.get("capture", {}))
        vision = VisionSettings(**raw.get("vision", {}))
        timing = TimingSettings(**raw.get("timing", {}))
        window = WindowSettings(**raw.get("window", {}))
        return Settings(capture=capture, vision=vision, timing=timing, window=window)

    @classmethod
    def _parse_maps(cls, raw: dict) -> tuple[dict[str, Act], dict[str, list[str]]]:
        acts: dict[str, Act] = {}
        for act_key, act_data in raw.get("acts", {}).items():
            stages = [Stage(**s) for s in act_data.get("stages", [])]
            acts[act_key] = Act(label=act_data["label"], stages=stages)

        farm_presets = raw.get("farm_presets", {})
        return acts, farm_presets

    def get_stage(self, stage_id: str) -> Optional[Stage]:
        return self._stage_index.get(stage_id)

    def get_template_path(self, template_name: str, base_dir: Path | None = None) -> Path:
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        return base_dir / "templates" / "stages" / f"{template_name}.png"

    def all_stages(self) -> list[Stage]:
        return list(self._stage_index.values())

    def get_farm_preset(self, name: str) -> list[str]:
        return self.farm_presets.get(name, [])

import json
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

DATA_PATH = Path(__file__).parent.parent / "tracker_data.json"


@dataclass
class StageTimer:
    stage_id: str
    last_collected: Optional[datetime] = None
    cooldown_minutes: int = 12

    @property
    def seconds_remaining(self) -> int:
        if self.last_collected is None:
            return 0
        elapsed = (datetime.now() - self.last_collected).total_seconds()
        remaining = self.cooldown_minutes * 60 - elapsed
        return max(0, int(remaining))

    @property
    def is_ready(self) -> bool:
        return self.seconds_remaining == 0

    @property
    def progress(self) -> float:
        """0.0 = recém-coletado, 1.0 = pronto para coletar."""
        if self.last_collected is None:
            return 1.0
        elapsed = (datetime.now() - self.last_collected).total_seconds()
        total = self.cooldown_minutes * 60
        return min(1.0, elapsed / total)

    @property
    def last_collected_str(self) -> str:
        if self.last_collected is None:
            return "—"
        return self.last_collected.strftime("%H:%M:%S")

    @property
    def countdown_str(self) -> str:
        secs = self.seconds_remaining
        if secs == 0:
            return "PRONTO!"
        m, s = divmod(secs, 60)
        return f"{m:02d}:{s:02d}"


@dataclass
class SessionStats:
    total_chests: int = 0
    by_stage: dict = field(default_factory=dict)
    session_start: Optional[str] = None

    def record(self, stage_id: str):
        self.total_chests += 1
        self.by_stage[stage_id] = self.by_stage.get(stage_id, 0) + 1

    @property
    def best_stage(self) -> Optional[str]:
        if not self.by_stage:
            return None
        return max(self.by_stage, key=self.by_stage.get)

    @property
    def uptime_str(self) -> str:
        if not self.session_start:
            return "—"
        start = datetime.fromisoformat(self.session_start)
        delta = datetime.now() - start
        hours, rem = divmod(int(delta.total_seconds()), 3600)
        mins = rem // 60
        if hours > 0:
            return f"{hours}h {mins:02d}m"
        return f"{mins}m"


class ChestTracker:
    """Tracks blue chest cooldowns per stage and persists data across sessions."""

    def __init__(self, data_path: Path = DATA_PATH, cooldown_minutes: int = 12):
        self.data_path = data_path
        self.cooldown_minutes = cooldown_minutes
        self._timers: dict[str, StageTimer] = {}
        self.session = SessionStats(session_start=datetime.now().isoformat())
        self.load()

    def load(self):
        if not self.data_path.exists():
            return
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for stage_id, ts_str in data.get("last_collected", {}).items():
                self._timers[stage_id] = StageTimer(
                    stage_id=stage_id,
                    last_collected=datetime.fromisoformat(ts_str),
                    cooldown_minutes=self.cooldown_minutes,
                )
        except Exception:
            pass

    def save(self):
        data = {
            "last_collected": {
                sid: t.last_collected.isoformat()
                for sid, t in self._timers.items()
                if t.last_collected
            },
            "all_time_stats": {
                "total_chests": self.session.total_chests,
                "by_stage": self.session.by_stage,
            },
        }
        try:
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def get_stage(self, stage_id: str) -> StageTimer:
        if stage_id not in self._timers:
            self._timers[stage_id] = StageTimer(
                stage_id=stage_id,
                cooldown_minutes=self.cooldown_minutes,
            )
        return self._timers[stage_id]

    def mark_collected(self, stage_id: str):
        timer = self.get_stage(stage_id)
        timer.last_collected = datetime.now()
        self.session.record(stage_id)
        self.save()

    def get_ready_stages(self, route: list[str]) -> list[str]:
        return [sid for sid in route if self.get_stage(sid).is_ready]

    def next_ready_in(self, route: list[str]) -> int:
        """Returns seconds until the next stage in route becomes ready."""
        remaining = [self.get_stage(sid).seconds_remaining for sid in route]
        if not remaining:
            return 0
        return min(remaining)

    def reset_stage(self, stage_id: str):
        """Manually reset a stage's timer (mark as never collected)."""
        if stage_id in self._timers:
            self._timers[stage_id].last_collected = None
            self.save()

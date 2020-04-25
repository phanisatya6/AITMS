from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class SignalState(Enum):
    RED = "R"
    YELLOW = "Y"
    GREEN = "G"


class LaneID(Enum):
    LANE_1 = 0
    LANE_2 = 1
    LANE_3 = 2
    LANE_4 = 3


@dataclass
class BoundingBox:
    x: int
    y: int
    width: int
    height: int

    @property
    def center_x(self) -> int:
        return self.x + self.width // 2

    @property
    def center_y(self) -> int:
        return self.y + self.height // 2

    @property
    def center(self) -> tuple[int, int]:
        return (self.center_x, self.center_y)


@dataclass
class CountingZone:
    x_start: int = 0
    x_end: int = 0
    y_start: int = 0
    y_end: int = 0


@dataclass
class LaneState:
    vehicle_count: int = 0
    signal_state: SignalState = SignalState.RED
    wait_time: int = 0
    remaining_time: int = 0
    is_locked: bool = False

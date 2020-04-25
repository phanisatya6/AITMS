from __future__ import annotations

from pathlib import Path
from typing import ClassVar


class Config:
    PROJECT_ROOT: ClassVar[Path] = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: ClassVar[Path] = PROJECT_ROOT / "data"

    VIDEO_SOURCES: ClassVar[list[str]] = [
        "second/Lane1mod.mp4",
        "second/Lane2mod.mp4",
        "second/Lane3mod.mp4",
        "second/Lane4mod.mp4",
    ]

    VIDEO_SOURCES_FALLBACK: ClassVar[list[str]] = [
        "first/L1.mp4",
        "first/L2.mp4",
        "first/L3.mp4",
        "first/L4.mp4",
    ]

    MIN_VEHICLE_WIDTH: ClassVar[int] = 75
    MIN_VEHICLE_HEIGHT: ClassVar[int] = 75
    GAUSSIAN_BLUR_KERNEL: ClassVar[tuple[int, int]] = (21, 21)
    THRESHOLD_VALUE: ClassVar[int] = 21
    DILATION_KERNEL_SIZE: ClassVar[int] = 5

    ZONE_Y_START_RATIO: ClassVar[float] = 0.785
    ZONE_Y_END_RATIO: ClassVar[float] = 0.805
    ZONE_X_END_RATIO: ClassVar[float] = 0.5

    SECONDS_PER_VEHICLE: ClassVar[int] = 2
    BUFFER_SECONDS: ClassVar[int] = 5
    MAX_GREEN_SECONDS: ClassVar[int] = 60
    CONTROL_LOOP_INTERVAL: ClassVar[float] = 0.1

    VIDEO_SCALE_PERCENT: ClassVar[int] = 30
    TRAFFIC_LIGHT_WIDTH: ClassVar[int] = 45
    TRAFFIC_LIGHT_HEIGHT: ClassVar[int] = 125
    LIGHT_RADIUS: ClassVar[int] = 18

    WINDOW_TITLE: ClassVar[str] = "AITMS - Adaptive Traffic Signal Control"
    WINDOW_BG: ClassVar[str] = "white"

    ZONE_FILL_COLOR: ClassVar[tuple[int, int, int]] = (100, 100, 255)
    COUNT_FILL_COLOR: ClassVar[tuple[int, int, int]] = (255, 100, 100)
    VEHICLE_BOX_COLOR: ClassVar[tuple[int, int, int]] = (0, 255, 0)
    VEHICLE_BOX_THICKNESS: ClassVar[int] = 2

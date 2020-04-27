from __future__ import annotations

import logging
import threading
from typing import Callable, Optional

from aitms.config import Config
from aitms.core.types import LaneID, SignalState

logger = logging.getLogger(__name__)


class DisplayTimer(threading.Thread):
    """Displays a countdown timer for a lane's remaining wait time."""

    def __init__(
        self,
        lane_id: int,
        total_seconds: int,
        on_tick: Callable[[int, int], None],
    ) -> None:
        super().__init__(daemon=True)
        self.lane_id = lane_id
        self.total_seconds = total_seconds
        self._on_tick = on_tick
        self._stop_event = threading.Event()

    def run(self) -> None:
        remaining = self.total_seconds
        while remaining > 0 and not self._stop_event.is_set():
            self._on_tick(self.lane_id, remaining)
            threading.Event().wait(1)
            remaining -= 1
        if not self._stop_event.is_set():
            self._on_tick(self.lane_id, 0)

    def cancel(self) -> None:
        self._stop_event.set()


class SignalController(threading.Thread):
    """PAAC (Priority-based Adaptive Auto Control) algorithm that
    dynamically allocates green signal time based on vehicle density."""

    def __init__(
        self,
        config: Config,
        get_vehicle_count: Callable[[int], int],
        set_signal: Callable[[int, SignalState], None],
        set_wait_time: Callable[[int, int], None],
        reset_count: Callable[[int], None],
    ) -> None:
        super().__init__(daemon=True)
        self._config = config
        self._get_vehicle_count = get_vehicle_count
        self._set_signal = set_signal
        self._set_wait_time = set_wait_time
        self._reset_count = reset_count
        self._lane_count = 4
        self._active_timer: Optional[DisplayTimer] = None

    def run(self) -> None:
        while True:
            threading.Event().wait(self._config.CONTROL_LOOP_INTERVAL)
            for lane_id in range(self._lane_count):
                vehicle_count = self._get_vehicle_count(lane_id)
                wait_time = vehicle_count * self._config.SECONDS_PER_VEHICLE

                logger.info("Lane %d - vehicles: %d, wait time: %d", lane_id, vehicle_count, wait_time)

                if wait_time < 1:
                    self._set_all_red()
                    continue

                wait_time = min(wait_time, self._config.MAX_GREEN_SECONDS)
                total_green_time = wait_time + self._config.BUFFER_SECONDS

                # Set this lane green, others red
                for i in range(self._lane_count):
                    self._set_signal(i, SignalState.GREEN if i == lane_id else SignalState.RED)

                self._set_wait_time(lane_id, total_green_time)

                # Start countdown timer
                self._active_timer = DisplayTimer(
                    lane_id, total_green_time, self._on_timer_tick,
                )
                self._active_timer.start()
                self._active_timer.join()
                self._active_timer = None

                self._reset_count(lane_id)
                logger.info("Lane %d count reset to 0", lane_id)

    def _set_all_red(self) -> None:
        for i in range(self._lane_count):
            self._set_signal(i, SignalState.RED)

    def _on_timer_tick(self, lane_id: int, remaining: int) -> None:
        self._set_wait_time(lane_id, remaining)

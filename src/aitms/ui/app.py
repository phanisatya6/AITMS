from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Optional

import tkinter as tk

from aitms.config import Config
from aitms.core.signal_controller import SignalController
from aitms.core.types import SignalState
from aitms.core.vehicle_detector import VehicleDetector
from aitms.ui.lane_panel import LanePanel

logger = logging.getLogger(__name__)


class AITMSApp:
    """Main Tkinter application window."""

    def __init__(self, config: Config) -> None:
        self._config = config
        self._root = tk.Tk()
        self._root.title(config.WINDOW_TITLE)
        self._root.configure(bg=config.WINDOW_BG)

        self._detectors: list[VehicleDetector] = []
        self._panels: list[LanePanel] = []
        self._signal_controller: Optional[SignalController] = None

        self._build_ui()
        self._init_detectors()
        self._init_controller()
        self._start_polling()

    def _build_ui(self) -> None:
        main_frame = tk.Frame(self._root, bg=self._config.WINDOW_BG)
        main_frame.pack(padx=10, pady=10)

        positions = [
            (0, 0),  # Lane 1 - top-left
            (0, 3),  # Lane 2 - top-right
            (4, 0),  # Lane 3 - bottom-left
            (4, 3),  # Lane 4 - bottom-right
        ]

        for lane_id, (row, col) in enumerate(positions):
            panel = LanePanel(main_frame, lane_id, self._config, row, col)
            self._panels.append(panel)

        # Spacers for layout
        for r, c in [(0, 2), (3, 0), (3, 3), (4, 2), (7, 0)]:
            tk.Label(main_frame, text="  ", bg=self._config.WINDOW_BG).grid(row=r, column=c)

        # Vertical spacers
        for r, c in [(0, 5), (4, 5)]:
            tk.Label(main_frame, text=" ", bg=self._config.WINDOW_BG).grid(row=r, column=c)

    def _resolve_video_path(self, index: int) -> Path:
        sources = self._config.VIDEO_SOURCES
        fallback = self._config.VIDEO_SOURCES_FALLBACK

        if index < len(sources):
            candidate = self._config.DATA_DIR / sources[index]
            if candidate.exists():
                return candidate

        if index < len(fallback):
            candidate = self._config.DATA_DIR / fallback[index]
            if candidate.exists():
                logger.warning("Using fallback video for lane %d: %s", index, candidate)
                return candidate

        raise FileNotFoundError(f"No video found for lane {index}")

    def _init_detectors(self) -> None:
        for lane_id in range(4):
            video_path = self._resolve_video_path(lane_id)
            detector = VehicleDetector(video_path, lane_id, self._config)
            self._detectors.append(detector)

        for d in self._detectors:
            d.start()

    def _init_controller(self) -> None:
        self._signal_controller = SignalController(
            config=self._config,
            get_vehicle_count=self._get_vehicle_count,
            set_signal=self._set_signal,
            set_wait_time=self._set_wait_time,
            reset_count=self._reset_count,
        )
        self._signal_controller.start()

    def _get_vehicle_count(self, lane_id: int) -> int:
        if lane_id < len(self._detectors):
            return self._detectors[lane_id].vehicle_count
        return 0

    def _set_signal(self, lane_id: int, state: SignalState) -> None:
        if lane_id < len(self._panels):
            self._panels[lane_id].set_signal(state)

    def _set_wait_time(self, lane_id: int, seconds: int) -> None:
        if lane_id < len(self._panels):
            self._panels[lane_id].update_wait_time(seconds)

    def _reset_count(self, lane_id: int) -> None:
        if lane_id < len(self._detectors):
            self._detectors[lane_id].vehicle_count = 0

    def _poll_video(self) -> None:
        for i, detector in enumerate(self._detectors):
            if i < len(self._panels):
                self._panels[i].update_video(detector.current_frame)
                if not detector.is_alive():
                    self._panels[i].update_count(detector.vehicle_count)
                else:
                    self._panels[i].update_count(detector.vehicle_count)

        self._root.after(50, self._poll_video)

    def _start_polling(self) -> None:
        self._root.after(50, self._poll_video)

    def run(self) -> None:
        logger.info("Starting AITMS application")
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._root.mainloop()

    def _on_close(self) -> None:
        logger.info("Shutting down...")
        for d in self._detectors:
            d.release()
        self._root.destroy()

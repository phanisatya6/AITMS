from __future__ import annotations

import tkinter as tk
from typing import ClassVar, Optional

import numpy as np
from numpy.typing import NDArray
from PIL import Image, ImageTk

from aitms.config import Config
from aitms.core.types import SignalState
from aitms.ui.traffic_light import TrafficLight


class LanePanel:
    """UI panel for a single lane: video feed, traffic light, and info labels."""

    FONT: ClassVar[tuple[str, int, str]] = ("Helvetica", 10, "bold")

    def __init__(
        self,
        parent: tk.Widget,
        lane_id: int,
        config: Config,
        row: int,
        column: int,
    ) -> None:
        self.lane_id = lane_id
        self._config = config

        # Video label
        self.video_label = tk.Label(parent, bg=config.WINDOW_BG)
        self.video_label.grid(row=row, column=column, padx=4, pady=4)

        # Traffic light
        self.traffic_light = TrafficLight(parent, config)
        self.traffic_light.grid(row=row, column=column + 1, padx=4, pady=4)

        # Info labels
        self.count_label = tk.Label(parent, text="Vehicles: 0", bg=config.WINDOW_BG, font=self.FONT)
        self.count_label.grid(row=row + 1, column=column, padx=4, pady=2, sticky="w")

        self.time_label = tk.Label(parent, text="Wait: 0s", bg=config.WINDOW_BG, font=self.FONT)
        self.time_label.grid(row=row + 2, column=column, padx=4, pady=2, sticky="w")

        self._photo: Optional[ImageTk.PhotoImage] = None

    def update_video(self, frame: Optional[NDArray]) -> None:
        if frame is None:
            return
        img = Image.fromarray(frame)
        self._photo = ImageTk.PhotoImage(image=img)
        self.video_label.configure(image=self._photo)

    def update_count(self, count: int) -> None:
        self.count_label.configure(text=f"Vehicles: {count}")

    def update_wait_time(self, seconds: int) -> None:
        self.time_label.configure(text=f"Wait: {seconds}s")

    def set_signal(self, state: SignalState) -> None:
        self.traffic_light.set_state(state)

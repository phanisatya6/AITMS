from __future__ import annotations

import tkinter as tk
from typing import ClassVar

from aitms.config import Config
from aitms.core.types import SignalState


class TrafficLight(tk.Canvas):
    LIGHT_COLORS: ClassVar[dict[SignalState, str]] = {
        SignalState.RED: "red",
        SignalState.YELLOW: "yellow",
        SignalState.GREEN: "green",
    }

    def __init__(self, parent: tk.Widget, config: Config) -> None:
        super().__init__(
            parent,
            width=config.TRAFFIC_LIGHT_WIDTH,
            height=config.TRAFFIC_LIGHT_HEIGHT,
            bg=config.WINDOW_BG,
            highlightthickness=0,
        )
        self._config = config
        r = config.LIGHT_RADIUS
        cx = config.TRAFFIC_LIGHT_WIDTH // 2

        # Red (top)
        self._red_light = self.create_oval(cx - r, 5, cx + r, 5 + 2 * r, fill="white", outline="black")
        # Yellow (middle)
        self._yellow_light = self.create_oval(cx - r, 5 + 2 * r + 5, cx + r, 5 + 4 * r + 5, fill="white", outline="black")
        # Green (bottom)
        self._green_light = self.create_oval(cx - r, 5 + 4 * r + 10, cx + r, 5 + 6 * r + 10, fill="white", outline="black")

        self.set_state(SignalState.RED)

    def set_state(self, state: SignalState) -> None:
        self.itemconfigure(self._red_light, fill="white")
        self.itemconfigure(self._yellow_light, fill="white")
        self.itemconfigure(self._green_light, fill="white")

        if state == SignalState.RED:
            self.itemconfigure(self._red_light, fill=self.LIGHT_COLORS[state])
        elif state == SignalState.YELLOW:
            self.itemconfigure(self._yellow_light, fill=self.LIGHT_COLORS[state])
        elif state == SignalState.GREEN:
            self.itemconfigure(self._green_light, fill=self.LIGHT_COLORS[state])

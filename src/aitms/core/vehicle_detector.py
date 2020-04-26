from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from numpy.typing import NDArray

from aitms.config import Config
from aitms.core.types import BoundingBox, CountingZone

logger = logging.getLogger(__name__)


class VehicleDetector(threading.Thread):
    """Performs vehicle detection on a single lane video feed using
    background subtraction and contour analysis."""

    def __init__(self, video_path: Path, lane_id: int, config: Config) -> None:
        super().__init__(daemon=True)
        self._video_path = video_path
        self.lane_id = lane_id
        self._config = config

        self.vehicle_count: int = 0
        self.current_frame: Optional[NDArray] = None

        self._first_frame: Optional[NDArray] = None
        self._cap: Optional[cv2.VideoCapture] = None
        self._frame_width: int = 0
        self._frame_height: int = 0

    def open(self) -> bool:
        self._cap = cv2.VideoCapture(str(self._video_path))
        if not self._cap.isOpened():
            logger.error("Failed to open video: %s", self._video_path)
            return False
        self._frame_width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self._frame_height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        logger.info(
            "Lane %d: opened %s (%dx%d)",
            self.lane_id,
            self._video_path.name,
            self._frame_width,
            self._frame_height,
        )
        return True

    @property
    def counting_zone(self) -> CountingZone:
        y_start = int(self._config.ZONE_Y_START_RATIO * self._frame_height)
        y_end = int(self._config.ZONE_Y_END_RATIO * self._frame_height)
        x_end = int(self._config.ZONE_X_END_RATIO * self._frame_width)
        return CountingZone(x_start=0, x_end=x_end, y_start=y_start, y_end=y_end)

    def _process_frame(self, frame: NDArray) -> NDArray:
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        grey = cv2.GaussianBlur(grey, self._config.GAUSSIAN_BLUR_KERNEL, 0)

        if self._first_frame is None:
            self._first_frame = grey
            return frame

        delta = cv2.absdiff(self._first_frame, grey)
        _, thresh = cv2.threshold(delta, self._config.THRESHOLD_VALUE, 255, cv2.THRESH_BINARY)
        thresh = cv2.dilate(thresh, np.ones((self._config.DILATION_KERNEL_SIZE, self._config.DILATION_KERNEL_SIZE)))

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        zone = self.counting_zone
        detections: list[BoundingBox] = []

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w < self._config.MIN_VEHICLE_WIDTH and h < self._config.MIN_VEHICLE_HEIGHT:
                continue
            box = BoundingBox(x, y, w, h)
            detections.append(box)
            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                self._config.VEHICLE_BOX_COLOR,
                self._config.VEHICLE_BOX_THICKNESS,
            )

        # Draw counting zone overlay
        cv2.rectangle(
            frame,
            (zone.x_start, zone.y_start),
            (zone.x_end, zone.y_end),
            self._config.ZONE_FILL_COLOR,
            -1,
        )

        # Count vehicles whose center falls within the zone
        counted = 0
        for box in detections:
            if (
                zone.y_start < box.center_y < zone.y_end
                and box.center_x < zone.x_end
            ):
                counted += 1

        # Update count if vehicles crossed the zone this frame
        if counted > 0:
            self.vehicle_count += counted
            # Flash the count region
            cv2.rectangle(
                frame,
                (zone.x_start, zone.y_end + 20),
                (zone.x_end, zone.y_start + 20),
                self._config.COUNT_FILL_COLOR,
                -1,
            )

        return frame

    def run(self) -> None:
        if not self.open():
            return

        while self._cap is not None and self._cap.isOpened():
            ret, frame = self._cap.read()
            if not ret:
                logger.info("Lane %d: end of video stream", self.lane_id)
                break

            processed = self._process_frame(frame)
            processed = cv2.cvtColor(processed, cv2.COLOR_BGR2RGBA)

            scale = self._config.VIDEO_SCALE_PERCENT / 100.0
            new_w = int(processed.shape[1] * scale)
            new_h = int(processed.shape[0] * scale)
            self.current_frame = cv2.resize(processed, (new_w, new_h), interpolation=cv2.INTER_AREA)

        self.release()

    def release(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None
            logger.info("Lane %d: released", self.lane_id)

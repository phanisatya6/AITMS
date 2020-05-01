<div align="center">
  <h1>🚦 AITMS — Automated Intelligent Traffic Management System</h1>
  <p>
    <strong>Adaptive traffic signal control powered by real-time computer vision</strong>
  </p>
  <p>
    <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">
    <img src="https://img.shields.io/badge/opencv-4.8%2B-green" alt="OpenCV 4.8+">
    <img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License">
    <img src="https://img.shields.io/badge/status-beta-yellow" alt="Status: Beta">
  </p>
</div>

---

## 📋 Overview

AITMS is a desktop application that simulates an **intelligent traffic signal control system** for a 4-way intersection. It uses **real-time computer vision** to detect vehicles in each lane via pre-recorded video feeds and dynamically allocates green signal time based on traffic density — replacing traditional fixed-timer traffic lights with an adaptive, demand-driven approach.

Unlike conventional traffic signals that cycle on fixed timers, AITMS:

- **Detects vehicles** in each lane using background subtraction and contour analysis
- **Counts vehicles** as they cross a virtual counting zone
- **Allocates green time** proportional to vehicle density (`count × 2 seconds`, capped at 60s)
- **Displays live video feeds** with detection overlays and a traffic light UI

> ⚠️ **Note:** This is a simulation using pre-recorded video files. In a production deployment, the same pipeline would connect to live CCTV camera feeds.

[▶️ Watch the demo on YouTube](https://youtu.be/aI7hh6BbZDY)

---

## ✨ Features

| Feature | Description |
|---|---|
| **Real-time vehicle detection** | Background subtraction + contour detection on each lane feed |
| **Adaptive signal timing** | PAAC (Priority-based Adaptive Auto Control) algorithm assigns green time based on actual traffic |
| **Multi-lane concurrent processing** | Each lane runs in its own thread for true parallel video processing |
| **Live video feed display** | Processed frames with bounding boxes and counting zone overlay shown in GUI |
| **Traffic light simulation** | Visual traffic light indicators (red/yellow/green) for each lane |
| **Countdown timer** | Displays remaining green/wait time for the active lane |
| **Configurable parameters** | Detection sensitivity, timing ratios, zone boundaries all adjustable |

---

## 🧠 How It Works

### System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Tkinter GUI (Main Thread)                    │
│  ┌──────────┐  ┌──────────┐          ┌──────────┐  ┌──────────┐   │
│  │ Lane 1   │  │ Lane 2   │   ...    │ Lane 4   │  │ Traffic  │   │
│  │ Video    │  │ Video    │          │ Video    │  │ Lights   │   │
│  └────┬─────┘  └────┬─────┘          └────┬─────┘  └──────────┘   │
│       │              │                     │                        │
├───────┴──────────────┴─────────────────────┴────────────────────────┤
│                    Background Threads                                │
│  ┌──────────────────┐   ┌──────────────────────────────────┐       │
│  │ VehicleDetector  │   │      SignalController            │       │
│  │  × 4 (one/lane)  │   │  (PAAC Algorithm - reads counts, │       │
│  │  OpenCV CV       │   │   sets signals, manages timers)  │       │
│  └──────────────────┘   └──────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────┘
```

### Detection Pipeline (per lane)

1. **Frame capture** — Read frame from video source
2. **Preprocessing** — Convert to grayscale, apply Gaussian blur
3. **Background subtraction** — Compute absolute difference from reference frame
4. **Thresholding + dilation** — Create binary motion mask
5. **Contour detection** — Find vehicle-sized blobs (width/height > 75px)
6. **Counting zone check** — If vehicle center falls within detection zone, increment count
7. **Overlay rendering** — Draw bounding boxes, counting zone, and count flash on frame

### Signal Control Algorithm (PAAC)

The Priority-based Adaptive Auto Control algorithm:

1. **Poll** each lane's vehicle count
2. **Compute** wait time: `count × 2 seconds` (max 60s)
3. **Set** the lane with traffic to **green**, all others to **red**
4. **Display** a live countdown timer
5. **Reset** that lane's count to 0
6. **Advance** to the next lane and repeat

If all lanes are empty, all signals remain red.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.10+** | Core language |
| **OpenCV** (`cv2`) | Video I/O, image processing, contour detection |
| **NumPy** | Array operations, image data handling |
| **Tkinter** | Desktop GUI framework (built into Python) |
| **Pillow** (`PIL`) | Image-to-Tkinter conversion for video display |
| **Threading** | Concurrent lane processing and signal control |

---

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/phanijsp/AITMS.git
cd AITMS

# (Optional) Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

### Video Data

The `data/` directory should contain the lane video files. Place your videos at:

```
data/
├── first/
│   ├── L1.mp4
│   ├── L2.mp4
│   ├── L3.mp4
│   └── L4.mp4
└── second/
    ├── Lane1mod.mp4
    ├── Lane2mod.mp4
    ├── Lane3mod.mp4
    └── Lane4mod.mp4
```

The system tries `data/second/Lane*mod.mp4` first, then falls back to `data/first/L*.mp4`.

---

## ▶️ Usage

```bash
# Run from the project root
python -m src.aitms

# Or if installed as a package
pip install -e .
python -m aitms
```

The application window will open with 4 video feeds arranged in a 2×2 grid, each with a traffic light indicator and vehicle count/wait-time labels.

### Controls

- Close the window to exit gracefully (all threads are cleaned up)
- Log output appears in the terminal

---

## 📁 Project Structure

```
AITMS/
├── src/
│   └── aitms/
│       ├── __init__.py          # Package metadata
│       ├── __main__.py          # `python -m aitms` entry point
│       ├── main.py              # Application entry point
│       ├── config.py            # All tunable parameters
│       ├── core/
│       │   ├── types.py         # Enums, dataclasses, type definitions
│       │   ├── vehicle_detector.py   # OpenCV detection pipeline
│       │   └── signal_controller.py  # PAAC algorithm + timers
│       ├── ui/
│       │   ├── traffic_light.py # Traffic light canvas widget
│       │   ├── lane_panel.py    # Single-lane UI panel
│       │   └── app.py           # Main Tkinter application
│       └── utils/
│           └── logging_setup.py # Logging configuration
├── data/                        # Video files (ignored by git)
├── docs/
│   └── documentation.pdf        # Original project report
├── reference/                   # Original monolithic code & assets
├── pyproject.toml               # Python packaging config
├── requirements.txt             # Dependencies
├── LICENSE                      # MIT License
└── README.md                    # This file
```

---

## ⚙️ Configuration

All tunable parameters are in `src/aitms/config.py`:

| Parameter | Default | Description |
|---|---|---|
| `MIN_VEHICLE_WIDTH` | 75 | Minimum contour width to count as vehicle |
| `MIN_VEHICLE_HEIGHT` | 75 | Minimum contour height to count as vehicle |
| `THRESHOLD_VALUE` | 21 | Binary threshold sensitivity |
| `ZONE_Y_START_RATIO` | 0.785 | Counting zone top boundary (% of frame height) |
| `ZONE_Y_END_RATIO` | 0.805 | Counting zone bottom boundary (% of frame height) |
| `ZONE_X_END_RATIO` | 0.5 | Counting zone right boundary (% of frame width, from left) |
| `SECONDS_PER_VEHICLE` | 2 | Green time per detected vehicle |
| `BUFFER_SECONDS` | 5 | Fixed buffer added to green time |
| `MAX_GREEN_SECONDS` | 60 | Maximum green signal duration |
| `VIDEO_SCALE_PERCENT` | 30 | Display scale factor |

---

## 🔧 Future Improvements

- **Deep learning detector**: Replace background subtraction with YOLO or SSD for more accurate vehicle classification
- **Multiple counting zones**: Detect vehicles at multiple points along the lane
- **Emergency vehicle priority**: Detect emergency vehicles (ambulance/fire truck) via siren detection or visual classification
- **Live camera support**: Connect to IP cameras or RTSP streams instead of video files
- **Data logging**: Record traffic patterns, signal times, and vehicle counts to CSV/DB
- **Pedestrian crossing integration**: Add pedestrian detection and crossing signals
- **Intersection coordination**: Network multiple intersections for corridor-level optimization
- **Web dashboard**: Build a real-time monitoring dashboard with metrics and graphs

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---



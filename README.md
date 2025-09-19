# Project Info
## Project Overview
- A host-side application to start/stop device acquisition via UDPcontrol frames and designed to visualize streaming MMW
radar sensor data in real time.
- Utilizing responsive PyQt UI (Start/Stop colocated with device IP/Port, dynamic sample size, Pause/Continue,
Y-axis zoom, non-negative view, hot-path updates via QTimer) to provid better interactive experience.
- Providing a robust data visualization/interaction: optional multiprocessing (IPC queues) for high-throughput
isolation, hardened Windows packaging (.ico, AppUserModelID, bundled assets), a focused troubleshooting guide
(bind/firewall/echo path/endianness), and safe shutdown (exit-time sendstop + UDP buffer drain) to prevent stale
artifacts
## Prerequisites
- Python 3.9–3.12 (Windows: install from python.org; macOS: use Homebrew or python.org installer)
- Git (optional, if you clone from a repo)
- Build tools: pyinstaller (we’ll install it in the virtual environment)
- Network: UDP reachable port (default 8080). Allow the app through firewall if prompted.
## Running in Virtual Enviroment (For macOS / Linux)
## Running in Virtual Enviroment (For Windows)
** go to your project folder (replace path!) **
- cd "C:\path\to\your\project"

# create and activate venv
py -3.11 -m venv venv
.\venv\Scripts\activate

# upgrade pip and install deps
python -m pip install --upgrade pip
pip install PyQt5 pyqtgraph numpy

# (optional) install for packaging
pip install pyinstaller

# run the app (replace with your main file name)
python oscilloscope.py

## Deployement
**XXXX:**
- XXXX
## Other

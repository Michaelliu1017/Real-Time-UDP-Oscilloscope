# Project Info
## Project Overview
- A host-side application to start/stop device acquisition via UDPcontrol frames and designed for visualizing streaming MMW
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

- go to your project folder<br/>
cd /path/to/your/project<br/>

- create and activate venv<br/>
python3 -m venv venv<br/>
source venv/bin/activate<br/>

- upgrade pip and install deps<br/>
python3 -m pip install --upgrade pip<br/>
pip install PyQt5 pyqtgraph numpy<br/>

- (optional) install for packaging<br/>
pip install pyinstaller<br/>

- run the app (replace with your main file name)<br/>
python3 oscilloscope.py<br/>

## Running in Virtual Enviroment (For Windows)
- go to your project folder<br/>
cd "C:\path\to\your\project"<br/>
- create and activate venv<br/>
py -3.11 -m venv venv<br/>
.\venv\Scripts\activate<br/>

- upgrade pip and install deps<br/>
python -m pip install --upgrade pip<br/>
pip install PyQt5 pyqtgraph numpy<br/>

- (optional) install for packaging<br/>
pip install pyinstaller<br/>
- run the app (replace with your main file name)<br/>
python oscilloscope.py<br/>

## Deployement
**XXXX:**
- XXXX
## Other

import sys
import socket
import struct
import numpy as np
import pyqtgraph as pg
if sys.platform.startswith('win'):
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u"projectb.oscope.1.1")

from PyQt5.QtGui import QIcon
from pathlib import Path
from PyQt5.QtCore import QTimer, QObject
from PyQt5.QtWidgets import (
    QApplication, QPushButton, QVBoxLayout, QWidget, QHBoxLayout,
    QLabel, QLineEdit
)
def resource_path(rel):
    base = getattr(sys, "_MEIPASS", Path(__file__).parent)
    return str(Path(base) / rel)


# Local Host Address
RECV_IP = "192.168.0.3"
#RECV_IP = "127.0.0.1"
RECV_PORT = 8080

# Target Device Address
DEVICE_IP_DEFAULT = "192.168.0.2"
DEVICE_PORT_DEFAULT = 8080  

class NonNegativeViewBox(pg.ViewBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseMode(self.PanMode)
    def updateAutoRange(self):
        super().updateAutoRange(); self.restrictToPositive()
    def restrictToPositive(self):
        (x0, x1), (y0, y1) = self.viewRange()
        changed = False
        if x0 < 0: x1 = x1 - x0; x0 = 0; changed = True
        if y0 < 0: y1 = y1 - y0; y0 = 0; changed = True
        if changed:
            self.setXRange(x0, x1, padding=0)
            self.setYRange(y0, y1, padding=0)
    def mouseDragEvent(self, ev, axis=None, **kwargs):
        super().mouseDragEvent(ev, axis=axis, **kwargs); self.restrictToPositive()
    def wheelEvent(self, ev, axis=None, **kwargs):
        super().wheelEvent(ev, axis=axis, **kwargs); self.restrictToPositive()

class ProjectB(QObject):
    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.app.aboutToQuit.connect(self.Termination)

        # ===== UI Container =====
        self.mainWidget = QWidget()
        self.mainWidget.setWindowTitle("GL Oscilloscope 1.0")
        icon = QIcon(resource_path("assets/icon.png"))
        self.app.setWindowIcon(icon)        # 影响任务栏/停靠栏
        self.mainWidget.setWindowIcon(icon) # 影响当前顶层窗口
        self.layout = QVBoxLayout(self.mainWidget)

        # ===== Receiving =====
        recv_layout = QHBoxLayout()
        recv_layout.addWidget(QLabel("本机接收:"))
        self.recv_ip_input = QLineEdit(RECV_IP); self.recv_ip_input.setFixedWidth(120)
        self.recv_port_input = QLineEdit(str(RECV_PORT)); self.recv_port_input.setFixedWidth(80)
        recv_apply_button = QPushButton("应用接收地址")
        recv_apply_button.clicked.connect(self.apply_recv_settings)
        recv_layout.addWidget(self.recv_ip_input)
        recv_layout.addWidget(self.recv_port_input)
        recv_layout.addWidget(recv_apply_button)
        self.layout.addLayout(recv_layout)

        # ===== Target =====
        dev_layout = QHBoxLayout()
        dev_layout.addWidget(QLabel("设备地址:"))
        self.dev_ip_input = QLineEdit(DEVICE_IP_DEFAULT); self.dev_ip_input.setFixedWidth(120)
        self.dev_port_input = QLineEdit(str(DEVICE_PORT_DEFAULT)); self.dev_port_input.setFixedWidth(80)
        dev_layout.addWidget(self.dev_ip_input)
        dev_layout.addWidget(self.dev_port_input)

        # Button "Send"
        self.stream_active = False
        self.send_toggle_btn = QPushButton("发送启动")
        self.send_toggle_btn.setFixedHeight(28)
        self.send_toggle_btn.clicked.connect(self.toggle_start_stop)
        dev_layout.addWidget(self.send_toggle_btn)
        #dev_layout.addStretch()
        self.layout.addLayout(dev_layout)

        # ===== Graph Display=====
        self.plotWidget = pg.GraphicsLayoutWidget()
        vb = NonNegativeViewBox()
        self.plot = self.plotWidget.addPlot(title="波形图", viewBox=vb)
        self.plot.setMouseEnabled(y=False)
        self.curve = self.plot.plot(pen="y")
        self.sample_count = 2000
        self.data = np.zeros(self.sample_count, dtype=np.float32)
        self.layout.addWidget(self.plotWidget)

        # ===== Button "Pause" =====
        self.pauseButton = QPushButton("暂停")
        self.pauseButton.clicked.connect(self.Pause)
        self.layout.addWidget(self.pauseButton)
        self.pauseFlag = False

        # ===== Y-axis Movement =====
        y_zoom_layout = QHBoxLayout()
        zoom_in_button = QPushButton("Y轴放大")
        zoom_out_button = QPushButton("Y轴缩小")
        zoom_in_button.clicked.connect(self.zoom_in_y)
        zoom_out_button.clicked.connect(self.zoom_out_y)
        y_zoom_layout.addStretch()
        y_zoom_layout.addWidget(zoom_in_button)
        y_zoom_layout.addWidget(zoom_out_button)
        y_zoom_layout.addStretch()
        self.layout.addLayout(y_zoom_layout)

        # ===== Sample Number =====
        sample_layout = QHBoxLayout()
        sample_layout.addWidget(QLabel("采样点数:"))
        self.sample_input = QLineEdit("1000"); self.sample_input.setFixedWidth(80)
        apply_button = QPushButton("应用")
        apply_button.clicked.connect(self.apply_sample_count)
        sample_layout.addWidget(self.sample_input)
        sample_layout.addWidget(apply_button)
        self.layout.addLayout(sample_layout)

        # ===== UDP Socket=====
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((RECV_IP, RECV_PORT))
        self.sock.setblocking(False)
        print(f"[UDP] 绑定接收 {RECV_IP}:{RECV_PORT}")

        # ===== Refreshing =====
        self.timer = QTimer()
        self.timer.timeout.connect(self.Update)
        self.timer.start(30)
  
    def apply_recv_settings(self):
        new_ip = self.recv_ip_input.text().strip()
        try:
            new_port = int(self.recv_port_input.text().strip())
            if self.sock:
                self.sock.close()
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((new_ip, new_port))
            self.sock.setblocking(False)
            print(f"[UDP] 已更新接收绑定为 {new_ip}:{new_port}")
        except Exception as e:
            print("[UDP] 监听地址设置失败:", e)

    def toggle_start_stop(self):

        dev_ip = self.dev_ip_input.text().strip()
        try:
            dev_port = int(self.dev_port_input.text().strip())
        except ValueError:
            print("[CMD] 设备端口无效"); return

        msg = b"sendstart" if not self.stream_active else b"sendstop"
        try:
            self.sock.sendto(msg, (dev_ip, dev_port))
            print(f"[CMD] {msg.decode()} -> {dev_ip}:{dev_port} (src={self.sock.getsockname()})")
            self.stream_active = not self.stream_active
            self.send_toggle_btn.setText("发送暂停" if self.stream_active else "发送启动")
        except Exception as e:
            print("[CMD] 发送失败：", e)

    def zoom_in_y(self):
        ymin, ymax = self.plot.viewRange()[1]
        c = (ymin + ymax) / 2.0
        delta = (ymax - ymin) * 0.8 / 2.0
        self.plot.setYRange(c - delta, c + delta)

    def zoom_out_y(self):
        ymin, ymax = self.plot.viewRange()[1]
        c = (ymin + ymax) / 2.0
        delta = (ymax - ymin) * 1.25 / 2.0
        self.plot.setYRange(c - delta, c + delta)

    def apply_sample_count(self):
        try:
            n = int(self.sample_input.text())
            assert n > 0
            self.sample_count = n
            self.data = np.zeros(self.sample_count, dtype=np.float32)
            self.curve.setData(self.data)
            print(f"[PLOT] 采样点数 -> {self.sample_count}")
        except Exception:
            print("[PLOT] 请输入有效正整数")

    def Update(self):
        if self.pauseFlag:
            return
        try:
            while True:
                packet, _ = self.sock.recvfrom(65536)
                if not packet:
                    break
                if len(packet) % 2 != 0:
                    continue
                cnt = len(packet) // 2
                values = struct.unpack(">" + "H" * cnt, packet)
                m = min(cnt, self.sample_count)
                if m <= 0:
                    continue
                self.data = np.roll(self.data, -m)
                self.data[-m:] = np.clip(np.array(values[-m:], dtype=np.float32), 0, None)
                x = np.arange(len(self.data), dtype=np.float32)
                self.curve.setData(x, self.data)
        except BlockingIOError:
            pass
        except Exception as e:
            print("[UDP] 接收错误:", e)

    def Pause(self):
        self.pauseFlag = not self.pauseFlag
        self.pauseButton.setText("继续" if self.pauseFlag else "暂停")
        if not self.pauseFlag:
            self.clear_socket_buffer()

    def clear_socket_buffer(self):
        try:
            while True:
                self.sock.recvfrom(65536)
        except BlockingIOError:
            pass

    def Termination(self):
        print("[EXIT] 清理资源...")
        try:
            # Send "sendstop" before exit
            dev_ip = self.dev_ip_input.text().strip()
            try:
                dev_port = int(self.dev_port_input.text().strip())
            except ValueError:
                dev_port = None

            if dev_ip and dev_port is not None and self.sock:
                try:
                    self.sock.sendto(b"sendstop", (dev_ip, dev_port))
                    print(f"[CMD] sendstop -> {dev_ip}:{dev_port} (src={self.sock.getsockname()})")
                except Exception as e:
                    print("[CMD] sendstop 发送失败：", e)

            self.timer.stop()
            if self.sock:
                self.sock.close()
            print("[EXIT] 完成")
        except Exception as e:
            print("[EXIT] 失败:", e)


    def run(self):
        self.mainWidget.resize(1024, 768)
        self.mainWidget.show()
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    ProjectB().run()

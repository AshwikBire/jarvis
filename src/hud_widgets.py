"""
Extra HUD widgets for the Jarvis dashboard: live clock, CPU/RAM radial gauges,
and a session-stats panel (uptime, messages, last response latency).
All custom-painted to match the holographic theme, no image assets.
"""
import math
import time
from datetime import datetime

import psutil
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont

CYAN = QColor(70, 220, 255)
CYAN_DIM = QColor(30, 120, 160)
AMBER = QColor(255, 200, 80)
GREEN = QColor(90, 255, 170)


class DigitalClock(QLabel):
    """Live HH:MM:SS + date readout, monospace HUD style."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            "color: #46DCFF; font-family: Consolas, monospace; font-size: 22px; "
            "font-weight: bold; letter-spacing: 2px;"
        )
        self.date_style = (
            "color: #1E7890; font-family: Consolas, monospace; font-size: 11px; letter-spacing: 3px;"
        )
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000)
        self._tick()

    def _tick(self):
        now = datetime.now()
        self.setText(now.strftime("%H:%M:%S"))


class DateLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            "color: #1E7890; font-family: Consolas, monospace; font-size: 11px; letter-spacing: 3px;"
        )
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(60000)
        self._tick()

    def _tick(self):
        now = datetime.now()
        self.setText(now.strftime("%A, %d %B %Y").upper())


class RadialGauge(QWidget):
    """Small circular gauge (0-100%) used for CPU / RAM readouts."""

    def __init__(self, label: str, color: QColor = CYAN, parent=None):
        super().__init__(parent)
        self.label = label
        self.color = color
        self.value = 0.0
        self.setFixedSize(84, 84)

    def set_value(self, v: float):
        self.value = max(0.0, min(100.0, v))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2 - 6
        r = min(w, h) / 2 - 12

        # Track
        track_pen = QPen(QColor(30, 60, 80, 120), 6)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.drawArc(int(cx - r), int(cy - r), int(r * 2), int(r * 2), 90 * 16, -270 * 16)

        # Value arc
        val_pen = QPen(self.color, 6)
        val_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(val_pen)
        span = -270 * (self.value / 100.0)
        painter.drawArc(int(cx - r), int(cy - r), int(r * 2), int(r * 2), 90 * 16, int(span * 16))

        # Percent text
        painter.setPen(QPen(QColor(220, 245, 255)))
        painter.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        painter.drawText(self.rect().adjusted(0, -6, 0, 0), Qt.AlignmentFlag.AlignCenter, f"{int(self.value)}%")

        # Label below
        painter.setPen(QPen(QColor(70, 220, 255, 180)))
        painter.setFont(QFont("Consolas", 8))
        painter.drawText(0, h - 6, w, 12, Qt.AlignmentFlag.AlignCenter, self.label)
        painter.end()


class SystemMonitor(QWidget):
    """CPU + RAM radial gauges, polled periodically via psutil."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        from PyQt6.QtWidgets import QHBoxLayout
        row = QHBoxLayout()
        self.cpu_gauge = RadialGauge("CPU", CYAN)
        self.ram_gauge = RadialGauge("RAM", AMBER)
        row.addWidget(self.cpu_gauge)
        row.addWidget(self.ram_gauge)
        layout.addLayout(row)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._poll)
        self.timer.start(1500)
        psutil.cpu_percent(interval=None)  # prime the non-blocking reading

    def _poll(self):
        self.cpu_gauge.set_value(psutil.cpu_percent(interval=None))
        self.ram_gauge.set_value(psutil.virtual_memory().percent)


class SessionStats(QWidget):
    """Uptime, message count, last response latency — plain-text HUD readout."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._start = time.time()
        self.message_count = 0
        self.last_latency = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.uptime_label = QLabel()
        self.msg_label = QLabel()
        self.latency_label = QLabel()
        for lbl in (self.uptime_label, self.msg_label, self.latency_label):
            lbl.setStyleSheet(
                "color: #9be8ff; font-family: Consolas, monospace; font-size: 11px; letter-spacing: 1px;"
            )
            layout.addWidget(lbl)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh)
        self.timer.start(1000)
        self._refresh()

    def record_message(self, latency_seconds: float):
        self.message_count += 1
        self.last_latency = latency_seconds
        self._refresh()

    def _refresh(self):
        elapsed = int(time.time() - self._start)
        m, s = divmod(elapsed, 60)
        h, m = divmod(m, 60)
        self.uptime_label.setText(f"UPTIME   {h:02d}:{m:02d}:{s:02d}")
        self.msg_label.setText(f"MESSAGES  {self.message_count}")
        lat_text = f"{self.last_latency:.1f}s" if self.last_latency is not None else "--"
        self.latency_label.setText(f"LAST REPLY  {lat_text}")

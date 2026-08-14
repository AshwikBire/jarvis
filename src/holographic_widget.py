"""
Holographic core visualizer for Jarvis.
Custom-painted PyQt6 widget: glowing rotating rings + particle scatter + pulse.
No external assets needed — everything is drawn with QPainter.
Enhanced with rainbow colors, multi-layer effects, and premium visuals.
Developed By Ashwik Bire
Portfolio: https://ashwikbire.github.io/My-Portfolio/
LinkedIn: https://www.linkedin.com/in/ashwik-bire-b2a000186/
"""

import math
import random
import sys
from PyQt6.QtWidgets import (
    QWidget, QSizePolicy, QApplication, QMainWindow, 
    QPushButton, QHBoxLayout, QVBoxLayout
)
from PyQt6.QtCore import Qt, QTimer, QPointF, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QRadialGradient, QBrush, QPainterPath

CYAN = QColor(70, 220, 255)
CYAN_DIM = QColor(30, 120, 160)
DEEP_NAVY = QColor(6, 10, 20)

# Per-state accent colors
STATE_COLORS = {
    "idle": QColor(70, 220, 255),
    "listening": QColor(90, 255, 170),
    "thinking": QColor(190, 120, 255),
    "speaking": QColor(255, 200, 80),
}

# Rainbow colors for rings
RAINBOW_COLORS = [
    QColor(255, 0, 0),      # Red
    QColor(255, 165, 0),    # Orange
    QColor(255, 255, 0),    # Yellow
    QColor(0, 255, 0),      # Green
    QColor(0, 0, 255),      # Blue
    QColor(75, 0, 130),     # Indigo
    QColor(238, 130, 238)   # Violet
]


class Particle:
    """Enhanced particle with trail and size variation"""
    def __init__(self, cx, cy, radius):
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(radius * 0.3, radius * 1.5)
        self.angle = angle
        self.radius = r
        self.speed = random.uniform(0.001, 0.015) * random.choice([-1, 1])
        self.size = random.uniform(1.5, 4.5)
        self.cx = cx
        self.cy = cy
        self.life = random.uniform(0.5, 1.0)
        self.phase = random.uniform(0, 2 * math.pi)
        self.color_offset = random.uniform(0, 360)
        self.trail = []

    def update(self):
        self.angle += self.speed
        self.phase += 0.02
        self.life = 0.7 + 0.3 * math.sin(self.phase)
        
        # Add trail
        pos = self.pos()
        self.trail.append((pos.x(), pos.y()))
        if len(self.trail) > 5:
            self.trail.pop(0)

    def pos(self):
        x = self.cx + self.radius * math.cos(self.angle)
        y = self.cy + self.radius * math.sin(self.angle) * 0.35
        return QPointF(x, y)


class HologramCanvas(QWidget):
    """Widget that draws the holographic core with rainbow rings"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(400)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("background: transparent;")
        self.core = None

    def set_core(self, core):
        self.core = core

    def paintEvent(self, event):
        if not self.core:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        base_r = min(w, h) / 2 * 0.7

        accent = STATE_COLORS.get(self.core._state, CYAN)
        theme_bg = self.core.current_theme["bg"] if hasattr(self.core, 'current_theme') else "#05080f"

        # ============================================================
        # 1. BACKGROUND GLOW (Multi-layer)
        # ============================================================
        bg_glow = QRadialGradient(cx, cy, base_r * 2.5)
        bg_glow.setColorAt(0.0, QColor(accent.red(), accent.green(), accent.blue(), 40))
        bg_glow.setColorAt(0.4, QColor(accent.red(), accent.green(), accent.blue(), 15))
        bg_glow.setColorAt(1.0, QColor(6, 10, 20, 0))
        painter.setBrush(QBrush(bg_glow))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), base_r * 2.5, base_r * 2.5)

        # Rainbow glow
        rainbow_glow = QRadialGradient(cx, cy, base_r * 1.8)
        rainbow_glow.setColorAt(0.0, QColor(255, 255, 255, 10))
        rainbow_glow.setColorAt(0.5, QColor(255, 200, 100, 8))
        rainbow_glow.setColorAt(1.0, QColor(6, 10, 20, 0))
        painter.setBrush(QBrush(rainbow_glow))
        painter.drawEllipse(QPointF(cx, cy), base_r * 1.8, base_r * 1.8)

        # ============================================================
        # 2. HEX GRID (faint, premium)
        # ============================================================
        painter.save()
        clip_path = QPainterPath()
        clip_path.addEllipse(QPointF(cx, cy), base_r * 1.9, base_r * 1.9)
        painter.setClipPath(clip_path)

        hex_pen = QPen(QColor(accent.red(), accent.green(), accent.blue(), 15), 0.8)
        painter.setPen(hex_pen)
        size = 20
        hstep = size * 1.8
        vstep = size * 1.55
        rows = int((base_r * 4) / vstep) + 2
        cols = int((base_r * 4) / hstep) + 2
        for row in range(-rows, rows):
            for col in range(-cols, cols):
                x = cx + col * hstep + (hstep / 2 if row % 2 else 0)
                y = cy + row * vstep
                painter.drawEllipse(QPointF(x, y), size * 0.3, size * 0.3)
        painter.restore()

        # ============================================================
        # 3. OUTER RADAR RING with tick marks (Rainbow)
        # ============================================================
        painter.save()
        painter.translate(cx, cy)
        
        for i in range(60):
            a = math.radians(i * 6 + self.core._angle * 0.2)
            tick_len = 10 if i % 5 == 0 else 5
            color = RAINBOW_COLORS[i % len(RAINBOW_COLORS)]
            color.setAlpha(80)
            tick_pen = QPen(color, 1.0)
            painter.setPen(tick_pen)
            outer_r = base_r * 1.12
            x1, y1 = outer_r * math.cos(a), outer_r * math.sin(a)
            x2, y2 = (outer_r - tick_len) * math.cos(a), (outer_r - tick_len) * math.sin(a)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
        painter.restore()

        # ============================================================
        # 4. OUTER SEGMENTED RING (RAINBOW - rotating)
        # ============================================================
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.core._angle)
        
        segments = 7
        gap = 8
        span = (360 / segments) - gap
        
        for i in range(segments):
            color = RAINBOW_COLORS[i % len(RAINBOW_COLORS)]
            pen = QPen(color, 2.8)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            start_angle = int((i * 360 / segments) * 16)
            painter.drawArc(
                int(-base_r * 0.95), int(-base_r * 0.95),
                int(base_r * 1.9), int(base_r * 1.9),
                start_angle, int(span * 16)
            )
        painter.restore()

        # ============================================================
        # 5. COUNTER-ROTATING DASHED RING (Rainbow)
        # ============================================================
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(-self.core._angle * 1.4)
        
        for i in range(6):
            color = RAINBOW_COLORS[(i + 3) % len(RAINBOW_COLORS)]
            color.setAlpha(60)
            pen2 = QPen(color, 1.4)
            pen2.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen2)
            mid_r = base_r * 0.82
            start = i * 60
            painter.drawArc(
                int(-mid_r), int(-mid_r),
                int(mid_r * 2), int(mid_r * 2),
                start * 16, 50 * 16
            )
        painter.restore()

        # ============================================================
        # 6. MIDDLE GLOW RING (Rainbow gradient)
        # ============================================================
        painter.save()
        painter.translate(cx, cy)
        
        hue = (self.core._ring_phase * 180) % 360
        color = QColor.fromHsv(int(hue), 200, 255, 100)
        pen_mid = QPen(color, 1.5)
        painter.setPen(pen_mid)
        mid_r2 = base_r * 0.65
        painter.drawEllipse(QPointF(0, 0), mid_r2, mid_r2)
        painter.restore()

        # ============================================================
        # 7. TIGHT INNER RING (Rainbow - active states)
        # ============================================================
        if self.core._state in ("listening", "thinking", "speaking"):
            painter.save()
            painter.translate(cx, cy)
            painter.rotate(self.core._angle * 2.0 + self.core._ring_phase * 30)
            
            hue = (self.core._ring_phase * 360) % 360
            color = QColor.fromHsv(int(hue), 255, 255, 180)
            pen3 = QPen(color, 2.2)
            painter.setPen(pen3)
            tight_r = base_r * 0.48
            painter.drawArc(
                int(-tight_r), int(-tight_r),
                int(tight_r * 2), int(tight_r * 2),
                0, int(220 * 16)
            )
            painter.restore()

        # ============================================================
        # 8. PULSING CORE (Rainbow + audio reactive)
        # ============================================================
        pulse_boost = self.core._pulse * 0.25 + self.core._level * 0.35
        inner_r = base_r * (0.25 + pulse_boost)

        glow_outer = QRadialGradient(cx, cy, inner_r * 3.0)
        hue_core = (self.core._ring_phase * 120) % 360
        glow_color = QColor.fromHsv(int(hue_core), 200, 255, 30)
        glow_outer.setColorAt(0.0, glow_color)
        glow_outer.setColorAt(1.0, QColor(6, 10, 20, 0))
        painter.setBrush(QBrush(glow_outer))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), inner_r * 3.0, inner_r * 3.0)

        core_grad = QRadialGradient(cx, cy, inner_r)
        core_color1 = QColor.fromHsv(int(hue_core), 255, 255, 230)
        core_color2 = QColor.fromHsv(int((hue_core + 60) % 360), 255, 200, 180)
        core_color3 = QColor.fromHsv(int((hue_core + 120) % 360), 200, 150, 60)
        
        core_grad.setColorAt(0.0, core_color1)
        core_grad.setColorAt(0.4, core_color2)
        core_grad.setColorAt(0.8, core_color3)
        core_grad.setColorAt(1.0, QColor(6, 10, 20, 0))
        painter.setBrush(QBrush(core_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), inner_r, inner_r)

        spot = QRadialGradient(cx - inner_r * 0.15, cy - inner_r * 0.15, inner_r * 0.3)
        spot.setColorAt(0.0, QColor(255, 255, 255, 180))
        spot.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(spot))
        painter.drawEllipse(QPointF(cx - inner_r * 0.15, cy - inner_r * 0.15), inner_r * 0.3, inner_r * 0.3)

        # ============================================================
        # 9. SPEAKING WAVEFORM BARS (Rainbow)
        # ============================================================
        if self.core._state == "speaking":
            painter.save()
            painter.translate(cx, cy)
            
            bar_count = 36
            for i in range(bar_count):
                a = (2 * math.pi / bar_count) * i
                amp = (0.4 + 0.6 * math.sin(self.core._speak_phase * 1.2 + i * 0.8)) * self.core._level
                r1 = base_r * 0.38
                r2 = r1 + base_r * 0.2 * amp
                
                hue_bar = (i * 10 + self.core._speak_phase * 50) % 360
                color_bar = QColor.fromHsv(int(hue_bar), 255, 255, 200)
                bar_pen = QPen(color_bar, 2.5)
                painter.setPen(bar_pen)
                
                x1, y1 = r1 * math.cos(a), r1 * math.sin(a)
                x2, y2 = r2 * math.cos(a), r2 * math.sin(a)
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            painter.restore()

        # ============================================================
        # 10. PARTICLES (Enhanced with rainbow colors)
        # ============================================================
        painter.setPen(Qt.PenStyle.NoPen)
        for p in self.core.particles:
            pos = p.pos()
            alpha = int(100 + 120 * p.life)
            if self.core._state == "thinking":
                alpha = int(alpha * 1.2)
            
            hue_p = (p.color_offset + self.core._ring_phase * 50) % 360
            c = QColor.fromHsv(int(hue_p), 200, 255, alpha)
            painter.setBrush(QBrush(c))
            painter.drawEllipse(pos, p.size * 0.7, p.size * 0.7)

            glow_trail = QRadialGradient(pos, p.size * 2.5)
            trail_color = QColor.fromHsv(int(hue_p), 200, 255, 30)
            glow_trail.setColorAt(0.0, trail_color)
            glow_trail.setColorAt(1.0, QColor(6, 10, 20, 0))
            painter.setBrush(QBrush(glow_trail))
            painter.drawEllipse(pos, p.size * 2.5, p.size * 2.5)

        # ============================================================
        # 11. SCANLINE SWEEP (Rainbow tinted)
        # ============================================================
        painter.save()
        clip_path2 = QPainterPath()
        clip_path2.addEllipse(QPointF(cx, cy), base_r * 1.9, base_r * 1.9)
        painter.setClipPath(clip_path2)

        scan_x = cx - base_r * 1.9 + (base_r * 3.8) * self.core._scan_y
        scan_grad = QRadialGradient(scan_x, cy, base_r * 0.4)
        hue_scan = (self.core._scan_y * 360) % 360
        scan_color = QColor.fromHsv(int(hue_scan), 200, 255, 40)
        scan_grad.setColorAt(0.0, scan_color)
        scan_grad.setColorAt(1.0, QColor(6, 10, 20, 0))
        painter.setBrush(QBrush(scan_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(int(scan_x - base_r * 0.4), int(cy - base_r * 2.2), int(base_r * 0.8), int(base_r * 4.4))
        painter.restore()

        # ============================================================
        # 12. OUTER BOUNDARY RING (Premium double ring)
        # ============================================================
        hue_outer = (self.core._ring_phase * 100) % 360
        outer_color = QColor.fromHsv(int(hue_outer), 200, 255, 50)
        pen_outer = QPen(outer_color, 0.8)
        painter.setPen(pen_outer)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(cx, cy), base_r * 0.99, base_r * 0.99)

        hue_inner = (self.core._ring_phase * 100 + 60) % 360
        inner_color = QColor.fromHsv(int(hue_inner), 200, 255, 25)
        pen_inner = QPen(inner_color, 3)
        painter.setPen(pen_inner)
        painter.drawEllipse(QPointF(cx, cy), base_r * 0.95, base_r * 0.95)

        # ============================================================
        # 13. CORNER GLOW ACCENTS
        # ============================================================
        for angle in [45, 135, 225, 315]:
            rad = math.radians(angle)
            x = cx + base_r * 1.05 * math.cos(rad)
            y = cy + base_r * 1.05 * math.sin(rad)
            
            accent_glow = QRadialGradient(x, y, base_r * 0.08)
            hue_acc = (self.core._ring_phase * 80 + angle) % 360
            acc_color = QColor.fromHsv(int(hue_acc), 200, 255, 30)
            accent_glow.setColorAt(0.0, acc_color)
            accent_glow.setColorAt(1.0, QColor(6, 10, 20, 0))
            painter.setBrush(QBrush(accent_glow))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(x, y), base_r * 0.08, base_r * 0.08)

        painter.end()


class HolographicCore(QWidget):
    """
    Premium holographic HUD with rainbow rings, particles, and state-driven animations.
    """

    # Add signal for communication
    message_signal = pyqtSignal(str, str)  # (message, type)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 450)
        self.setMaximumSize(1200, 1100)

        # ---- Animation state ----
        self._angle = 0.0
        self._pulse = 0.0
        self._pulse_dir = 1
        self._state = "idle"
        self._level = 0.0
        self._scan_y = 0.0
        self._speak_phase = 0.0
        self._ring_phase = 0.0
        self._glow_intensity = 0.0

        # ---- Theme ----
        self.current_theme = {"bg": "#05080f"}

        # ---- Particles ----
        self.particles = []
        self._init_particles()

        # ---- Timer ----
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(30)

        # ---- Canvas ----
        self.canvas = HologramCanvas()
        self.canvas.set_core(self)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def _init_particles(self):
        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        radius = min(w, h) / 2 * 0.8
        self.particles = [Particle(cx, cy, radius) for _ in range(100)]

    def resizeEvent(self, event):
        self._init_particles()
        super().resizeEvent(event)

    def set_state(self, state: str):
        self._state = state
        # Emit signal when state changes
        self.message_signal.emit(f"State: {state.upper()}", "system")

    def set_level(self, level: float):
        self._level = max(0.0, min(1.0, level))

    def _tick(self):
        speed = {"idle": 0.3, "listening": 1.0, "thinking": 2.2, "speaking": 0.8}.get(self._state, 0.5)
        self._angle = (self._angle + speed) % 360

        pulse_speed = {"idle": 0.012, "listening": 0.04, "thinking": 0.0, "speaking": 0.07}.get(self._state, 0.02)
        self._pulse += pulse_speed * self._pulse_dir
        if self._pulse > 1.0:
            self._pulse, self._pulse_dir = 1.0, -1
        elif self._pulse < 0.0:
            self._pulse, self._pulse_dir = 0.0, 1

        self._ring_phase += 0.015
        self._scan_y = (self._scan_y + 0.004) % 1.0
        self._speak_phase += 0.3

        # Auto level simulation
        if self._state == "speaking":
            self._level = 0.4 + 0.35 * abs(math.sin(self._speak_phase)) + 0.15 * abs(math.sin(self._speak_phase * 2.7))
        elif self._state == "listening":
            self._level = 0.3 + 0.2 * abs(math.sin(self._speak_phase * 0.6))
        else:
            self._level *= 0.92

        self._glow_intensity = 0.3 + 0.7 * self._pulse

        for p in self.particles:
            p.update()

        self.canvas.update()


# ============================================================
# USAGE EXAMPLE
# ============================================================
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QHBoxLayout, QWidget, QVBoxLayout

    class DemoWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Holographic Core — Ashwik Bire")
            self.setMinimumSize(600, 650)
            self.setStyleSheet("""
                QMainWindow {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #05080f, stop:1 #0a121f);
                }
            """)

            central = QWidget()
            self.setCentralWidget(central)
            layout = QVBoxLayout(central)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.core = HolographicCore()
            layout.addWidget(self.core, alignment=Qt.AlignmentFlag.AlignCenter)

            # Control buttons
            btn_layout = QHBoxLayout()
            btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            for state in ["idle", "listening", "thinking", "speaking"]:
                btn = QPushButton(state.capitalize())
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: rgba(70, 220, 255, 0.05);
                        color: rgba(140, 180, 220, 0.6);
                        border: 1px solid rgba(70, 220, 255, 0.08);
                        border-radius: 20px;
                        padding: 6px 18px;
                        font-size: 11px;
                        font-weight: 300;
                        letter-spacing: 1px;
                        text-transform: uppercase;
                    }}
                    QPushButton:hover {{
                        background: rgba(70, 220, 255, 0.12);
                        border-color: rgba(70, 220, 255, 0.2);
                        color: rgba(180, 210, 240, 0.8);
                    }}
                    QPushButton:pressed {{
                        background: rgba(70, 220, 255, 0.2);
                    }}
                """)
                btn.clicked.connect(lambda checked, s=state: self.core.set_state(s))
                btn_layout.addWidget(btn)

            layout.addLayout(btn_layout)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = DemoWindow()
    window.show()
    sys.exit(app.exec())
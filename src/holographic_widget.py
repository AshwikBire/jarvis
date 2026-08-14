"""
Advanced Holographic Core Visualizer — Jarvis UI
Developed By Ashwik Bire
Portfolio: https://ashwikbire.github.io/My-Portfolio/
LinkedIn: https://www.linkedin.com/in/ashwik-bire-b2a000186/
"""

import math
import random
import time
from datetime import datetime

# Try to import psutil, but don't fail if not available
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("⚠️ psutil not installed. Performance metrics will be disabled.")
    print("   Install with: pip install psutil")

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, 
    QTextEdit, QFrame, QSizePolicy, QPushButton,
    QScrollArea, QApplication, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF, QSize, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QRadialGradient, QBrush,
    QPainterPath, QFont, QLinearGradient, QAction,
    QKeySequence, QDragEnterEvent, QDropEvent, QMouseEvent,
    QShortcut  # <-- QShortcut is in QtGui, not QtWidgets!
)

# ---- Premium color palette ----
CYAN = QColor(70, 220, 255)
CYAN_DIM = QColor(30, 120, 160)
DEEP_NAVY = QColor(6, 10, 20)
GOLD = QColor(255, 200, 80)
PURPLE = QColor(190, 120, 255)
GREEN = QColor(90, 255, 170)

STATE_COLORS = {
    "idle": QColor(70, 220, 255),
    "listening": QColor(90, 255, 170),
    "thinking": QColor(190, 120, 255),
    "speaking": QColor(255, 200, 80),
}

STATE_GLOW = {
    "idle": QColor(70, 220, 255, 40),
    "listening": QColor(90, 255, 170, 50),
    "thinking": QColor(190, 120, 255, 45),
    "speaking": QColor(255, 200, 80, 55),
}

# ---- Theme colors ----
class Theme:
    DARK = {
        "bg": "#05080f",
        "bg2": "#0a121f",
        "bg3": "rgba(10, 20, 40, 0.3)",
        "text": "rgba(160, 200, 240, 0.9)",
        "text2": "rgba(140, 180, 220, 0.6)",
        "border": "rgba(70, 220, 255, 0.06)",
        "input_bg": "rgba(6, 10, 20, 0.5)",
        "scrollbar": "rgba(70, 220, 255, 0.15)",
    }
    LIGHT = {
        "bg": "#e8f0f8",
        "bg2": "#d0dce8",
        "bg3": "rgba(200, 220, 240, 0.5)",
        "text": "rgba(10, 30, 60, 0.9)",
        "text2": "rgba(30, 60, 100, 0.7)",
        "border": "rgba(30, 80, 140, 0.1)",
        "input_bg": "rgba(200, 220, 240, 0.6)",
        "scrollbar": "rgba(30, 80, 140, 0.2)",
    }


class Particle:
    """Enhanced particle with trail and size variation"""
    def __init__(self, cx, cy, radius):
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(radius * 0.3, radius * 1.5)
        self.angle = angle
        self.radius = r
        self.speed = random.uniform(0.001, 0.012) * random.choice([-1, 1])
        self.size = random.uniform(1.5, 4.0)
        self.cx = cx
        self.cy = cy
        self.life = random.uniform(0.5, 1.0)
        self.phase = random.uniform(0, 2 * math.pi)

    def update(self):
        self.angle += self.speed
        self.phase += 0.02
        self.life = 0.7 + 0.3 * math.sin(self.phase)

    def pos(self):
        x = self.cx + self.radius * math.cos(self.angle)
        y = self.cy + self.radius * math.sin(self.angle) * 0.35
        return QPointF(x, y)


class HologramCanvas(QWidget):
    """Widget that draws the holographic core"""
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
        
        # Get theme background color
        theme_bg = self.core.current_theme["bg"] if hasattr(self.core, 'current_theme') else "#05080f"

        # ============================================================
        # 1. BACKGROUND GLOW
        # ============================================================
        bg_glow = QRadialGradient(cx, cy, base_r * 2.2)
        bg_glow.setColorAt(0.0, QColor(accent.red(), accent.green(), accent.blue(), 50))
        bg_glow.setColorAt(0.5, QColor(accent.red(), accent.green(), accent.blue(), 12))
        bg_glow.setColorAt(1.0, QColor(6, 10, 20, 0))
        painter.setBrush(QBrush(bg_glow))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), base_r * 2.2, base_r * 2.2)

        # ============================================================
        # 2. HEX GRID (faint, premium)
        # ============================================================
        painter.save()
        clip_path = QPainterPath()
        clip_path.addEllipse(QPointF(cx, cy), base_r * 1.9, base_r * 1.9)
        painter.setClipPath(clip_path)

        hex_pen = QPen(QColor(accent.red(), accent.green(), accent.blue(), 18), 0.8)
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
        # 3. OUTER RADAR RING with tick marks
        # ============================================================
        painter.save()
        painter.translate(cx, cy)
        tick_pen = QPen(QColor(accent.red(), accent.green(), accent.blue(), 80), 1.0)
        painter.setPen(tick_pen)
        outer_r = base_r * 1.12
        for i in range(60):
            a = math.radians(i * 6 + self.core._angle * 0.2)
            tick_len = 10 if i % 5 == 0 else 5
            x1, y1 = outer_r * math.cos(a), outer_r * math.sin(a)
            x2, y2 = (outer_r - tick_len) * math.cos(a), (outer_r - tick_len) * math.sin(a)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
        painter.restore()

        # ============================================================
        # 4. OUTER SEGMENTED RING (rotating)
        # ============================================================
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.core._angle)
        pen = QPen(accent, 2.2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        segments = 6
        gap = 12
        span = (360 / segments) - gap
        for i in range(segments):
            start_angle = int((i * 360 / segments) * 16)
            painter.drawArc(
                int(-base_r * 0.95), int(-base_r * 0.95),
                int(base_r * 1.9), int(base_r * 1.9),
                start_angle, int(span * 16)
            )
        painter.restore()

        # ============================================================
        # 5. COUNTER-ROTATING DASHED RING
        # ============================================================
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(-self.core._angle * 1.4)
        pen2 = QPen(QColor(accent.red(), accent.green(), accent.blue(), 50), 1.2)
        pen2.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen2)
        mid_r = base_r * 0.82
        painter.drawEllipse(QPointF(0, 0), mid_r, mid_r)
        painter.restore()

        # ============================================================
        # 6. TIGHT INNER RING (active states)
        # ============================================================
        if self.core._state in ("listening", "thinking", "speaking"):
            painter.save()
            painter.translate(cx, cy)
            painter.rotate(self.core._angle * 2.0 + self.core._ring_phase * 30)
            pen3 = QPen(QColor(accent.red(), accent.green(), accent.blue(), 140), 1.8)
            painter.setPen(pen3)
            tight_r = base_r * 0.48
            painter.drawArc(
                int(-tight_r), int(-tight_r),
                int(tight_r * 2), int(tight_r * 2),
                0, int(220 * 16)
            )
            painter.restore()

        # ============================================================
        # 7. GLOWING CORE (pulse + audio reactive)
        # ============================================================
        pulse_boost = self.core._pulse * 0.25 + self.core._level * 0.35
        inner_r = base_r * (0.25 + pulse_boost)

        # Outer glow
        glow_outer = QRadialGradient(cx, cy, inner_r * 2.5)
        glow_outer.setColorAt(0.0, QColor(accent.red(), accent.green(), accent.blue(), 30))
        glow_outer.setColorAt(1.0, QColor(6, 10, 20, 0))
        painter.setBrush(QBrush(glow_outer))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), inner_r * 2.5, inner_r * 2.5)

        # Core gradient
        core_grad = QRadialGradient(cx, cy, inner_r)
        light = QColor(255, 255, 255) if self.core._state != "idle" else QColor(200, 240, 255)
        core_grad.setColorAt(0.0, QColor(light.red(), light.green(), light.blue(), 230))
        core_grad.setColorAt(0.4, QColor(accent.red(), accent.green(), accent.blue(), 180))
        core_grad.setColorAt(0.8, QColor(accent.red(), accent.green(), accent.blue(), 60))
        core_grad.setColorAt(1.0, QColor(accent.red(), accent.green(), accent.blue(), 0))
        painter.setBrush(QBrush(core_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), inner_r, inner_r)

        # Inner bright spot
        spot = QRadialGradient(cx - inner_r * 0.15, cy - inner_r * 0.15, inner_r * 0.3)
        spot.setColorAt(0.0, QColor(255, 255, 255, 160))
        spot.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(spot))
        painter.drawEllipse(QPointF(cx - inner_r * 0.15, cy - inner_r * 0.15), inner_r * 0.3, inner_r * 0.3)

        # ============================================================
        # 8. SPEAKING WAVEFORM BARS
        # ============================================================
        if self.core._state == "speaking":
            painter.save()
            painter.translate(cx, cy)
            bar_pen = QPen(QColor(255, 220, 120, 200), 2.8)
            painter.setPen(bar_pen)
            bar_count = 32
            for i in range(bar_count):
                a = (2 * math.pi / bar_count) * i
                amp = (0.4 + 0.6 * math.sin(self.core._speak_phase * 1.2 + i * 0.8)) * self.core._level
                r1 = base_r * 0.38
                r2 = r1 + base_r * 0.2 * amp
                x1, y1 = r1 * math.cos(a), r1 * math.sin(a)
                x2, y2 = r2 * math.cos(a), r2 * math.sin(a)
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            painter.restore()

        # ============================================================
        # 9. PARTICLES (enhanced)
        # ============================================================
        painter.setPen(Qt.PenStyle.NoPen)
        for p in self.core.particles:
            pos = p.pos()
            alpha = int(100 + 120 * p.life)
            if self.core._state == "thinking":
                alpha = int(alpha * 1.2)
            c = QColor(accent.red(), accent.green(), accent.blue(), alpha)
            painter.setBrush(QBrush(c))
            painter.drawEllipse(pos, p.size * 0.7, p.size * 0.7)

            # Glow trail
            glow_trail = QRadialGradient(pos, p.size * 2)
            glow_trail.setColorAt(0.0, QColor(accent.red(), accent.green(), accent.blue(), 20))
            glow_trail.setColorAt(1.0, QColor(accent.red(), accent.green(), accent.blue(), 0))
            painter.setBrush(QBrush(glow_trail))
            painter.drawEllipse(pos, p.size * 2, p.size * 2)

        # ============================================================
        # 10. SCANLINE SWEEP
        # ============================================================
        painter.save()
        clip_path2 = QPainterPath()
        clip_path2.addEllipse(QPointF(cx, cy), base_r * 1.9, base_r * 1.9)
        painter.setClipPath(clip_path2)

        scan_x = cx - base_r * 1.9 + (base_r * 3.8) * self.core._scan_y
        scan_grad = QRadialGradient(scan_x, cy, base_r * 0.4)
        scan_grad.setColorAt(0.0, QColor(accent.red(), accent.green(), accent.blue(), 35))
        scan_grad.setColorAt(1.0, QColor(accent.red(), accent.green(), accent.blue(), 0))
        painter.setBrush(QBrush(scan_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(int(scan_x - base_r * 0.4), int(cy - base_r * 2.2), int(base_r * 0.8), int(base_r * 4.4))
        painter.restore()

        # ============================================================
        # 11. OUTER BOUNDARY RING (premium double ring)
        # ============================================================
        pen_outer = QPen(QColor(accent.red(), accent.green(), accent.blue(), 50), 0.8)
        painter.setPen(pen_outer)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(cx, cy), base_r * 0.99, base_r * 0.99)

        pen_inner = QPen(QColor(accent.red(), accent.green(), accent.blue(), 20), 3)
        painter.setPen(pen_inner)
        painter.drawEllipse(QPointF(cx, cy), base_r * 0.95, base_r * 0.95)

        painter.end()


class DraggableFileWidget(QFrame):
    """Widget that supports drag & drop for file uploads"""
    file_dropped = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumHeight(80)
        self.setStyleSheet("""
            QFrame {
                background: rgba(6, 10, 20, 0.3);
                border: 2px dashed rgba(70, 220, 255, 0.1);
                border-radius: 12px;
                padding: 10px;
            }
            QFrame:hover {
                border-color: rgba(70, 220, 255, 0.25);
                background: rgba(70, 220, 255, 0.03);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.label = QLabel("📎 Drag & Drop Files Here\nor click to browse")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                color: rgba(140, 180, 220, 0.4);
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
                background: transparent;
                padding: 10px;
            }
        """)
        layout.addWidget(self.label)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QFrame {
                    background: rgba(70, 220, 255, 0.05);
                    border: 2px dashed rgba(70, 220, 255, 0.3);
                    border-radius: 12px;
                    padding: 10px;
                }
            """)
            
    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QFrame {
                background: rgba(6, 10, 20, 0.3);
                border: 2px dashed rgba(70, 220, 255, 0.1);
                border-radius: 12px;
                padding: 10px;
            }
        """)
        
    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet("""
            QFrame {
                background: rgba(6, 10, 20, 0.3);
                border: 2px dashed rgba(70, 220, 255, 0.1);
                border-radius: 12px;
                padding: 10px;
            }
        """)
        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path:
                files.append(file_path)
        if files:
            self.file_dropped.emit(files)
            
    def mousePressEvent(self, event: QMouseEvent):
        # Open file dialog on click
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files",
            "",
            "All Files (*.*);;Text Files (*.txt);;PDF Files (*.pdf);;Images (*.png *.jpg *.jpeg);;Word Documents (*.docx)"
        )
        if files:
            self.file_dropped.emit(files)


class HolographicCore(QWidget):
    """
    Premium holographic HUD with UI/UX enhancements:
    - Dark/Light mode switching
    - Activity log
    - Performance metrics
    - Keyboard shortcuts
    - Drag & drop file upload
    - Pin/Unpin messages
    """

    # Signal to send messages to main app
    message_signal = pyqtSignal(str, str)  # (message, type)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(700, 800)
        self.setMaximumSize(1400, 1100)

        # ---- Theme ----
        self.is_dark_mode = True
        self.current_theme = Theme.DARK

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

        # ---- Chat messages with pin support ----
        self.chat_messages = []
        self.pinned_messages = set()

        # ---- Uploaded files ----
        self.uploaded_files = []

        # ---- Performance metrics ----
        if HAS_PSUTIL:
            self.performance_timer = QTimer()
            self.performance_timer.timeout.connect(self._update_performance)
            self.performance_timer.start(2000)  # Update every 2 seconds
        else:
            self.performance_timer = None

        # ---- Particles ----
        self.particles = []
        self._init_particles()

        # ---- Timer ----
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(30)

        # ---- UI Layout ----
        self._setup_ui()
        
        # ---- Keyboard Shortcuts ----
        self._setup_shortcuts()
        
        # ---- Initial messages ----
        self.add_chat_message("🟢 System initialized", "system")
        self.add_chat_message("💡 Press Ctrl+H for help", "info")
        self.add_chat_message("📎 Drag & drop files or click to upload", "info")

    def _setup_ui(self):
        """Setup the UI with all enhancements"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(12)

        # ---- HEADER: Developed By Ashwik Bire ----
        header_frame = self._create_header()
        main_layout.addWidget(header_frame)

        # ---- Toolbar with theme toggle, shortcuts, etc. ----
        toolbar = self._create_toolbar()
        main_layout.addWidget(toolbar)

        # ---- Hologram Canvas ----
        self.canvas = HologramCanvas()
        self.canvas.set_core(self)
        self.canvas.setMinimumHeight(400)
        main_layout.addWidget(self.canvas, stretch=2)

        # ---- File Upload Area (Drag & Drop) ----
        self.file_upload_widget = DraggableFileWidget()
        self.file_upload_widget.file_dropped.connect(self._handle_file_upload)
        main_layout.addWidget(self.file_upload_widget)

        # ---- Chat/Status Area ----
        chat_frame = self._create_chat_area()
        main_layout.addWidget(chat_frame)

        # ---- Status and Controls ----
        bottom_frame = self._create_bottom_bar()
        main_layout.addWidget(bottom_frame)

        self.setLayout(main_layout)
        self._apply_theme()

    def _create_header(self):
        """Create the header with name and links"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: rgba(10, 20, 40, 0.3);
                border-radius: 16px;
                border: 1px solid rgba(70, 220, 255, 0.06);
                padding: 8px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.setSpacing(4)

        # Main name heading
        name_label = QLabel("✦ Developed By <b>Ashwik Bire</b> ✦")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("""
            QLabel {
                color: rgba(160, 200, 240, 0.9);
                font-size: 20px;
                font-weight: 600;
                font-family: 'Segoe UI', 'Inter', sans-serif;
                letter-spacing: 3px;
                background: transparent;
                padding: 4px 0;
            }
        """)
        header_layout.addWidget(name_label)

        # Links row
        links_layout = QHBoxLayout()
        links_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        links_layout.setSpacing(20)

        portfolio_link = QLabel(
            '<a href="https://ashwikbire.github.io/My-Portfolio/" style="color: #6ac8ff; text-decoration: none; font-weight: 400; font-size: 13px;">🌐 Portfolio</a>'
        )
        portfolio_link.setOpenExternalLinks(True)
        portfolio_link.setStyleSheet("""
            QLabel {
                font-family: 'Segoe UI', sans-serif;
                background: transparent;
                padding: 4px 16px;
                border-radius: 14px;
                border: 1px solid rgba(70, 220, 255, 0.08);
            }
            QLabel:hover {
                border-color: rgba(70, 220, 255, 0.3);
                background: rgba(70, 220, 255, 0.06);
            }
        """)

        linkedin_link = QLabel(
            '<a href="https://www.linkedin.com/in/ashwik-bire-b2a000186/" style="color: #6ac8ff; text-decoration: none; font-weight: 400; font-size: 13px;">🔗 LinkedIn</a>'
        )
        linkedin_link.setOpenExternalLinks(True)
        linkedin_link.setStyleSheet("""
            QLabel {
                font-family: 'Segoe UI', sans-serif;
                background: transparent;
                padding: 4px 16px;
                border-radius: 14px;
                border: 1px solid rgba(70, 220, 255, 0.08);
            }
            QLabel:hover {
                border-color: rgba(70, 220, 255, 0.3);
                background: rgba(70, 220, 255, 0.06);
            }
        """)

        links_layout.addWidget(portfolio_link)
        links_layout.addWidget(linkedin_link)
        header_layout.addLayout(links_layout)

        return header_frame

    def _create_toolbar(self):
        """Create toolbar with theme toggle, shortcuts, etc."""
        toolbar = QFrame()
        toolbar.setStyleSheet("""
            QFrame {
                background: rgba(10, 20, 40, 0.15);
                border-radius: 12px;
                border: 1px solid rgba(70, 220, 255, 0.04);
                padding: 6px;
            }
        """)
        layout = QHBoxLayout(toolbar)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.setSpacing(8)

        # Theme toggle button
        self.theme_btn = QPushButton("🌓 Dark Mode")
        self.theme_btn.setStyleSheet("""
            QPushButton {
                background: rgba(70, 220, 255, 0.05);
                color: rgba(140, 180, 220, 0.6);
                border: 1px solid rgba(70, 220, 255, 0.08);
                border-radius: 14px;
                padding: 4px 14px;
                font-size: 11px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton:hover {
                background: rgba(70, 220, 255, 0.1);
                border-color: rgba(70, 220, 255, 0.15);
            }
        """)
        self.theme_btn.clicked.connect(self._toggle_theme)
        layout.addWidget(self.theme_btn)

        # Performance metrics button (only if psutil is available)
        self.perf_btn = QPushButton("📊 Performance")
        self.perf_btn.setStyleSheet(self.theme_btn.styleSheet())
        self.perf_btn.clicked.connect(self._toggle_performance)
        if not HAS_PSUTIL:
            self.perf_btn.setEnabled(False)
            self.perf_btn.setToolTip("Install psutil for performance metrics")
        layout.addWidget(self.perf_btn)

        # Clear chat button
        clear_btn = QPushButton("🗑️ Clear Chat")
        clear_btn.setStyleSheet(self.theme_btn.styleSheet())
        clear_btn.clicked.connect(self._clear_chat)
        layout.addWidget(clear_btn)

        # Keyboard shortcuts hint
        shortcut_label = QLabel("⌨️ Ctrl+H help")
        shortcut_label.setStyleSheet("""
            QLabel {
                color: rgba(140, 180, 220, 0.2);
                font-size: 10px;
                font-family: 'Segoe UI', sans-serif;
                padding: 0 8px;
            }
        """)
        layout.addWidget(shortcut_label)

        # Performance display (initially hidden)
        self.perf_label = QLabel("CPU: 0% | RAM: 0MB")
        self.perf_label.setStyleSheet("""
            QLabel {
                color: rgba(140, 180, 220, 0.3);
                font-size: 10px;
                font-family: 'Consolas', monospace;
                padding: 0 8px;
                background: rgba(70, 220, 255, 0.03);
                border-radius: 8px;
            }
        """)
        if not HAS_PSUTIL:
            self.perf_label.setText("⚡ Performance unavailable")
        self.perf_label.hide()
        layout.addWidget(self.perf_label)

        layout.addStretch()

        # Activity log count
        self.activity_count = QLabel("📋 0 activities")
        self.activity_count.setStyleSheet("""
            QLabel {
                color: rgba(140, 180, 220, 0.3);
                font-size: 10px;
                font-family: 'Segoe UI', sans-serif;
                padding: 0 8px;
            }
        """)
        layout.addWidget(self.activity_count)

        return toolbar

    def _create_chat_area(self):
        """Create the chat/console area with pin support"""
        chat_frame = QFrame()
        chat_frame.setStyleSheet("""
            QFrame {
                background: rgba(6, 10, 20, 0.5);
                border-radius: 14px;
                border: 1px solid rgba(70, 220, 255, 0.06);
                padding: 4px;
            }
        """)
        chat_layout = QVBoxLayout(chat_frame)
        chat_layout.setSpacing(4)

        # Chat header with pin indicator
        chat_header = QHBoxLayout()
        chat_label = QLabel("💬 JARVIS CONSOLE")
        chat_label.setStyleSheet("""
            QLabel {
                color: rgba(70, 220, 255, 0.2);
                font-size: 9px;
                font-weight: 400;
                letter-spacing: 4px;
                font-family: 'Segoe UI', sans-serif;
                padding: 2px 8px;
            }
        """)
        chat_header.addWidget(chat_label)
        chat_header.addStretch()
        
        self.pin_indicator = QLabel("📌 Pinned: 0")
        self.pin_indicator.setStyleSheet("""
            QLabel {
                color: rgba(70, 220, 255, 0.15);
                font-size: 9px;
                font-family: 'Segoe UI', sans-serif;
                padding: 2px 8px;
            }
        """)
        chat_header.addWidget(self.pin_indicator)
        chat_layout.addLayout(chat_header)

        # Chat text area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMinimumHeight(100)
        self.chat_display.setMaximumHeight(180)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background: rgba(6, 10, 20, 0.3);
                border: none;
                border-radius: 10px;
                color: rgba(160, 200, 240, 0.7);
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                padding: 10px 14px;
                selection-background-color: rgba(70, 220, 255, 0.15);
            }
            QTextEdit:focus {
                border: 1px solid rgba(70, 220, 255, 0.1);
            }
            QScrollBar:vertical {
                background: rgba(6, 10, 20, 0.5);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(70, 220, 255, 0.15);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(70, 220, 255, 0.25);
            }
        """)
        chat_layout.addWidget(self.chat_display)

        return chat_frame

    def _create_bottom_bar(self):
        """Create the bottom status and control bar"""
        bottom_frame = QFrame()
        bottom_frame.setStyleSheet("""
            QFrame {
                background: rgba(10, 20, 40, 0.2);
                border-radius: 14px;
                border: 1px solid rgba(70, 220, 255, 0.04);
                padding: 6px;
            }
        """)
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bottom_layout.setSpacing(12)

        # Status indicator
        self.status_label = QLabel("● IDLE")
        self.status_label.setStyleSheet("""
            QLabel {
                color: rgba(70, 220, 255, 0.3);
                font-size: 10px;
                font-weight: 300;
                letter-spacing: 4px;
                font-family: 'Segoe UI', sans-serif;
                padding: 4px 12px;
                background: rgba(70, 220, 255, 0.04);
                border-radius: 20px;
            }
        """)
        bottom_layout.addWidget(self.status_label)

        # State buttons
        for state in ["idle", "listening", "thinking", "speaking"]:
            btn = QLabel(state.upper())
            btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
            btn.setStyleSheet(f"""
                QLabel {{
                    background: rgba(70, 220, 255, 0.04);
                    color: rgba(140, 180, 220, 0.4);
                    border: 1px solid rgba(70, 220, 255, 0.06);
                    border-radius: 20px;
                    padding: 6px 24px;
                    font-size: 11px;
                    font-weight: 400;
                    letter-spacing: 2px;
                    font-family: 'Segoe UI', sans-serif;
                }}
                QLabel:hover {{
                    background: rgba(70, 220, 255, 0.1);
                    border-color: rgba(70, 220, 255, 0.15);
                    color: rgba(180, 210, 240, 0.7);
                }}
            """)
            btn.mousePressEvent = lambda e, s=state: self.set_state(s)
            bottom_layout.addWidget(btn)

        return bottom_frame

    def _setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Ctrl+H - Show help
        self.help_shortcut = QShortcut(QKeySequence("Ctrl+H"), self)
        self.help_shortcut.activated.connect(self._show_help)

        # Ctrl+T - Toggle theme
        self.theme_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        self.theme_shortcut.activated.connect(self._toggle_theme)

        # Ctrl+C - Clear chat
        self.clear_shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        self.clear_shortcut.activated.connect(self._clear_chat)

        # Ctrl+1-4 - State shortcuts
        for i, state in enumerate(["idle", "listening", "thinking", "speaking"], 1):
            shortcut = QShortcut(QKeySequence(f"Ctrl+{i}"), self)
            shortcut.activated.connect(lambda s=state: self.set_state(s))

        # Ctrl+U - Upload files
        self.upload_shortcut = QShortcut(QKeySequence("Ctrl+U"), self)
        self.upload_shortcut.activated.connect(self._trigger_upload)

        # Ctrl+P - Toggle performance
        self.perf_shortcut = QShortcut(QKeySequence("Ctrl+P"), self)
        self.perf_shortcut.activated.connect(self._toggle_performance)

        # F1 - Help
        self.f1_shortcut = QShortcut(QKeySequence("F1"), self)
        self.f1_shortcut.activated.connect(self._show_help)

    def _show_help(self):
        """Show help dialog with shortcuts"""
        help_text = """
        <h3>⌨️ Keyboard Shortcuts</h3>
        <table style='color: rgba(160, 200, 240, 0.8);'>
        <tr><td><b>Ctrl+H</b></td><td>Show help</td></tr>
        <tr><td><b>Ctrl+T</b></td><td>Toggle theme</td></tr>
        <tr><td><b>Ctrl+C</b></td><td>Clear chat</td></tr>
        <tr><td><b>Ctrl+1</b></td><td>Idle state</td></tr>
        <tr><td><b>Ctrl+2</b></td><td>Listening state</td></tr>
        <tr><td><b>Ctrl+3</b></td><td>Thinking state</td></tr>
        <tr><td><b>Ctrl+4</b></td><td>Speaking state</td></tr>
        <tr><td><b>Ctrl+U</b></td><td>Upload files</td></tr>
        <tr><td><b>Ctrl+P</b></td><td>Toggle performance</td></tr>
        <tr><td><b>F1</b></td><td>Show help</td></tr>
        <tr><td><b>Esc</b></td><td>Close help</td></tr>
        </table>
        """
        QMessageBox.information(self, "Keyboard Shortcuts", help_text)

    def _toggle_theme(self):
        """Toggle between dark and light mode"""
        self.is_dark_mode = not self.is_dark_mode
        self.current_theme = Theme.DARK if self.is_dark_mode else Theme.LIGHT
        self.theme_btn.setText("🌙 Dark Mode" if self.is_dark_mode else "☀️ Light Mode")
        self._apply_theme()
        self.add_chat_message(f"🎨 Theme switched to {'Dark' if self.is_dark_mode else 'Light'} mode", "system")

    def _apply_theme(self):
        """Apply the current theme to all widgets"""
        theme = self.current_theme
        
        # Main window style
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {theme['bg']};
                color: {theme['text']};
                font-family: 'Segoe UI', sans-serif;
            }}
        """)
        
        # Update chat display
        self.chat_display.setStyleSheet(f"""
            QTextEdit {{
                background: {theme['input_bg']};
                border: none;
                border-radius: 10px;
                color: {theme['text']};
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                padding: 10px 14px;
                selection-background-color: rgba(70, 220, 255, 0.15);
            }}
            QTextEdit:focus {{
                border: 1px solid rgba(70, 220, 255, 0.1);
            }}
            QScrollBar:vertical {{
                background: {theme['input_bg']};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {theme['scrollbar']};
                border-radius: 4px;
                min-height: 20px;
            }}
        """)

        # Update frame backgrounds
        for frame in self.findChildren(QFrame):
            if frame.styleSheet():
                old_bg = frame.styleSheet()
                if "background:" in old_bg:
                    continue
                frame.setStyleSheet(f"""
                    QFrame {{
                        background: {theme['bg3']};
                        border-radius: 14px;
                        border: 1px solid {theme['border']};
                        padding: 6px;
                    }}
                """)

        # Update buttons
        for btn in self.findChildren(QPushButton):
            if btn.styleSheet() and "background:" not in btn.styleSheet():
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: rgba(70, 220, 255, 0.05);
                        color: {theme['text2']};
                        border: 1px solid {theme['border']};
                        border-radius: 14px;
                        padding: 4px 14px;
                        font-size: 11px;
                        font-family: 'Segoe UI', sans-serif;
                    }}
                    QPushButton:hover {{
                        background: rgba(70, 220, 255, 0.1);
                        border-color: rgba(70, 220, 255, 0.15);
                    }}
                """)

        # Update labels
        for label in self.findChildren(QLabel):
            if label.styleSheet() and "color:" in label.styleSheet():
                continue
            label.setStyleSheet(f"""
                QLabel {{
                    color: {theme['text2']};
                    font-family: 'Segoe UI', sans-serif;
                }}
            """)

    def _toggle_performance(self):
        """Toggle performance metrics display"""
        if not HAS_PSUTIL:
            self.add_chat_message("⚠️ psutil not installed. Install with: pip install psutil", "warning")
            return
            
        if self.perf_label.isVisible():
            self.perf_label.hide()
            self.add_chat_message("📊 Performance metrics hidden", "info")
        else:
            self.perf_label.show()
            self.add_chat_message("📊 Performance metrics shown", "info")
            self._update_performance()

    def _update_performance(self):
        """Update performance metrics"""
        if not HAS_PSUTIL:
            return
            
        try:
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            ram_used = memory.used / (1024 * 1024)  # MB
            
            cpu_color = "🟢" if cpu < 50 else ("🟡" if cpu < 80 else "🔴")
            mem_color = "🟢" if ram_used < 1000 else ("🟡" if ram_used < 2000 else "🔴")
            
            self.perf_label.setText(f"{cpu_color} CPU: {cpu:.0f}% | {mem_color} RAM: {ram_used:.0f}MB")
            self.perf_label.setStyleSheet(f"""
                QLabel {{
                    color: rgba(140, 180, 220, 0.5);
                    font-size: 10px;
                    font-family: 'Consolas', monospace;
                    padding: 0 8px;
                    background: rgba(70, 220, 255, 0.03);
                    border-radius: 8px;
                }}
            """)
        except Exception as e:
            self.perf_label.setText(f"⚡ Error: {str(e)[:20]}")

    def _handle_file_upload(self, files):
        """Handle uploaded files via drag & drop or browse"""
        for file_path in files:
            self.uploaded_files.append(file_path)
            file_name = file_path.split("/")[-1]
            self.add_chat_message(f"📎 File uploaded: {file_name}", "system")
            self.add_chat_message(f"   📂 Path: {file_path}", "info")
            
            # Try to read text from file
            try:
                if file_path.endswith('.txt'):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()[:200]
                        self.add_chat_message(f"   📝 Preview: {content}...", "info")
                elif file_path.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    self.add_chat_message(f"   🖼️ Image file detected ({file_name})", "info")
                elif file_path.endswith('.pdf'):
                    self.add_chat_message(f"   📄 PDF file detected ({file_name})", "info")
                elif file_path.endswith('.docx'):
                    self.add_chat_message(f"   📝 Word document detected ({file_name})", "info")
                else:
                    self.add_chat_message(f"   📁 File type: {file_path.split('.')[-1].upper()}", "info")
            except Exception as e:
                self.add_chat_message(f"   ⚠️ Could not preview: {str(e)[:50]}", "warning")
        
        self.activity_count.setText(f"📋 {len(self.uploaded_files)} files")
        
        # Emit signal to main app
        self.message_signal.emit(f"📎 {len(files)} file(s) uploaded", "system")

    def _trigger_upload(self):
        """Trigger file upload dialog via shortcut"""
        self.file_upload_widget.mousePressEvent(None)

    def _clear_chat(self):
        """Clear the chat display"""
        self.chat_display.clear()
        self.chat_messages = []
        self.pinned_messages.clear()
        self.pin_indicator.setText("📌 Pinned: 0")
        self.add_chat_message("🗑️ Chat cleared", "system")

    def add_chat_message(self, message, msg_type="info"):
        """Add a message to the chat display with pin support"""
        colors = {
            "system": "#46dcff",
            "info": "#90c8f0",
            "warning": "#ffc870",
            "error": "#ff6b6b",
            "user": "#90ffaa",
        }
        color = colors.get(msg_type, "#90c8f0")
        
        # Store message with metadata
        msg_data = {
            "text": message,
            "type": msg_type,
            "color": color,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "pinned": False
        }
        self.chat_messages.append(msg_data)
        
        # Add pin button indicator (right-click to pin)
        pin_icon = "📌" if msg_data["pinned"] else ""
        formatted_msg = f'<span style="color: {color};">{pin_icon} [{msg_data["timestamp"]}] ▶ {message}</span>'
        
        self.chat_display.append(formatted_msg)
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
        
        self.activity_count.setText(f"📋 {len(self.chat_messages)} activities")
        
        # Emit signal to main app
        self.message_signal.emit(message, msg_type)

    def pin_message(self, index):
        """Pin/unpin a message by index"""
        if 0 <= index < len(self.chat_messages):
            msg = self.chat_messages[index]
            msg["pinned"] = not msg["pinned"]
            if msg["pinned"]:
                self.pinned_messages.add(index)
            else:
                self.pinned_messages.discard(index)
            
            # Refresh chat display
            self._refresh_chat()
            self.pin_indicator.setText(f"📌 Pinned: {len(self.pinned_messages)}")
            self.add_chat_message(f"📌 Message {'pinned' if msg['pinned'] else 'unpinned'}", "info")

    def _refresh_chat(self):
        """Refresh the chat display with current messages"""
        self.chat_display.clear()
        # Show pinned messages first
        for idx, msg in enumerate(self.chat_messages):
            if idx in self.pinned_messages:
                pin_icon = "📌 "
                formatted = f'<span style="color: {msg["color"]};">{pin_icon}[{msg["timestamp"]}] ▶ {msg["text"]} [PINNED]</span>'
                self.chat_display.append(formatted)
        
        # Then show unpinned messages
        for idx, msg in enumerate(self.chat_messages):
            if idx not in self.pinned_messages:
                formatted = f'<span style="color: {msg["color"]};">[{msg["timestamp"]}] ▶ {msg["text"]}</span>'
                self.chat_display.append(formatted)

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
        self.status_label.setText(f"● {state.upper()}")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: rgba({STATE_COLORS[state].red()}, {STATE_COLORS[state].green()}, {STATE_COLORS[state].blue()}, 0.4);
                font-size: 10px;
                font-weight: 300;
                letter-spacing: 4px;
                font-family: 'Segoe UI', sans-serif;
                padding: 4px 12px;
                background: rgba({STATE_COLORS[state].red()}, {STATE_COLORS[state].green()}, {STATE_COLORS[state].blue()}, 0.06);
                border-radius: 20px;
            }}
        """)
        
        self.add_chat_message(f"🔄 State changed to: {state.upper()}", "system")
        self.message_signal.emit(f"State: {state.upper()}", "system")

    def set_level(self, level: float):
        self._level = max(0.0, min(1.0, level))

    def _tick(self):
        # ---- Rotation speed ----
        speed_map = {"idle": 0.3, "listening": 1.0, "thinking": 2.2, "speaking": 0.8}
        self._angle = (self._angle + speed_map.get(self._state, 0.5)) % 360

        # ---- Pulse ----
        pulse_speed = {"idle": 0.012, "listening": 0.04, "thinking": 0.0, "speaking": 0.07}
        self._pulse += pulse_speed.get(self._state, 0.02) * self._pulse_dir
        if self._pulse > 1.0:
            self._pulse, self._pulse_dir = 1.0, -1
        elif self._pulse < 0.0:
            self._pulse, self._pulse_dir = 0.0, 1

        # ---- Ring phase ----
        self._ring_phase += 0.015

        # ---- Scan ----
        self._scan_y = (self._scan_y + 0.004) % 1.0

        # ---- Speak phase ----
        self._speak_phase += 0.3

        # ---- Auto level ----
        if self._state == "speaking":
            self._level = 0.4 + 0.35 * abs(math.sin(self._speak_phase)) + 0.15 * abs(math.sin(self._speak_phase * 2.7))
        elif self._state == "listening":
            self._level = 0.3 + 0.2 * abs(math.sin(self._speak_phase * 0.6))
        else:
            self._level *= 0.92

        # ---- Glow intensity ----
        self._glow_intensity = 0.3 + 0.7 * self._pulse

        # ---- Update particles ----
        for p in self.particles:
            p.update()

        self.canvas.update()


# ============================================================
# USAGE EXAMPLE
# ============================================================
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow

    class DemoWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Holographic Core — Ashwik Bire")
            self.setMinimumSize(800, 900)
            self.setStyleSheet("""
                QMainWindow {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #05080f, stop:1 #0a121f);
                }
            """)

            central = QWidget()
            self.setCentralWidget(central)
            layout = QVBoxLayout(central)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.core = HolographicCore()
            layout.addWidget(self.core, alignment=Qt.AlignmentFlag.AlignCenter)

            # Connect signal
            self.core.message_signal.connect(self._on_message)

            # Add some demo activity
            QTimer.singleShot(1000, lambda: self.core.add_chat_message("🎯 Drag & drop files or use Ctrl+U", "info"))
            QTimer.singleShot(2000, lambda: self.core.add_chat_message("⌨️ Press Ctrl+H for keyboard shortcuts", "info"))

        def _on_message(self, message, msg_type):
            # Handle messages from the core widget
            print(f"[{msg_type}] {message}")

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = DemoWindow()
    window.show()
    sys.exit(app.exec())
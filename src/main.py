"""
Jarvis — Advanced Holographic AI Assistant with Natural Voice
Complete AI Assistant with Chat, Voice, and Document RAG
Developed By Ashwik Bire
Portfolio: https://ashwikbire.github.io/My-Portfolio/
LinkedIn: https://www.linkedin.com/in/ashwik-bire-b2a000186/
GitHub: https://github.com/AshwikBire
"""

import sys
import os
import time
import hashlib
import asyncio
import tempfile
import re
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QPushButton, QTextEdit, 
    QLineEdit, QFrame, QScrollArea, QMessageBox,
    QFileDialog, QListWidget, QListWidgetItem, QSizePolicy,
    QSplitter, QProgressBar, QDialog, QDialogButtonBox,
    QFormLayout, QLineEdit as QLineEditWidget,
    QComboBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize, QEvent, QUrl
from PyQt6.QtGui import (
    QFont, QPalette, QColor, QShortcut, QKeySequence, 
    QLinearGradient, QBrush, QPainter, QPen, QIcon, QPixmap,
    QDesktopServices
)

# Import holographic widget
from holographic_widget import HolographicCore, STATE_COLORS

# Try to import local modules
try:
    from ollama_client import OllamaClient
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False
    print("⚠️ ollama_client.py not found")

# Check for TTS dependencies
try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False
    print("⚠️ edge-tts not installed. Install with: pip install edge-tts")

try:
    import pygame
    pygame.mixer.init()
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False
    print("⚠️ pygame not installed. Install with: pip install pygame")


# ============================================================
# API KEY DIALOG (Startup)
# ============================================================

class APIKeyDialog(QDialog):
    """Dialog to get Nemotron API key on startup"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔑 Nemotron API Key Required")
        self.setMinimumSize(550, 280)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #05080f, stop:0.5 #0a121f, stop:1 #060e1a);
                border: 1px solid rgba(70, 220, 255, 0.1);
                border-radius: 16px;
            }
            QLabel {
                color: rgba(160, 200, 240, 0.8);
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            QLineEdit {
                background: rgba(6, 10, 20, 0.6);
                border: 1px solid rgba(70, 220, 255, 0.1);
                border-radius: 8px;
                color: rgba(160, 200, 240, 0.9);
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
                padding: 8px 12px;
            }
            QLineEdit:focus {
                border-color: rgba(70, 220, 255, 0.3);
            }
            QPushButton {
                background: rgba(70, 220, 255, 0.08);
                color: rgba(160, 200, 240, 0.7);
                border: 1px solid rgba(70, 220, 255, 0.06);
                border-radius: 8px;
                padding: 8px 20px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(70, 220, 255, 0.15);
                border-color: rgba(70, 220, 255, 0.15);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Title
        title = QLabel("🔑 NVIDIA Nemotron API Key")
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #46dcff;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel(
            "Enter your NVIDIA Nemotron API key to use cloud AI.\n"
            "Get your free key at: build.nvidia.com\n\n"
            "💡 You can also use Local AI (Ollama) without a key."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: rgba(140, 180, 220, 0.5); font-size: 12px;")
        layout.addWidget(desc)
        
        # API Key input
        form = QFormLayout()
        form.setSpacing(10)
        
        self.api_key_input = QLineEditWidget()
        self.api_key_input.setPlaceholderText("nvapi-...")
        self.api_key_input.setEchoMode(QLineEditWidget.EchoMode.Password)
        self.api_key_input.setMinimumHeight(36)
        form.addRow("API Key:", self.api_key_input)
        
        # Show/Hide key checkbox
        show_layout = QHBoxLayout()
        self.show_key_checkbox = QPushButton("👁️ Show")
        self.show_key_checkbox.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: rgba(140, 180, 220, 0.3);
                border: none;
                font-size: 11px;
                padding: 2px 8px;
            }
            QPushButton:hover {
                color: rgba(140, 180, 220, 0.5);
            }
        """)
        self.show_key_checkbox.clicked.connect(self._toggle_key_visibility)
        show_layout.addWidget(self.show_key_checkbox)
        show_layout.addStretch()
        form.addRow("", show_layout)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        skip_btn = QPushButton("Skip (Use Local AI)")
        skip_btn.setStyleSheet("""
            QPushButton {
                background: rgba(90, 255, 170, 0.05);
                color: rgba(90, 255, 170, 0.5);
                border: 1px solid rgba(90, 255, 170, 0.06);
                border-radius: 8px;
                padding: 8px 20px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(90, 255, 170, 0.12);
                border-color: rgba(90, 255, 170, 0.12);
                color: rgba(90, 255, 170, 0.7);
            }
        """)
        skip_btn.clicked.connect(self.reject)
        button_layout.addWidget(skip_btn)
        
        button_layout.addStretch()
        
        save_btn = QPushButton("✅ Save API Key")
        save_btn.setStyleSheet("""
            QPushButton {
                background: rgba(70, 220, 255, 0.08);
                color: rgba(70, 220, 255, 0.7);
                border: 1px solid rgba(70, 220, 255, 0.06);
                border-radius: 8px;
                padding: 8px 24px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: rgba(70, 220, 255, 0.15);
                border-color: rgba(70, 220, 255, 0.15);
                color: rgba(70, 220, 255, 0.9);
            }
        """)
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
    def _toggle_key_visibility(self):
        if self.api_key_input.echoMode() == QLineEditWidget.EchoMode.Password:
            self.api_key_input.setEchoMode(QLineEditWidget.EchoMode.Normal)
            self.show_key_checkbox.setText("🙈 Hide")
        else:
            self.api_key_input.setEchoMode(QLineEditWidget.EchoMode.Password)
            self.show_key_checkbox.setText("👁️ Show")
    
    def get_api_key(self):
        return self.api_key_input.text().strip()


# ============================================================
# TEXT-TO-SPEECH ENGINE
# ============================================================

class TTSEngine:
    """Natural text-to-speech using Microsoft Edge TTS"""
    
    def __init__(self):
        self.is_speaking = False
        self.is_enabled = True
        self.current_thread = None
        self.voice = "en-US-JennyNeural"
        self.rate = "-5%"
        self.pitch = "+0Hz"
        
    def speak(self, text):
        if not self.is_enabled or not text:
            return
        if not HAS_EDGE_TTS or not HAS_PYGAME:
            return
            
        self.stop()
        self.current_thread = QThread()
        self.current_thread.run = lambda: self._speak_sync(text)
        self.current_thread.start()
        
    def _speak_sync(self, text):
        self.is_speaking = True
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_path = temp_file.name
            temp_file.close()
            
            communicate = edge_tts.Communicate(text, self.voice, rate=self.rate, pitch=self.pitch)
            asyncio.run(communicate.save(temp_path))
            
            if HAS_PYGAME and os.path.exists(temp_path):
                pygame.mixer.music.load(temp_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                    
            try:
                os.unlink(temp_path)
            except:
                pass
        except Exception as e:
            print(f"⚠️ TTS error: {e}")
        finally:
            self.is_speaking = False
            
    def stop(self):
        if HAS_PYGAME:
            try:
                pygame.mixer.music.stop()
            except:
                pass
        self.is_speaking = False
        if self.current_thread:
            self.current_thread.quit()
            self.current_thread.wait()
            self.current_thread = None
            
    def toggle(self):
        self.is_enabled = not self.is_enabled
        if not self.is_enabled:
            self.stop()
        return self.is_enabled


# ============================================================
# DOCUMENT PROCESSOR (RAG)
# ============================================================

class DocumentProcessor:
    def __init__(self):
        self.documents = []
        self.chunks = []
        self.data_path = Path("data/documents")
        self.data_path.mkdir(parents=True, exist_ok=True)
    
    def add_document(self, file_path, content, file_type="txt"):
        doc_id = hashlib.md5(file_path.encode()).hexdigest()[:8]
        doc = {
            'id': doc_id,
            'path': file_path,
            'name': os.path.basename(file_path),
            'type': file_type,
            'size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            'added': datetime.now().isoformat(),
            'content': content[:500]
        }
        for i, existing in enumerate(self.documents):
            if existing['id'] == doc_id:
                self.documents[i] = doc
                break
        else:
            self.documents.append(doc)
        
        chunks = self._chunk_text(content)
        for i, chunk in enumerate(chunks):
            self.chunks.append({
                'doc_id': doc_id,
                'chunk_id': i,
                'content': chunk,
                'preview': chunk[:100] + '...' if len(chunk) > 100 else chunk
            })
        return doc_id
    
    def _chunk_text(self, text, chunk_size=500, overlap=50):
        if not text:
            return []
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        return chunks
    
    def search(self, query, top_k=3):
        results = []
        query_words = set(query.lower().split())
        for chunk in self.chunks:
            chunk_words = set(chunk['content'].lower().split())
            score = len(query_words.intersection(chunk_words))
            if score > 0:
                results.append({
                    'chunk': chunk,
                    'score': score,
                    'preview': chunk['content'][:200] + '...' if len(chunk['content']) > 200 else chunk['content']
                })
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def get_context(self, query, top_k=3):
        results = self.search(query, top_k)
        if not results:
            return None
        context = "Context from uploaded documents:\n\n"
        for i, result in enumerate(results):
            context += f"[Document {i+1}]: {result['preview']}\n\n"
        return context
    
    def get_documents(self):
        return self.documents
    
    def clear_all(self):
        self.documents = []
        self.chunks = []


# ============================================================
# CHAT WORKER WITH TTS
# ============================================================

class ChatWorker(QThread):
    response_ready = pyqtSignal(str)
    status_update = pyqtSignal(str, str)
    speaking_started = pyqtSignal()
    speaking_finished = pyqtSignal()
    progress_update = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.message = ""
        self.client = None
        self.doc_processor = None
        self.tts_engine = None
        self.voice_enabled = True
        self.use_nemotron = False
        self.nemotron_api_key = ""
        self.ai_model = "local"  # "local" or "nemotron"
        
    def setup(self, message, client, doc_processor=None, tts_engine=None, 
              voice_enabled=True, ai_model="local", nemotron_api_key=""):
        self.message = message
        self.client = client
        self.doc_processor = doc_processor
        self.tts_engine = tts_engine
        self.voice_enabled = voice_enabled
        self.ai_model = ai_model
        self.nemotron_api_key = nemotron_api_key
        
    def run(self):
        try:
            self.status_update.emit("", "#be78ff")
            self.progress_update.emit(20)
            
            # Get context from documents
            context = None
            if self.doc_processor and self.doc_processor.documents:
                context = self.doc_processor.get_context(self.message)
            self.progress_update.emit(40)
            
            # Build prompt
            if context:
                full_prompt = f"{context}\n\nUser question: {self.message}\n\nAnswer based on the above context:"
            else:
                full_prompt = self.message
            
            # Get response based on selected AI
            if self.ai_model == "nemotron" and self.nemotron_api_key:
                response = self._get_nemotron_response(full_prompt)
            else:
                if self.client and hasattr(self.client, 'chat'):
                    response = self.client.chat(full_prompt)
                else:
                    response = "⚠️ No LLM client available. Please ensure Ollama is running."
            
            self.progress_update.emit(60)
            
            if context:
                response = f"📄 {response}"
            
            self.response_ready.emit(response)
            self.progress_update.emit(80)
            
            # Speak the response
            if self.voice_enabled and self.tts_engine and HAS_EDGE_TTS and HAS_PYGAME:
                self.status_update.emit("speaking", "#ffc850")
                self.speaking_started.emit()
                
                clean_response = self._clean_for_speech(response)
                self.tts_engine.speak(clean_response)
                
                timeout = 0
                while self.tts_engine.is_speaking and timeout < 600:
                    time.sleep(0.1)
                    timeout += 1
                    self.progress_update.emit(80 + int(timeout / 6))
                
                self.speaking_finished.emit()
                self.status_update.emit("", "#46dcff")
            else:
                self.status_update.emit("", "#46dcff")
            
            self.progress_update.emit(100)
            
        except Exception as e:
            self.response_ready.emit(f"⚠️ Error: {str(e)}")
            self.status_update.emit("", "#46dcff")
            self.progress_update.emit(100)
    
    def _clean_for_speech(self, text):
        text = re.sub(r'\*\*', '', text)
        text = re.sub(r'\*', '', text)
        text = re.sub(r'`', '', text)
        text = re.sub(r'#', '', text)
        text = re.sub(r'📄', '', text)
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F1E0-\U0001F1FF"
            u"\U00002500-\U00002BEF"
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\U0001f926-\U0001f937"
            u"\U00010000-\U0010ffff"
            u"\u2640-\u2642" 
            u"\u2600-\u2B55"
            u"\u200d"
            u"\u23cf"
            u"\u23e9"
            u"\u231a"
            u"\ufe0f"
            u"\u3030"
            "]+", flags=re.UNICODE)
        text = emoji_pattern.sub('', text)
        return text.strip()
    
    def _get_nemotron_response(self, prompt):
        import requests
        if not self.nemotron_api_key:
            return "❌ Nemotron API key not provided."
        url = "https://api.nvcf.nvidia.com/v2/nvcf/pexec/functions"
        headers = {
            "Authorization": f"Bearer {self.nemotron_api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 500
        }
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response")
            else:
                return f"❌ API Error: {response.status_code}"
        except Exception as e:
            return f"❌ Connection error: {str(e)}"


# ============================================================
# MAIN WINDOW
# ============================================================

class JarvisWindow(QMainWindow):
    def __init__(self, nemotron_api_key=""):
        super().__init__()
        self.setWindowTitle("J.A.R.V.I.S. — Advanced AI Assistant")
        
        # Start with a good default size
        screen = QApplication.primaryScreen().geometry()
        width = int(screen.width() * 0.85)
        height = int(screen.height() * 0.85)
        self.setMinimumSize(1200, 750)
        self.resize(width, height)
        
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #05080f, stop:0.5 #0a121f, stop:1 #060e1a);
            }
        """)
        
        # Initialize components
        self.ollama_client = None
        self.doc_processor = DocumentProcessor()
        self.tts_engine = TTSEngine()
        self.voice_enabled = True
        self.nemotron_api_key = nemotron_api_key
        self.ai_model = "local"  # "local" or "nemotron"
        self.is_processing = False
        self.start_time = datetime.now()
        self.message_count = 0
        self._processing_core_message = False
        
        if HAS_OLLAMA:
            try:
                self.ollama_client = OllamaClient()
                self.ollama_client.set_model("qwen2.5:3b")
            except Exception as e:
                print(f"⚠️ Failed to initialize Ollama: {e}")
                self.ollama_client = None
        
        self._setup_ui()
        self._setup_shortcuts()
        self._init_status()
        
        self.perf_timer = QTimer()
        self.perf_timer.timeout.connect(self._update_performance)
        self.perf_timer.start(3000)
        
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.WindowStateChange:
            self._handle_resize()
        return super().eventFilter(obj, event)

    def resizeEvent(self, event):
        self._handle_resize()
        super().resizeEvent(event)

    def _handle_resize(self):
        width = self.width()
        is_small = width < 1400
        
        if hasattr(self, 'splitter'):
            if is_small:
                self.splitter.setSizes([int(width * 0.5), int(width * 0.5)])
            else:
                self.splitter.setSizes([int(width * 0.55), int(width * 0.45)])

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # ---- HEADER ----
        header = self._create_header()
        main_layout.addWidget(header)

        # ---- SPLITTER ----
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(6)
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background: rgba(70, 220, 255, 0.06);
                border-radius: 3px;
                margin: 5px 0px;
            }
            QSplitter::handle:hover {
                background: rgba(70, 220, 255, 0.15);
            }
        """)

        # Left: Holographic Core (55%)
        left_panel = self._create_holographic_panel()
        self.splitter.addWidget(left_panel)

        # Right: Chat Panel (45%)
        right_panel = self._create_chat_panel()
        self.splitter.addWidget(right_panel)

        width = self.width()
        self.splitter.setSizes([int(width * 0.55), int(width * 0.45)])

        main_layout.addWidget(self.splitter)

        # ---- STATUS BAR ----
        status_bar = self._create_status_bar()
        main_layout.addWidget(status_bar)

        self._refresh_document_list()
        QTimer.singleShot(200, self.input_field.setFocus)

    def _create_header(self):
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: rgba(6, 10, 20, 0.6);
                border: 1px solid rgba(70, 220, 255, 0.08);
                border-radius: 14px;
                padding: 6px 16px;
            }
        """)
        header.setMinimumHeight(60)
        header.setMaximumHeight(76)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(8)

        # Brand
        brand = QHBoxLayout()
        brand.setSpacing(8)
        
        logo = QLabel("✦")
        logo.setStyleSheet("QLabel { color: #46dcff; font-size: 24px; font-weight: 300; }")
        brand.addWidget(logo)
        
        title = QLabel("J.A.R.V.I.S.")
        title.setStyleSheet("""
            QLabel {
                color: rgba(160, 200, 240, 0.9);
                font-size: 16px;
                font-weight: 600;
                font-family: 'Segoe UI', sans-serif;
                letter-spacing: 2px;
            }
        """)
        brand.addWidget(title)
        
        subtitle = QLabel("AI Assistant")
        subtitle.setStyleSheet("""
            QLabel {
                color: rgba(70, 220, 255, 0.3);
                font-size: 9px;
                font-weight: 300;
                letter-spacing: 3px;
                font-family: 'Segoe UI', sans-serif;
                padding: 2px 0 0 2px;
            }
        """)
        brand.addWidget(subtitle)
        
        brand.addStretch()
        layout.addLayout(brand)

        # ---- Developer Credit with Links ----
        dev_frame = QFrame()
        dev_frame.setStyleSheet("""
            QFrame {
                background: rgba(70, 220, 255, 0.03);
                border: 1px solid rgba(70, 220, 255, 0.04);
                border-radius: 10px;
                padding: 2px 8px;
            }
        """)
        dev_layout = QHBoxLayout(dev_frame)
        dev_layout.setContentsMargins(8, 2, 8, 2)
        dev_layout.setSpacing(6)
        
        dev_label = QLabel("✦ Developed By")
        dev_label.setStyleSheet("color: rgba(140, 180, 220, 0.3); font-size: 9px;")
        dev_layout.addWidget(dev_label)
        
        name_label = QLabel("Ashwik Bire")
        name_label.setStyleSheet("color: rgba(70, 220, 255, 0.5); font-size: 10px; font-weight: 600;")
        dev_layout.addWidget(name_label)
        
        # Separator
        sep = QLabel("|")
        sep.setStyleSheet("color: rgba(140, 180, 220, 0.1); font-size: 9px;")
        dev_layout.addWidget(sep)
        
        # Portfolio Link
        portfolio_btn = QPushButton("🌐")
        portfolio_btn.setToolTip("Portfolio")
        portfolio_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: rgba(140, 180, 220, 0.2);
                border: none;
                font-size: 11px;
                padding: 2px 4px;
            }
            QPushButton:hover {
                color: rgba(70, 220, 255, 0.4);
            }
        """)
        portfolio_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://ashwikbire.github.io/My-Portfolio/")))
        dev_layout.addWidget(portfolio_btn)
        
        # LinkedIn Link
        linkedin_btn = QPushButton("🔗")
        linkedin_btn.setToolTip("LinkedIn")
        linkedin_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: rgba(140, 180, 220, 0.2);
                border: none;
                font-size: 11px;
                padding: 2px 4px;
            }
            QPushButton:hover {
                color: rgba(70, 220, 255, 0.4);
            }
        """)
        linkedin_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://linkedin.com/in/ashwik-bire-b2a000186")))
        dev_layout.addWidget(linkedin_btn)
        
        # GitHub Link
        github_btn = QPushButton("🐙")
        github_btn.setToolTip("GitHub")
        github_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: rgba(140, 180, 220, 0.2);
                border: none;
                font-size: 11px;
                padding: 2px 4px;
            }
            QPushButton:hover {
                color: rgba(70, 220, 255, 0.4);
            }
        """)
        github_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/AshwikBire")))
        dev_layout.addWidget(github_btn)
        
        layout.addWidget(dev_frame)

        # ---- Controls ----
        controls = QHBoxLayout()
        controls.setSpacing(6)

        btn_style = """
            QPushButton {
                background: rgba(70, 220, 255, 0.05);
                color: rgba(140, 180, 220, 0.6);
                border: 1px solid rgba(70, 220, 255, 0.06);
                border-radius: 8px;
                padding: 4px 10px;
                font-size: 9px;
                font-weight: 400;
                font-family: 'Segoe UI', sans-serif;
                letter-spacing: 0.3px;
            }
            QPushButton:hover {
                background: rgba(70, 220, 255, 0.12);
                border-color: rgba(70, 220, 255, 0.15);
                color: rgba(180, 210, 240, 0.8);
            }
            QPushButton:pressed {
                background: rgba(70, 220, 255, 0.2);
            }
        """

        # AI Model Selector
        self.ai_combo = QComboBox()
        self.ai_combo.addItem("🧠 Local (Ollama)", "local")
        self.ai_combo.addItem("☁️ Nemotron (Cloud)", "nemotron")
        self.ai_combo.setStyleSheet("""
            QComboBox {
                background: rgba(70, 220, 255, 0.05);
                color: rgba(140, 180, 220, 0.6);
                border: 1px solid rgba(70, 220, 255, 0.06);
                border-radius: 8px;
                padding: 4px 10px;
                font-size: 9px;
                font-family: 'Segoe UI', sans-serif;
                min-width: 120px;
            }
            QComboBox:hover {
                background: rgba(70, 220, 255, 0.12);
                border-color: rgba(70, 220, 255, 0.15);
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background: #0a121f;
                color: rgba(160, 200, 240, 0.8);
                border: 1px solid rgba(70, 220, 255, 0.06);
                selection-background-color: rgba(70, 220, 255, 0.1);
            }
        """)
        self.ai_combo.currentIndexChanged.connect(self._on_ai_changed)
        controls.addWidget(self.ai_combo)

        # Voice toggle
        self.voice_btn = QPushButton("🔊 ON")
        self.voice_btn.setStyleSheet(btn_style)
        self.voice_btn.setFixedHeight(28)
        self.voice_btn.clicked.connect(self._toggle_voice)
        controls.addWidget(self.voice_btn)

        # Upload button
        upload_btn = QPushButton("📎 Upload")
        upload_btn.setStyleSheet(btn_style)
        upload_btn.setFixedHeight(28)
        upload_btn.clicked.connect(self._upload_document)
        controls.addWidget(upload_btn)

        # Clear chat
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.setStyleSheet(btn_style)
        clear_btn.setFixedHeight(28)
        clear_btn.clicked.connect(self._clear_chat)
        controls.addWidget(clear_btn)

        # Stop speaking button
        stop_btn = QPushButton("⏹️ Stop")
        stop_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 70, 70, 0.05);
                color: rgba(255, 100, 100, 0.4);
                border: 1px solid rgba(255, 70, 70, 0.06);
                border-radius: 8px;
                padding: 4px 10px;
                font-size: 9px;
                font-weight: 400;
                font-family: 'Segoe UI', sans-serif;
                letter-spacing: 0.3px;
            }
            QPushButton:hover {
                background: rgba(255, 70, 70, 0.12);
                border-color: rgba(255, 70, 70, 0.12);
                color: rgba(255, 100, 100, 0.6);
            }
        """)
        stop_btn.setFixedHeight(28)
        stop_btn.clicked.connect(self._stop_speaking)
        controls.addWidget(stop_btn)

        # API Key button
        self.api_btn = QPushButton("🔑 API Key")
        self.api_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 200, 80, 0.05);
                color: rgba(255, 200, 80, 0.5);
                border: 1px solid rgba(255, 200, 80, 0.06);
                border-radius: 8px;
                padding: 4px 10px;
                font-size: 9px;
                font-weight: 400;
                font-family: 'Segoe UI', sans-serif;
                letter-spacing: 0.3px;
            }
            QPushButton:hover {
                background: rgba(255, 200, 80, 0.12);
                border-color: rgba(255, 200, 80, 0.12);
                color: rgba(255, 200, 80, 0.7);
            }
        """)
        self.api_btn.setFixedHeight(28)
        self.api_btn.clicked.connect(self._show_api_key_dialog)
        
        # Show key status
        if self.nemotron_api_key:
            self.api_btn.setText("🔑 Key Set ✅")
            self.api_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(90, 255, 170, 0.05);
                    color: rgba(90, 255, 170, 0.6);
                    border: 1px solid rgba(90, 255, 170, 0.06);
                    border-radius: 8px;
                    padding: 4px 10px;
                    font-size: 9px;
                    font-weight: 400;
                    font-family: 'Segoe UI', sans-serif;
                    letter-spacing: 0.3px;
                }
                QPushButton:hover {
                    background: rgba(90, 255, 170, 0.12);
                    border-color: rgba(90, 255, 170, 0.12);
                    color: rgba(90, 255, 170, 0.8);
                }
            """)
        controls.addWidget(self.api_btn)

        layout.addLayout(controls)

        return header

    def _create_holographic_panel(self):
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: rgba(6, 10, 20, 0.5);
                border: 1px solid rgba(70, 220, 255, 0.06);
                border-radius: 14px;
                padding: 0px;
            }
        """)
        panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(0)

        label = QLabel("⚡ HOLOGRAPHIC CORE")
        label.setStyleSheet("""
            QLabel {
                color: rgba(70, 220, 255, 0.10);
                font-size: 7px;
                font-weight: 300;
                letter-spacing: 4px;
                font-family: 'Segoe UI', sans-serif;
                padding: 2px 8px;
            }
        """)
        layout.addWidget(label)

        self.holographic_core = HolographicCore()
        self.holographic_core.message_signal.connect(self._on_core_message)
        self.holographic_core.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.holographic_core, stretch=1)

        return panel

    def _create_chat_panel(self):
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: rgba(6, 10, 20, 0.5);
                border: 1px solid rgba(70, 220, 255, 0.06);
                border-radius: 14px;
            }
        """)
        panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(6)

        # Chat header
        chat_header = QHBoxLayout()
        chat_title = QLabel("💬 CHAT")
        chat_title.setStyleSheet("""
            QLabel {
                color: rgba(70, 220, 255, 0.18);
                font-size: 8px;
                font-weight: 400;
                letter-spacing: 4px;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        chat_header.addWidget(chat_title)
        chat_header.addStretch()

        self.doc_badge = QLabel("📄 0")
        self.doc_badge.setStyleSheet("""
            QLabel {
                color: rgba(140, 180, 220, 0.2);
                font-size: 8px;
                font-family: 'Segoe UI', sans-serif;
                padding: 1px 8px;
                border: 1px solid rgba(70, 220, 255, 0.04);
                border-radius: 8px;
            }
        """)
        chat_header.addWidget(self.doc_badge)
        
        # Speaking indicator
        self.speaking_indicator = QLabel("🔇")
        self.speaking_indicator.setStyleSheet("""
            QLabel {
                color: rgba(140, 180, 220, 0.15);
                font-size: 12px;
                padding: 1px 4px;
            }
        """)
        chat_header.addWidget(self.speaking_indicator)
        
        layout.addLayout(chat_header)

        # ---- CHAT DISPLAY (Visible) ----
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background: rgba(6, 10, 20, 0.4);
                border: 1px solid rgba(70, 220, 255, 0.04);
                border-radius: 10px;
                color: rgba(180, 210, 240, 0.85);
                font-family: 'Consolas', 'Segoe UI', monospace;
                font-size: 12px;
                padding: 12px 14px;
                selection-background-color: rgba(70, 220, 255, 0.1);
            }
            QTextEdit:focus {
                border-color: rgba(70, 220, 255, 0.1);
            }
            QScrollBar:vertical {
                background: rgba(6, 10, 20, 0.5);
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: rgba(70, 220, 255, 0.12);
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(70, 220, 255, 0.2);
            }
        """)
        self.chat_display.setMinimumHeight(200)
        layout.addWidget(self.chat_display, stretch=2)

        # ---- PROGRESS BAR ----
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background: rgba(6, 10, 20, 0.3);
                border: 1px solid rgba(70, 220, 255, 0.04);
                border-radius: 4px;
                height: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #46dcff, stop:0.33 #ff6b6b, stop:0.66 #ffc850, stop:1 #be78ff);
                border-radius: 4px;
            }
        """)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # ---- DOCUMENT LIST ----
        doc_frame = QFrame()
        doc_frame.setStyleSheet("""
            QFrame {
                background: rgba(6, 10, 20, 0.3);
                border: 1px solid rgba(70, 220, 255, 0.03);
                border-radius: 8px;
                max-height: 44px;
            }
        """)
        doc_layout = QHBoxLayout(doc_frame)
        doc_layout.setContentsMargins(6, 2, 6, 2)

        doc_label = QLabel("📎")
        doc_label.setStyleSheet("color: rgba(140, 180, 220, 0.2); font-size: 9px;")
        doc_layout.addWidget(doc_label)

        self.doc_list = QListWidget()
        self.doc_list.setMaximumHeight(30)
        self.doc_list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                color: rgba(160, 200, 240, 0.4);
                font-family: 'Segoe UI', sans-serif;
                font-size: 8px;
                padding: 1px;
            }
            QListWidget::item {
                padding: 1px 4px;
                border-radius: 3px;
            }
            QListWidget::item:hover {
                background: rgba(70, 220, 255, 0.05);
            }
        """)
        doc_layout.addWidget(self.doc_list, stretch=1)

        clear_docs = QPushButton("✕")
        clear_docs.setMaximumWidth(18)
        clear_docs.setFixedHeight(18)
        clear_docs.setStyleSheet("""
            QPushButton {
                background: rgba(255, 70, 70, 0.05);
                color: rgba(255, 100, 100, 0.2);
                border: none;
                border-radius: 5px;
                font-size: 7px;
                padding: 1px;
            }
            QPushButton:hover {
                background: rgba(255, 70, 70, 0.15);
                color: rgba(255, 100, 100, 0.5);
            }
        """)
        clear_docs.clicked.connect(self._clear_documents)
        doc_layout.addWidget(clear_docs)

        layout.addWidget(doc_frame)

        # ---- INPUT AREA ----
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background: rgba(6, 10, 20, 0.4);
                border: 1px solid rgba(70, 220, 255, 0.06);
                border-radius: 10px;
                padding: 2px;
            }
            QFrame:focus-within {
                border-color: rgba(70, 220, 255, 0.15);
            }
        """)
        input_frame.setFixedHeight(44)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(8, 2, 4, 2)
        input_layout.setSpacing(4)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask Jarvis... (Enter to send, auto-speaks!)")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: rgba(200, 220, 240, 0.85);
                font-size: 12px;
                font-family: 'Segoe UI', sans-serif;
                padding: 6px 4px;
            }
            QLineEdit::placeholder {
                color: rgba(140, 180, 220, 0.2);
                font-style: italic;
            }
        """)
        self.input_field.returnPressed.connect(self._send_message)
        input_layout.addWidget(self.input_field)

        self.send_btn = QPushButton("➤")
        self.send_btn.setFixedSize(32, 32)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(70, 220, 255, 0.2),
                    stop:1 rgba(70, 220, 255, 0.05));
                color: rgba(160, 200, 240, 0.7);
                border: 1px solid rgba(70, 220, 255, 0.1);
                border-radius: 8px;
                font-size: 16px;
                font-weight: 300;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(70, 220, 255, 0.3),
                    stop:1 rgba(70, 220, 255, 0.1));
                border-color: rgba(70, 220, 255, 0.2);
                color: rgba(200, 230, 255, 0.9);
            }
            QPushButton:pressed {
                background: rgba(70, 220, 255, 0.2);
            }
            QPushButton:disabled {
                opacity: 0.3;
            }
        """)
        self.send_btn.clicked.connect(self._send_message)
        input_layout.addWidget(self.send_btn)

        layout.addWidget(input_frame)

        return panel

    def _create_status_bar(self):
        status = QFrame()
        status.setStyleSheet("""
            QFrame {
                background: rgba(6, 10, 20, 0.4);
                border: 1px solid rgba(70, 220, 255, 0.04);
                border-radius: 10px;
                padding: 2px;
            }
        """)
        status.setFixedHeight(30)
        layout = QHBoxLayout(status)
        layout.setContentsMargins(12, 2, 12, 2)

        self.status_label = QLabel("● READY")
        self.status_label.setStyleSheet("""
            QLabel {
                color: rgba(70, 220, 255, 0.3);
                font-size: 8px;
                font-weight: 300;
                letter-spacing: 2px;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        layout.addWidget(self.status_label)

        layout.addStretch()

        self.activity_label = QLabel("📋 0 msgs • 📄 0 docs • ⏱️ 00:00:00")
        self.activity_label.setStyleSheet("""
            QLabel {
                color: rgba(140, 180, 220, 0.15);
                font-size: 7px;
                font-family: 'Consolas', monospace;
                letter-spacing: 0.3px;
            }
        """)
        layout.addWidget(self.activity_label)

        hint = QLabel("⌨️ Ctrl+H")
        hint.setStyleSheet("""
            QLabel {
                color: rgba(140, 180, 220, 0.06);
                font-size: 7px;
                font-family: 'Segoe UI', sans-serif;
                padding: 0 6px;
            }
        """)
        layout.addWidget(hint)

        return status

    def _setup_shortcuts(self):
        self.focus_shortcut = QShortcut(QKeySequence("Ctrl+Shift+I"), self)
        self.focus_shortcut.activated.connect(self.input_field.setFocus)
        
        self.clear_shortcut = QShortcut(QKeySequence("Ctrl+Shift+C"), self)
        self.clear_shortcut.activated.connect(self._clear_chat)
        
        self.voice_shortcut = QShortcut(QKeySequence("Ctrl+Shift+V"), self)
        self.voice_shortcut.activated.connect(self._toggle_voice)
        
        self.upload_shortcut = QShortcut(QKeySequence("Ctrl+U"), self)
        self.upload_shortcut.activated.connect(self._upload_document)
        
        self.help_shortcut = QShortcut(QKeySequence("Ctrl+H"), self)
        self.help_shortcut.activated.connect(self._show_help)
        
        self.escape_shortcut = QShortcut(QKeySequence("Esc"), self)
        self.escape_shortcut.activated.connect(self._clear_input)
        
        self.stop_shortcut = QShortcut(QKeySequence("Ctrl+Shift+S"), self)
        self.stop_shortcut.activated.connect(self._stop_speaking)

    def _init_status(self):
        self._add_message("🤖", "Jarvis initialized. How can I help you?", "assistant")
        self._add_message("🗣️", "I can read responses aloud automatically!", "system")
        self._add_message("📄", "Upload documents to ask questions about them.", "system")
        self._add_message("🧠", "Select AI: Local (Ollama) or Nemotron (Cloud)", "system")
        
        if self.nemotron_api_key:
            self._add_message("✅", "Nemotron API key is set! You can use cloud AI.", "system")
        else:
            self._add_message("💡", "Click 'API Key' to set Nemotron key for cloud AI.", "system")
        
        if HAS_OLLAMA and self.ollama_client and self.ollama_client.is_available:
            self._add_message("✅", "Ollama connected: qwen2.5:3b (Local AI)", "system")
        else:
            self._add_message("⚠️", "Ollama not connected. Please ensure Ollama is running.", "system")
        
        if HAS_EDGE_TTS and HAS_PYGAME:
            self._add_message("🔊", "Natural voice TTS ready (Jenny Neural)", "system")

    def _show_help(self):
        help_text = """
        <h3 style='color: #46dcff;'>⌨️ Keyboard Shortcuts</h3>
        <table style='color: rgba(160, 200, 240, 0.8); font-size: 12px;'>
        <tr><td><b>Enter</b></td><td>Send message</td></tr>
        <tr><td><b>Ctrl+Shift+I</b></td><td>Focus input</td></tr>
        <tr><td><b>Ctrl+Shift+C</b></td><td>Clear chat</td></tr>
        <tr><td><b>Ctrl+Shift+V</b></td><td>Toggle voice</td></tr>
        <tr><td><b>Ctrl+Shift+S</b></td><td>Stop speaking</td></tr>
        <tr><td><b>Ctrl+U</b></td><td>Upload document</td></tr>
        <tr><td><b>Ctrl+H</b></td><td>Show help</td></tr>
        <tr><td><b>Esc</b></td><td>Clear input</td></tr>
        </table>
        <br>
        <h3 style='color: #46dcff;'>🤖 AI Models</h3>
        <table style='color: rgba(160, 200, 240, 0.8); font-size: 12px;'>
        <tr><td><b>Local (Ollama)</b></td><td>qwen2.5:3b - Free, offline</td></tr>
        <tr><td><b>Nemotron</b></td><td>NVIDIA Cloud AI - Faster, needs API key</td></tr>
        </table>
        """
        QMessageBox.information(self, "Help & Shortcuts", help_text)

    def _on_ai_changed(self, index):
        """Handle AI model change"""
        self.ai_model = self.ai_combo.currentData()
        
        if self.ai_model == "nemotron" and not self.nemotron_api_key:
            self._show_api_key_dialog()
            if not self.nemotron_api_key:
                # Revert to local
                self.ai_combo.setCurrentIndex(0)
                self.ai_model = "local"
                return
        
        model_name = "Nemotron (Cloud)" if self.ai_model == "nemotron" else "Local (Ollama)"
        self._add_message(f"🧠 Switched to {model_name}", "system")
        
        if self.ai_model == "nemotron":
            self.ai_combo.setStyleSheet("""
                QComboBox {
                    background: rgba(255, 200, 80, 0.05);
                    color: rgba(255, 200, 80, 0.6);
                    border: 1px solid rgba(255, 200, 80, 0.06);
                    border-radius: 8px;
                    padding: 4px 10px;
                    font-size: 9px;
                    font-family: 'Segoe UI', sans-serif;
                    min-width: 120px;
                }
                QComboBox:hover {
                    background: rgba(255, 200, 80, 0.12);
                    border-color: rgba(255, 200, 80, 0.12);
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox QAbstractItemView {
                    background: #0a121f;
                    color: rgba(160, 200, 240, 0.8);
                    border: 1px solid rgba(70, 220, 255, 0.06);
                    selection-background-color: rgba(70, 220, 255, 0.1);
                }
            """)
        else:
            self.ai_combo.setStyleSheet("""
                QComboBox {
                    background: rgba(90, 255, 170, 0.05);
                    color: rgba(90, 255, 170, 0.6);
                    border: 1px solid rgba(90, 255, 170, 0.06);
                    border-radius: 8px;
                    padding: 4px 10px;
                    font-size: 9px;
                    font-family: 'Segoe UI', sans-serif;
                    min-width: 120px;
                }
                QComboBox:hover {
                    background: rgba(90, 255, 170, 0.12);
                    border-color: rgba(90, 255, 170, 0.12);
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox QAbstractItemView {
                    background: #0a121f;
                    color: rgba(160, 200, 240, 0.8);
                    border: 1px solid rgba(70, 220, 255, 0.06);
                    selection-background-color: rgba(70, 220, 255, 0.1);
                }
            """)

    def _show_api_key_dialog(self):
        """Show API key dialog"""
        dialog = APIKeyDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            key = dialog.get_api_key()
            if key:
                self.nemotron_api_key = key
                self.api_btn.setText("🔑 Key Set ✅")
                self.api_btn.setStyleSheet("""
                    QPushButton {
                        background: rgba(90, 255, 170, 0.05);
                        color: rgba(90, 255, 170, 0.6);
                        border: 1px solid rgba(90, 255, 170, 0.06);
                        border-radius: 8px;
                        padding: 4px 10px;
                        font-size: 9px;
                        font-weight: 400;
                        font-family: 'Segoe UI', sans-serif;
                        letter-spacing: 0.3px;
                    }
                    QPushButton:hover {
                        background: rgba(90, 255, 170, 0.12);
                        border-color: rgba(90, 255, 170, 0.12);
                        color: rgba(90, 255, 170, 0.8);
                    }
                """)
                self._add_message("🔑", "Nemotron API key saved successfully!", "system")
                
                # Auto-switch to Nemotron if currently selected
                if self.ai_model == "nemotron":
                    self._add_message("🧠", "Nemotron is ready to use!", "system")
            else:
                self._add_message("⚠️", "No API key provided.", "warning")

    def _clear_input(self):
        self.input_field.clear()

    def _clear_chat(self):
        reply = QMessageBox.question(
            self, "Clear Chat", "Clear chat history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.chat_display.clear()
            self.message_count = 0
            self._update_activity_info()
            self._add_message("🗑️", "Chat cleared.", "system")

    def _toggle_voice(self):
        self.voice_enabled = self.tts_engine.toggle()
        self.voice_btn.setText(f"🔊 {'ON' if self.voice_enabled else 'OFF'}")
        self._add_message(f"🔊 Voice {'ON' if self.voice_enabled else 'OFF'}", "system")

    def _stop_speaking(self):
        self.tts_engine.stop()
        self.speaking_indicator.setText("⏹️")
        QTimer.singleShot(1000, lambda: self.speaking_indicator.setText("🔇"))

    def _upload_document(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Documents",
            "",
            "All Supported (*.txt *.pdf *.docx *.md);;Text Files (*.txt);;PDF Files (*.pdf);;Word Documents (*.docx);;Markdown (*.md)"
        )
        if not file_paths:
            return
        
        for file_path in file_paths:
            try:
                file_name = os.path.basename(file_path)
                ext = file_path.split('.')[-1].lower()
                content = ""
                
                if ext == 'txt' or ext == 'md':
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                elif ext == 'pdf':
                    try:
                        import PyPDF2
                        with open(file_path, 'rb') as f:
                            reader = PyPDF2.PdfReader(f)
                            content = ""
                            for page in reader.pages:
                                content += page.extract_text() + "\n"
                    except ImportError:
                        self._add_message("⚠️", f"PyPDF2 not installed. Can't read PDF: {file_name}", "warning")
                        continue
                elif ext == 'docx':
                    try:
                        import docx
                        doc = docx.Document(file_path)
                        content = "\n".join([para.text for para in doc.paragraphs])
                    except ImportError:
                        self._add_message("⚠️", f"python-docx not installed. Can't read DOCX: {file_name}", "warning")
                        continue
                else:
                    self._add_message("⚠️", f"Unsupported file type: {file_name}", "warning")
                    continue
                
                if not content.strip():
                    self._add_message("⚠️", f"No text extracted from: {file_name}", "warning")
                    continue
                
                self.doc_processor.add_document(file_path, content, ext)
                self._add_message("📄", f"Uploaded: {file_name} ({len(content)} chars)", "system")
                
            except Exception as e:
                self._add_message("⚠️", f"Error uploading {file_name}: {str(e)}", "error")
        
        self._refresh_document_list()
        self._update_activity_info()

    def _clear_documents(self):
        reply = QMessageBox.question(
            self, "Clear Documents", "Remove all uploaded documents?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.doc_processor.clear_all()
            self._refresh_document_list()
            self._update_activity_info()
            self._add_message("🗑️", "All documents cleared.", "system")

    def _refresh_document_list(self):
        self.doc_list.clear()
        docs = self.doc_processor.get_documents()
        for doc in docs:
            item = QListWidgetItem(f"📄 {doc['name']}")
            item.setData(Qt.ItemDataRole.UserRole, doc['id'])
            self.doc_list.addItem(item)
        self.doc_badge.setText(f"📄 {len(docs)}")
        self._update_activity_info()

    def _send_message(self):
        message = self.input_field.text().strip()
        if not message or self.is_processing:
            return
        
        self.input_field.clear()
        self._add_message("👤", message, "user")
        self.message_count += 1
        self._update_activity_info()
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.input_field.setEnabled(False)
        self.send_btn.setEnabled(False)
        self.is_processing = True
        
        self.worker = ChatWorker()
        self.worker.setup(
            message, 
            self.ollama_client, 
            self.doc_processor, 
            self.tts_engine,
            self.voice_enabled, 
            self.ai_model,
            self.nemotron_api_key
        )
        self.worker.response_ready.connect(self._on_response_ready)
        self.worker.status_update.connect(self._on_worker_status)
        self.worker.speaking_started.connect(self._on_speaking_started)
        self.worker.speaking_finished.connect(self._on_speaking_finished)
        self.worker.progress_update.connect(self._on_progress_update)
        self.worker.start()

    def _on_response_ready(self, response):
        self._add_message("🤖", response, "assistant")
        self.input_field.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.is_processing = False
        self.input_field.setFocus()

    def _on_worker_status(self, status, color_hex):
        if status == "speaking":
            self.holographic_core.set_state("speaking")

    def _on_speaking_started(self):
        self.holographic_core.set_state("speaking")
        self.speaking_indicator.setText("🔊")
        self.speaking_indicator.setStyleSheet("color: #46dcff; font-size: 12px;")

    def _on_speaking_finished(self):
        self.holographic_core.set_state("idle")
        self.speaking_indicator.setText("🔇")
        self.speaking_indicator.setStyleSheet("color: rgba(140, 180, 220, 0.15); font-size: 12px;")
        self.progress_bar.setVisible(False)

    def _on_progress_update(self, value):
        self.progress_bar.setValue(value)

    def _add_message(self, sender, message, msg_type="assistant"):
        colors = {
            "user": "#90ffaa",
            "assistant": "#90c8f0",
            "system": "#46dcff",
            "warning": "#ffc870",
            "error": "#ff6b6b",
            "info": "#6ac8ff",
        }
        color = colors.get(msg_type, "#90c8f0")
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        formatted = f'<span style="color: rgba(140, 180, 220, 0.15); font-size: 7px;">[{timestamp}]</span> '
        formatted += f'<span style="color: {color}; font-weight: 600;">{sender}</span> '
        formatted += f'<span style="color: rgba(180, 210, 240, 0.85);">{message}</span>'
        
        self.chat_display.append(formatted)
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )

    def _update_activity_info(self):
        elapsed = datetime.now() - self.start_time
        hours = int(elapsed.total_seconds() // 3600)
        minutes = int((elapsed.total_seconds() % 3600) // 60)
        seconds = int(elapsed.total_seconds() % 60)
        doc_count = len(self.doc_processor.get_documents())
        self.activity_label.setText(
            f"📋 {self.message_count} msgs • 📄 {doc_count} docs • ⏱️ {hours:02d}:{minutes:02d}:{seconds:02d}"
        )

    def _update_performance(self):
        try:
            import psutil
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            ram_used = memory.used / (1024 * 1024)
            doc_count = len(self.doc_processor.get_documents())
            self.activity_label.setText(
                f"📋 {self.message_count} msgs • 📄 {doc_count} docs • "
                f"⏱️ {self._get_uptime()} • ⚡ CPU: {cpu:.0f}% • RAM: {ram_used:.0f}MB"
            )
        except:
            pass

    def _get_uptime(self):
        elapsed = datetime.now() - self.start_time
        hours = int(elapsed.total_seconds() // 3600)
        minutes = int((elapsed.total_seconds() % 3600) // 60)
        seconds = int(elapsed.total_seconds() % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _on_core_message(self, message, msg_type):
        if self._processing_core_message:
            return
        self._processing_core_message = True
        try:
            colors = {
                "system": "#46dcff",
                "info": "#90c8f0",
                "warning": "#ffc870",
                "error": "#ff6b6b",
                "user": "#90ffaa",
            }
            color = colors.get(msg_type, "#46dcff")
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted = f'<span style="color: rgba(140, 180, 220, 0.15); font-size: 7px;">[{timestamp}]</span> '
            formatted += f'<span style="color: {color}; font-weight: 600;">💠</span> '
            formatted += f'<span style="color: rgba(180, 210, 240, 0.85);">{message}</span>'
            self.chat_display.append(formatted)
            self.chat_display.verticalScrollBar().setValue(
                self.chat_display.verticalScrollBar().maximum()
            )
        finally:
            self._processing_core_message = False

    def closeEvent(self, event):
        self.tts_engine.stop()
        event.accept()


# ============================================================
# MAIN ENTRY POINT
# ============================================================

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Dark theme palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(6, 10, 20))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(160, 200, 240))
    palette.setColor(QPalette.ColorRole.Base, QColor(6, 10, 20))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(10, 20, 40))
    palette.setColor(QPalette.ColorRole.Text, QColor(160, 200, 240))
    palette.setColor(QPalette.ColorRole.Button, QColor(10, 20, 40))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(160, 200, 240))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(70, 220, 255))
    app.setPalette(palette)
    
    # Show API key dialog on startup
    api_key = ""
    dialog = APIKeyDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        api_key = dialog.get_api_key()
    
    window = JarvisWindow(api_key)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
"""
Text-to-Speech module for Jarvis
Uses edge-tts (Microsoft's free TTS service) with pygame for playback
"""

import asyncio
import threading
import queue
import tempfile
import os
import time
from typing import Optional

try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False
    print("⚠️ edge-tts not installed. Voice output will be disabled.")
    print("   Install with: pip install edge-tts")

try:
    import pygame
    pygame.mixer.init()
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False
    print("⚠️ pygame not installed. Voice output will be disabled.")
    print("   Install with: pip install pygame")

# Global state
_current_speaking = False
_speech_queue = queue.Queue()
_voice_thread = None
_stop_signal = False
_voice_enabled = True


def _speak_worker():
    """Background thread worker for TTS"""
    global _current_speaking, _stop_signal
    
    while not _stop_signal:
        try:
            # Get text from queue (timeout to check stop signal)
            text = _speech_queue.get(timeout=0.5)
            
            if not _voice_enabled:
                continue
                
            _current_speaking = True
            
            # Generate speech file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_path = temp_file.name
            temp_file.close()
            
            try:
                # Use edge-tts with a clear voice
                voice = "en-US-JennyNeural"  # Clear female voice
                rate = "-5%"  # Slightly slower for clarity
                pitch = "+0Hz"
                
                # Generate speech
                communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
                asyncio.run(communicate.save(temp_path))
                
                # Play audio
                if HAS_PYGAME and os.path.exists(temp_path):
                    pygame.mixer.music.load(temp_path)
                    pygame.mixer.music.play()
                    
                    # Wait for playback to finish
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                        if _stop_signal:
                            pygame.mixer.music.stop()
                            break
                            
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
            except Exception as e:
                print(f"⚠️ TTS error: {e}")
                
            finally:
                _current_speaking = False
                
        except queue.Empty:
            continue
        except Exception as e:
            print(f"⚠️ Worker error: {e}")


def speak_async(text: str):
    """Speak text asynchronously"""
    if not HAS_EDGE_TTS or not HAS_PYGAME:
        print("⚠️ TTS not available")
        return
    
    global _voice_thread
    
    # Start worker if not running
    if _voice_thread is None or not _voice_thread.is_alive():
        _voice_thread = threading.Thread(target=_speak_worker, daemon=True)
        _voice_thread.start()
    
    # Add to queue
    _speech_queue.put(text)


def speak_sync(text: str):
    """Speak text synchronously (blocks until done)"""
    speak_async(text)
    while is_speaking():
        time.sleep(0.1)


def is_speaking() -> bool:
    """Check if TTS is currently speaking"""
    return _current_speaking


def stop_speaking():
    """Stop current speech"""
    global _current_speaking, _stop_signal
    
    _stop_signal = True
    _current_speaking = False
    
    if HAS_PYGAME:
        try:
            pygame.mixer.music.stop()
        except:
            pass


def set_voice_enabled(enabled: bool):
    """Enable or disable voice output"""
    global _voice_enabled
    _voice_enabled = enabled
    
    if not enabled:
        stop_speaking()


def get_voice_status() -> dict:
    """Get current voice status"""
    return {
        "enabled": _voice_enabled,
        "speaking": _current_speaking,
        "queue_size": _speech_queue.qsize(),
        "tts_available": HAS_EDGE_TTS and HAS_PYGAME
    }


# Cleanup on exit
import atexit
@atexit.register
def _cleanup():
    global _stop_signal
    _stop_signal = True
    if HAS_PYGAME:
        try:
            pygame.mixer.quit()
        except:
            pass
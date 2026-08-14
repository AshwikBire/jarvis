"""
Ollama Client - Local LLM wrapper for Jarvis
"""

import requests
import json
import time
from typing import Optional, List, Dict


class OllamaClient:
    """Client for interacting with local Ollama instance"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model_name = "qwen2.5:3b"
        self.conversation_history: List[Dict[str, str]] = []
        self.is_available = False
        
        # Check if Ollama is running
        try:
            response = requests.get(f"{base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                self.is_available = True
                print("✅ Ollama connected successfully")
            else:
                print("⚠️ Ollama is running but returned unexpected response")
        except:
            print("⚠️ Ollama not reachable. Please ensure Ollama is running.")
            print("   Start with: ollama serve")
    
    def set_model(self, model_name: str):
        """Set the model to use"""
        self.model_name = model_name
        
    def chat(self, message: str) -> str:
        """Send a chat message and get response"""
        if not self.is_available:
            return "⚠️ Ollama is not available. Please ensure Ollama is running."
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })
        
        # Prepare request
        payload = {
            "model": self.model_name,
            "messages": self.conversation_history,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 500
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                assistant_message = data.get("message", {}).get("content", "")
                
                # Add assistant message to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                
                # Keep history manageable (last 20 messages)
                if len(self.conversation_history) > 20:
                    self.conversation_history = self.conversation_history[-20:]
                
                return assistant_message
            else:
                return f"⚠️ Error: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "⚠️ Request timed out. The model might be thinking too long."
        except requests.exceptions.ConnectionError:
            return "⚠️ Could not connect to Ollama. Please ensure it's running."
        except Exception as e:
            return f"⚠️ Error: {str(e)}"
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def list_models(self) -> List[str]:
        """List available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [m.get("name", "") for m in models]
            return []
        except:
            return []
    
    def get_model_info(self) -> dict:
        """Get information about the current model"""
        return {
            "model": self.model_name,
            "available": self.is_available,
            "history_length": len(self.conversation_history)
        }
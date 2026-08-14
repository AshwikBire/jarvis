"""
Cloud brain option: NVIDIA NIM API (free tier), running Nemotron.
OpenAI-compatible endpoint, so we just point the official openai SDK at it.

Setup: copy .env.example to .env in the project root and paste your free
NVIDIA API key there (get one at https://build.nvidia.com). This file reads
that key from the environment — the key itself never lives in this code.
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL_NAME = "nvidia/llama-3.3-nemotron-super-49b-v1"
BASE_URL = "https://integrate.api.nvidia.com/v1"

SYSTEM_PROMPT = (
    "You are Jarvis, a personal AI assistant. Your replies are converted to "
    "speech, so write the way you'd actually talk — short sentences, no "
    "markdown, no bullet lists, no headers, no asterisks. Default to 1-3 "
    "sentences unless the user asks for detail or a list.\n\n"
    "Be direct and confident — give your best answer first. Tone: calm, "
    "capable, a little witty, never robotic. Address the user as 'sir' "
    "only occasionally, not every reply."
)


class NemotronBrain:
    def __init__(self):
        self.api_key = os.environ.get("NVIDIA_API_KEY", "")
        self.client = OpenAI(base_url=BASE_URL, api_key=self.api_key) if self.api_key else None
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]

    def is_available(self) -> tuple[bool, str]:
        if not self.api_key or self.api_key.startswith("nvapi-your-key"):
            return False, (
                "No NVIDIA API key found.\n"
                "Copy .env.example to .env and paste your free key from build.nvidia.com"
            )
        try:
            # Lightweight check — a real call, but capped tiny, just to confirm auth works
            self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=1,
            )
            return True, "OK"
        except Exception as e:
            return False, f"NVIDIA API error: {e}"

    def ask(self, user_text: str) -> str:
        if not self.client:
            return "[No NVIDIA API key configured — see .env.example]"
        self.history.append({"role": "user", "content": user_text})
        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=self.history,
                temperature=0.5,
                top_p=0.9,
                max_tokens=300,
            )
            reply = response.choices[0].message.content
            self.history.append({"role": "assistant", "content": reply})
            if len(self.history) > 20:
                self.history = [self.history[0]] + self.history[-18:]
            return reply
        except Exception as e:
            return f"[Error talking to NVIDIA API: {e}]"

    def reset(self):
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]

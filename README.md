# Jarvis — Local AI Assistant (Stage 1–3, voice out)

Holographic-UI desktop assistant, no API keys, no cloud subscription costs.
Runs on Windows/Mac/Linux with just 8GB RAM (CPU-only is fine).

## What's included right now
- Advanced holographic HUD — layered rotating rings, radar ticks, hex-grid backdrop,
  scan-line sweep, particles, and a state-reactive core (color shifts for idle /
  listening / thinking / speaking) — pure PyQt6, no image assets
- **Live dashboard widgets**: digital clock + date, CPU/RAM radial gauges (real
  system stats via psutil), and a session panel showing uptime, message count,
  and last-reply latency
- Working text chat wired to a **local** LLM via Ollama (qwen2.5:3b), tuned for
  shorter, more confident, speech-friendly replies
- Jarvis speaks its replies out loud (edge-tts) with a live waveform animation
- A VOICE: ON/OFF toggle button if you want text-only at times
- Threaded throughout so the UI never freezes while thinking or speaking

## 📸 Screenshots

### Main Interface
<div align="center">
  <img src="screenshots/main-interface.png" alt="Jarvis Main Interface" width="100%">
  <br>
  <em>Jarvis - Holographic AI Assistant Interface</em>
</div>

### Important: one piece isn't fully offline
The brain (Ollama/qwen2.5:3b) is 100% local — no internet, no API key, ever.
**Voice output (edge-tts) needs an internet connection** — it's a free Microsoft
service with no key required, but it does call out to the internet each time
Jarvis speaks. If you want zero-internet operation end to end, ask and I'll swap
this for `pyttsx3` (fully offline, more robotic-sounding voice).

## Two AI brains, switchable
- **LOCAL** — Ollama + qwen2.5:3b, fully offline, free forever, slower on 8GB RAM
- **NEMOTRON** — NVIDIA's free cloud API, needs internet, much faster and sharper

Switch anytime with the BRAIN button on the left panel — each keeps its own
separate conversation history.

### One-time Nemotron setup (optional — skip if you only want local)
1. Get a free key at **build.nvidia.com** → sign up (no card needed) → Get API Key
   (starts with `nvapi-`)
2. Copy `.env.example` to `.env`:
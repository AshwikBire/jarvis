# 

# \- Advanced holographic HUD with rainbow rings, particles, scanline sweep, and state-reactive core

# \- Natural voice output using Microsoft Edge TTS (Jenny Neural)

# \- Dual AI brains: Local (Ollama/qwen2.5:3b) and Cloud (NVIDIA Nemotron)

# \- Document upload \& RAG (PDF, DOCX, TXT, MD)

# \- API key manager in UI for Nemotron

# \- 10+ keyboard shortcuts

# \- Real-time CPU \& RAM monitoring

# \- Responsive design

# 

# \---

# 

# \## Two AI Brains, Switchable

# 

# \- \*\*LOCAL\*\* — Ollama + qwen2.5:3b, fully offline, free forever

# \- \*\*NEMOTRON\*\* — NVIDIA's free cloud API, faster and sharper

# 

# Switch anytime with the AI dropdown menu in the header.

# 

# \### One-time Nemotron Setup (Optional)

# 

# 1\. Get a free key at \*\*build.nvidia.com\*\*

# 2\. Click the \*\*"API Key"\*\* button in the Jarvis interface

# 3\. Paste your key and save

# 4\. Select \*\*"Nemotron (Cloud)"\*\* from the AI dropdown

# 

# \---

# 

# \## Setup (One-time, \~10 Minutes)

# 

# \### 1. Install Ollama

# Download from \*\*https://ollama.com/download\*\* and install.

# 

# \### 2. Pull the Model

# ollama pull qwen2.5:3b

# 

# text

# 

# \### 3. Verify Ollama is Running

# ollama list

# 

# text

# 

# \### 4. Install Python Dependencies

# pip install -r requirements.txt

# 

# text

# 

# \### 5. Run Jarvis

# python src/main.py

# 

# text

# 

# \---

# 

# \## Keyboard Shortcuts

# 

# | Shortcut | Action |

# |----------|--------|

# | Enter | Send message |

# | Ctrl+Shift+I | Focus input |

# | Ctrl+Shift+C | Clear chat |

# | Ctrl+Shift+V | Toggle voice |

# | Ctrl+Shift+S | Stop speaking |

# | Ctrl+Shift+B | Toggle brain |

# | Ctrl+U | Upload document |

# | Ctrl+H | Show help |

# | Esc | Clear input |

# 

# \---

# 

# \## Project Structure

# jarvis/

# ├── src/

# │ ├── main.py # App entry point, UI layout

# │ ├── holographic\_widget.py # Holographic HUD visualizer

# │ ├── ollama\_client.py # Local LLM wrapper

# │ └── tts.py # Text-to-speech engine

# ├── data/ # Document storage for RAG

# ├── screenshots/ # Screenshots for README

# ├── requirements.txt

# ├── README.md

# └── .gitignore

# 

# text

# 

# \---

# 

# \## Troubleshooting

# 

# | Issue | Solution |

# |-------|----------|

# | Ollama not connected | Run `ollama serve` in terminal |

# | Voice not working | Install `edge-tts` and `pygame` |

# | Nemotron API error | Check API key in UI |

# | PDF reading fails | Install `PyPDF2` |

# | DOCX reading fails | Install `python-docx` |

# | PyQt6 install fails | On Linux: `sudo apt install libxcb-cursor0` |

# 

# \---

# 

# \## Updating an Existing Install

# 

# 1\. Replace your old `src/` folder with the new one

# 2\. Merge/replace `requirements.txt`

# 3\. Run: `pip install -r requirements.txt`

# 4\. Run as usual: `python src/main.py`

# 

# \---

# 

# \## Developer

# 

# \*\*Ashwik Bire\*\*

# 

# \- Portfolio: https://ashwikbire.github.io/My-Portfolio/

# \- LinkedIn: https://linkedin.com/in/ashwik-bire-b2a000186

# \- GitHub: https://github.com/AshwikBire

# 

# \---

# 

# \## License

# 

# MIT License

# 

# Copyright (c) 2024 Ashwik Bire




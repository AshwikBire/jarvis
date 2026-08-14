# \# J.A.R.V.I.S. — Advanced Holographic AI Assistant

# 

# \*\*J.A.R.V.I.S.\*\* (Just A Rather Very Intelligent System) — A holographic AI assistant with natural voice, document understanding, and dual AI brains.

# 

# \---

# 

# \## 📸 Screenshots

# 

# \### Main Interface

# !\[Main Interface](screenshots/main\_interface.png)

# 

# \### Holographic Core

# !\[Holographic Core](screenshots/holographic\_core.png)

# 

# \### Chat \& Voice

# !\[Chat Interface](screenshots/chat\_interface.png)

# 

# \### Document Upload \& RAG

# !\[Document Upload](screenshots/document\_upload.png)

# 

# \---

# 

# \## What's Included Right Now

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

# 📄 Complete .gitignore

# gitignore

# venv/

# \_\_pycache\_\_/

# \*.pyc

# .env

# data/

# .DS\_Store

# \*.log

# \*.mp3

# \*.wav

# \*.tmp

# \*.temp



# 📄 Complete requirements.txt

# txt

# PyQt6>=6.5.0

# psutil>=5.9.0

# requests>=2.31.0

# python-dotenv>=1.0.0

# edge-tts>=6.1.0

# pygame>=2.5.0

# PyPDF2>=3.0.0

# python-docx>=0.8.11



# 🚀 Complete One-Command Setup

# Run this in CMD from C:\\Users\\INDIA\\Desktop\\jarvis:

# 

# cmd

# cd C:\\Users\\INDIA\\Desktop\\jarvis \&\& mkdir screenshots \&\& git init \&\& git add . \&\& git commit -m "Initial commit: J.A.R.V.I.S. holographic AI assistant with voice, RAG, and dual AI" \&\& git branch -M main \&\& git remote add origin https://github.com/AshwikBire/jarvis.git \&\& git push -u origin main



# 📸 Add Screenshots

# Save these images in screenshots/ folder:

# 

# text

# screenshots/

# ├── main\_interface.png

# ├── holographic\_core.png

# ├── chat\_interface.png

# └── document\_upload.png



# ✅ Final Check

# Visit: https://github.com/AshwikBire/jarvis

# 

# You should see:

# 

# ✅ README.md with all sections

# 

# ✅ Screenshots visible in README

# 

# ✅ All source files

# 

# ✅ Requirements and .gitignore

# 

# Your fresh repository with visible screenshots is ready! 🚀

# 




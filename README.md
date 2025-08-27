# click2html

**Click → Capture → HTML**

A lightweight Python tool: **F2** starts/stops capture mode (each session gets its own folder).  
Every **mouse click** creates a **screenshot** of a small square around the click position (default 20×20 px) and logs the **coordinates**.  
**ESC** cleanly exits the program.  
Exports are saved per session as both **HTML** (with thumbnails) and **TXT**.

## Features
- **F2**: Toggle capture mode — each session creates a folder `capture_YYYYMMDD_HHMMSS/`
- **Mouse click**: saves image (`NNN_xxyy.png`) + coordinate
- **Per-session exports**:  
  - `index.html` (table with thumbnails & links to images)  
  - `coordinates_*.txt`
- **ESC**: Exit the script

## Installation
```bash
python -m venv .venv
# Windows:
. .venv/Scripts/activate
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt

# click2html

**Click → Capture → HTML**

A lightweight Python tool to capture mouse click coordinates with mini screenshots.  
Each capture session is saved in its own folder, including an **HTML report** with thumbnails and a **TXT log** of all coordinates.

---

## ✨ Features
- **F2**: Toggle capture mode — each session creates its own folder `capture_YYYYMMDD_HHMMSS/`
- **Mouse click**: saves image (`NNN_xxyy.png`) + coordinate
- **Per-session exports**:  
  - `index.html` — table with thumbnails and links to original images  
  - `coordinates_*.txt` — plain text log of coordinates and image file names
- **ESC**: Exit the script cleanly

---

## 📦 Installation
Clone the repository and set up dependencies:

```bash
git clone https://github.com/<your-username>/click2html.git
cd click2html

python -m venv .venv
# Windows:
. .venv/Scripts/activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
````

---

## ▶️ Usage

Run the script:

```bash
python click2html.py
```

Controls:

* **F2** → start/stop capture mode
* **ESC** → exit the program

Outputs are stored in a timestamped session folder, e.g.:

```
capture_20250827_203000/
├─ 001_1234x5678.png
├─ 002_1300x800.png
├─ coordinates_20250827_203000.txt
└─ index.html
```

Open `index.html` in your browser to view a table with all clicks, their coordinates, and linked thumbnails.

---

## ⚙️ Configuration

You can adjust settings at the top of `click2html.py`:

* `PADDING_PX` → default `10` (creates a 20×20 region around each click)
* `IMG_FORMAT` → `png` recommended (alternatively `jpg`, `gif`)
* `THUMB_PX` → size of thumbnails in HTML report (default `60`)
* `NUM_ZERO_PAD` → numbering style (e.g. `3` → `001`)

---

## 📝 Notes

* **Windows**: global hooks (pynput) may require admin rights.
* **Linux/Wayland**: depending on your compositor, global hooks/screenshots may be restricted.
* **Privacy**: screenshots include your screen content — only use on your own systems.
* **Games/Apps**: automated input or capture may violate their Terms of Service — use responsibly.

---

## 🙌 Credits

This tool is built with the help of these libraries:

* [pynput](https://pypi.org/project/pynput/) — global keyboard & mouse hooks
* [mss](https://pypi.org/project/mss/) — fast screenshot capture
* [Pillow](https://pypi.org/project/Pillow/) — image saving and processing

---

## 📄 License

MIT © 2025 Dave Jordan
See [LICENSE](LICENSE) for details.

```

#!/usr/bin/env python3
"""
Click-Capture with F2 toggle:
- F2: start/stop capture mode
- In capture mode: every mouse click saves coordinates + a 20x20 screenshot (±10 px)
- On stopping: writes coordinate list as TXT with timestamp
"""

from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional

from pynput import keyboard, mouse
from mss import mss
from PIL import Image

# -------------------------
# Configuration
# -------------------------
PADDING_PX = 25           # Pixels in each direction -> 50x50 region
IMG_FORMAT = "png"        # "png" recommended
NUM_ZERO_PAD = 3          # "001"
THUMB_PX = 60             # Thumbnail size in HTML report
# -------------------------

capture_mode = False

# Session-specific state (re-initialized for each F2 start)
clicks: List[Tuple[int, int, str]] = []   # (x, y, relative_img_path_in_session)
counter: int = 0
SESSION_TS: Optional[str] = None
SESSION_DIR: Optional[Path] = None
REPORT_PATH: Optional[Path] = None
TXT_PATH: Optional[Path] = None

def start_session():
    """Start a new capture session (creates its own folder)."""
    global clicks, counter, SESSION_TS, SESSION_DIR, REPORT_PATH, TXT_PATH
    clicks = []
    counter = 0
    SESSION_TS = datetime.now().strftime("%Y%m%d_%H%M%S")
    SESSION_DIR = Path.cwd() / f"capture_{SESSION_TS}"
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH = SESSION_DIR / "index.html"                     
    TXT_PATH = SESSION_DIR / f"coordinates_{SESSION_TS}.txt"     
    print(f"[INFO] Session started: {SESSION_DIR}")

def end_session():
    """End the current session and write exports."""
    if not SESSION_DIR:
        return
    write_txt()
    write_html_report()
    print(f"[OK] HTML report: {REPORT_PATH}")
    print(f"[OK] TXT file:   {TXT_PATH}")
    print(f"[INFO] Session ended: {SESSION_DIR.name}")

def toggle_capture():
    """Toggle capture mode on/off via F2."""
    global capture_mode
    capture_mode = not capture_mode
    if capture_mode:
        start_session()
        print("[INFO] Capture mode: ACTIVE")
    else:
        print("[INFO] Capture mode: INACTIVE")
        end_session()

def write_txt():
    """Write captured coordinates into a TXT file."""
    if not clicks or not TXT_PATH:
        print("[INFO] No coordinates captured. Skipping TXT export.")
        return
    with open(TXT_PATH, "w", encoding="utf-8") as f:
        for idx, (x, y, rel_img) in enumerate(clicks, start=1):
            num = str(idx).zfill(NUM_ZERO_PAD)
            f.write(f"{num} {x},{y} {rel_img}\n")

def write_html_report():
    """Write the HTML report with thumbnails + coordinates."""
    if not clicks or not REPORT_PATH or not SESSION_TS or not SESSION_DIR:
        return
    rows = []
    for idx, (x, y, rel_img) in enumerate(clicks, start=1):
        num = str(idx).zfill(NUM_ZERO_PAD)
        rows.append(f"""
        <tr>
          <td class="num">{num}</td>
          <td class="coords">{x},{y}</td>
          <td class="imgcell">
            <a href="{rel_img}" target="_blank" title="{rel_img}">
              <img src="{rel_img}" alt="{x},{y}">
            </a>
          </td>
        </tr>
        """)
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Capture Report {SESSION_TS}</title>
<style>
  body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 24px; }}
  h1 {{ margin: 0 0 8px; }}
  .meta {{ color: #555; margin-bottom: 16px; }}
  table {{ border-collapse: collapse; width: 100%; max-width: 900px; }}
  th, td {{ border: 1px solid #ddd; padding: 8px 10px; text-align: left; }}
  thead th {{ background: #f6f6f6; }}
  .num {{ width: 72px; font-variant-numeric: tabular-nums; }}
  .coords {{ width: 160px; font-variant-numeric: tabular-nums; }}
  .imgcell img {{
    width: {THUMB_PX}px; height: {THUMB_PX}px; object-fit: contain;
    image-rendering: pixelated;
    display: block;
  }}
</style>
</head>
<body>
  <h1>Capture Report</h1>
  <div class="meta">
    Session: <b>{SESSION_TS}</b> · Folder: <code>{SESSION_DIR.name}</code> · Capture size: {PADDING_PX*2}×{PADDING_PX*2}px (±{PADDING_PX})
  </div>
  <table>
    <thead>
      <tr><th>#</th><th>Coordinates (x,y)</th><th>Screenshot</th></tr>
    </thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
</body>
</html>
"""
    REPORT_PATH.write_text(html, encoding="utf-8")

def grab_square_around(x: int, y: int, half_size: int):
    """Grab a 2*half_size x 2*half_size square around the mouse click (e.g. 20x20)."""
    # mss must be opened in the current thread (important for Windows thread safety)
    with mss() as sct:
        mon0 = sct.monitors[0]
        screen_left = mon0["left"]
        screen_top = mon0["top"]
        screen_right = screen_left + mon0["width"]
        screen_bottom = screen_top + mon0["height"]

        left = x - half_size
        top = y - half_size
        width = half_size * 2
        height = half_size * 2

        # Clip to screen boundaries
        if left < screen_left:
            left = screen_left
        if top < screen_top:
            top = screen_top
        if left + width > screen_right:
            left = screen_right - width
        if top + height > screen_bottom:
            top = screen_bottom - height

        bbox = {"left": int(left), "top": int(top), "width": int(width), "height": int(height)}
        shot = sct.grab(bbox)
        img = Image.frombytes("RGB", (shot.width, shot.height), shot.rgb)
        return img

def on_click(x, y, button, pressed):
    """Mouse click handler."""
    global counter
    if not capture_mode or not pressed or not SESSION_DIR:
        return
    try:
        counter += 1
        num = str(counter).zfill(NUM_ZERO_PAD)
        img = grab_square_around(x, y, PADDING_PX)

        fname = f"{num}_{x}x{y}.{IMG_FORMAT.lower()}"
        out_path = SESSION_DIR / fname
        save_params = {"quality": 95} if IMG_FORMAT.lower() in ("jpg", "jpeg") else {}
        img.save(out_path, IMG_FORMAT.upper(), **save_params)

        # Save relative path (report lives in the same folder)
        rel_path = fname
        clicks.append((x, y, rel_path))
        print(f"[CAPTURE] {num}: ({x},{y}) -> {SESSION_DIR.name}/{rel_path}")
    except Exception as e:
        print(f"[ERROR] Capture at ({x},{y}): {e}")

def on_press(key):
    """Keyboard press handler."""
    try:
        if key == keyboard.Key.f2:
            toggle_capture()
        elif key == keyboard.Key.esc:   # ESC exits
            print("[INFO] ESC pressed – exiting …")
            return False  # Stop KeyboardListener
    except Exception as e:
        print(f"[ERROR] Keyboard handler: {e}")

def main():
    print("=== Click-Capture started ===")
    print("Key F2: toggle capture mode (separate folder per session)")
    print("ESC: exit\n")

    with mouse.Listener(on_click=on_click) as mouse_listener, \
         keyboard.Listener(on_press=on_press) as key_listener:
        try:
            mouse_listener.join()
            key_listener.join()
        except KeyboardInterrupt:
            pass
        finally:
            # If capture was active, still write exports before quitting
            if capture_mode:
                print("[INFO] Manual stop – writing exports …")
                end_session()
            print("=== Finished ===")

if __name__ == "__main__":
    main()

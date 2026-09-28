# 🖱️ Auto Mouse & Keyboard Macro v1.8

<div align="center">

**Automate your mouse and keyboard with scriptable, recordable macros**

[![Tests](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/actions/workflows/tests.yml/badge.svg)](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![GUI](https://img.shields.io/badge/GUI-Tkinter-2ea043)
![Library](https://img.shields.io/badge/pynput-1.8.2-orange)
![Platform](https://img.shields.io/badge/Platform-Windows-blue)

[📄 เอกสารภาษาไทย (README)](README.md) • [📘 คู่มือฉบับสมบูรณ์ (TUTORIAL)](TUTORIAL.md) • [📋 CHANGELOG](CHANGELOG.md)

</div>

---

## 📸 Screenshot

<div align="center">
<img src="images/screenshot.png" alt="Main window" width="640">
<br><em>Main window: icon menu + profile bar + command table + all controls</em>
</div>

---

## ✨ Features

| Feature | Details |
|---|---|
| 🔴 **RECORD** (F9) | Record mouse clicks and key presses in real time, with automatic delays |
| ▶️ **START / REPEAT** (F6) | Play enabled rows once, in a loop, or a fixed number of rounds |
| ⏹️ **STOP** (F8) | Instant stop — even in the middle of a long delay; releases stuck keys/buttons automatically |
| 🌐 **Global hotkeys** | F6/F8/F9/F10 work even when the window is not focused |
| 🖼️ **Image Click** | Find an image on screen (OpenCV) and click it — with search area `@x,y,w,h` and per-row confidence `#90` |
| 📸 **Snapshot tool** | Drag a rectangle on screen to capture .png templates for Image Click, right inside the app |
| 🎬 **16+ actions** | Click / double-click / modifier-click, scroll, move mouse (absolute/relative), save/restore cursor, type text (Thai supported), launch app, wait for image, beep, press/release/tap keys |
| 🎲 **Random delays** | Secs `1-3` = random 1–3 s per row; speed multiplier 0.25×–4×; return mouse to start |
| 👤 **Profiles** | Keep multiple scripts and switch instantly (`macro_profiles.json`) |
| ⏰ **Scheduler** | Play automatically every N minutes or daily at HH:MM |
| 📝 **Play log** | Every run is logged to `macro_log_<date>.txt` (daily rotation, auto-trimmed) |
| ⌨️ **CLI mode** | Run scripts without the GUI — great for Windows Task Scheduler |

---

## 🚀 Getting started

### Option A — download the .exe

Grab `AutoMouseMacro.exe` from the [Releases](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/releases) page and double-click. No Python needed.
(Or build it yourself: `build.bat`.)

### Option B — run from source

```bash
py -m pip install -r requirements.txt   # pynput (+ opencv-python & Pillow for Image Click)
py auto_macro.py
```

### Basic workflow

1. Click **RECORD** (F9) and do your thing — clicks and keys are written to the table.
2. Edit rows if needed: double-click any cell to edit, double-click X/Y to grab the current mouse position (3 s countdown), click the first column to enable/disable a row.
3. Click **START** (F6) to play once, **REPEAT** to loop, **STOP** (F8) to stop instantly.

**Hotkeys:** F6 play • F8 stop • F9 record • F10 toggle infinite loop — they work system-wide.

---

## 🖼️ Image Click

Put a `.png` file name in the **Additional** column of an *Image Click* or *Wait for Image* row:

```
button.png                    # search the whole screen, 80% confidence
button.png@100,200,300,80     # search only the area (100,200) 300×80 px
button.png@100,200,300,80#90  # same area, 90% confidence
button.png#65                 # whole screen, relaxed 65% confidence
```

Use the built-in **📸 snapshot button** (toolbar, rightmost) to capture a template: the app hides itself, you drag a transparent rectangle around the target, and save it as a .png.

Requires `opencv-python` and `Pillow` (everything else works without them).

---

## ⌨️ Command-line mode

```bash
py auto_macro.py script.json                 # play once
py auto_macro.py script.json --loop          # loop forever
py auto_macro.py script.json --loops 5       # 5 rounds
py auto_macro.py script.json --speed 2       # 2× speed
py auto_macro.py script.json --no-log        # disable play log
py auto_macro.py script.json --stop-file D:\stop.flg   # create this file = stop now
```

Stop from anywhere with **F8**/**Esc** (even unfocused), **Esc**/**q** in the CLI window, or **Ctrl+C**.
`--stop-file` lets other programs (or Task Scheduler chains) stop the macro by simply creating a file.

## 📝 Play log

Every run appends to `macro_log_<YYYY-MM-DD>.txt` (rotates daily, trimmed to 500 lines):

```
08:57:05 [START] เริ่มเล่น (CLI) ความเร็ว 1x รอบ=1 แถวที่เล่น=3  <- test.json
08:57:05 [STEP] รอบ 1 แถว 1/3 Press Key ctrl (0.0 วิ)  <- test.json
08:57:08 [STOP] หยุดโดยผู้ใช้ (F8/Esc/Ctrl+C)  <- test.json
```

- **GUI:** toggle it in **Settings** (remembered automatically)
- **CLI:** disable with `--no-log`
- Useful to audit what a script did, how long each row took, and when it was stopped

---

## 📂 Example scripts

Ready-to-load JSON scripts live in [`examples/`](../examples/) — from a safe auto-typer to an Image Click demo with a sample target image.

---

## 🧪 Tests & build

```bash
py -m unittest test_auto_macro -v    # 63 unit tests
build.bat                            # build dist/AutoMouseMacro.exe (PyInstaller)
```

CI runs all tests on Python 3.12/3.13/3.14 (Windows) on every push; pushing a tag like `v1.8` builds the .exe and publishes a GitHub Release automatically.

## 🛠️ Tech

Single-file Python 3.8+ app (`auto_macro.py`): Tkinter GUI + `pynput` for input control, optional `opencv-python` + `Pillow` for image matching. Full project guide for developers: [AGENTS.md](../AGENTS.md) (Thai).

## 📄 License

See the repository. Inspired by "Auto Mouse v1.3"; additional actions researched from automouseclick.com.

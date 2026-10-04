# 🖱️ Auto Mouse & Keyboard Macro v2.11.0

<div align="center">

# Automate your mouse + keyboard — record once, replay forever

**Free & open source. No ads, no sign-up, single .exe.**

### ⬇️ Download — no Python needed

[**📦 Get AutoMouseMacro.exe for Windows**](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/releases/latest)<br>
[All releases](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/releases) ·
[ภาษาไทย](README.md) · [🔌 Plugin marketplace](PLUGINS.md) ·
[🧩 Engine (embed in your own project)](../macro_engine.py)

</div>

<div align="center">

**Automate your mouse and keyboard with scriptable, recordable macros**

[![Tests](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/actions/workflows/tests.yml/badge.svg)](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![GUI](https://img.shields.io/badge/GUI-Tkinter-2ea043)
![Library](https://img.shields.io/badge/pynput-1.8.2-orange)
![Platform](https://img.shields.io/badge/Platform-Windows-blue)

[📄 เอกสารภาษาไทย (README)](README.md) • [📘 Full guide EN (TUTORIAL)](TUTORIAL.en.md) •
[🔌 Plugin marketplace](PLUGINS.md) • [📋 CHANGELOG](CHANGELOG.md) • [🗺️ ROADMAP](ROADMAP.md)

</div>

---

## 📸 Screenshot

<div align="center">
<img src="images/screenshot.png" alt="Main window" width="640">
<br><em>Main window: icon menu + profile bar + command table + all controls</em>
</div>

<div align="center">
<img src="images/demo.gif" alt="Live demo GIF — cursor following a running script" width="320">
<br><em>Live play demo (recorded from the real program)</em>
</div>

---

## ✨ Features

| Feature | Details |
|---|---|
| 🔴 **RECORD** (F9) | Record mouse clicks and key presses in real time, with automatic delays |
| ▶️ **START / REPEAT** (F6) | Play enabled rows once, in a loop, or a fixed number of rounds |
| ⏹️ **STOP** (F8) | Instant stop — even in the middle of a long delay; releases stuck keys/buttons automatically |
| 🌐 **Global hotkeys** | F6/F8/F9/F10 work even when the window is not focused |
| ⚡ **Hot-profiles** (F1–F4) | Pick a script folder once, then F1–F4 loads the 1st–4th .json (sorted by name) and plays it instantly |
| 📜 **Log viewer** | Browse past play logs inside the app (📝 Log menu), per-day files |
| 🖼️ **Image Click** | Find an image on screen (OpenCV) and click it — with search area `@x,y,w,h` and per-row confidence `#90` |
| 📸 **Snapshot tool** | Drag a rectangle on screen to capture .png templates for Image Click, right inside the app |
| 🎬 **16+ actions** | Click / double-click / modifier-click, scroll, move mouse (absolute/relative), save/restore cursor, type text (Thai supported), launch app, wait for image, beep, press/release/tap keys |
| 🎲 **Shuffle & sampling** | Randomize row order and/or play only x% of rows — resampled every round |
| 🧙 **Record wizard** | Record → review → trial-play → save, all in one dialog |
| 📊 **Play statistics** | Daily 14-day chart + monthly totals (12 months) aggregated from logs |
| 💾 **Export/Import settings** | Move PCs or back up everything (rows + profiles + options) as one file from Settings |
| 🗄️ **Automatic backups** | Every app close snapshots settings into backups/ — keep 1–90 days (default 7) |
| 🌐 **Switchable UI language** | Thai / English from Settings — applies instantly |
| ❓ **Full in-app Help** | Scrollable guide covering every feature + a button that opens TUTORIAL |
| 🩺 **Startup self-check** | Verifies pynput / OpenCV / global hotkey / admin rights — shown in Settings |
| 🎲 **Random delays** | Secs `1-3` = random 1–3 s per row; speed multiplier 0.25×–4×; return mouse to start |
| 👤 **Profiles** | Keep multiple scripts and switch instantly (`macro_profiles.json`) |
| ⏰ **Scheduler** | Play automatically every N minutes or daily at HH:MM |
| 📝 **Play log** | Every run is logged to `macro_log_<date>.txt` (daily rotation, auto-trimmed) |
| ⌨️ **CLI mode** | Run scripts without the GUI — great for Windows Task Scheduler |
| 🔌 **Custom Action plugins** (v1.16) | Drop a small .py into `plugins/` and it becomes a new Action — see [plugins/README.md](../plugins/README.md) |
| 🔀 **If Image** (v1.17) | Condition: image **not found** → skip the next N rows (N = the row's Repeat value). Supports Search Area & threshold like Image Click |
| 🔀 **Else If Image** (v1.18) | Two-way condition: If found → play group A then skip group B; not found → play group B |
| 🎨 **Wait for Pixel Color** (v1.18) | Wait until point (x,y) matches a color (`300,300 #ffffff`) before continuing |
| 🔁 **If Loop** (v1.21) | Round condition: Additional = round number N (e.g. `3`) → from round N on, skip the next N rows (Repeat) — great for "first round setup, skip afterwards" |
| 🕐 **If Time** (v1.21) | Time condition: Additional = `HH:MM` (e.g. `22:30`) → past that time today, skip the next N rows (Repeat) |
| 🗂️ **Section header** (v1.21) | Right-click → "Convert to Section header": a group label row that never plays or counts — long scripts stay readable |
| 📁📂 **Collapse/expand groups** (v1.22) | Right-click a header → collapse: members disappear from the table but **still play normally**; press again to expand in the exact original order |
| 🎨 **Row colors by category** (v1.22) | Conditions = light yellow · keyboard = light purple · special actions = light blue · mouse rows keep the zebra stripes — spot groups at a glance |
| ⏱ **Per-action stats** (v1.18) | Stats shows the top 5 time-consuming Actions — spot your script's bottleneck instantly |
| 🔍 **Find / Undo / Paste** (v1.17) | `Ctrl+F` search rows · `Ctrl+Z` undo delete (50 levels) · 📋 Paste menu inserts JSON rows from clipboard |
| 🎨 **If Pixel Color** (v2.5) | Point-color condition: match → continue, mismatch → skip N rows (append `Ns` to re-check before deciding) |
| 🎨 **Read Pixel Color** (v2.5) | Read a point's color into a variable: Additional `name x,y` → `{name}` |
| 🔢 **If Variable** (v2.5) | Compare variables: numbers (`n > 5`) or text (`code = A-1`, `msg ~ failed`) — Repeat = rows to skip when false |
| 🖱️ **Drag to reorder** (v2.5) | Press-hold and drag rows; drop above/below by cursor half; autoscroll; drag the whole selection; multi-select + Delete (v2.4); Alt+↑/↓ |
| 🔁 **Undo/Redo + Notes** (v2.5) | `Ctrl+Z`/`Ctrl+Y` covers cell edits too · a Note column per row · find & replace-all in `Ctrl+F` |
| 🛡 **Self-healing hotkeys** (v2.4) | Dead global-hotkey listeners are detected and restarted automatically — STOP must always work |
| ⏱ **Safety timeout** (v2.4) | Auto-stop after N minutes of playing (1–720) — Settings or CLI `--max-minutes` |
| 🔀 **If Image retry window** (v2.4) | Append `5s` to Additional = re-check for up to 5 s before deciding (fixes screens that are still loading) |
| 📤 **Export .bat/.sh** (v2.3) | Generate double-click launchers next to your saved script (Windows/Linux/macOS) |
| 🔎 **`--validate`** (v2.4) | Validate every row and report problems without playing — before the overnight run |
| 🔌 **Plugins v2.5** | New built-ins: Screenshot · Toast (Windows 10/11) · Write Log · Ask Input — plus `ctx["vars"]` to share script variables |
| 🔗 **AND conditions** (v2.6.0) | Append `&&` to any main condition — every part must be true: `img.png && 300,300 #ffffff && n > 5` (If Image/Pixel/Variable; understood by `--validate`) |
| 🧱 **Block Start/End** (v2.6.0) | Condition blocks + sub-loops: `if ...` skips the whole block when false, `until ... max N` repeats until true (8-level nesting, `--validate` checks pairs) |
| 🕒 **Per-time profiles** (v2.8.0) | Daily mode accepts several times, and each time may bind its own profile: `08:00, 12:30=morning job, 22:00` — at that time the profile is loaded and played automatically |
| 🔀 **AutoHotkey interop** (v2.7.0) | 🔀 menu: export the current script as .ahk / import .ahk files (Send/Click/MouseMove/Sleep/Run) into the table — pushes undo for you |
| 🔀 **.ahk variables both ways** (v2.8.0) | export `Set Variable` → `n := 5` / `If Variable` → `if (n > 5)` · import `n := 0` / `n += 2` / `if (n > 5)` back as rows |
| 🔌 **Community plugins** (v2.8.0) | new examples Random Pause / Counter / Open URL + an issue template for submitting plugins (criteria: docs/PLUGINS.md) |
| 🗜️ **Collapse blocks** (v2.8.1) | right-click a Block Start to collapse rows up to its matching Block End (same mechanism as Sections) — hidden rows still play and save correctly, nested collapse refused automatically |
| 🔍 **Validate button in GUI** (v2.8.1) | 🔀 menu → 🔍 Validate checks the whole script with the same engine as --validate and reports "row N: reason" in a dialog |
| 🚦 **START pre-validates** (v2.9.0) | pressing START runs the same validate_rows engine — on issues it asks to skip broken rows (they are really skipped), if every row is broken it refuses to play |
| 🗜️ **Collapse/expand all** (v2.9.0) | right-menu "Collapse all" folds every Section + block at once, "Expand all" restores the full table in the exact original order |
| 🔀 **.ahk blocks both ways** (v2.9.0) | export Block Start → `if (…) {` / `Loop, N {` / `} Until,` · import them back as Block Start/End rows — untranslatable image/color conditions become comments for the whole block, no stray braces |
| 🧪 **Dry-run (v2.10)** | 🧪 menu / CLI `--dry-run` — rehearse the whole script (conditions/blocks/delays/variables walk every path) without touching mouse/keys — real input rows are replaced with report lines |
| 📝 **Dry-run report file** (v2.10.1) | when a dry run ends it writes `dry_report_<date>.txt` with the full path + a count of what would run — a mid-run stop still saves the part walked (GUI + CLI) |
| 🔗 **Condition results as variables (v2.10)** | a trailing `>name` token on any condition row stores the result "1"/"0" — later rows use `{name}` or chain If Variable |
| 📦 **Batch runner (v2.10)** | CLI `--queue LIST.txt` plays many scripts back-to-back — validates every file first (one broken = whole queue cancelled) + per-file summary + [QUEUE] log |
| 🗂️ **Queue Bat** (v2.10.1) | 🗂️ menu picks a queue list file → writes .bat/.sh next to it — double-click plays the whole queue, no commands to type |
| 🗃️ **Log tools** (v2.11) | 📝 window adds "Archive old" (moves old logs/dry-reports into monthly `log_archive/` folders) / "Clear old" buttons and lists dry-run reports · automatic cleanup on close is configurable in Settings (keep 1–365 days, archive or delete) |

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
py auto_macro.py script.json --max-minutes 60  # safety timeout: auto-stop after 60 min
py auto_macro.py script.json --validate        # validate only, don't play (exit 1 on problems)
py auto_macro.py --version                     # print version
```

Stop from anywhere with **F8**/**Esc** (even unfocused), **Esc**/**q** in the CLI window, or **Ctrl+C**.
`--stop-file` lets other programs (or Task Scheduler chains) stop the macro by simply creating a file.
Custom Action **plugins** work in the CLI too — the header lists the loaded plugins.
**Image actions (v2.2)** — Image Click / If Image / Else If Image / Wait for Image all run in the
CLI now (previously skipped with a warning). `py engine_cli.py script.json --json-lines` reads a
script one JSON row per line (blank lines and `# comments` skipped).

**Watchdog mode** — `--watchdog` restarts the script automatically after it finishes (pause N seconds,
default 3), forever, until stopped: perfect for unattended monitoring jobs. Every restart is logged
as `[WATCHDOG]`. Combine with `--shuffle` / `--rows-pct` for non-repetitive runs.

## 📝 Play log

Every run appends to `macro_log_<YYYY-MM-DD>.txt` (rotates daily, trimmed to 500 lines):

```
08:57:05 [START] เริ่มเล่น (CLI) ความเร็ว 1x รอบ=1 แถวที่เล่น=3  <- test.json
08:57:05 [STEP] รอบ 1 แถว 1/3 Press Key ctrl (0.0 วิ)  <- test.json
08:57:08 [STOP] หยุดโดยผู้ใช้ (F8/Esc/Ctrl+C)  <- test.json
```

- **GUI:** toggle it in **Settings** (remembered automatically)
- **Browse history:** the **📝 Log** menu opens a built-in log viewer with per-day files
- **CLI:** disable with `--no-log`
- Useful to audit what a script did, how long each row took, and when it was stopped

## ⚡ Hot-profiles (F1–F4)

For workflows that switch scripts constantly:

1. **⚡ Hot-profile** menu → choose a folder containing your .json scripts (remembered)
2. Files are sorted by name — positions 1–4 map to **F1–F4**
3. Press **F1** to **F4** (works even unfocused) → that script loads and plays instantly
4. Stop with F8 as usual

Example: a folder with `a.json`, `b.json`, `c.json` → F1=a, F2=b, F3=c

---

## 📂 Example scripts

Ready-to-load JSON scripts live in [`examples/`](../examples/) — from a safe auto-typer to an Image Click demo with a sample target image.

---

## 🧪 Tests & build

```bash
py -m unittest test_auto_macro -v    # 370+ unit tests (+ test_e2e: 15 end-to-end)
py -m unittest test_e2e -v           # 15 end-to-end tests (real CLI runs)
build.bat                            # build dist/AutoMouseMacro.exe (PyInstaller)
```

CI runs all tests on Python 3.12/3.13/3.14 (Windows) on every push; pushing a tag like `v1.8` builds the .exe and publishes a GitHub Release automatically.

## 🛠️ Tech

Single-file Python 3.8+ app (`auto_macro.py`): Tkinter GUI + `pynput` for input control, optional `opencv-python` + `Pillow` for image matching. Full project guide for developers: [AGENTS.md](../AGENTS.md) (Thai).

## 📄 License

See the repository. Free & open source — no ads, no tracking; all scripts stay on your machine as plain .json files.
Use only for tasks you are authorized to automate (don't use it with games/services that prohibit bots).

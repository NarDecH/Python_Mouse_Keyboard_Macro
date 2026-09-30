# 📘 TUTORIAL (EN) — Auto Mouse & Keyboard Macro

> Complete English guide: from installation to complex scripts, with hands-on exercises.
> (Thai full version: [TUTORIAL.md](TUTORIAL.md) · this file mirrors it chapter by chapter)

---

## Chapter 1 — Install & first run

**Ready-made .exe (recommended):** grab `AutoMouseMacro.exe` from the
[Releases](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/releases/latest) page and
double-click — no Python needed.

**From source:**

```bash
py -m pip install -r requirements.txt   # pynput (+ opencv-python Pillow for Image Click)
py auto_macro.py                        # or run.bat
```

The main window is a table — one row = one event:
`enabled(☑) / # / X / Y / Button(Action) / Additional / Mins / Secs / Repeat`

Start safe: load `examples/01_auto_typer.json` (types text, never clicks) and press ▶ START.

---

## Chapter 2 — Recording your first script

1. Press **RECORD** (F9) — the listener captures every mouse click, keystroke and scroll.
2. Do your task once, then press F9 again (or STOP).
3. Review the rows: idle gaps become delays (Secs), scroll becomes Scroll Up/Down rows.
4. Fine-tune coordinates/delays by double-clicking any cell, then press **START** (F6).

---

## Chapter 3 — Playing options

| Control | Meaning |
|---|---|
| START / F6 | play enabled (☑) rows once |
| REPEAT | repeat until STOP |
| "Loop forever" / F10 | infinite loops |
| Loops box (0 = unlimited) | play the whole script N times |
| Speed 0.25×–4× | divide delays by this factor |
| Shuffle / Row % (v1.10) | random order / random subset each round |
| Restore mouse position | return the cursor to where START was pressed |

Stop channels — every one reacts within ~50 ms: **STOP button / F8 anywhere /
Esc / Ctrl+C**, and stuck keys or mouse buttons are released automatically.

---

## Chapter 4 — Actions reference

**Mouse:** Left/Right/Middle Click + Down/Up, Double Click, Ctrl/Shift/Alt+Click,
Scroll Up/Down (notches in Additional), Move Mouse, Move Mouse by Offset,
Save/Restore Cursor.

**Keyboard:** Tap/Press/Release Key — Additional accepts `a`, `5`, `space`, `enter`, `esc`,
`ctrl`, `shift`, `alt`, `win`, `f1`–`f12`, arrows, `pgup`, `prtsc`, VK codes like `27`,
or combos `Ctrl+W`, `Ctrl+Shift+T`, `Win+D` (v1.20.4). Physical keys are layout-independent.

**Extra (v1.5+):** Type Text (Thai + emoji, Unicode input — correct on any keyboard layout),
Launch App (`notepad.exe` or `https://...`), Beep, Set/Read Clipboard (v1.20),
Set Variable (v1.19), Image Click / Wait for Image (needs `opencv-python Pillow`),
Wait for Pixel Color (v1.18), If Pixel Color / Read Pixel Color / If Variable (v2.5),
Custom plugins (v1.16).

Search Area syntax for image actions: `button.png@100,200,300,400` = search only that box,
`#90` = threshold 90%.

---

## Chapter 5 — Conditions: If Image / Else If Image (v1.17–1.18)

Make the script **decide by itself**:

```text
row 1  If Image (btn.png)        ← check
rows 2-3 ...group A (played when found)
row 4  Else If Image (btn.png) Repeat = 2
rows 5-6 ...group B (played when not found)
```

- If Image **found** → play group A, the Else row then skips group B.
- **Not found** → group A is skipped (by the If row's Repeat), group B plays.
- One rule everywhere: **the Repeat column of a condition row = number of rows to skip.**

Wait for Pixel Color: Additional `x,y #RRGGBB`, e.g. `300,300 #ffffff` — waits (max 30 s,
`60s` token overrides) until the pixel matches, then continues.

**If Image retry window (v2.4):** append `Ns` to the Additional column, e.g. `img.png 5s` =
keep re-checking for up to 5 seconds before deciding — fixes pages that are still loading.

---

## Chapter 5B — Round/time conditions + Section headers (v1.21–1.22)

**If Loop** — Additional = round number `3`: from round 3 on, skip the next N rows
(Repeat). Perfect for "first round setup, skip afterwards".

**If Time** — Additional = `HH:MM` e.g. `22:30`: past that time today, skip N rows.
Use the **🕐 current time (+15 min)** toolbar button (v1.22) to fill it instantly.

**Section headers** — right-click → "Convert to Section header": a group label row that
never plays, never counts, never delays. **Collapse/expand groups** (v1.22): right-click a
header → collapse — members vanish from the table (header shows `(ย่อ N แถว)`) but they
**still play exactly the same**; expand again in the exact original order. Deleting a
collapsed header auto-expands it first — rows are never lost.

**Row colors (v1.22):** conditions = light yellow · keyboard = light purple · special
actions = light blue · mouse rows keep the zebra stripes — purely visual.

**Exercise:** run `py auto_macro.py examples/10_conditions_v21.json --loops 3` — on round 3
the "round 3+" row disappears: that's If Loop working.

---

## Chapter 6 — Variables and clipboard (v1.19–1.20)

- **Set Variable** — Additional `name = value`, `name += 5`, `name -= 5`.
- Use `{name}` in any X / Y / Additional / Mins / Secs / Repeat cell.
- **Set Clipboard / Read Clipboard** — put text on the clipboard or read it into a variable.
- Variables reset each time you press play.

Demo: `examples/08_variables.json`, `examples/09_clipboard.json`.

---

## Chapter 7 — Profiles and schedule

- **Profiles bar** — store several scripts and switch; autosave keeps them in
  `macro_profiles.json`.
- **Hot-profiles (v1.9)** — pick a folder, then F1–F4 loads the 1st–4th .json (sorted by
  name) and plays immediately.
- **Schedule** — play "every N minutes" or "daily at HH:MM"; a background thread pushes
  commands to the UI through a queue (thread-safe).

---

## Chapter 8 — CLI (command line)

```bash
py auto_macro.py script.json                 # play without opening the GUI
py auto_macro.py script.json --loops 5 --speed 2
py auto_macro.py script.json --loop          # infinite
py auto_macro.py script.json --watchdog 3    # restart when finished (v1.10)
py auto_macro.py script.json --max-minutes 60  # v2.4: safety timeout — auto-stop after 60 min
py auto_macro.py script.json --validate      # v2.4: validate every row, don't play (exit 1 on problems)
py auto_macro.py --version                   # print the version
py engine_cli.py script.json                 # v2.1: engine-only CLI (no GUI code at all)
py engine_cli.py script.jsonl --json-lines   # v2.2: one JSON row per line (skips #comments)
```

Stops: F8/Esc anywhere, Esc/q in the console, Ctrl+C, or `--stop-file PATH`
(create the file to stop).
**Image actions work in the CLI since v2.2** — Image Click, If Image, Else If Image and
Wait for Image use the same OpenCV search as the GUI (a missing image file is reported
and the run continues).

---

## Chapter 9 — Stats, log and backups

- Every play appends to `macro_log_YYYY-MM-DD.txt` (toggle in Settings, `--no-log` for CLI).
- **📊 Stats** — totals, daily bar chart (14 days), monthly totals, and the
  **Top 5 actions by total time** (v1.18) to find bottlenecks.
- **📝 Log viewer** — read logs in-app.
- **Automatic backup (v1.13)** — on every close the whole workspace + profiles + settings
  are saved to `backups/` and trimmed (default 7 days, configurable 1–90 in Settings).
- **Export/Import settings** — one file to move machines.

---

## Chapter 10 — Plugins (v1.16+)

Ten built-in plugins ship with the project: Sleep, Message Box, Play Sound, Webhook,
Multi Image Click, **Screenshot**, **Toast** (Windows 10/11 notification),
**Write Log** and **Ask Input** (asks the user for a value and stores it in a variable).

Drop a short Python file into `plugins/` — it appears in the Action dropdown:

```python
ACTION_NAME = "Open Notepad and wait"

def run(ctx, row):
    import os, time
    os.startfile("notepad.exe")
    time.sleep(1.5)
```

`ctx` provides `mouse`, `kb`, `log()`, `cfg`, `stop_check()` (return early on STOP) and
`ui` (msg/beep). Broken files are skipped — the program never crashes because of a plugin.
Full API and ideas: [PLUGINS.md](PLUGINS.md). The **🔌 plugins** toolbar button opens the
folder for you.

---

## Chapter 11 — Troubleshooting

| Symptom | Fix |
|---|---|
| Mouse doesn't move | Run as administrator (games/admin windows block input); run the 🧪 self-test in Settings |
| F6/F8 don't respond | Global hotkey status in Settings; see the log note about `GlobalHotKeys` — the app uses `keyboard.Listener` on purpose |
| Typed text is wrong | v1.20.2 types Unicode directly; check the target window has focus and finished loading |
| Image never found | Check Search Area, lighting/threshold; keep the template .png exactly as on screen |
| STOP "stuck" mid-delay | Should never happen — all delays sleep in 50 ms slices; report it with the log file |
| Stuck Ctrl / mouse button | STOP releases everything tracked by Press Key / Down automatically |

---

## Chapter 12 — Keyboard shortcuts

| Key | Action |
|---|---|
| F6 / F8 | play / stop (global — no focus needed) |
| F9 / F10 | record / toggle infinite loop |
| F1–F4 | hot-profile play 1–4 |
| Delete | delete selected row (multi-select with Ctrl/Shift+click, v2.4) |
| Ctrl+F / Ctrl+Z | find & replace-all / undo (50 levels) |
| Ctrl+Y | redo — cell edits are undoable too (v2.5) |
| Alt+↑/↓ | move the selected rows up/down (v2.5) |

### AND conditions (v2.5.4)

Append `&&` to any main condition's Additional — **every part must be true** to continue,
otherwise the next N rows (Repeat) are skipped, same single rule as before:

```text
If Image        img.png && 300,300 #ffffff && n > 5
                ← image found AND pixel color matches AND variable n > 5
If Pixel Color  300,300 #ffffff && 400,400 #000000   ← both points must match
If Variable     n > 5 && code = A-1                  ← several variables at once
```

Timeout tokens still work with `&&` (`img.png 5s && ...` re-checks for 5 s before deciding),
and `--validate` understands `&&` and reports every broken part per row.

---

## Chapter 13 — What's new in v2.x (quick summary)

### 13.1 Extensions (v2.0–2.3)
- **Engine separated from the GUI** — `macro_engine.py` is pure Python (no Tk); a slim
  `engine_cli.py` runs it directly · the 🔌 toolbar button opens the plugins folder ·
  plugin marketplace: [PLUGINS.md](PLUGINS.md).
- **📤 Export Bat menu** — generates `.bat` (Windows) + `.sh` (Linux/macOS) launchers next to
  your saved script; double-click to run (extra args like `--loop` are forwarded).

### 13.2 Robustness (v2.4)
- **Self-healing global hotkeys** — a dead listener is detected and restarted automatically
  (rate-limited to once per 10 s) and announced in the statusbar/log. Principle: STOP must always work.
- **Safety timeout** — Settings "auto-stop after N minutes" (1–720) · CLI: `--max-minutes N`.
- **If Image retry window** — append `Ns` (e.g. `img.png 5s`) to re-check before deciding.
- **Multi-select rows** — Ctrl/Shift+click then Delete removes the whole set (undoable).
- **Schedule picks a profile** — choose which profile to load at play time; Settings shows the current appointment.
- **`--validate`** — report every problematic row without playing (exit code 1 when found).
- Template cache for image search — 1000 rounds no longer read the .png 1000 times.

### 13.3 Full conditions + an easier table (v2.5)
- **If Pixel Color** — point-color condition: match → continue, mismatch → skip N rows (`Ns` re-checks first).
- **Read Pixel Color** — store a point's color into `{name}` (Additional: `name x,y`).
- **If Variable** — compare variables: numbers (`round > 5`) or text (`code = A-1`, `msg ~ failed`).
- **Image Click sets `{img_x}/{img_y}`** — click relative to the found image.
- **`rand a-b` in Set Variable** — `luck = rand 1-100` stores a random number.
- **Drag to reorder** — press-hold and drag; drop above/below by cursor half; autoscroll;
  drag the whole selection; dropping on a collapsed group is blocked.
- **Redo (Ctrl+Y) + full undo** — cell edits are undoable · a **Note column** per row ·
  **find & replace-all** in Ctrl+F.
- **4 new plugins** — Screenshot · Toast · Write Log · Ask Input (`ctx["vars"]` shares script variables).

---

*Guide for code v2.5.4 · Complete Thai tutorial with more exercises: [TUTORIAL.md](TUTORIAL.md) ·
Project docs: [README.md](README.md) · Plugin marketplace: [PLUGINS.md](PLUGINS.md)*

# 📘 TUTORIAL (EN) — Auto Mouse & Keyboard Macro

> Complete English guide: from installation to complex scripts, with hands-on exercises.
> (Thai full version: [TUTORIAL.md](TUTORIAL.md) · this file mirrors it chapter by chapter)
> Other translations: [中文](TUTORIAL.zh.md) · [日本語](TUTORIAL.ja.md)

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
- **Schedule** — play "every N minutes" or "daily at HH:MM"; daily accepts several
  comma-separated times like `08:00,12:30,22:00` (v2.7.0); a background thread pushes
  commands to the UI through a queue (thread-safe).
- **Per-time profiles (v2.8.0)** — a daily entry may bind its own profile with
  `HH:MM=profile`, e.g. `08:00, 12:30=morning job, 22:00` — at that time the profile is
  loaded and played automatically; times without `=` use the default profile.

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

### AND conditions (v2.6.0)

Append `&&` to any main condition's Additional — **every part must be true** to continue,
otherwise the next N rows (Repeat) are skipped, same single rule as before:
(v2.14.1: a skip consumes only straight-line rows — Section/Block Start/End never eat one,
and a block jump/loop-back always cancels any pending skip)

```text
If Image        img.png && 300,300 #ffffff && n > 5
                ← image found AND pixel color matches AND variable n > 5
If Pixel Color  300,300 #ffffff && 400,400 #000000   ← both points must match
If Variable     n > 5 && code = A-1                  ← several variables at once
```

Timeout tokens still work with `&&` (`img.png 5s && ...` re-checks for 5 s before deciding),
and `--validate` understands `&&` and reports every broken part per row.

### Block Start / Block End — condition blocks & sub-loops (v2.6.0)

The `🔷 Block Start` → `🔷 Block End` action pair wraps a group of rows (nesting up to 8) —
put the command in Block Start's Additional:

```text
(empty)            always open — just for structure
if img.png         condition false → skip the whole block (matching End found by bracket counting)
if n > 5           variable / pixel / image conditions, && mixing works
until img.png      sub-loop: after End, jump back and repeat until the image is found (max 1000)
until n >= 5 max 20  loop until n >= 5, at most 20 rounds — then leave the loop
max 10             no condition — repeat the block body 10 times
```

Unlike If Image you **never count rows** — skip/back-jumps follow the Start/End pair, so editing
rows inside the block is safe. `--validate` checks pair matching, nesting depth and Additional
formats before playing. Try the demo: `py auto_macro.py examples/12_blocks.json`
(skip-block / count-to-5 sub-loop / 2-level nesting — beeps only, safe).

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

- **Collapse blocks (v2.8.1)** — right-click a Block Start row to collapse the rows between
  it and its matching Block End (same mechanism as Sections) — hidden rows still play and
  save correctly; nested collapse is refused automatically.
- **Validate button (v2.8.1)** — the 🔍 Validate menu checks the whole script with the same
  engine as `--validate` and reports "row N: reason" in a dialog, no CLI needed.

---

- **START pre-validates (v2.9.0)** — pressing START runs `validate_rows` automatically:
  on issues it asks "play skipping broken rows?" — confirm = only valid rows play, decline =
  go back and fix; if every row is broken nothing plays at all (no more silent failures).
- **Collapse all / Expand all (v2.9.0)** — right-menu: "Collapse all" folds every Section +
  block at once (outer groups swallow inner ones top-down); "Expand all" walks back until the
  table is fully restored in the exact original order.
- **.ahk block support both ways (v2.9.0)** — export: `if n > 5` → `if (n > 5) { … }`,
  `max 3` → `Loop, 3 {`, `until n >= 5` → `Loop { … } Until, n >= 5` (conditions join with
  `&&`, text search `~` → `InStr()`); image/color conditions that can't translate become a
  comment for the whole block — no stray braces, the .ahk always runs · import converts all
  three forms back to Block Start/End rows.

- **Dry-run (v2.10)** — 🧪 menu or `--dry-run`: walks the whole script like a real run
  (conditions/blocks/delays/variables follow every path) but real input rows are replaced
  with "DRY-RUN: would click…" reports — rehearse before an overnight job with zero risk.
- **Condition results as variables (v2.10)** — append `>name` to any condition row
  (`img.png >found`, `n > 3 >res`): the result ("1"/"0") is stored in that variable and
  later rows use `{found}` or chain If Variable — condition chaining, no new actions.
- **Batch runner (v2.10)** — `py auto_macro.py --queue list.txt`: one script path per line,
  every file validated before anything plays (a broken file cancels the whole queue), files
  run back-to-back without keypresses, per-file summary at the end + [QUEUE] log entries.
- **Log notes skipped rows (v2.9.1)** — rows that fail START pre-validation (or CLI up-front
  validation) are written to the log as [SKIP] lines "row N skipped (reason)" plus a
  played/skipped summary — overnight jobs can be reviewed to see exactly what ran ·
  scheduled sessions skip broken rows automatically without a dialog (previously the
  3 a.m. run sat waiting for someone to click OK).

---

## Chapter 14 — Deep dive: Dry-run · condition results as variables · batch runner (v2.10)

### 14.1 Dry-run — rehearse before the real run (v2.10.1 adds a report file)

Principle: walk the script doing *everything except real input* — conditions, blocks, delays
and variables run for real along every path, but real input rows (clicks/keys/typing/launch
app/clipboard) are replaced with a "DRY-RUN: would …" report — mouse/keyboard never move.

When to use it: complex nested conditions where you want to know which path will fire, and
before releasing overnight jobs (schedule/watchdog) — rehearse first, no risk while asleep.

How: **🧪 Dry-run** menu (GUI) or `py auto_macro.py script.json --dry-run` (CLI).

**New in v2.10.1 — a report file:** when the dry run ends the program writes a copy of the
whole path to `dry_report_<date>.txt` next to the program, with a summary of what would run
— great for long jobs on small screens (a mid-run stop still saves the path walked so far,
marked as stopped). Wait for Image/Pixel report instantly instead of waiting (dry runs stay
fast); plugins are reported instead of executed; the report never crashes the program.

### 14.2 Condition results as variables — the `>name` token

Any condition row (If Image / If Pixel / If Variable / If Loop / If Time) accepts a trailing
`>name` in Additional — the result "1" (true) / "0" (false) is stored in that variable:

| Condition row | Additional | Result |
|---|---|---|
| If Image | `green.png >found` | found → `{found}`=1, missing → `{found}`=0 |
| If Pixel Color | `300,300 #ffffff >colorok` | `{colorok}`=1 when it matches |
| If Variable | `n > 3 >past` | `{past}`=1 when n>3 |
| If Loop | `10 >ten` | loop ≥ 10 → `{ten}`=1 |

Then chain: another **If Variable** (`found = 1`) to branch, a **Block Start** condition
(`if found = 1`) to wrap a whole section, or quote it in text (`Result: {found}`).
Names must not be `on`/`of`/`and`; the token is stripped before image lookup; variables
reset every time a play starts.

### 14.3 Batch runner — `--queue` + the 🗂️ Queue Bat button (v2.10.1)

Create `list.txt` (one script path per line, `#` comments skipped) and run
`py auto_macro.py --queue list.txt` — every file is validated first (a broken file cancels
the whole queue), files run back-to-back with no keypress, and a per-file summary prints at
the end.

**New in v2.10.1:** the **🗂️ Queue Bat** menu picks a list file and writes `list.bat` +
`list.sh` next to it — double-click plays the whole queue, no commands to type (relative
paths resolve against the list's folder, so move the folder together and it still works).

### Exercises (safe — nothing clicks on screen)

1. **Rehearse:** open `examples/14_dry_run_cond_vars.json` → 🧪 Dry-run → Beep/Message Box
   rows report "DRY-RUN: would…" while If Loop/variables run for real → afterwards open
   `dry_report_<date>.txt` and compare the "summary" line against the table.
2. **Store a condition result:** build 4 rows — If Loop `3 >done` (Repeat=1) · Beep ·
   If Variable `done = 1` (Repeat=1) · Beep — loops: 3 → rounds 1–2 skip the last Beep
   ({done}=0); round 3 skips the first Beep but plays the last one ({done}=1).
   Use a dry-run to check the path before pressing START.
3. **First queue:** 💾 Save two scripts → create `list.txt` with both names →
   🗂️ Queue Bat → double-click `list.bat` and read the per-file summary.

---

## Chapter 15 — Log tools (v2.11): monthly archive · clear old days

Play logs (`macro_log_<date>.txt`) and dry-run reports (`dry_report_<date>.txt`) rotate
daily, and today's log is trimmed to its last 500 lines — jobs that need a longer history
use the v2.11 log tools:

### 15.1 From the 📝 Log window
- **Archive old** — moves every log/dry-report except today's into `log_archive/`
  monthly folders named from the date in the file, e.g.
  `log_archive/2026-09/macro_log_2026-09-20.txt` — kept forever, never deleted
- **Clear old...** — deletes old files (today's kept) — always asks first and cannot be
  undone; when unsure, archive instead
- The file dropdown now lists dry-run reports too (logs only before)

### 15.2 Automate it (Settings)
- ☑ "Clean old logs on exit" + days (1–365) — closing the program handles files older
  than the limit (off by default, nothing touched until you enable it)
- ☑ "Archive to log_archive/ instead of deleting" — checked = safe, old files move
  instead of disappearing

⚠️ Today's file is never touched by either mode — it is still being written.

---

## Chapter 16 — GUI Queue Runner (v2.12): play many files inside the app, live monitor

Chapter 14 played queues through the CLI `--queue` / the 🗂️ Queue Bat button in a
console — v2.12 adds the **📑 Run Queue** menu so the queue runs inside the program
with a live view of every file, no console needed.

### 16.1 Start a queue
1. Prepare a `.txt` list in the same format (one script path per line, skip `#` and
   blank lines, relative paths resolved against the list's folder) — the same list you
   would feed to `--queue`/Queue Bat works as-is
2. Press 📑 Run Queue → pick the list → the window lists every file with status
   "รอเล่น (waiting)"
3. Press **▶ เริ่มเล่นคิว (Play queue)** — every file is validated first (a broken file
   cancels the whole queue without playing a single row, exactly like the CLI), then
   files play one by one: the current row turns blue, the label above shows the current
   file, and the box below streams the CLI output live (last 200 lines kept)

### 16.2 Per-file status
| Status | Meaning |
|---|---|
| กำลังเล่น… (blue) | this file is running |
| จบครบ ✔ (green) | finished every row on its own |
| ถูกหยุด (orange) | stopped mid-file |
| พบปัญหา (exit N) (red) | ended with a problem — the queue still continues to the next file |
| ตรวจไม่ผ่าน / ไม่พบไฟล์ (red) | pre-play validation failed — whole queue cancelled |
| — (ยกเลิก) (grey) | skipped because the whole queue was stopped |

### 16.3 Two stop levels
- **⏹ หยุดไฟล์นี้ (Stop this file)** — stops the current file and **continues with the
  next one** (built on the CLI's `--stop-file`, with a dedicated stop file per queue
  entry so other files are never affected)
- **⏹⏹ หยุดทั้งคิว (Stop everything)** — stops the current file and cancels all
  remaining ones
- **F8/Esc while playing = stop the whole queue** — same meaning as the original CLI
  `--queue`; don't confuse it with "stop this file"

Tip: when the queue ends you can press ▶ again (all statuses reset) · closing the
window while playing asks first, then stops the whole queue for you · closing the
program while playing stops the queue automatically · the queue runs on its own thread
through the real CLI logic — you can still edit the table or load other scripts while
it plays

### Exercises (safe — nothing clicks on screen)

1. Build two scripts (Beep rows are enough) + a `list.txt` and play them through
   📑 Run Queue — watch each status go "รอเล่น" → "กำลังเล่น…" → "จบครบ ✔".
2. While the queue plays, press **⏹ หยุดไฟล์นี้** — confirm the first file shows
   "ถูกหยุด" but the second still finishes "จบครบ ✔", and the summary reads
   "สำเร็จ 1/2 (ถูกหยุด 1)".
3. Make a list that references a missing script and press ▶ — confirm nothing plays at
   all (validation first) and the missing file is marked "ไม่พบไฟล์".

---

## Chapter 17 — Plugin API v3: your own conditions (v2.13)

This chapter extends Custom Actions (v1.16) — besides writing plugins as **actions**, you
can now write them as **conditions**, covering spots where the built-in If Image/If Variable
still fall short.

### 17.1 Declare a condition in a plugin
The old pair is `ACTION_NAME` + `run(ctx, row)` — a condition declares another pair:

```python
# plugins/file_exists.py (ships with the program — a real example)
import os

CONDITION_NAME = "File Exists"

def check(ctx, row):
    """Return True/False — never raise · never touch mouse/keys (dry-run calls check)"""
    try:
        path = str(row.get("additional") or "").strip()
        return bool(path) and os.path.isfile(path)
    except Exception:
        return False
```

The single condition rule: **True = keep playing · False = skip N rows (N = Repeat)** ·
one file may declare both ACTION_NAME and CONDITION_NAME (names must differ) · the name must
not collide with built-in actions or other plugins (a colliding file is skipped with the
reason recorded — see `load_plugins.last_failed`)

### 17.2 Use it in a script, two ways
1. **The Action column** — double-click the Action cell and pick the condition name (added
   to the dropdown automatically); Additional = the condition's argument (`{variables}` are
   substituted before `check` runs), and a trailing `>name` stores the result as "1"/"0"
   like built-in conditions
2. **Block Start/End** — write `if File Exists C:\\work\\done.flag` in the Block Start
   Additional (mix with `&&`, e.g. `if File Exists f.txt && n > 3`) — a false condition
   skips the whole block

### 17.3 Good to know
- **Validation covered** — 🔍 Validate / `--validate` / the START check all accept condition
  plugin names
- **Dry-run runs it for real** — conditions already walk for real (Chapter 14) → `check` is
  really invoked, so write it read-only (files/screen colours/variables — no clicks/typing)
- **.ahk** — condition rows and blocks referencing a condition plugin are exported as whole-
  block comments (AHK can't express them — manage the block yourself there)
- Full guide + community plugin criteria: [PLUGINS.md](PLUGINS.md) · example:
  `examples/14_condition_plugin.json`

### Exercises (safe — nothing clicks on screen)

1. Open `examples/14_condition_plugin.json` and play it — the File Exists row pointing to
   "ไม่มีจริง.txt" (a missing file) skips the next Beep row (Repeat = 1).
2. Write your own condition plugin, e.g. `CONDITION_NAME = "After 6pm"` with a `check`
   comparing `time.localtime()` — put it in a Block Start as `if After 6pm` and try it
   morning vs evening.
3. Create a file with a duplicate name (e.g. CONDITION_NAME = "Left Click") and restart —
   confirm the program still opens fine and the colliding name never shows in the dropdown.

---

## Chapter 18 — Built-in condition plugins · 🧩 · --dry-report (v2.14)

### 18.1 The four conditions that ship with the program

The `plugins/` folder now includes four ready-to-use conditions — use them as an Action
or inside Block Start right away:

| Condition | Additional | True when |
|---|---|---|
| `File Exists` | file path | the file exists |
| `Internet Up` | (empty) or `host[:port]` and/or `Ns` | TCP connect succeeds (default 1.1.1.1:443, 2 s) |
| `Process Running` | process name, e.g. `chrome` | a process is running (tasklist/pgrep) |
| `Window Exists` | text in a window title, e.g. `Notepad` | a window whose title matches is open |

Mixable Block Start example: `if Internet Up && Process Running chrome` — the block plays only
when the network is up AND Chrome is running · on an OS without the tool (e.g. no xdotool) the
condition is simply False — the program never crashes.

### 18.2 The 🧩 button inserts a condition row

Once a condition plugin is loaded, the toolbar shows **🧩 เงื่อนไข plugin** — pick a name from
the dropdown, type the argument, press insert and a new row appears under the selected one
(Repeat = rows to skip when the condition is false, editable later) · Ctrl+Z undoable ·
the button only appears when a condition plugin is loaded.

### 18.3 CLI --dry-report PATH

`--dry-run` always wrote its report to `dry_report_<date>.txt` next to the program (v2.10.1) —
now you can choose your own:

```bash
py auto_macro.py script.json --dry-run --dry-report C:\reports\night_{date}.txt
```

- `{date}` = today's date (e.g. `night_2026-10-05.txt`) — perfect for overnight jobs
- Appends to the same file (each run is a new block separated by a blank line)
- Requires `--dry-run` — alone it warns and plays normally
- The in-app 🧪 Dry-run menu can pick the path too (path field + file picker — kept until the
  program closes)

Full example: `examples/15_system_conditions.json`

---

## Chapter 19 — Play a single section group (v2.15)

### 19.1 Right-click a header → "Play this group only"

Long scripts split into stages with Section headers (⬛) can now be tested/run one group at a time:
**right-click a Section header row → ▶ Play this group only** — the program plays just the enabled
(☑) rows inside that group, up to the next header, then stops. No more disabling other rows by hand.

- Runs through the **real player — the same path as START** — validate/STOP (F8)/row highlight/log
  /loop counting all apply
- **Collapsed rows inside the group still play** — collapse a group to save screen space and it
  still plays in full (the same promise since v1.22)
- A group with nothing enabled warns on the statusbar ("no enabled rows in this group") and
  exits quietly without starting the player

Exercise: build a script with 3 groups (prep/work/cleanup), two Beep rows each → right-click the
"work" header → play this group only → you hear only B1, B2.

### 19.2 CLI --only-section ชื่อ

```bash
py auto_macro.py script.json --only-section งาน
```

- Matches the header name exactly (case-sensitive) — prints the row range + count, then plays only
  that group
- Unknown name = warns "section not found" and **plays everything** as usual (never a silent
  empty run)
- Same pipeline as a full play — validate/STOP/`--max-minutes`/[SKIP] logging all apply, so it
  composes with `--queue`/watchdog, e.g. a queue where each file plays only its own group

### 19.3 Move whole groups (v2.15.1 — Group order)

Groups in the wrong order? No need to drag row by row — **right-click a header → "Move group up"
/ "Move group down"** swaps the whole [header + rows + collapsed stash rows] unit with the
neighbouring group in one step (or click a header and press **Alt+↑/↓**, or use the ▲▼ buttons —
same result).

- Collapsed stash rows always follow their own header — collapse a group, move it, rows stay
  inside the group
- A Block Start/End spanning the group (Start in one group, End in another) = refused with a
  warning, so blocks can't break
- Made a mistake? **Ctrl+Z** undoes · moving the first group up / last group down is a no-op

Exercise: create groups A/B/C, press "Move group up" on B twice → order becomes B, A, C —
then Ctrl+Z back to A, B, C.

## Chapter 20 — Script launchers · Event timeline · Community condition plugins (v2.16)

### 20.1 🚀 Script launcher pair — double-click = play (Issue #3)

Daily repeated tasks no longer need the main window:

1. Arrange the script and press **💾 Save**
2. Press the **🚀 Launcher** menu — the app writes a pair of files next to the script:
   - `script.bat` — picks the route for you: with `AutoMouseMacro.exe` in the same folder it
     starts the exe directly (the console flash disappears), otherwise it falls back to
     `py auto_macro.py` + pause so errors stay visible
   - `script.lnk` (Windows) — with an exe it points straight at the exe (program icon,
     cleanest), otherwise at the .bat
3. **Double-click the .lnk (or the .bat)** = that script plays immediately

- Append CLI args by editing the .bat, e.g. `--loop --speed 2` (full list:
  `py auto_macro.py --help`)
- Complements the existing 📤 Export Bat (bat/sh pair) and 🗂️ Queue Bat (pair for a queue
  list file)
- .lnk creation uses PowerShell (Windows only) — other OSes still get the .bat/.sh pair

Exercise: save a 2-Beep script as `morning.json` → 🚀 Launcher → double-click
`morning.lnk` → hear two beeps without ever opening the main app.

### 20.2 ⏱ Event timeline — debug nested conditions (Issue #4)

For scripts with If Image / If Variable / Block Start stacked in layers, the 📝 Log window
now has an **⏱ Event timeline (latest run)** button:

- Each row = one event: **time · result (▶ played / ⏭ skipped / ℹ other) · row i/N ·
  event · seconds** — green = played, orange = skipped (the reason sits in the event
  column, e.g. `If Loop · skip 2 rows`), grey = system info
- The **"Run:" dropdown** walks back through every run of the day, with a summary header
  like `13:02:11 — demo.json (played 12 · skipped 3)` — the latest run is preselected
- Data comes from the existing log (`parse_log_timeline` in the engine) — the Settings log
  switch works as before; with logging off there is no timeline (the log is the only source)

Exercise: a script with If Loop skipping 1 row + Beep, run once → open the timeline →
the If Loop row is orange with "skip 1 row" and Beep is green.

### 20.3 🔌 New community condition plugins (Issue #5)

Three conditions ship with the app (same rules as every condition plugin — use as an
Action or inside Block Start `&&`, `{vars}` supported, no new dependencies):

| Condition | Additional | True when |
|---|---|---|
| **Window Focused** | text in the window title, e.g. `Documents` | the **currently focused** window's title contains it (unlike Window Exists which scans every window) |
| **File Newer Than** | `report.csv > done.flag` or `setup.zip 60s` | the first file is newer than the second / the file was modified within the last N seconds |
| **HTTP Status** | `https://api.local/health 200 3s` | the URL answers with the expected code (no code = any 2xx; `3s` = 3-second timeout) |

Real example: before the main work group, use Block Start `if HTTP Status
https://api.local/health 200 && Process Running chrome` — API down or browser closed =
the whole group is skipped.

Exercise: create `a.txt` + `b.txt`, modify a.txt last → a File Newer Than row
`a.txt > b.txt` reports "condition true, continue" in the console/log — then check the
⏱ timeline to see the result in one window.

---

*Guide for code v2.16.0 · Complete Thai tutorial with more exercises: [TUTORIAL.md](TUTORIAL.md) ·
Project docs: [README.md](README.md) · Plugin marketplace: [PLUGINS.md](PLUGINS.md)*

# 📋 CHANGELOG (English) — Auto Mouse & Keyboard Macro

> English translation of [CHANGELOG.md](CHANGELOG.md) (Thai, the authoritative full history).
> Newer versions appear in the Thai original first — this file covers the recent releases.

## [2.18.0] — 2026-10-08

### 🎲 Group-level play order (closes [Issue #10](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/issues/10) — milestone v2.18)
- **Shuffle the order of section groups** — GUI: a **"Shuffle groups"** checkbox next to the
  existing row shuffle (remembered in conf, included in settings Export/Import) · CLI:
  `--shuffle-groups` — the program shuffles **whole group chunks** (header + member rows move
  together); rows inside a group keep their order — great for guessing games / randomized daily
  routines without rewriting the script · enabling both shuffles at once is not allowed
  (group shuffle wins)
- **Single engine source:** `select_groups(rows, names)` (pick groups by section name —
  duplicate names select every match, no names = all groups, input list is never mutated) +
  `shuffle_group_order(items)` (shuffles chunks while keeping each group intact — the leading
  chunk before the first header is its own chunk; uses module-level `random.shuffle` so tests
  can patch it easily) · `--only-section` used to accept a single name — now it **accepts
  several comma-separated groups**, e.g. `--only-section "Prep,Cleanup"` (a single name keeps
  the old behavior exactly; no group found = warn and play everything)
- Row highlighting stays correct while groups are shuffled (matched via `id()`, not position)

### 🧪 Group-level Dry-run (closes [Issue #11](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/issues/11))
- **Right-click a section header → "🧪 Dry-run this group"** — rehearse just that group:
  conditions/variables/blocks actually run while mouse/keyboard/clipboard rows are replaced with
  "DRY-RUN: would…" — nothing touches your mouse or keys (all v2.10 dry-run logic — skip counts,
  variables, conditions are computed for real) · results go to the same log as a normal dry-run
  with the source label "Dry-run group: name"
- Rehearse group by group before releasing a huge script — no need to dry-run the entire file

### 🐛 Latent v2.10 bug — dry-run wrote [STEP] lines to the log
- **Dry-run used to write [STEP] rows into macro_log just like real plays** — the log mixed in
  events that never happened, skewing ⏱ Timeline and 📊 Stats — DRY mode now writes no STEP
  lines (the walk itself already lives in the dry report, as v2.10 designed)

### 📚 Docs + tests
- **New example `examples/18_group_order.json`** — 3 Beep-only groups (Prep / Main / Cleanup),
  platform-neutral: passes `--validate`, plays for real, and is exercised with
  `--only-section "เตรียม,ล้าง"` and `--shuffle-groups`
- **12 new tests** (TestGroupPlayOrder 10 — engine select_groups/shuffle_group_order + CLI
  single-name/comma/not-found, TestGroupPlayOrderGui 2 — GUI group shuffle keeps chunks over 2
  rounds + group dry-run never touches the mouse) · 3 existing conf tests gained the
  `shuffle_groups` key (v2.11 lesson: a MagicMock fixture must set attrs the new code reads)
  → **568 unit + 20 E2E = 588**
- **OR (`||`) design** added to `docs/DESIGN-nested-if.md` (proposal: split `||` into sub-pieces
  then AND inside each — skip rules/validate/.ahk/row colors/`>name` tokens covered) —
  **collecting votes on [Issue #9](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/issues/9)**
  before implementing
- LANDING.html updated with v2.17.x + v2.18 features · ROADMAP ticks items 2/3 of the v2.18 plan

## [2.17.1] — 2026-10-07

### 🔊 Configurable Beep (closes [Issue #8](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/issues/8) — milestone v2.17)
- **The Beep row's Additional now accepts `freq=1000 dur=200 count=3`** — frequency (Hz) /
  duration (ms) / number of beeps, individually or together, case-insensitive —
  **leaving it empty keeps the exact same system-default sound** (existing scripts need no change)
- **Windows plays a real tone via `winsound.Beep`** (stdlib only — same route as the Play Sound
  plugin) — the .exe's beep becomes a real tone instead of a silent bell · other OSes
  (Linux/macOS) have no winsound and fall back to the old bell automatically — errors are
  swallowed everywhere; a broken sound never stops the script
- **STOP works between repeated beeps** — checked before every tone (a long count stops instantly)
- **.ahk export follows the settings** — `SoundBeep, freq, dur` (empty = the old `SoundBeep, 750, 300`)
- New engine pieces: `parse_beep_spec` (pure parser) + `ActionRunner.do_beep()` (single source
  for GUI/CLI — the sound comes from the OS, not Tk, so it can be called directly)

### 🗺️ v2.18 roadmap (after reviewing [RFC Issue #1](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/issues/1) + the v2.17 milestone)
- Highlights: **OR (`||`) in combined conditions** (left over from RFC question 1 — vote at
  Issue #1/#9) · group-level play order (shuffle/loop specific groups) · heavy-script helpers
  (group-level dry-run) · community plugin submissions always welcome (docs/PLUGINS.md)

### 📚 Docs + tests
- **7 new tests** (TestBeepSettings — parser/unchanged-when-empty/values+defaults/STOP/
  fallback/ahk/dry-run — fake winsound via sys.modules so Windows and CI Linux/macOS take
  the same path) → **556 unit + 20 E2E = 576**

## [2.17.0] — 2026-10-07

### 🧩 New community condition plugins (3) ([Issue #6](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/issues/6) — milestone v2.17)
- **Disk Space Low** — `[drive/path] N[GB|MB|KB|B]`, e.g. `D: 2GB` — free space below the
  limit = true (protects file-writing/backup jobs from dying midway) · bare numbers = MB ·
  stdlib shutil only · unreadable disk = false, never raises
- **Process CPU** — `name [limit%] [Ns]`, e.g. `chrome 5% 3s` — process's average CPU above
  the limit = true (samples cpu-time at two points Ns apart and divides by core count; the
  first call establishes the baseline) — Windows: ctypes Toolhelp32+GetProcessTimes only,
  Linux: /proc · no matching process = false
- **Window Closed** — no window whose title contains the text = true — **the inverse of
  Window Exists** (finish work when the target window closes, e.g. game closed → clean up)
  · empty Additional = false (guards against a typo silently reading as "already closed")
- All three follow the standing plugin rules: `check` never raises · usable as an Action or
  inside Block Start `&&` · `{vars}` supported · the condition dropdown, 🧩, validate and
  dry-run all pick them up automatically

### 📅 Task Scheduler + 🚀 Launcher guide ([Issue #7](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/issues/7))
- **New TUTORIAL chapter 21 (Thai)** — combining script + launcher + Task Scheduler into a
  scheduled job step by step (Run only when logged on, why the "Start in" field matters for
  relative paths, test with the Run button) + stopping externally with `--stop-file` +
  reviewing runs via the ⏱ timeline + a **go-live checklist** (validate → dry-run →
  --max-minutes → logging on → one Run test before the real day)

### 📚 Docs + tests
- **New example `examples/17_condition_plugins_v217.json`** — demonstrates the 3 new
  conditions at boundaries that decide identically on every machine (999999GB always true ·
  1KB always false · process/window names that never exist) · each false condition eats its
  own Beep, no skip cascade
- **5 new tests** (TestPluginsV17 4 + TestExample17PluginsV217 1) → **549 unit + 20 E2E =
  569**
- PLUGINS.md lists the 3 plugins · examples/README row 17 · ROADMAP ticks #6/#7 · zh/ja
  short notes

## [2.16.1] — 2026-10-07

### 🐛 Bug found by testing the real .exe — runtime files vanished on every .exe exit
- **Inside the .exe (PyInstaller onefile), `__file__` points at the `_MEI` temp folder which
  is deleted when the program exits** — `macro_conf.json`/`macro_profiles.json`/
  `macro_log_<date>.txt`/`dry_report_<date>.txt` and log_archive were all written there =
  **the .exe lost its settings/logs/stats/dry-run reports on every close** (the 📝 Log and
  📊 Stats windows inside the .exe read the wrong folder and appeared empty)
- **Fixed with a single `app_base_dir()` helper in the engine** — running from the .exe =
  the folder containing the exe file (same approach `load_plugins`/`open_plugins_folder`
  already used correctly) · source runs = the auto_macro.py folder, exactly as before ·
  covers CONF/PROFILES/log_path/dry_report_path/log_stats_summary/log_daily_series/
  log_monthly_series/log_archive_path/cleanup_old_logs/resolve_image_path (relative images
  now resolve next to the exe)
- **The bug was found by actually testing the released .exe** — downloaded
  AutoMouseMacro.exe v2.16.0 and ran a Beep-only script via its CLI: played through
  "จบแล้ว ✔" with exit 0 (the product works) but the log vanished on exit → traced it to
  the root cause · regression test simulates frozen mode in a subprocess (setting
  `sys.frozen` before import, like PyInstaller) and checks CONF/PROFILES/log/dry-report/
  log_archive/image paths

### 📚 Also
- **New example `examples/16_condition_plugins_v216.json`** — demonstrates the 3 new
  condition plugins (File Newer Than / Window Focused / HTTP Status) platform-neutrally:
  true from committed files, false from names that never exist; each false condition eats
  its own Beep (no skip cascade swallowing other rows) — run from the examples folder and
  open the ⏱ timeline to see it row by row (validate + real CLI test included)
- `examples/README.md` adds the missing rows for 14_condition_plugin and
  15_system_conditions (skipped back in v2.13/v2.14) plus the new 16
- **LANDING.html** now shows the v2.16 features (launcher pair · timeline · condition
  plugin set)
- **Opened [milestone v2.17](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/milestone/2)**
  + issues #6–#9 (next community plugins / Task Scheduler + launcher / configurable Beep /
  OR in combined conditions — awaiting votes) + the plan in ROADMAP
- **3 new tests** (TestFrozenPaths 2 + TestExample16PluginsV216 1) → **544 unit + 20 E2E
  = 564**

## [2.16.0] — 2026-10-07

### 🏁 Milestone v2.15 complete — script launchers · event timeline · new community condition plugins

### 🚀 Script launcher pair .bat + .lnk ([Issue #3](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/issues/3))
- **New 🚀 Launcher menu** — creates a launcher next to a saved script: double-click it
  (or the .lnk) to **play that script immediately** — no main window, no command line,
  perfect for tasks that run every day (extends Export Bat / Queue Bat)
- **Picks the fastest route for you** — with `AutoMouseMacro.exe` next to the script the
  .lnk points straight at the exe (program icon, no console flash); without an exe the
  .lnk points at the .bat which itself picks: exe → start exe (non-blocking), otherwise
  falls back to `py auto_macro.py` + pause so errors stay visible
- **New engine helpers** `launcher_bat()` (ASCII-only .bat body, codepage-safe, extra
  args pass through `%*`, e.g. `--loop`) and `create_shortcut_lnk()` via PowerShell
  WScript.Shell (CREATE_NO_WINDOW keeps the console from flashing; other OS / missing
  PowerShell = quiet False, the .bat still works) · success reports via statusbar only ·
  script must be saved first, same as Export Bat

### ⏱ Event timeline from the log ([Issue #4](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/issues/4))
- **"⏱ Event timeline (latest run)" button in the 📝 Log window** — a new view for
  debugging deeply nested condition scripts: reads the existing [START]/[STEP]/[SKIP] log
  and shows the latest run row by row (time · ▶ played/⏭ skipped/ℹ other · row i/N ·
  button + condition result · seconds) colour-coded green/orange/grey
- **Runs split automatically** — a dropdown walks back through each play (starts at
  [START], ends at [STOP]/[END]) with a summary header "start HH:MM:SS · file · played N ·
  skipped N · N events" — the latest run is always preselected
- **New engine** `parse_log_timeline()` (pure function — unknown line formats become
  "info" events, nothing is lost) + `timeline_run_label()` · multi-word action names
  ("Left Click") split by longest-name-first matching against ACTIONS_ALL — unknown
  plugin names fall back to the first token

### 🔌 New community condition plugins (3) ([Issue #5](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/issues/5))
- **Window Focused** — the **currently focused** window's title contains the text = true
  (unlike Window Exists which scans every window — Windows: GetForegroundWindow via
  ctypes, Linux: xdotool, macOS: osascript) — keep working while the work window stays
  on top
- **File Newer Than** — two forms: `fileA > fileB` (A newer than B = true — watch file
  conversion jobs) and `file Ns` (modified within the last N seconds = true — wait for a
  download to land) · paths with spaces are fine
- **HTTP Status** — `URL [code] [Ns]`, e.g. `https://api.local/health 200 3s` — stdlib
  urllib only, no explicit code = any 2xx counts · an expected 4xx/5xx can also be true
  (HTTPError's e.code is compared) · gate work on API health
- All three follow the standing plugin rules: `check` must never raise (broken input =
  false), usable as an Action or inside Block Start with `&&`, `{vars}` supported, no
  new dependencies

### 📚 Docs + tests
- **19 new tests** (TestLauncherPair 7 + TestLogTimeline 4 + TestLogTimelineGui 3 +
  TestPluginsV16 5 — including an HTTP Status test against a real localhost server) →
  **541 unit + 20 E2E = 561**
- TUTORIAL chapter 20 (Thai/English) + short zh/ja notes · PLUGINS.md lists the 3 new
  plugins · ROADMAP: milestone v2.15 fully closed (issues #2–#5)

## [2.15.1] — 2026-10-06

### ⇅ Move whole section groups (closes the remaining part of [Issue #2](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/issues/2) — Group order)
- **Right-click a Section header → "⬆ Move group up" / "⬇ Move group down"** — swaps the
  whole [header + visible rows + collapsed stash rows] unit with the neighbouring group —
  reorder play-by-group without dragging row by row · collapsed stash rows are bound to
  their own row iids so they always follow their own header (the "collapse never changes
  what plays" promise still holds)
- **Alt+↑/↓ (or the ▲▼ buttons) on a header now moves the whole group too** — previously it
  moved just the header row (making neighbouring rows leak into the group); collapsed or
  expanded headers behave the same · a first group moved up / last group moved down is a no-op
- **Block Start/End spanning the group = refused with a warning** — the new order's block
  depth is checked before any move (an End appearing before its Start would break the block)
  · Ctrl+Z undoes a move as usual (the existing undo/expand-collapsed mechanics v1.22/v2.5)
- **CI: one automatic retry for cross-platform failures** — Xvfb closing the display mid-suite /
  macOS SIGTRAP (CGEventTap) have been seen with unchanged code (proven on v2.15.0: the rerun
  passed) — the Linux/macOS unit + E2E steps now re-run the full suite once with a warning
  annotation (the suite must genuinely pass — this is not skipping tests)
- **6 new tests** (TestGroupMove — swap groups up/down, whole preamble block, collapsed rows
  travel with the group, block-crossing refused, undo, Alt+↓ keyboard path) →
  **522 unit + 20 E2E = 542**

## [2.15.0] — 2026-10-06

### ▶️ Play a single section group (first item of the v2.15 plan — milestone [No.1](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/milestone/1))
- **Right-click a Section header → "▶ Play this group only"** — plays only the enabled (☑) rows
  inside that group, up to the next header, through the **real player — the same path as START**
  (validate/STOP/highlight/log/loop counting) — no more disabling other rows by hand; long scripts
  split into stages can be tested and run one group at a time
- **Collapsed rows inside the group still play** — the group's stash (`_section_stash`) is read
  first, honoring the "collapse never changes what plays" promise (v1.22/v2.9.1) · a group with
  nothing enabled warns on the statusbar ("no enabled rows in this group") and exits quietly
- **CLI `--only-section ชื่อ`** — play a single group from the command line (same contract as the
  GUI): exact header-name match → only that group's rows play (prints the row range + count) ·
  unknown name = warns "section not found" and plays everything as usual · same pipeline as a
  full play — validate/STOP/loop counting/[SKIP] all apply
- **New plumbing** — `_row_from_values`/`_section_range`/`_play_section` +
  `_start_player_inner(items=, src_name=)` (the player can now accept rows handed to it + the
  START log line names the source "group: <name>") — previously the player only read the table
- **i18n** — new keys `grp_empty` + `ctx_play_group` in Thai and English
- **GitHub milestone v2.15** — milestone No.1 + issues #2–#5 created from the ROADMAP plan
  (group play + group reordering / per-script .bat / event timeline / condition-plugin marketplace)
- **Fixed a CI Linux/macOS abort — Tcl_AsyncDelete** — each GUI test class created a fresh
  MacroApp but never stopped its listener threads (_gk hotkey/_sched_loop/recorder); the
  accumulating threads kept allocating during the suite, so GC finalized an old interpreter's Tcl
  object "on the wrong thread" and the whole process aborted (it died when the next GUI class
  started) — `_Tk.destroy` now stops the app's threads (via `root._app` patched in the test file),
  cancels `after` timers and runs `gc.collect()` on the main thread — Tcl state is always finalized
  on the correct thread; production code is untouched (users close through `_on_close` as before)
- **5 new tests** (TestSectionOnlyPlay — 2 real-play GUI + empty-group warning + 2 CLI ·
  the real-play tests were refactored into a shared `_GuiPlayBase` harness — parent tests no
  longer run twice) → **516 unit + 20 E2E = 536**

## [2.14.1] — 2026-10-06

### Formal skip×Block rule + Latest dry-run report button
- **The skip×Block rule is now official (one contract across all three runners: GUI / CLI / engine_cli)** —
  a condition's skip (If Image/If Loop/If Time/If Variable/plugin) consumes only straight-line rows:
  Section/Block Start/End **never eat one**, and a block jump (false condition) or loop-back
  **always cancels any pending skip** · the GUI used to consume skips before checking block/section
  rows, unlike the CLI (proven on CI Linux: a skip crossed a Block Start and swallowed a condition
  row) — covered by TestSkipBlockRule (CLI + engine_cli) + a new GUI test
- **Fixed a latent engine_cli bug (since v2.1)** — the skip-consuming branch had no `pi += 1`:
  "skip N rows" stalled on the same row and then **played it**, never skipping the following rows
- **"Latest dry-run report" button in the 📝 Log window** — selects the newest dry_report file
  instantly (no report yet = statusbar warning only — the iron rule) · tests press the real button
  via invoke
- **v2.15 plan** added to ROADMAP — group-based play order / per-script .bat / event timeline from
  logs / next round of community condition plugins
- **5 new tests** (TestSkipBlockRule 2 + TestLatestDryReportBtn 2 + GUI 1) →
  **511 unit + 20 E2E = 531**

## [2.14.0] — 2026-10-05

### 🧩 Ready-to-use condition plugins + custom dry-run report path
- **Three new condition plugins ship with the program** — `Internet Up` (socket-only stdlib check,
  Additional = `host[:port]` and/or `Ns` — defaults to 1.1.1.1:443), `Process Running`
  (tasklist/pgrep — case-insensitive, ignores the .exe suffix), `Window Exists`
  (ctypes EnumWindows / xdotool on Linux) — usable as an Action or inside Block Start,
  mixable with `&&` like every condition · unsupported OS = False, the program never crashes
  (existing plugin rule)
- **🧩 Condition-plugin button** — pick a condition from a dropdown, type its argument and the row
  is inserted for you (row numbers + cond tag colors refresh automatically · Ctrl+Z undoable ·
  the button only appears when a condition plugin is loaded)
- **CLI `--dry-report PATH`** — choose the dry-run report file yourself, in both the main CLI and
  engine_cli (`{date}` = today; requires `--dry-run` — alone it warns and plays normally) —
  **closes the last ROADMAP item** (pending since v2.10.1)
- **🧪 Dry-run menu picks the report path** — path field + file picker (kept for the session,
  not saved to conf — job-specific) · appends to the same file · `{date}` works the same
- New example `examples/15_system_conditions.json` + `_template.py` references the new plugins +
  v2.14 post in `docs/ANNOUNCE.md`
- **13 new tests** (TestDryReportPath 5 + TestPluginsV14 5 + TestInsertCondPluginGui 3) →
  **506 unit + 20 E2E = 526**
- **Pre-release: example 15 + tests made platform-neutral** — the Process Running check now uses
  `python` (present wherever this program can run — the old `explorer` only exists on Windows,
  and its pending skips swallowed the following condition rows both in straight lines and across
  Block Start jumps) + the Window Exists row moved to the end + a window name that exists
  on no OS instead of `Notepad` · every GUI test class now cancels pending `after` timers before
  destroying root (via `_Tk` in the test file) — prevents "invalid command name" spam and a
  macOS SIGTRAP crash (CI)

## [2.13.0] — 2026-10-05

### 🔌 Plugin API v3 — condition plugins (CONDITION_NAME + check) usable everywhere a condition fits
- **Declare conditions inside a plugin** — besides the original `ACTION_NAME`+`run`, a plugin
  file can now declare `CONDITION_NAME = "name"` + `def check(ctx, row) -> bool` (one file may
  declare both, with different names) — **True = keep playing · False = skip N rows (N = Repeat,
  the single rule shared by every condition)**
- **Two ways to use it** — ① the Action column = condition name (added to the dropdown
  automatically, rows get the condition colour) ② Block Start/End → `if condition [argument]`
  (mixable with `&&` with pixel/variable/image conditions)
- **The `>name` token works too** — store the condition result into a variable exactly like
  built-in conditions (v2.10 mechanism)
- **Every path covered** — `validate_rows` (--validate / 🔍 Validate / the START check / queues
  in both CLI and GUI) accepts condition names · GUI / CLI / engine_cli all evaluate through the
  single runner (`evaluate_plugin_condition`), always checked before the delay and before the
  row is mistakenly played as an action · a crashing `check` = warning + keep playing, no skip
  (same policy as a crashing action plugin)
- **Dry-run runs it for real** — conditions/blocks/variables already walk for real (v2.10) → the
  plugin's `check` is invoked for real too
- **.ahk export** — condition rows and blocks referencing a condition plugin are written as
  comments for the whole block (prescan prevents stray braces — same rule as image/pixel)
- **Duplicate names rejected both ways** — `CONDITION_NAME` must not collide with built-in
  actions, other actions, or other conditions (so a row button is never ambiguous) — a colliding
  file is skipped with the reason recorded in `load_plugins.last_failed`, like a broken file
- **New example plugin `file_exists.py`** — the "File Exists" condition (True when the file
  exists, `{variables}` supported) + example `examples/14_condition_plugin.json` +
  scaffold in `plugins/_template.py` + the Plugin API v3 section in [docs/PLUGINS.md](PLUGINS.md)

### 📚 Docs + tests
- **16 new tests** (TestConditionPlugins 10 + TestConditionPluginsGui 3 +
  TestConditionPluginsCli 3 — the CLI side runs the real `cli_main`) → **493 unit + 20 E2E = 513**, all green
- TUTORIAL chapter 17 (Thai/English) + section 20 in the HTML + short zh/ja summaries ·
  ROADMAP closes the "Plugin API v3" item

---

## [2.12.0] — 2026-10-05

### 📑 GUI Queue Runner — play queues inside the app with a live monitor (item 2 of the v2.11 proposal set)
- **New 📑 Run Queue menu** — pick a queue list .txt (same format as CLI `--queue` and
  🗂️ Queue Bat) and play the files one by one **inside the program, no console needed**
  · the live window shows: a file table (# / file / status), a current-file label, a
  real-time CLI output box (last 200 lines kept) and an end-of-queue summary
  (succeeded x/N, elapsed time)
- **Per-file status colours** — playing (blue) / finished ✔ (green) / stopped (orange) /
  problem exit N (red) / failed validation–missing file (red) / cancelled (grey)
- **Two stop levels** — "⏹ หยุดไฟล์นี้ / Stop this file" stops the current file and
  **continues with the next one** (implemented through the CLI's `--stop-file`, with one
  stop file per queue entry so file boundaries never collide) · "⏹⏹ หยุดทั้งคิว / Stop
  everything" stops the current file and cancels all remaining ones · F8/Esc while
  playing = stop the whole queue (same meaning as the original CLI `--queue`)
- **Same rules as the CLI** — every file is validated with the engine `validate_rows`
  before the first file plays (a broken file cancels the whole queue, exactly like
  v2.10) · a finished file is followed by the next immediately · `--no-log` follows the
  program's log setting · when the queue ends you can press ▶ to run it again
- **Thread-safe per project rules** — the worker thread calls `cli_main` (the real CLI
  logic) and pushes status into a `queue.Queue`; a poller (500 ms, the existing
  `_sched_poll` pattern) updates the UI on the main thread only · CLI stdout is captured
  by `_QueueOutCapture` (also survives a windowed .exe where stdout is None) · closing
  the window while playing asks first, then stops the whole queue and closes when the
  thread ends · closing the program while playing stops the queue automatically
- **New engine helper `parse_queue_list()`** — parses the list .txt (one path per line,
  skips # and blank lines, relative paths resolved against the list's folder) — one
  source for both CLI `--queue` (refactored to use it, behaviour/messages unchanged) and
  the Run Queue window

### 📚 Docs + tests
- **13 new tests** (TestQueueListParse 3 + TestQueueRunnerGui 10 — including an end-to-end
  through the real `cli_main` with Beep-only scripts) → **477 unit + 20 E2E = 497** all
  passing
- TUTORIAL Chapter 16 (Thai/English) + topic 19 in the HTML + short zh/ja notes ·
  ROADMAP: closed the "GUI queue player" item from the v2.11 proposal set

---

## [2.11.0] — 2026-10-04

### 🗃️ Log tools — monthly archive / clear old days
- **New engine function `cleanup_old_logs()`** — one place to handle old log/dry-report
  files: `archive=True` moves them into `log_archive/YYYY-MM/` (monthly folders from the
  date in the file name — kept forever, fixing the 500-line daily rotation losing old
  history) · `archive=False` deletes · `keep_days=N` keeps the last N days (omitted =
  everything except today) · **today's file is never touched** (still being written) ·
  files with unexpected names are skipped · existing destination file = skip, never
  overwrite · error-tolerant everywhere like backup (secondary features must never crash
  the program)
- **📝 Log window: 2 new buttons** — "เก็บถาวรวันเก่า / Archive old" (moves now) +
  "ล้างวันเก่า... / Clear old..." (asks before deleting) — success reports via statusbar
  only · the file list is rebuilt after cleanup
- **📝 Log window now shows Dry-run reports** — the dropdown includes
  `dry_report_<date>.txt` (left over from v2.10.1 — previously you had to open the folder)
- **Automatic cleanup on close (Settings)** — checkbox "clean old logs on exit" + days
  1–365 + archive/delete choice — remembered in conf (`log_keep_days`/`log_archive`);
  default 0 = off, nothing is touched until you enable it · travels with Export/Import
  settings too

### 🖥️ engine_cli dry-run report (left over from v2.10.1)
- **`py engine_cli.py script.json --dry-run` now writes the report file** — like the main
  CLI: captures DRY-RUN lines + writes in finally (a mid-run stop still saves the part
  walked) + prints "รายงาน Dry-run: <path>" after the run

### 📚 Docs + tests
- **11 new tests** (TestLogTools 6 + TestLogToolsGui 4 + engine_cli dry-report 1) →
  **464 unit + 20 E2E = 484** all passing
- ROADMAP: closed the "log tools" item from the v2.11 proposal set

---

## [2.10.1] — 2026-10-03

### 📝 Dry-run report file (follow-up to v2.10's Dry-run)
- **When a dry run ends it writes `dry_report_<date>.txt` next to the program** — a copy of
  the whole path walked, one line per entry, with a header (script/rows/loops) and a
  closing count of what would really run, sorted by frequency, e.g. "สรุปจะทำจริง: Left
  Click ×4, Beep ×2" — great for long jobs on small screens · **GUI:** captures DRY-RUN
  messages during play, writes in finally (always restores the original callback) ·
  **CLI:** prints the report path after each round (watchdog gets a report every round) ·
  a mid-run stop still saves the part walked, marked as stopped · real play never writes ·
  every error swallowed — the report must never crash the program (like log_write) ·
  new [DRY] log mode (parse_log_stats does not count it as STEP) · blocks separated by
  a blank line

### 🗂️ Queue Bat — export queue batch files from the GUI (follow-up to v2.10's --queue)
- **New 🗂️ Queue Bat menu** — pick a queue list .txt → writes `list.bat` (Windows) +
  `list.sh` (Linux/macOS) next to it; double-click plays the whole queue through `--queue`
  with no commands to type — easy hand-off to shift-mates · new engine helpers
  `batch_queue_export_bat`/`batch_queue_export_sh` (same style as v2.3) · cancelling the
  file dialog writes nothing

### 📚 Docs + tests
- **New TUTORIAL chapter 14 (Thai/English) + chapter 17 in the HTML** — a deep dive into
  all three v2.10 features (Dry-run / condition results as variables / batch runner) with
  three follow-along exercises in the style of the existing chapters · zh/ja short
  summaries · fixed a date-dependent test bug: TestBackup hardcoded 2026-09-25, so it
  broke on its own once the real date passed 7 days (now computed from now) · 10 new
  tests (TestDryReport 4 + TestQueueBatchExport 5 + a dry-report GUI test in
  TestPlayLoopGui) → **453 unit + 20 E2E = 474**
- **ROADMAP: v2.11 proposals** — plugin conditions (Plugin API v3) / more log tools /
  a GUI queue runner with progress

---

## [2.10.0] — 2026-10-02

### 🧪 Dry-run — rehearse the whole script without touching mouse/keyboard
- **🧪 Dry-run menu (GUI)** — after a confirmation the script plays with a `dry_run` flag:
  conditions/blocks/delays/variables walk every real path, but every real input row
  (mouse/keys/typing/launch app/clipboard/beep/wait for image or pixel/plugins) is replaced
  with a "DRY-RUN: would click…" report — the window title shows [ DRY-RUN ] until done,
  then normal mode returns automatically · single implementation point in `ActionRunner`
  (GUI/CLI/engine_cli all behave identically)
- **CLI `--dry-run`** — the same thing from the command line, with a banner line up front

### 🔗 Condition results as variables — the `>name` token
- **If Image / If Pixel Color / If Variable / If Loop / If Time accept a trailing `>name`** —
  stores the condition result "1" (true) / "0" (false) into a variable: `img.png >found`,
  `300,300 #ffffff >colorok`, `n > 3 >res` — later rows use `{found}` or chain another
  `If Variable ผล = 1` (condition chaining with zero new actions) · parsed by the single
  `parse_cond_store` helper (guards on/of/and from being taken as variable names) · the
  token is stripped before `&&` splitting / image lookup so images still resolve

### 📦 Batch runner — CLI `--queue LIST.txt`
- **Play many scripts back-to-back** — one path per line (skips #comments/blank lines,
  relative paths resolve against the list file's folder) · **every file is validated before
  the first one plays** with the same engine `validate_rows` as --validate — one broken file
  cancels the whole queue, nothing plays (same idea as START-validate v2.9.0) · files run
  one after another **without waiting for a keypress** (same idea as schedule auto-skip
  v2.9.1) · stopping mid-file stops the whole queue · a per-file summary prints at the end
  plus [QUEUE] log entries (start/end/cancel/summary) · all-good = exit 0, any broken file
  = exit 1 · exit code 130 (stopped by user) does not count as a queue failure

### 🧰 Other
- CLI `script` argument is now optional — `--queue` needs no placeholder file · 16 new tests
  (TestDryRunEngine/TestCondStore/TestQueueCli/TestCliDryRun + E2E TestQueueDryRunE2E +
  example 14 wired into TestAhkBlocks) → **443 unit + 20 E2E = 463** ·
  new examples `14_dry_run_cond_vars.json` + `queue_sample.txt` ·
  ROADMAP: the three finished v2.10 proposals are checked off

---

## [2.9.1] — 2026-10-01

### 📝 Log makes skipped rows obvious (extends the START validation of v2.9.0)
- **New [SKIP] log mode** — every row that fails validation is logged as "row N skipped
  (reason)" plus a "played X of Y rows" summary · the START line lists the skipped rows as
  `ข้าม=1,3` — overnight/scheduled jobs can be reviewed to see exactly what ran and what
  was skipped (`parse_log_stats` does not count [SKIP] as STEP — existing stats stay exact)
- **CLI validates up front** — the same engine `validate_rows` as `--validate` runs before
  playing: the whole broken-row report prints first and those rows are excluded (previously
  rows warned one-by-one during play) · if every row is broken the run exits with code 1 and
  the message "fix per the report or run --validate" — a watchdog left overnight no longer
  wastes time playing a script that is broken end to end · the END line and round summaries
  report skipped counts
- **Schedule skips broken rows automatically** — when a scheduled session starts and rows
  are broken: skip them and log every [SKIP] (previously the dialog sat waiting for someone
  to click OK — at 3 a.m. nobody clicks) · pressing START by hand still asks exactly as
  before · all-broken in auto mode = log written, exit quietly
- **Tests** — added **TestE2EStartValidateSkip 3** (report + real skip, log [SKIP] +
  skip-list, all-broken exit 1) + example 13 wired into tests (TestAhkBlocks 7 tests) →
  **429 unit + 18 E2E = 447**
- **New example `examples/13_start_validate_ahk_blocks.json`** — demonstrates START-validate
  plus the if/until/max blocks that export to .ahk completely (validate passes + exact
  roundtrip, verified by tests)
- **Docs** — English changelog `docs/CHANGELOG.en.md` (2.9.0–2.8.0 fully translated;
  check_docs now enforces the version heading) · ROADMAP gains a new set of 5 v2.10 proposals
  (Dry-run / condition results as variables / batch runner / plugins as conditions / log tools)

---

## [2.9.0] — 2026-10-01

### 🚦 START pre-validates the script (same engine as 🔍 Validate)
- **Pressing START now runs `validate_rows()` from the engine** — on issues it asks
  "play skipping broken rows?" · confirm = only valid rows play (broken rows are really
  skipped) · decline = go back and fix · if every row is broken nothing plays at all
- Kills the "pressed START and nothing happened" class of bugs — rows with empty keys or
  missing images that used to fail silently mid-play are caught up front

### 🗜️ Right-menu: Collapse all / Expand all
- **"Collapse all (Sections + blocks)"** — walks top-down and folds every Section head and
  Block Start (outer groups swallow inner ones — rows already hidden with an earlier group
  are skipped, never collapsed twice) · **"Expand all"** — toggles every collapsed head back
  until the table is full again, in the exact original order
- Fixed `_group_members` crashing (ValueError) on a head that was already hidden inside an
  outer group

### 🔀 .ahk block support both ways
- **export** — Block Start with an if-variable condition → `if (n > 5) {` … `}` · `max N` →
  `Loop, N {` · `until cond` → `Loop {` … `} Until, cond` (multiple conditions join with
  `&&`, text search `name ~ word` → `InStr(name, "word")`) · image/color conditions that
  cannot translate become comments for the whole block (no stray braces — the exported .ahk
  must always run)
- **import** — `if (...) {` / `Loop, N {` / `Loop {` + `Until,` (same line as `}` or on its
  own line) come back as BLOCK_START (`if`/`max`/`until`) … BLOCK_END · `InStr` maps back to `~`
- **Roundtrip verified** — if/max/until convert out-and-back exactly · stray braces and odd
  nested parens are skipped safely

### 🧪 Tests
- Added **TestAhkBlocks 6** (export if/max/until, image = comment, import ×3, roundtrip,
  junk braces) + **TestCollapseAll 3** (both kinds collapsed / expand restores 6 rows /
  empty table) + **TestUnifiedPlayValidation 3** (skip broken rows on confirm / decline
  doesn't play / all-broken warns) → **428 unit + 15 E2E = 443** · all previous tests pass

---

## [2.8.0] — 2026-10-01

### 🕒 Per-time schedule profiles
- **Each daily time can bind its own profile** — enter `08:00, 12:30=morning job, 22:00` in
  the Schedule dialog and at 12:30 the profile "morning job" loads and plays by itself;
  times without `=` keep the default profile dropdown (v2.4/v2.7)
- **engine** — `parse_sched_entry()` ("HH:MM" or "HH:MM=profile" → (time, profile), broken =
  None), `sched_time_profiles()` extracts the mapping, `parse_hhmm_list()` strips `=profile`
  for compatibility · the scheduler pushes `("play", profile)` and the UI poller loads that
  profile's rows before playing

### 🔀 .ahk variables & conditions both ways
- **export** — `Set Variable` → `n := 5` / `n += 2` · `If Variable` → `if (n > 5)` ·
  `{name}` references → `n` · everything else is always quoted `""` (Thai words are never
  misread as variables)
- **import** — `n := 0` / `n += 2` → Set Variable · `if (n > 5)` → If Variable ·
  `x := y` → `x = {y}` (reference syntax)
- Untranslatable rows stay comments, same as before

### 🚪 Community plugin gate
- New issue template `plugin_submission.md` + PR checklist with the 6 criteria from
  docs/PLUGINS.md · three community example plugins: **Random Pause / Counter / Open URL**,
  each with standard tests (TestPluginsCommunity)

### 🧪 Tests
- Added schedule per-time-profile tests + .ahk variable roundtrip tests + community plugin
  tests → **416 unit + 15 E2E = 431** · all previous tests pass

---

*Older versions: see the complete Thai history in [CHANGELOG.md](CHANGELOG.md) ·
Docs: [README.md](README.md) (Thai) · [README.en.md](README.en.md) (English) ·
Tutorial: [TUTORIAL.md](TUTORIAL.md) / [TUTORIAL.en.md](TUTORIAL.en.md)*

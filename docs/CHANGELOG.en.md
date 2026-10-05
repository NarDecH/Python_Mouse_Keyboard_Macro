# 📋 CHANGELOG (English) — Auto Mouse & Keyboard Macro

> English translation of [CHANGELOG.md](CHANGELOG.md) (Thai, the authoritative full history).
> Newer versions appear in the Thai original first — this file covers the recent releases.

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

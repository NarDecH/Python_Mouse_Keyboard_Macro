# 📋 CHANGELOG (English) — Auto Mouse & Keyboard Macro

> English translation of [CHANGELOG.md](CHANGELOG.md) (Thai, the authoritative full history).
> Newer versions appear in the Thai original first — this file covers the recent releases.

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

# AGENTS.md — Python Mouse Keyboard Macro

> เวอร์ชันปัจจุบัน: v2.14.0 — ดู `docs/CHANGELOG.md`

แนวทางการทำงานสำหรับ AI agent และนักพัฒนาในโปรเจกต์นี้

## ภาพรวมโปรเจกต์

- **ชื่อ:** Auto Mouse & Keyboard Macro v1.6
- **ไฟล์หลัก:** `auto_macro.py` (ไฟล์เดียวจบตอนแจกจ่าย) + `macro_engine.py` (engine ล้วน ไม่มี Tk —
  แหล่งจริงของบล็อก ENGINE-BEGIN/END ใน auto_macro.py · **แก้ engine ที่ macro_engine.py เสมอ**
  แล้วรัน `py build_singlefile.py` ซิงก์กลับก่อน build .exe — กฎ "ไฟล์เดียวจบ" ยังคงอยู่ผ่าน build script)
- **แรงบันดาลใจ:** UX ตารางคำสั่ง + ปุ่ม START/STOP/REPEAT/ RECORD แบบกดแล้วเล่นซ้ำ
- **หน้าที่:** บันทึกและเล่นซ้ำการคลิกเมาส์ + การกดคีย์ตามสคริปต์ที่ผู้ใช้ตั้งไว้
- **ฟีเจอร์เสริม v1.4:** Global Hotkey, คลิกตามภาพ (OpenCV), โปรไฟล์หลายสคริปต์,
  เล่นอัตโนมัติตามเวลา (schedule), unit tests (`test_auto_macro.py`)
- **ฟีเจอร์เสริม v1.5 (จาก automouseclick.com):** Scroll, Double Click, คลิก+Modifier,
  Move Mouse (+Offset), Save/Restore Cursor, Type Text, Launch App, Wait for Image,
  Beep, ดีเลย์สุ่ม (Secs "1-3"), ตัวคูณความเร็ว, จำนวนรอบสคริปต์, คืนเมาส์จุดเดิม
- **ฟีเจอร์เสริม v1.6:** CLI mode (`py auto_macro.py script.json`), Right-click menu
  บนตาราง (คัดลอก/แทรก/ลบ), Progress bar + ตัวนับรอบใน statusbar
- **ฟีเจอร์เสริม v1.7–v1.7.1:** Search Area (`@x,y,w,h`), threshold รายแถว (`#90`),
  ปุ่มจับภาพลากกรอบ, CI/CD (GitHub Actions + Release จาก tag), TUTORIAL
- **ฟีเจอร์เสริม v1.8:** log การเล่น (`macro_log_วันที่.txt` เปิด/ปิดใน Settings),
  `--stop-file`, global hotkey ใช้ `keyboard.Listener` (ไม่ใช่ GlobalHotKeys — ดูหมายเหตุ)
- **ฟีเจอร์เสริม v1.9:** Log viewer (เมนู 📝 Log), Hot-profile F1–F4 (โหลด+เล่นทันที),
  E2E tests (`test_e2e.py` — รัน CLI จริงทดสอบการหยุดทุกครั้ง)
- **ฟีเจอร์เสริม v1.10:** เล่นสุ่มลำดับ/สัดส่วน (`pick_play_order` + `--shuffle/--rows-pct`),
  Record wizard (เมนู 🧙 — ใช้ `_pending_rows` + กลไก RECORD เดิม), CLI `--watchdog`
  (จบแล้วเริ่มใหม่อัตโนมัติ + log `[WATCHDOG]`)
- **ฟีเจอร์เสริม v1.11:** Self-check ตอนเปิด (`_self_check` + `self_check_text` แสดงใน
  Settings), สถิติจาก log (`parse_log_stats`/`log_stats_summary` + เมนู 📊 Stats),
  สคริปต์เฝ้าระบบ `examples/05` + `run_watchdog.bat`, หน้าเว็บ `docs/LANDING.html`
  ⚠️ ตั้งชื่อคลาสเทสต์ซ้ำกันไม่ได้ — คลาสหลังจะบังคลาสหน้า (เคยทำให้เทสต์ hotkey หาย) ตรวจด้วย `grep -c "class Test"`
- **ฟีเจอร์เสริม v1.12:** กราฟสถิติรายวันใน Stats (`log_daily_series` + canvas),
  Export/Import การตั้งค่าทั้งหมด (Settings — kind=automousemacro-settings),
  ปุ่ม 🧪 ทดสอบระบบจริงใน Settings (ขยับเมาส์+บี๊บ)
- **ฟีเจอร์เสริม v1.13:** Backup อัตโนมัติตอนปิดโปรแกรม (`backup_snapshot`/`prune_backups`
  ลง backups/ เก็บ 7 วัน), Help ฉบับเต็ม (หน้าต่างเลื่อนได้ + ปุ่มเปิด TUTORIAL.html)
  ⚠️ ลิงก์ใน docs/*.md ที่อยู่นอกโฟลเดอร์ตัวเองต้องมี ../ นำหน้า — ตรวจลิงก์ทุกไฟล์ก่อน push
- **ฟีเจอร์เสริม v1.14:** ตั้งค่า backup ได้ (เปิด/ปิด + 1–90 วัน ใน conf), i18n ไทย/อังกฤษ
  (`TR` + `tr(lang, key)` + `self._t(key)` — สลับใน Settings ผ่าน `_apply_language`)
  และ `docs/ANNOUNCE.md` โพสต์แนะนำโปรแกรมสำเร็จรูป
- **ฟีเจอร์เสริม v1.15:** i18n ครบทุก dialog (Settings/context menu/หัวตาราง),
  สรุปการใช้งานรวมรายเดือน (`log_monthly_series` + กราฟใน Stats),
  CONTRIBUTING.md + issue/PR templates, เทสต์เปิด dialog จริงด้วย Tk จำลอง
  (TestUiDialogs — ไม่มี display จะ skip อัตโนมัติ)
- **ฟีเจอร์เสริม v1.16:** Custom Action plugins — โฟลเดอร์ `plugins/*.py` ประกาศ
  `ACTION_NAME` + `run(ctx, row)` เป็น Action ใหม่ (GUI dropdown + CLI) โหลดผ่าน
  `load_plugins()` (ข้ามไฟล์พัง/ชื่อซ้ำ ไม่พังโปรแกรม — รายชื่อที่ข้ามใน `last_failed`),
  GIF สาธิตใน README (`docs/images/demo.gif`), `docs/ROADMAP.md` แผน v1.17→v2.0
- **ฟีเจอร์เสริม v1.17:** ค้นหาแถว (`_find_rows`/`_find_dialog` — Ctrl+F, Enter ซ้ำ = ผลถัดไป),
  Undo (`_push_undo`/`_undo_delete` — Ctrl+Z เก็บ snapshot 50 ชั้น, _load_rows/วางคลิปบอร์ด
  ก็ push ก่อนแทนที่เสมอ), วางจากคลิปบอร์ด (`_paste_rows_clipboard` — เมนู 📋 รับรายการล้วน
  และไฟล์ Export), If Image (`IF_IMAGE` — ภาพไม่เจอ → ตั้ง `self._ifimg_skip = N`
  ลูปเล่นข้าม N แถวถัดไป; N = คอลัมน์ Repeat ของแถว If Image),
  `_find_image_pos()` รวมตรรกะค้นภาพ (Image Click/If Image ใช้ร่วมกัน),
  เดโม่ `examples/06_plugin_demo.json`
- **ฟีเจอร์เสริม v1.18:** Wait for Pixel Color (`WAIT_PIXEL` — Additional `x,y #RRGGBB`,
  parse ผ่าน `parse_pixel_spec`/`parse_color_hex`, อ่านสีด้วย `pixel_color_at` (PIL),
  เทียบด้วย `color_close` tol 20; GUI รอจริง 30 วิ, CLI เช็คครั้งเดียว),
  Else If Image (`ELSE_IMAGE` — ใช้ `self._last_if_found` จาก If Image ล่าสุด:
  เจอ → ข้ามกลุ่ม B ตาม Repeat, ไม่เจอ → เล่นกลุ่ม B),
  สถิติราย Action (`parse_log_stats` รวม dict `actions` + `top_actions_summary` + ตารางใน Stats),
  เดโม่ `examples/07_conditions.json` + TUTORIAL บทที่ 5A
- **แก้บั๊ก v1.18.1 (4 จุด พิสูจน์ด้วยการรันจริง):**
  (1) `_rows_for_play` หายไปตั้งแต่ v1.10 — rename เป็น `_play_options` แล้วลืมสร้างเมธอดเดิม
  (body เดิมกลายเป็น dead code ค้างท้ายฟังก์ชัน) → กด START ใน GUI พังทันที
  ⚠️ อย่า mock `_start_player` ในเทสต์จนไม่ได้ทดสอบการเรียกจริง — ตอนนี้มี
  `TestPlayLoopFixes` + `TestPlayLoopGui` (เล่นจริงด้วยแถว Beep ล้วน ไม่มีจอ skip)
  (2) `_player` เดิม `if loop: break` ทำ REPEAT/วนซ้ำไม่จำกัด เล่นแค่ 1 รอบ —
  แก้เป็นวนจน STOP; **schedule ใช้ `_start_player(False, once=True)`** เล่นรอบเดียวต่อการเรียก
  (3) `_player` เดิมบังคับ `_shuffle=False/_pct=100` ทับค่าจาก UI → สุ่มลำดับ/สัดส่วนไม่มีผล
  (4) `on_kb` อ้างตัวแปร `pressed` ที่ไม่มีจริง → กดคีย์ตอน RECORD เป็น NameError ไม่มีแถวถูกอัด
- **ฟีเจอร์เสริม v1.19:** ตัวแปรในสคริปต์ (`Set Variable` + `VAR_ACTIONS` — parse ผ่าน
  `parse_set_var`/`apply_set_var`, แทนค่าผ่าน `subst_row`/`substitute_vars` ด้วย `{ชื่อ}` —
  ชื่อไทยได้ `_VAR_NAME` รวม mark ไทย, เริ่มใหม่ทุกครั้งที่เริ่มเล่น `self._vars`/`cli_vars`
  — ⚠️ `cli_vars` ต้องอยู่ scope ของ `cli_main` ไม่ใช่ `play_once` เพราะ `do_step` closure
  มองไม่เห็น), ปุ่ม 🎨 จับสี (`_pick_pixel_color` + `_apply_pixel_spec`),
  timeout ตั้งได้ (`parse_wait_timeout` — token `60s` ท้าย Additional),
  จำค่าการเล่น+schedule ลง conf, CLI เตือน action ไม่รองรับ,
  **player thread ไม่เรียก Tk แล้ว** — `_start_player` ส่ง `items = [(row, iid)]`,
  beep ขอผ่าน `_ui_state["beep"]` ให้ poller เป็นคน `bell()`, ไฮไลต์ใช้ iid ตรง
  (แก้เพี้ยนเมื่อมีแถวปิด), `_sched_check()` แยกออกจากเธรด (โหมดรายวันเทียบเฉพาะ
  HH:MM — เดิมเทียบผิดรูปแบบไม่มีวันติด), `pixel_color_at` grab 1×1,
  เวอร์ชันแหล่งเดียว `__version__` + TestVersionConsistency กันเอกสารค้าง
- **ฟีเจอร์เสริม v1.20:** คลิปบอร์ด (`Set Clipboard`/`Read Clipboard` — GUI ผ่าน
  `_ui_state["clipboard"]`/`["read_clipboard"]` ให้ poller ตั้ง/อ่านบน main thread เท่านั้น,
  CLI ผ่าน `clip_set`/`clip_get` — Windows: Win32 CF_UNICODETEXT ผ่าน ctypes
  (ตั้ง restype/argtypes ให้ครบกัน handle โดนตัดบน 64-bit), macOS: pbcopy/pbpaste,
  Linux: wl-copy/xclip/xsel), Plugin API v2 (ctx เพิ่ม `stop_check()` + `ui={"msg","beep"}`
  ทั้ง GUI/CLI), TUTORIAL บทที่ 12 (ตัวแปร+คลิปบอร์ด), เดโม่ `examples/09_clipboard.json`
- **แก้บั๊ก v1.20.1:** `HotkeyEdit.__init__` ลืมเก็บ `self.on_done` (พังตั้งแต่ v1.4 —
  ดับเบิลคลิกแก้เซลล์แล้วกดตกลง/Enter = AttributeError ค่าไม่ถูกบันทึก; X/Y ใช้อีกเส้นทาง
  จึงไม่เจอ) ⚠️ dialog ทุกตัวควรมีเทสต์ "เปิด + ใช้งานจริง" อย่างน้อย 1 ตัว —
  บั๊กชนิดนี้อยู่รอดได้เพราะมีแต่เทสต์ "เปิดได้ไม่ crash"
- **แก้บั๊ก v1.20.2:** Type Text เดิมใช้ `KeyCode.from_char()` พึ่ง keyboard layout
  active (VkKeyScanW) — เครื่องที่ active เป็น layout ไทยพิมพ์อังกฤษ/สัญลักษณ์แล้ว
  เพี้ยนทั้งบรรทัด ("D" → "ิ", "RRRRRRRRR") → ตอนนี้พิมพ์ผ่าน `send_unicode_char()`
  = SendInput KEYEVENTF_UNICODE (ctypes ล้วน, Windows; OS อื่น fallback ทาง pynput)
  ⚠️ อย่ากลับไปพิมพ์ข้อความด้วย virtual key — พิมพ์ข้อความให้ใช้ Unicode path เสมอ
  (`\n` = Enter, อักขระเกิน BMP แยก surrogate pair — ดู `_unicode_input_records`)
- **ฟีเจอร์เสริม v1.21:** เงื่อนไขนับรอบ/เวลา (`If Loop`/`If Time` — Additional เลขรอบ N /
  HH:MM, parse ผ่าน `parse_if_loop`/`parse_if_time`, **กฎเดียว: Repeat = จำนวนแถวที่ข้าม**
  ทุกเงื่อนไขรวม If Image/Else, GUI ใช้ `self._ifimg_skip` + `self._loop_no` ในลูปเล่น,
  CLI ใช้ `skip_n` — ⚠️ แถวเงื่อนไขต้อง `break`/`continue` **ก่อน** do_step เสมอ ไม่งั้นโดน
  เตือน "ยังไม่รองรับใน CLI" และเช็คการข้ามต้องอยู่ **ก่อนดีเลย์** ทั้งสองโหมด),
  หัวข้อ Section (`SECTION_HEADER` = "⬛ หัวข้อ" — แถวจัดระเบียบ: ไม่เล่น/ไม่นับเลขใน
  `refresh_nums`/ไม่หน่วง, สลับกลับเป็น Left Click ได้ผ่าน `_row_toggle_section`,
  เพิ่มด้วยเมนูขวา `_add_section`), เดโม่ `examples/10_conditions_v21.json`
- **ฟีเจอร์เสริม v1.22:** สีแถวตามหมวด Action (`ROW_STYLE` + `row_tag()`/`row_tags()` — เงื่อนไข=cond
  คีย์=key พิเศษ=special แถวเมาส์=แถบ even/odd เดิม, ทุกจุด insert/item ต้องใช้ `row_tags()`),
  ปุ่ม 🕐 จับเวลา (`_apply_current_time` — เวลาปัจจุบัน +15 นาที ข้ามเที่ยงคืน, ทำงานแบบ
  `_apply_pixel_spec`), ย่อ/ขยายกลุ่ม Section (`_group_toggle` + `_section_stash` — แถวซ่อน
  **เล่นปกติ** เพราะไม่อยู่ใน tree, ⚠️ ตัวตรวจป้ายย่อคือ regex `_COLLAPSED_RE` = suffix
  `\(ย่อ N แถว\)\s*$` — **ใช้ .search เท่านั้น** เพราะหัวข้อมีชื่อนำหน้า, ลบหัวข้อที่ย่อ =
  `_on_del_cleanup` ขยายคืนก่อน, `_serialize` รวมแถวใน stash, undo ผ่าน `_undo_restore_collapsed`,
  ย้ายกลุ่ม = `_move_collapsed_group`)
- **v2.0 (phase 1):** แยก engine — `macro_engine.py` = ค่าคงที่/parser/คลิปบอร์ด/unicode/
  log/stats/plugins **ไม่มี Tk** (นำไปฝัง/เทสต์แยกได้) ใน `auto_macro.py` บล็อกเดียวกันถูกเก็บ
  ระหว่างป้าย `# === ENGINE-BEGIN` … `# === ENGINE-END` — **ห้ามแก้บล็อกใน auto_macro.py ตรง ๆ**
  แก้ที่ macro_engine.py แล้วรัน `py build_singlefile.py` (เทสต์ TestEngineSplit ตรวจว่า sync ตรงกัน
  ด้วย inspect.getsource ทุกฟังก์ชันสำคัญ) — build .exe ยังใช้ auto_macro.py ไฟล์เดียวเสมอ
- **v2.1 (phase 2):** ActionRunner ใน macro_engine.py = กลไก "ทำ 1 แถว" แหล่งเดียว —
  GUI/CLI ส่ง controller + callbacks (`stop_check/on_beep/on_message/on_clipboard_*`/
  `plugin_lookup/unsupported_cb`) เข้า runner แล้วเรียก `execute(r)` · ⚠️ อย่ากลับไปเขียน
  do_step สองชุด, คีย์ค้างอยู่ใน `runner.pressed_keys/pressed_btns` + `release_all()`,
  เงื่อนไข If Loop/If Time ประเมินผ่าน `ActionRunner.evaluate_condition()` (skip_n + msg),
  CLI ย่อย `engine_cli.py` import engine ตรง ๆ ไม่แตะ Tk · ปุ่ม 🔌 = `open_plugins_folder`
  (ตลาด plugin: docs/PLUGINS.md) · เอกสารอังกฤษเต็ม docs/TUTORIAL.en.md
- **v2.2 (phase 3 จบ):** engine ครบทุกส่วน — ① **Recorder** ใน macro_engine.py = กลไก
  RECORD ล้วน (listener threads ผลักเข้า `recorder.pending_rows`, UI ดึง `drain_pending()` ทุก tick,
  `on_event` callback ห้ามแตะ Tk) — MacroApp ไม่มี listener ของตัวเองแล้ว ② **ค้นภาพลง engine**
  (`parse_search_area`/`grab_area_bgr`/`find_image_pos` + `find_image_pos.last_error`) ③
  **If Image/Else อยู่ใน `ActionRunner.execute`** (ตั้ง last_if_found/skip_n เอง, ผูก
  `find_image_cb`/`wait_image_cb` ตอนสร้าง runner) — GUI จัดการผ่าน `_execute_condition_row`
  ตัวเดียวสำหรับเงื่อนไขทั้ง 4 ④ **CLI ค้นภาพได้จริง** (ทั้งตัวหลักและ engine_cli —
  `--json-lines` อ่าน 1 แถว/บรรทัด ข้าม #comment) ⑤ plugin ใหม่ play_sound/webhook/
  multi_image_click · ⚠️ poller ทน msg tuple ไม่ครบ (`len(msg) == 2` เช็คใน _start_poller)
- **v2.3 (ชุมชน/cross-platform):** เมนู 📤 Export Bat (`export_batch_files` — สร้าง
  .bat/.sh ข้างสคริปต์ที่ Save แล้ว ดับเบิลคลิกรันผ่าน CLI ได้; helpers
  `batch_export_bat`/`batch_export_sh` อยู่ใน engine), `--version` flag ทั้ง CLI หลัก
  และ engine_cli, plugin ที่แจกมา 5 ตัวมีเทสต์ครบ (`TestPluginsComplete` — มาตรฐาน:
  รัน run(ctx, row) ด้วย ctx จำลอง + ทน input พัง), CI เพิ่ม job ubuntu/macos
  (Linux รัน E2E ใต้ xvfb, macOS continue-on-error เพราะสิทธิ์ accessibility)
- **v2.4 (ความทนทาน/การใช้งาน):** self-healing hotkey (`_gk_start()` แยกจาก
  `_start_global_hotkeys` — poller ตรวจ `is_alive` รีสตาร์ตเอง กันยิงรัวด้วย
  `_gk_heal_at`), Safety timeout (Settings "หยุดเองหลังเล่น N นาที" จำลง conf +
  CLI `--max-minutes`), If Image retry window (Additional ต่อท้าย `Ns` ผ่าน
  parse_wait_timeout — ไม่ใส่ = ตรวจครั้งเดียวเหมือนเดิม), ตารางเลือกหลายแถว
  (extended — `_on_del` ลบทั้งชุดได้เลย), Schedule เลือกโปรไฟล์ (`_sched_profile`
  จำ conf — ถึงเวลาโหลดแถวโปรไฟล์ก่อนเล่น), Settings แสดง schedule/plugins status,
  แคช template ใน `find_image_pos` (`_template_cache` ตาม mtime+size), CLI
  `--validate` (engine `validate_rows()` คืน list (แถว, เหตุผล)), CI coverage report
  ใน Step Summary
- **v2.5 (เงื่อนไขครบวงจร/ชุด C):** If Pixel Color (เงื่อนไขสีจุด — runner.execute
  + retry token), Read Pixel Color (อ่านสีเก็บ `{ชื่อ}` — parse 'ชื่อ x,y' เอง
  ห้ามใช้ parse_pixel_spec เพราะมันบังคับมีสี), If Variable (`parse_if_var` —
  เทียบตัวเลข/ข้อความ/~contains; evaluate_condition รับ `variables=` kw แล้ว —
  ⚠️ ไม่มีตัวแปร = เงื่อนไขไม่จริง → ข้าม N), Image Click ตั้ง `{img_x}/{img_y}`,
  Set Variable รับ `rand a-b`, plugin ctx เพิ่ม `"vars"` (ชี้ dict เดียวกับ
  runner.variables — plugin เขียนค่าแถวถัดไปใช้ได้), ชุด C: ลากสลับแถวเต็มรูปแบบ
  (v2.5.1: `_drag_reorder` คำนวณลำดับปลายทาง — วางก่อน/หลังตามครึ่งแถว, autoscroll,
  ลากทั้งก้อนที่เลือก, แถวไฮไลต์ tag "drag", ห้ามวางบนกลุ่มย่อ) ·
  ⚠️ v2.5.2: bind `<Button-1>` ต้องมาก่อน `<ButtonPress-1>` แล้ว drag ผ่าน
  add="+" — ไม่งั้น _on_click (bind ทีหลังไม่มี add) เขียนทับ press binding
  รวมของ event เดียวกัน → _on_drag_start ไม่ถูกเรียก (ต้นตอลากไม่ทำงาน) ·
  🤖 docs/PROMPT.md = พรอมต์มาตรฐานพา AI ตัวใหม่เข้าโปรเจกต์ (เวอร์ชันต้องตรง) +
  Alt+↑↓ + Redo (Ctrl+Y — `_redo_stack`, `_restore_rows` ร่วมกับ undo,
  _apply_edit push undo) + คอลัมน์ Note (COLS/EDIT_COLS/serialize/paste —
  ไม่ส่งเข้า runner) + ค้นหา  แทนที่ (`_replace_all` ใน Ctrl+F dialog) ·
  plugin ใหม่ screenshot/toast/write_log/ask_input (ctx["vars"])
- **v2.7:** **Schedule หลายนัดหมาย** — สถานะใหม่ `self._sched` = dict เดียว
  `{mode, every, times, profile}` (property `_sched_mode/_sched_every/_sched_at/_sched_profile`
  คงไว้ให้โค้ดเก่า — setter/getter join/split comma ให้เอง), โหมด daily รับหลายเวลาคั่น comma
  (`08:00,12:30,22:00`) parse ผ่าน `parse_hhmm_list`/`parse_sched_list` + `sched_migrate`
  (แหล่งเดียวใน engine · conf รูปแบบเก่า sched_mode/every/at/profile ถูก migrate อัตโนมัติ
  · รูปแบบพัง = ปิดอยู่ ไม่มีวันพัง), dialog ใหม่มีปุ่ม 🕐/＋/ล้าง, Export settings เวอร์ชัน 2
  ขน `"sched"` ไปด้วย · **ทำงานร่วม .ahk** — เมนู 🔀 `ahk_dialog` → `ahk_export`/`ahk_import`
  ผ่าน engine `rows_to_ahk`/`ahk_to_rows` (import push undo ให้เอง · export ต้อง 💾 Save ก่อน
  · รองรับ Send/Click/MouseMove/Sleep/Run — แถวไม่รองรับเป็น comment) ·
  **เกณฑ์รีวิว plugin ชุมชน 6 ข้อ** (docs/PLUGINS.md) + scaffold เทสต์ใน `plugins/_template.py` ·
  **เอกสารจีน/ญี่ปุ่น** `docs/TUTORIAL.zh.md` + `TUTORIAL.ja.md` (แปลจาก en ครบทุกบท —
  ⚠️ เอกสารหลักต้องมีเวอร์ชันปัจจุบันทุกไฟล์ — `py tools/check_docs.py` ก่อน push)
- **ฟีเจอร์เสริม v2.8:** Schedule รายเวลาเลือกโปรไฟล์ (ช่องเวลารับ `HH:MM=ชื่อโปรไฟล์` —
  engine `parse_sched_entry`/`sched_time_profiles`, `_sched_check` ยิง tuple `("play", prof)`
  · `_sched_poll` ให้โปรไฟล์ของเวลาชนะตั้งต้น, `parse_hhmm_list` ตัด `=โปรไฟล์` ให้เอง) ·
  **.ahk ตัวแปรสองทิศ** (export `Set Variable` → `n := 5` / `If Variable` → `if (n > 5)` ·
  import `n := 0`/`n += 2`/`if (n > 5)` — ⚠️ กติกา: อ้างตัวแปรเฉพาะรูปแบบ `{ชื่อ}` เท่านั้น,
  ข้อความอื่นครอบ `""` เสมอ แม้ตรง `_VAR_NAME` — กันคำไทยโดนตีความเป็นตัวแปร) ·
  **ประตูรับ plugin ชุมชน** (issue template `plugin_submission.md` + PR checklist เกณฑ์ 6 ข้อ ·
  plugin ตัวอย่างใหม่ random_pause/counter/open_url พร้อมเทสต์ TestPluginsCommunity)
- **ฟีเจอร์เสริม v2.8.1:** ย่อ/ขยายกลุ่มบล็อก Block Start→End (ค้างจาก DESIGN-nested-if —
  กลไก `_section_stash` เดียวกับ Section, `_group_members` หาสมาชิกด้วย
  `find_block_end_index`, กันซ้อนย่อ = ปฏิเสธพร้อมเตือน, ลบหัวที่ย่อ = ขยายคืนก่อน) ·
  **เมนู 🔍 Validate** (`validate_dialog` — engine `validate_rows` เดียวกับ CLI --validate
  รายงาน "แถว N: เหตุผล" เป็นหน้าต่าง) ·
  ⚠️ **แก้บั๊กแฝง v1.22:** `_rows_and_iids_for_play` เดิมอ่านเฉพาะแถวที่มองเห็น → แถวใน
  กลุ่ม/บล็อกที่ย่ออยู่ "ไม่ถูกเล่น" ขัดสัญญา "ย่อแล้วเล่นเหมือนเดิม" — ตอนนี้แทรกแถวซ่อนกลับ
  ตามลำดับ (iid=None = ข้ามไฮไลต์) + ตัดป้าย `(ย่อ N แถว)` ออกจากเงื่อนไขก่อนเล่น —
  ⚠️ เพิ่มกลไกซ่อนแถวใหม่ต้องอัพเดตทั้ง `_serialize` + `_rows_and_iids_for_play` เสมอ
- **ฟีเจอร์เสริม v2.9.0:** START ตรวจก่อนเล่น (`_start_player` เรียก engine `validate_rows`
  เดียวกับ 🔍 Validate — พบปัญหา askyesno ยืนยัน → ข้ามแถวพังจริง (`bad` set index),
  ทุกแถวพัง showinfo ไม่เล่น · ⚠️ กด START แล้วเงียบ = บั๊กที่ห้ามกลับไปเป็นอีก) ·
  **เมนูขวา ย่อทั้งหมด/ขยายทั้งหมด** (`_collapse_all_groups` เดินบนลงล่าง กลุ่มนอกกลืนกลุ่มใน —
  ตรวจ iid ยังอยู่ในตารางก่อนย่อ · `_expand_all_groups` วน toggle หัวที่ย่อ ·
  ⚠️ `_group_members` กัน iid ที่ถูกย่อไปกับกลุ่มนอก — เคย ValueError) ·
  **.ahk บล็อกสองทิศ** (export `_ahk_block_cond` แปลง if-variable → `if (…) {`…`}` /
  `max N` → `Loop, N {` / `until` → `} Until,` — แปลไม่ได้ = prescan `skip_ends` ทำทั้งบล็อก
  comment ไม่มีปีกกาลลอย · import prescan `untils` (`}`+Until บรรทัดเดียวหรือแยกบรรทัด) —
  ⚠️ ลูปหลัก import ต้อง `enumerate(raw_lines)` ให้ `li` ตรงเสมอ) — เทสต์ TestAhkBlocks/
  TestCollapseAll/TestUnifiedPlayValidation
- **ฟีเจอร์เสริม v2.9.1:** log [SKIP] — แถวที่ START-validate/CLI ตรวจไม่ผ่านถูกบันทึก
  "แถว N ถูกข้าม (เหตุผล)" ทุกแถว + สรุปผ่าน/ข้าม (parse_log_stats ไม่นับ [SKIP] เป็น STEP —
  สถิติไม่เพี้ยน) · CLI ตรวจตั้งแต่หัว (`cli_issue_rows` set ตัดแถวพังก่อนเล่น — ทุกแถวพัง
  exit 1) · schedule auto-skip (`_start_player` = wrapper → `_start_player_inner(loop,
  once, auto=False)` — auto=True ไม่เด้งถาม ทุกแถวพัง log แล้วออกเงียบ — ⚠️ เทสต์ที่เคยชี้
  `_start_player` ต้องชี้ inner ให้ครบ) · CHANGELOG.en.md (check_docs บังคับหัวข้อเวอร์ชัน) ·
  ตัวอย่าง examples/13 — เทสต์ TestE2EStartValidateSkip
- **ฟีเจอร์เสริม v2.10:** **Dry-run** (เมนู 🧪 `dry_run_menu` + CLI `--dry-run` — ActionRunner
  รับ `dry_run=True`: แถวใน `_DRY_ACTIONS` ถูกแทนด้วย "DRY-RUN: จะ…" — เงื่อนไข/บล็อก/ตัวแปร
  เดินจริง · GUI: `_start_player_inner(…, dry=)` → `_player(…, dry=)` ตั้ง `runner.dry_run`
  แล้วรีเซ็ตใน finally) · **ผลเงื่อนไขเป็นตัวแปร** (โทเคน `>ชื่อ` ท้าย Additional ของเงื่อนไข
  ทุกชนิด — parse ผ่าน `parse_cond_store` แหล่งเดียว · runner.execute ตัดโทเคนก่อนแตก &&
  แล้วเก็บผ่าน `_save_cond_result` (self.cond_store — เคลียร์ทุกครั้ง) · If Loop/If Time
  เก็บผ่าน dict `variables` ที่ evaluate_condition รับเข้ามา — เมธอดเป็น staticmethod ไม่มี self)
  · **Batch runner** (CLI `--queue LIST.txt` → `cli_queue_run` — ลิสต์บรรทัดละพาธ ข้าม # ·
  ตรวจทุกไฟล์ด้วย validate_rows ก่อนเริ่มเล่น พัง = ยกเลิกทั้งคิว exit 1 · เรียก cli_main ต่อ
  ไฟล์โดยตัด --queue ออกจาก argv (⚠️ ไม่ตัด = วนเรียกตัวเองไม่รู้จบ) · สรุปรายไฟล์ + log
  [QUEUE] · exit code 130 = หยุดโดยผู้ใช้ ไม่นับพัง) · `script` positional เป็น optional
  (nargs="?") — เทสต์ TestDryRunEngine/TestCondStore/TestQueueCli/TestCliDryRun +
  TestQueueDryRunE2E (E2E) + ตัวอย่าง 14/queue_sample.txt เข้า TestAhkBlocks
- **ฟีเจอร์เสริม v2.10.1 (ต่อยอด v2.10):** **รายงาน Dry-run เป็นไฟล์** (`dry_report_path()`
  ข้างโปรแกรมเหมือน log_path — ต้อง patch ในเทสต์เสมอ · `dry_report_block()` pure +
  `dry_report_summary()` นับจาก _DRY_ACTIONS เรียงยาว→สั้น · `dry_report_write()` ทน error
  ทุกจุด คั่นบล็อกบรรทัดว่าง, log mode "DRY" — parse_log_stats ไม่นับเป็น STEP ·
  GUI: `_player` ครอบ `runner.on_message` ตอน dry แล้ว**คืน callback เดิมใน finally เสมอ** ·
  CLI: `_cli_message` ดักบรรทัด DRY-RUN + พิมพ์พาธรายงานหลังแต่ละรอบ) ·
  **เมนู 🗂️ Queue Bat** (`export_queue_batch_files` — เลือกลิสต์ .txt แล้วเขียน .bat/.sh
  ข้างลิสต์ผ่าน `batch_queue_export_bat/sh` · ⚠️ เมธอดสำเร็จต้องแจ้งผ่าน statusbar
  เท่านั้น (เหมือน 📤 Export Bat) — ห้าม showinfo เพราะเทสต์ GUI จะค้างรอ dialog ·
  ยกเลิก = จบเงียบ) · แก้บั๊กเทสต์ date-dependent: TestBackup hardcode วันที่ 2026-09-25
  พังเองเมื่อวันจริงเลย 7 วัน — **วันที่ในเทสต์ต้องคำนวณจาก now เสมอ** · เทสต์
  TestDryReport/TestQueueBatchExport + dry-report GUI ใน TestPlayLoopGui →
  453 unit + 20 E2E = 473
- **ฟีเจอร์เสริม v2.11.0:** **เครื่องมือ log** (engine `cleanup_old_logs(base_dir,
  keep_days=None, archive=True, today=None)` — จัดการ log/dry-report วันเก่าแหล่งเดียว:
  archive=True ย้ายลง `log_archive/YYYY-MM/` แยกโฟลเดอร์รายเดือนจากวันที่ในชื่อไฟล์,
  False = ลบ · **ไฟล์วันนี้ไม่แตะเสมอ** · ชื่อไม่ตรง `_LOG_DAY_RE` ไม่แตะ · ปลายทางมีไฟล์
  = ข้ามไม่ทับ · ทน error ทุกจุดเหมือน backup) · หน้าต่าง 📝 Log: ปุ่ม "เก็บถาวรวันเก่า"/
  "ล้างวันเก่า..." (askyesno ก่อนลบ สำเร็จแจ้ง statusbar เท่านั้น) + dropdown รวม
  `dry_report_*.txt` แล้ว (ของค้าง v2.10.1) · Settings: ☑ จัดการ log วันเก่าตอนปิดโปรแกรม
  + วัน 1–365 + เก็บถาวร/ลบ — conf `log_keep_days` (0 = ปิด) / `log_archive` +
  Export/Import · `_on_close` เรียก cleanup อัตโนมัติเมื่อเปิดฟีเจอร์ ·
  **engine_cli --dry-run เขียนรายงานไฟล์แล้ว** (ของค้าง v2.10.1 — ดัก DRY-RUN เขียนตอน
  finally + พิมพ์พาธ) · ⚠️ fixture เทสต์ที่ใช้ MagicMock แล้วโค้ดอ่าน attr ใหม่ ต้อง set
  attr นั้นใน fixture เอง — `getattr(mock, "x", default)` คืน mock อัตโนมัติ ไม่ใช่ default
  (ทำ json.dump พัง 6 เทสต์ตอนทำ v2.11) · เทสต์ TestLogTools/TestLogToolsGui +
  engine_cli dry-report → 464 unit + 20 E2E = 484
- **ฟีเจอร์เสริม v2.12.0:** **ผู้เล่นคิวแบบ GUI** (เมนู 📑 Run Queue = `queue_run_dialog` —
  เลือกไฟล์ลิสต์ .txt รูปแบบเดียวกับ `--queue` แล้วเล่นทีละไฟล์ในโปรแกรมเลย) ·
  engine `parse_queue_list(list_path)` แหล่งเดียวของไฟล์ลิสต์ (CLI `--queue` refactor
  มาใช้ — ข้อความ/พฤติกรรมเดิมทุกอย่าง) · หน้าต่างสด: ตารางไฟล์ (#/ไฟล์/สถานะ สีตามผล
  tag qrun/qok/qstop/qbad/qskip) + ป้ายไฟล์ปัจจุบัน + กล่องผลลัพธ์ CLI ทันที (เก็บ
  200 บรรทัดล่าสุด) + สรุปท้ายคิว · **เธรดเล่นเรียก `cli_main` จริง** (โลจิก CLI ทุกอย่าง)
  ผลักเหตุการณ์เข้า `self._qr_q` (queue.Queue) ให้ `_queue_run_poll` (after 500ms,
  แพตเทิร์น `_sched_poll`) อัพเดตบน main thread — ⚠️ เธรดแตะเฉพาะ `_qr_q`/
  `_qr_current`/`_qr_stop_*` เท่านั้น · หยุด 2 ระดับ: "หยุดไฟล์นี้" = สร้าง stop-file
  รายไฟล์ (`--stop-file` ของ CLI — `_queue_make_stopfile` ตาม idx กันชนขอบเขตไฟล์)
  เล่นถัดไปต่อ / "หยุดทั้งคิว" + F8/Esc = หยุดทุกไฟล์ที่เหลือ (rc 130 โดยไม่มี flag
  `_qr_stop_file` = ตั้ง `_qr_stop_all` เอง) · stdout ของ CLI ถูกดักด้วย
  `_QueueOutCapture` (ทน stdout=None บน .exe windowed) · ปิดหน้าต่าง/ปิดโปรแกรมขณะ
  เล่น = สั่งหยุดทั้งคิวก่อนเสมอ (`_qr_close_when_done` รอเธรดจบค่อยปิดจริง) ·
  เทสต์ TestQueueListParse/TestQueueRunnerGui (app จริง + patch `am.cli_main` —
  รวม E2E ผ่าน cli_main จริงแบบ Beep ล้วน) → 477 unit + 20 E2E = 497
- **ฟีเจอร์เสริม v2.13.0:** **Plugin API v3 — เงื่อนไขจาก plugin** (plugin ประกาศ
  `CONDITION_NAME` + `check(ctx, row) -> bool` — โหลดผ่าน `load_plugins()` แหล่งเดิม,
  เงื่อนไขเก็บ `load_plugins.last_conditions` = [(ชื่อ, module)], ชื่อซ้ำกันข้าม
  Action/เงื่อนไขทั้งสองทิศ = ข้ามไฟล์เก็บ last_failed) · จับชื่อใน Action ผ่าน
  `match_condition_name(text, names)` (จับ "ชื่อ [อาร์กิวเมนต์]" ชื่อยาวสุดมาก่อน) ·
  `ActionRunner` รับ `conditions=` + เมธอดใหม่ `_plugin_ctx()` (refactor ctx แหล่งเดียว)/
  `_match_cond()`/`_run_cond_check()` (check พัง = เตือน "#c00" คืน False)/
  `evaluate_plugin_condition(btn, r)` คืน (skip_n, message) — ผ่านทุกจุดเล่น GUI/CLI
  (เรียกก่อน fallback `evaluate_condition`), รองรับโทเคน `>ชื่อ` เก็บผลเงื่อนไขเหมือนเงื่อนไขในตัว ·
  `evaluate_block_condition` ผสม `&&` กับเงื่อนไข plugin ได้ · validate/dry-run/ค้นหา/
  สีแถว (`row_tag(button, cond_names=())` tag "cond")/`.ahk` export
  (`rows_to_ahk(rows, condition_names=())` — บล็อกที่มีชิ้นเงื่อนไข plugin = comment ทั้งบล็อก)
  รับชื่อเงื่อนไขครบ · ตัวอย่าง `plugins/file_exists.py` (File Exists) + `examples/14` +
  เทสต์ TestConditionPlugins/TestConditionPluginsGui/TestConditionPluginsCli →
  493 unit + 20 E2E = 513
- **ฟีเจอร์เสริม v2.14.0:** **plugin เงื่อนไขสำเร็จรูป 3 ตัว** (Internet Up — socket
  stdlib ล้วน ค่าเริ่ม 1.1.1.1:443 รอ 2 วิ token `host[:port]`/`Ns` · Process Running —
  tasklist /FO CSV (Windows) / pgrep -f (Linux/macOS) เทียบไม่สนตัวพิมพ์+ตัด .exe ·
  Window Exists — ctypes EnumWindows+GetWindowTextW (Windows) / xdotool (Linux) —
  ทุกตัวทน error คืน False เสมอ ไม่เพิ่ม dependency) · **ปุ่ม 🧩 เงื่อนไข plugin**
  (`_insert_cond_plugin` — combobox ชื่อเงื่อนไข sorted + ช่องอาร์กิวเมนต์ แทรกแถวใต้แถวเลือก
  พร้อม `_push_undo` + `row_tags(..., cond_names)` + `refresh_nums()`; ไม่มี plugin
  เงื่อนไข = ไม่สร้างปุ่ม) · **CLI `--dry-report PATH`** (`dry_report_write(lines,
  src=None, path=)` — path= ทับ `dry_report_path()`, `{date}` แทนวันที่วันนี้ใน engine
  เสมอ; ทั้ง CLI หลักและ engine_cli — ใช้ลำพังไม่มี --dry-run = เตือนและไม่มีผล) ·
  ตัวอย่าง `examples/15_system_conditions.json` + เทสต์ 13 ตัว (TestDryReportPath 5 +
  TestPluginsV14 5 + TestInsertCondPluginGui 3) → 506 unit + 20 E2E = 526 ·
  ⚠️ ตัวอย่างที่เล่นจริงในเทสต์ต้องเป็นกลาง platform — เงื่อนไขที่ผลต่างตาม OS
  (Process Running `explorer` เจอเฉพาะ Windows) ห้ามอยู่หน้าแถวที่ต้องตัดสินเอง
  (skip ค้างกลืน) และห้ามอ้างชื่อหน้าต่าง/โปรเซสที่มีเฉพาะบาง OS ·
  ⚠️ เทสต์ GUI ต้องยกเลิก timer `after` ค้างก่อน destroy root (คลาส `_Tk` ในไฟล์เทสต์ —
  spam "invalid command name" และบน macOS แตก SIGTRAP exit 133)

## เทคโนโลยี

| ส่วน | เทคโนโลยี |
|---|---|
| ภาษา | Python 3.8+ (แนะนำ 3.12 ขึ้นไป — เครื่องพัฒนาใช้ 3.14) |
| GUI | Tkinter (มากับ Python, ไม่ต้องติดตั้งเพิ่ม) + ttk.Treeview |
| ควบคุมเมาส์/คีย์บอร์ด | `pynput` >= 1.7.6 |
| Image Click (ตัวเลือก) | `opencv-python` + `Pillow` (ไม่ติดตั้งก็ใช้ส่วนอื่นได้) |
| Build .exe | PyInstaller (ไฟล์ spec: `auto_macro.spec`) |
| ทดสอบ | `unittest` (รัน: `py -m unittest test_auto_macro -v`) |
| Platform เป้าหมาย | Windows (โค้ดรองรับ Linux/macOS ด้วยไลบรารีเดียวกัน) |

## โครงสร้างไฟล์

```
├── auto_macro.py        # โปรแกรมหลัก (GUI, recorder, player) — บล็อก ENGINE sync จาก macro_engine.py
├── macro_engine.py      # engine ล้วน (ค่าคงที่/parser/คลิปบอร์ด/unicode/log/stats/plugins) ไม่มี Tk (v2.0)
├── build_singlefile.py  # รวม macro_engine.py กลับเป็น auto_macro.py — รันก่อน build .exe เสมอ
├── test_auto_macro.py   # unit tests (unittest)
├── auto_macro.spec      # PyInstaller spec → build dist/AutoMouseMacro.exe
├── build.bat            # สคริปต์ build .exe อัตโนมัติ
├── run.bat              # รันโปรแกรมจากซอร์สด้วย py
├── requirements.txt     # pynput + opencv-python + Pillow
├── docs/
│   ├── README.md / .html
│   ├── RESEARCH.md / .html
│   ├── CHANGELOG.md / .html
│   └── images/               # รูปประกอบเอกสาร (screenshot.png, demo.gif ฯลฯ)
└── dist/AutoMouseMacro.exe   # ผลลัพธ์ build (สร้างโดย build.bat)
```

> ไฟล์ runtime ที่โปรแกรมสร้างเอง (ไม่ commit): `macro_conf.json`, `macro_profiles.json`,
> `__pycache__/`, `build/`, `dist/` — ดู `.gitignore`

## คำสั่งที่ใช้บ่อย

```bash
py -m pip install -r requirements.txt   # ติดตั้งไลบรารี
py auto_macro.py                        # รันจากซอร์ส (หรือ run.bat)
py -m unittest test_auto_macro -v       # รัน unit tests
py auto_macro.py script.json            # เล่นสคริปต์แบบ CLI (ไม่เปิด GUI)
build.bat                               # build .exe (หรือ: py -m PyInstaller auto_macro.spec --noconfirm --clean)
```

> เครื่องนี้ `python` ใน PATH เป็น stub ของ Windows Store — **ใช้ `py` launcher แทนเสมอ**

## สถาปัตยกรรมภายใน auto_macro.py

- **`MacroApp`** — คลาสหลัก สร้าง UI ทั้งหมด (เมนูไอคอน, ตาราง Treeview, ปุ่ม START/STOP/REPEAT/RECORD, statusbar)
- **โมเดลข้อมูล:** แต่ละแถวในตาราง = เหตุการณ์ 1 รายการ
  `enabled(☑) / # / X / Y / Button(Action) / Additional / Mins / Secs / Repeat`
  - คอลัมน์ `chk` เป็น checkbox จำลองด้วยอักขระ ☑/☐ (คลิกเพื่อสลับ)
- **Recorder:** `pynput` Listener (เธรดแยก) จับ mouse click + key press ระหว่าง RECORD
  - **ข้อควรระวัง:** listener thread ห้ามเรียก Tk API ตรง ๆ — ต้องผลักข้อมูลเข้า
    `self._pending_rows` / `self._live_pos` / `self._live_key` แล้วให้ UI poller
    (`_start_poller` ทุก 120 ms) ค่อยมาอัพเดตหน้าจอ — นี่คือรูปแบบ thread-safe ของโปรเจกต์นี้
- **Player:** `threading.Thread` ไล่เล่นแถวที่ ☑ ตามลำดับ: `sleep(Mins*60+Secs)` →
  ทำเหตุการณ์ (เมาส์: ย้ายพิกัด + press/release/click, คีย์: press/release/tap) วนตาม `Repeat`
  - `STOP` ตั้ง `self.running = False` — ลูปเช็คทุกจุดและออกเอง
  - หยุดแม่นยำ (v1.7.1+): `_sleep_check` แบ่ง sleep ชิ้นละ 50 ms, `_play_gen`
    (generation counter) กันเล่นซ้อนเธรด, คีย์/ปุ่มค้างอยู่ใน `ActionRunner.pressed_keys/
    pressed_btns` แหล่งเดียว — STOP เรียก `_release_stuck` → `runner.release_all()`
    (v2.2.1: ลบ `_pressed_keys` กลไกเก่าออกแล้ว · GUI และ CLI ทำเหมือนกัน)
  - CLI หยุดได้ 4 ช่องทาง: F8/Esc ผ่าน Listener, Esc/q จากคอนโซล (msvcrt),
    Ctrl+C, และ `--stop-file`
  - CLI `--watchdog N`: จบแล้วหน่วง N วิแล้วเริ่มใหม่ (ปล่อยคีย์ค้าง+log ทุกรอบ) —
    หยุดถาวรได้ทุกช่องทางหยุด
- **Hotkey:** Tk binding (เมื่อโฟกัส) + `keyboard.Listener` จับคู่คีย์เอง (กดได้แม้ไม่โฟกัส —
  เธรดแยก ห้ามแตะ Tk ตรง ๆ ต้อง `root.after(0, ...)` ผลักงานเข้า main thread)
  F6 เล่น / F8 หยุด / F9 บันทึก / F10 วนซ้ำไม่จำกัด / F1–F4 hot-profile
- **Hot-profile:** `self._hp_dir` (โฟลเดอร์จากเมนู ⚡, จำใน macro_conf.json) — F(n) โหลด
  ไฟล์ .json ลำดับที่ n เรียงตามชื่อ (`_hot_profile_load`) แล้วเรียก `_start_player(False)`
  เสมอผ่าน `root.after(0, ...)` ตามรูปแบบ thread-safe
- **เมนู:** `_menu_items()` (classmethod) คืนรายการ (icon, label, method, color) —
  เพิ่มปุ่มเมนูใหม่ที่นี่และทดสอบว่าเมธอดมีจริงด้วย `TestMenuItems`
  ⚠️ **อย่ากลับไปใช้ `GlobalHotKeys`** — พิสูจน์แล้ว (v1.8) ว่าบน pynput 1.8.x บางเครื่อง
  listener เริ่มทำงาน (`alive=True`) แต่ไม่ยิง callback แม้กดคีย์จริง; `keyboard.Listener`
  ธรรมดารับเหตุการณ์ได้ปกติ
- **Log:** `log_write(mode, message, src)` เขียน `macro_log_YYYY-MM-DD.txt` (หมุนรายวัน,
  ตัดเกือบเหลือ 500 บรรทัดด้วย `prune_log`) — โหมด START/STEP/STOP/END ทั้ง GUI
  (คุมด้วย `self._log_enabled` จาก Settings, จำใน macro_conf.json) และ CLI (`--no-log`)
  ดูย้อนหลังจากในโปรแกรมได้ด้วย `view_log()` (เมนู 📝 Log) และสรุปสถิติด้วย
  `view_stats()` (เมนู 📊) ที่อ่านผ่าน `log_stats_summary()`
- **Self-check:** `_self_check()` รันตอน __init__ เก็บผลใน `self._checks`
  (mouse/hotkey/opencv/admin/conf_writable) — แสดงผลผ่าน `self_check_text()` ใน Settings
  พร้อมปุ่ม 🧪 ทดสอบระบบจริง (self_test ใน settings_dialog — ขยับเมาส์/บี๊บให้ผู้ใช้ยืนยันเอง)
- **Export/Import:** `export_settings()`/`import_settings()` — ไฟล์เดียวรวม rows +
  profiles + log_enabled + hot_profile_dir (ตรวจ `kind=automousemacro-settings` ก่อนนำเข้า)
- **Backup:** `_on_close` เรียก `_on_close_backup()` → `backup_snapshot()` เขียน
  backups/backup_วันที่_เวลา.json แล้ว `prune_backups()` ลบเก่าตาม `self._backup_days`
  (เปิด/ปิดด้วย `self._backup_enabled` — จำใน macro_conf.json) — ทน error ทุกจุด
- **i18n:** ข้อความปุ่ม/สถานะหลัก + dialog ทุกตัวอยู่ใน `TR` (th/en) — ใช้ `self._t("key")`
  สลับผ่าน `_apply_language()` ตอนบันทึก Settings (เพิ่มข้อความใหม่ใส่ทั้งสองภาษาเสมอ)
- **E2E tests:** `test_e2e.py` รัน CLI จริงเป็น subprocess (สคริปต์ Beep ล้วนปลอดภัย) —
  ทดสอบหยุดผ่าน stop-file กลางดีเลย์ยาว/จบเอง/หยุดก่อนเริ่ม รัน: `py -m unittest test_e2e -v`
  ห้ามถือว่า listener ใช้ได้เพราะ `alive=True` — ต้องทดสอบด้วยการกด/หยุดจริง
- **โปรไฟล์:** `macro_profiles.json` เก็บ dict ชื่อโปรไฟล์ → รายการแถว
  แถบเลือกโปรไฟล์อยู่ใต้เมนู (สร้าง/เปลี่ยนชื่อ/ลบ/สลับ — สลับก่อนบันทึกของเดิมอัตโนมัติ)
- **Schedule:** เธรด `_sched_loop` ตรวจเวลาทุก 5 วิ ผลักคำสั่งเข้า `queue.Queue` →
  UI poller (`_sched_poll` ทุก 500 ms) หยิบมาเล่น — โหมด "ทุก N นาที" และ "รายวัน HH:MM"
- **Plugins (v1.16):** `load_plugins()` โหลด `plugins/*.py` (เรียงชื่อ, ไฟล์ขึ้นต้น `_` = ข้าม)
  — แต่ละไฟล์ประกาศ `ACTION_NAME` + `run(ctx, row)`; ctx = {mouse, kb, log(ข้อความ), cfg}
  ผูกเข้า GUI (dropdown Action + `_plugin_module` ตอนเล่น + `_validate_rows` ยอมรับ) และ
  CLI (`cli_plugins` เล่นจริง พร้อม print รายชื่อในหัวโปรแกรม) — ไฟล์พัง/ไม่มี ACTION_NAME/
  ชื่อซ้ำกับ ACTIONS_ALL → ข้ามไฟล์นั้น (เก็บใน `load_plugins.last_failed`) โปรแกรมไม่พัง
  ตัวอย่าง: `plugins/sleep_seconds.py`, `plugins/message_box.py`, `_template.py` + คู่มือ
- **Image Click:** Action `Image Click` + ช่อง Additional = ไฟล์ .png หรือ
  `ไฟล์.png@x,y,กว้าง,สูง` (Search Area — `_parse_search_area` แยก path/กรอบจาก @;
  cv2.matchTemplate, threshold 0.80, คลิกจุดศูนย์กลาง; ปิดฟีเจอร์อัตโนมัติถ้าไม่มี opencv)
- **examples/:** สคริปต์ตัวอย่างสำเร็จรูป 4 ไฟล์ + target.png (ป้ายทดสอบ Image Click)
  — validate ผ่าน `ACTIONS_ALL`/`parse_key` ของโค้ดจริงเสมอก่อน commit
- **Actions v1.5:** Scroll Up/Down (จำนวนใน Additional), Double Click, Ctrl/Shift/Alt+Click
  (press mod → click → release ใน finally), Move Mouse (+Offset), Save/Restore Cursor
  (`self._saved_pos`), Type Text (tap ทีละตัวอักษร), Launch App (`os.startfile`),
  Wait for Image (วนทุก 0.5 วิ timeout 30 วิ), Beep (`root.bell()`)
- **ดีเลย์สุ่ม:** `delay_range(secs)` คืน (lo, hi) — Secs "1-3" = สุ่ม 1–3 วิ;
  คูณความเร็ว (`self._speed_mult`) หารหลังสุ่ม; จำนวนรอบสคริปต์ = `self._script_loops`
  (0 = ไม่จำกัด); คืนเมาส์จุดเดิม = `self._restore_pos` (เริ่มจากตำแหน่งตอนกด START)
- **Save/Load:** JSON รายแถว ฟิลด์ `enabled,x,y,button,additional,mins,secs,repeat`
  - เปิด/ปิดโปรแกรมจะ autosave/autorestore ที่ `macro_conf.json` (อยู่ข้างสคริปต์)
- **`parse_key()`:** แปลงข้อความ Additional → ออบเจ็กต์คีย์ pynput (รองรับชื่อพิเศษ เช่น
  esc/ctrl/pgup/prtsc, ตัวอักษรเดี่ยว, ตัวเลข = virtual key code)

## ข้อตกลงการเขียนโค้ด

1. **เก็บทุกอย่างใน `auto_macro.py` ไฟล์เดียว** — อย่าแยกโมดูลเว้นแต่ผู้ใช้ขอ
2. คอมเมนต์/ข้อความ UI/เอกสาร เป็น**ภาษาไทย**; ชื่อตัวแปร/ฟังก์ชัน เป็นภาษาอังกฤษ
3. ไม่เพิ่ม dependency ใหม่โดยไม่จำเป็น (มาตรฐาน: stdlib + pynput เท่านั้น)
4. โค้ดที่เกี่ยวกับ Tk ต้องรันบน main thread เท่านั้น — สื่อสารข้ามเธรดผ่าน dict สถานะ + poller
5. แก้ UI ตารางแล้วต้องเรียก `refresh_nums()` เสมอ
6. ทดสอบหลังแก้เสมอ: `py -m py_compile auto_macro.py`, `py -m unittest test_auto_macro -v`
   และรัน `py auto_macro.py` สั้น ๆ (ใช้ `timeout 6 py auto_macro.py` แล้วเช็ค stderr)
7. เพิ่มฟีเจอร์/แก้บั๊ก → อัพเดต `docs/CHANGELOG.md` + `.html` ด้วยเวอร์ชันใหม่ด้านบนสุด

## เอกสาร (docs/)

- ทุกเอกสารทำเป็นคู่ **.md + .html** (HTML สวยงาม เปิดในเบราว์เซอร์ได้ทันที) **ภาษาไทย**
- HTML ใช้ CSS inline ในไฟล์ ไม่พึ่ง CDN (เปิดออฟไลน์ได้) ธีมสีเขียว/ฟ้าตามโปรแกรม
- รูปประกอบอยู่ที่ `docs/images/` — อ้างแบบ relative (`images/screenshot.png`)
- อัพเดต CHANGELOG ทุกครั้งที่เพิ่มฟีเจอร์/แก้บั๊ก โดยเพิ่มเวอร์ชันใหม่ด้านบนสุด

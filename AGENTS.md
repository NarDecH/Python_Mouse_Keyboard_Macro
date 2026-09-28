# AGENTS.md — Python Mouse Keyboard Macro

> เวอร์ชันปัจจุบัน: v1.18.1 — ดู `docs/CHANGELOG.md`

แนวทางการทำงานสำหรับ AI agent และนักพัฒนาในโปรเจกต์นี้

## ภาพรวมโปรเจกต์

- **ชื่อ:** Auto Mouse & Keyboard Macro v1.6
- **ไฟล์หลัก:** `auto_macro.py` (ไฟล์เดียวจบ — GUI + engine ในไฟล์เดียว)
- **แรงบันดาลใจ:** โปรแกรม "Auto Mouse v1.3" (ดูรูปตัวอย่าง `pic.png` / `docs/images/pic.png`)
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
├── auto_macro.py        # โปรแกรมหลักทั้งหมด (GUI, recorder, player)
├── test_auto_macro.py   # unit tests (unittest)
├── auto_macro.spec      # PyInstaller spec → build dist/AutoMouseMacro.exe
├── build.bat            # สคริปต์ build .exe อัตโนมัติ
├── run.bat              # รันโปรแกรมจากซอร์สด้วย py
├── requirements.txt     # pynput + opencv-python + Pillow
├── pic.png              # รูปตัวอย่างต้นแบบ
├── docs/
│   ├── README.md / .html
│   ├── RESEARCH.md / .html
│   ├── CHANGELOG.md / .html
│   └── images/pic.png
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
    (generation counter) กันเล่นซ้อนเธรด, `_pressed_keys`/`_pressed_btns` ปล่อยคีย์/ปุ่ม
    ค้างตอน STOP (GUI และ CLI ทำเหมือนกัน)
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
- รูปประกอบอยู่ที่ `docs/images/` — อ้างแบบ relative (`images/pic.png`)
- อัพเดต CHANGELOG ทุกครั้งที่เพิ่มฟีเจอร์/แก้บั๊ก โดยเพิ่มเวอร์ชันใหม่ด้านบนสุด

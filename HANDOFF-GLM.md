# 🤝 HANDOFF → GLM (z code) — สรุปโปรเจกต์ + กฎเหล็ก + ทิศทางต่อไป

> เขียนเมื่อ 3 ต.ค. 2026 หลังปล่อย **v2.10.1** (commit `a71d4a4`) —
> อ่านคู่กับ `AGENTS.md` (สถาปัตยกรรม/ประวัติทุกเวอร์ชัน) และ `docs/PROMPT.md` (พรอมต์มาตรฐาน
> + กฎเหล็ก 10 ข้อจากบั๊กจริง) ก่อนลงมือทุกครั้ง · เวอร์ชันปัจจุบันดูที่ `__version__` ใน
> `macro_engine.py` ต้นไฟล์เสมอ (อย่าเชื่อเลขในไฟล์อื่นที่อาจค้าง)

---

## 1) โปรเจกต์คืออะไร

**Auto Mouse & Keyboard Macro** — โปรแกรม Python/Tkinter บันทึก+เล่นซ้ำเมาส์/คีย์บอร์ด
แบบตารางคำสั่ง (มีเงื่อนไข If Image/Pixel/Variable/Loop/Time, ตัวแปร, บล็อกซ้อน, ปลั๊กอิน,
schedule, .ahk สองทิศ, CLI ครบ) · แจกเป็น `.exe` ไฟล์เดียวผ่าน GitHub Releases

- repo: `github.com/NarDecH/Python_Mouse_Keyboard_Macro` (branch `main`)
- ไฟล์หลัก: `auto_macro.py` (GUI+CLI) + `macro_engine.py` (engine ล้วน ไม่มี Tk)
- เทสต์: 453 unit (`test_auto_macro.py`) + 20 E2E (`test_e2e.py`) = **473 ผ่านหมด**
- CI: Tests (Windows matrix + ubuntu/macos E2E) + Docs Check — เขียวทุก workflow
- Release ล่าสุด: tag `v2.10.1` → `release.yml` build `AutoMouseMacro.exe` อัตโนมัติ

## 2) กฎเหล็ก (ผิด = บั๊กระดับ release พัง — เคยเจอมาแล้วทุกข้อ)

1. **แก้ engine ที่ `macro_engine.py` เท่านั้น** แล้วรัน `py -X utf8 build_singlefile.py`
   ซิงก์เข้าบล็อก ENGINE-BEGIN/END ใน `auto_macro.py` ก่อน build .exe — ห้ามแก้บล็อกใน
   auto_macro.py ตรง ๆ (เทสต์ TestEngineSplit จับตอน sync ไม่ตรง)
2. **ใช้ `py -X utf8` เสมอ** (`python` ใน PATH เครื่องนี้เป็น stub ของ Windows Store)
3. **เธรดอื่นห้ามเรียก Tk** — ผลักงานผ่าน `self._ui_state` + poller หรือ `root.after(0, …)`
   (โครงแบบเดียวของโปรเจกต์นี้ — recorder/player/hotkey/schedule ทำตามนี้ทั้งหมด)
4. **ฟังก์ชัน log/รายงาน/backup ต้องทน error ทุกจุด** (try/except ครบ) — ของรองห้ามทำ
   โปรแกรมพัง
5. **เวอร์ชันแหล่งเดียว** `__version__` ใน macro_engine.py → bump แล้วต้อง sync + แก้
   README ×3 + TUTORIAL th/en/zh/ja footer + TUTORIAL.html + README.html (title/hero/footer)
   + หัวข้อ `## [X.Y.Z]` ใน CHANGELOG.md + CHANGELOG.en.md (การ์ดใหม่บนสุด) + CHANGELOG.html
   + AGENTS.md หัว+bullet — สรุป: **รัน `py -X utf8 tools/check_docs.py` ให้ผ่านก่อน push
   ทุกครั้ง** (มันจับลิงก์พัง + เวอร์ชันค้าง + หัวข้อซ้ำให้อัตโนมัติ)
6. **เมนูใหม่ต้องผ่าน `_menu_items()`** + มีเมธอดจริง (TestMenuItems ตรวจ) · เมธอดสำเร็จ
   **แจ้งผ่าน statusbar เท่านั้น ห้าม messagebox.showinfo ตอนสำเร็จ** — เทสต์ GUI จะค้างรอ
   dialog จริง (เจอตอนทำ 🗂️ Queue Bat) · ถาม/เตือน (ยืนยัน/ลบ) ใช้ messagebox ได้ปกติ
7. **เทสต์ห้าม hardcode วันที่** — คำนวณจาก `datetime.now()` เสมอ (TestBackup เคยพังเอง
   เมื่อวันจริงเลย 7 วัน) · **เทสต์ที่ patch log/report path ต้อง patch ฟังก์ชันพาธ**
   (`log_path`/`dry_report_path`) — ห้ามปล่อยเขียนไฟล์ทิ้งข้างโค้ด
8. **เทสต์ E2E patch พาธด้วย `os.path.join` เสมอ** — แบ็กสแลชเดี่ยวพังบน Linux/macOS CI
9. **ข้อความ UI ใหม่ใส่ `TR` ทั้ง th/en** · คอมเมนต์/เอกสารภาษาไทย, ตัวแปร/ฟังก์ชันอังกฤษ
10. **ทุกฟีเจอร์ต้องมีเทสต์** — รันชุดเต็มก่อน commit เสมอ:
    `py -X utf8 -m unittest test_auto_macro test_e2e 2>&1 | grep -E "^(Ran|OK|FAILED)"`

## 3) คำสั่งที่ใช้บ่อย

```bash
py -X utf8 -m unittest test_auto_macro test_e2e 2>&1 | grep -E "^(Ran|OK|FAILED)"   # ชุดเต็ม (473)
py -X utf8 tools/check_docs.py                      # เอกสาร: ลิงก์/เวอร์ชัน/หัวข้อ CHANGELOG
py -X utf8 build_singlefile.py                      # sync engine → auto_macro.py (ก่อน build .exe เสมอ)
timeout 10 py -X utf8 auto_macro.py 2>err.tmp       # smoke: exit=124 + stderr ว่าง = ผ่าน
py -X utf8 auto_macro.py script.json --dry-run      # ซ้อมเล่น (ออกรายงาน dry_report_วันที่.txt)
py -X utf8 auto_macro.py --queue list.txt           # รันหลายสคริปต์ต่อกัน
build.bat                                           # build dist/AutoMouseMacro.exe
```

เฝ้า CI ผ่าน API (ใช้ `git credential fill` เอง):

```bash
TOKEN=$(printf "protocol=https\nhost=github.com\n" | git credential fill | grep ^password= | cut -d= -f2)
curl -s -H "Authorization: token $TOKEN" "https://api.github.com/repos/NarDecH/Python_Mouse_Keyboard_Macro/actions/runs?head_sha=<SHA>" | py -X utf8 -c "import json,sys; [print(r['name'],r['status'],r['conclusion']) for r in json.load(sys.stdin)['workflow_runs']]"
```

## 4) สถานะล่าสุด — สิ่งที่ทำไปแล้ว (v2.10.1, commit `a71d4a4`)

- **รายงาน Dry-run เป็นไฟล์** — จบ dry-run เขียน `dry_report_วันที่.txt` ข้างโปรแกรม:
  engine เพิ่ม `dry_report_filename/path/block/summary/write` (block = pure, summary นับ
  จาก `_DRY_ACTIONS` เรียงยาว→สั้น, write ทน error + คั่นบล็อกบรรทัดว่าง, log mode "DRY"
  ไม่นับเป็น STEP) · GUI `_player` ครอบ `runner.on_message` ตอน dry แล้วคืน callback เดิม
  ใน finally เสมอ · CLI `_cli_message` ดักบรรทัด DRY-RUN + พิมพ์ "รายงาน Dry-run: <path>"
  หลังแต่ละรอบ · ถูกหยุดกลางคันก็บันทึกส่วนที่เดินผ่าน · ไฟล์เข้า .gitignore แล้ว
- **เมนู 🗂️ Queue Bat** — `export_queue_batch_files`: เลือกลิสต์ .txt → เขียน .bat/.sh
  ข้างลิสต์ผ่าน engine helpers ใหม่ `batch_queue_export_bat/sh` (สไตล์เดียวกับ v2.3)
  ดับเบิลคลิกรัน `--queue` ทั้งชุด
- **TUTORIAL บทที่ 14** (ไทย + อังกฤษ) / บทที่ 17 ใน HTML — บทเรียนเชิงลึก v2.10 ครบ
  3 ฟีเจอร์ (Dry-run/ผลเงื่อนไขเป็นตัวแปร `>ชื่อ`/Batch runner `--queue`) + แบบฝึกหัด 3 ข้อ
  · zh/ja เพิ่มสรุปสั้น + footer เวอร์ชัน
- **ROADMAP** — ปิดชุดข้อเสนอ v2.10 ครบ + เปิดชุด **ข้อเสนอ v2.11** 3 ข้อ (ดูหัวข้อ 5)
- **แก้บั๊กเทสต์ date-dependent** — TestBackup hardcode วันที่ 2026-09-25 พังเองตอน
  วันจริงเลย 7 วัน → คำนวณจาก `now()` แล้ว (กฎข้อ 7)
- เทสต์ใหม่ 10 ตัว: TestDryReport(4) + TestQueueBatchExport(5) + dry-report เล่นจริงใน
  TestPlayLoopGui(1) + assertion รายงานใน E2E → 473 ผ่านหมด · check_docs ผ่าน ·
  commit `a71d4a4` push แล้ว · CI: Docs Check เขียวทันที, Tests กำลังรันตอนเขียนไฟล์นี้
  · **ถ้ายังไม่ได้แท็ก: push แล้วเฝ้า CI ให้เขียว → tag `v2.10.1` → ตรวจ Release มี .exe**
  (ตามขั้นตอนหัวข้อ 6)

## 5) ทิศทางต่อไป — ทำอะไรได้เลย

ตาม ROADMAP (`docs/ROADMAP.md` หัว "ข้อเสนอ v2.11") เรียงตามควรทำก่อน:

1. **เครื่องมือ log เพิ่ม** (ระดับเล็ก — แนะนำเริ่มตัวนี้) — เมนู/ปุ่มเปิดโฟลเดอร์ log,
   เคลียร์วันเก่า, เก็บถาวรรายเดือน · ใช้รูปแบบเดียวกับ backup (ทน error + ตั้งค่าใน
   Settings + จำใน conf)
2. **ผู้เล่นคิวแบบ GUI ติดตามผล** (ระดับกลาง) — ตอนนี้ `--queue` อยู่เฉพาะ CLI ·
   หน้าต่างดูคิวแบบสด (ไฟล์ปัจจุบัน/ผลรายไฟล์) + ปุ่มหยุดไฟล์นี้/หยุดทั้งคิว —
   ต่อยอดจาก 🗂️ Queue Bat ที่เพิ่งทำ · ⚠️ ระวังกฎข้อ 3 (ผลักสถานะผ่าน `queue.Queue` +
   poller เหมือน `_sched_poll` ไม่ใช่เรียก Tk จากเธรด)
3. **Plugin เป็นเงื่อนไขได้ — Plugin API v3** (ระดับใหญ่) — plugin ประกาศ
   `CONDITION_NAME` + `check(ctx, row) -> bool` ใช้ใน Block Start/If ได้ · ต้องออกแบบ
   ผ่าน `validate_rows` + dry-run + .ahk export ให้ครบก่อนทำ (แนวเดียวกับเงื่อนไขในตัว)
4. **ของเล็กที่ค้างไว้ให้ (เก็บจาก v2.10.1):** `engine_cli.py` ยังไม่เขียนรายงาน dry-run
   (ตัวหลักทำแล้ว) · พิจารณา flag `--dry-report PATH` ถ้าผู้ใช้ขอเลือกที่เก็บ ·
   dry-report ยังไม่มีที่ดูใน GUI (อาจเพิ่มเมนู 📝 Log ให้เห็น dry_report_*.txt ด้วย)

หลักคิดตอนเพิ่มฟีเจอร์: กลไกหลักลง **engine** (ทดสอบแยกได้) · GUI จูนเฉพาะการแสดงผล ·
เงื่อนไข/บล็อกทุกชนิดต้องเดินได้ใน **dry-run** ด้วย · เพิ่ม parser ใหม่ = อย่าลืม
`validate_rows` + `.ahk` export (ถ้าเกี่ยว)

## 6) ขั้นตอนปล่อยเวอร์ชัน (ทำตามลำดับ — เคยทำจนจบ v2.10.0 และ v2.10.1)

1. แก้โค้ด+เทสต์+เอกสาร → ชุดเต็ม 473+ OK + check_docs ผ่าน + smoke ผ่าน
2. bump `__version__` ใน macro_engine.py → `py -X utf8 build_singlefile.py` → แก้เอกสาร
   ทุกจุดตามกฎข้อ 5 (check_docs เป็นผู้ตัดสิน)
3. commit สไตล์ `vX.Y.Z: <สรุปไทย>` ลงท้ายบรรทัด:

   ```
   🤖 Generated with Codebuff
   Co-Authored-By: Codebuff <noreply@codebuff.com>
   ```

4. `git push origin main` → เฝ้า CI ด้วยคำสั่งหัวข้อ 3 จนทุก workflow เขียว
   (Tests ใช้เวลา ~5-8 นาที, Docs Check เร็ว)
5. `git tag vX.Y.Z && git push origin vX.Y.Z` → `release.yml` build .exe อัตโนมัติ
   (release-notes.yml ดึงหัวข้อ CHANGELOG เป็น body)
6. ตรวจ Release: `curl -s -H "Authorization: token $TOKEN" https://api.github.com/repos/NarDecH/Python_Mouse_Keyboard_Macro/releases/tags/vX.Y.Z`
   — ต้องมี asset `AutoMouseMacro.exe` (~71MB) + notes

## 7) บทเรียนบั๊กสำคัญ (รายละเอียดเต็มใน AGENTS.md — อ่านส่วน ⚠️ ทั้งหมดก่อนแก้โค้ด)

- กด START แล้วเงียบ = ร้ายแรงที่สุด (v1.18.1) — ทุกเทสต์ player ต้องเล่นจริง อย่า mock
  `_start_player`
- เทสต์ "เปิด dialog ได้" ไม่พอ — ต้องมี "เปิด + ใช้งานจริง" อย่างน้อย 1 ตัว (บั๊ก
  HotkeyEdit อยู่รอด 6 เวอร์ชันเพราะเทสต์แค่เปิด)
- คลาสเทสต์ชื่อซ้ำ = คลาสหลังบังคลาสหน้า (เทสต์หายเงียบ ๆ) — ตรวจด้วย
  `grep -c "class Test" test_auto_macro.py` เทียบจำนวนที่รัน
- listener ที่ `alive=True` ≠ ทำงาน — E2E ต้องกด/หยุดจริงเสมอ
- พิมพ์ข้อความใช้ Unicode path (`send_unicode_char`) เท่านั้น ห้ามกลับไป virtual key
- ลิงก์ใน docs/*.md ที่อยู่นอกโฟลเดอร์ตัวเองต้องมี `../` นำหน้า — check_docs ตรวจให้

---

*ถ้าอ่านจบแล้ว: เริ่มจาก `AGENTS.md` + `docs/PROMPT.md` → เลือกงานจากหัวข้อ 5 → ทำตาม
ขั้นตอนหัวข้อ 6 จน Release · คำถามยอดฮิตตอบด้วยโค้ดจริงจาก `macro_engine.py` เสมอ*

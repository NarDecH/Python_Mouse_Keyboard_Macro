# 🤖 PROMPT.md — พรอมต์มาตรฐานสำหรับ AI ช่วยพัฒนาโปรเจกต์นี้

> **วิธีใช้:** คัดลอกข้อความในบล็อกด้านล่างทั้งหมดไปวางตอนเริ่มบทสนทนากับ AI
> (ChatGPT / Claude / Copilot / ZCode ฯลฯ) แล้วตามด้วยงานที่ต้องการ
> ก่อนใช้ ตรวจว่าเลขเวอร์ชันตรงกับ `__version__` ปัจจุบันใน `macro_engine.py`
>
> อ้างอิงล่าสุด: v2.5.2 — ดู `docs/CHANGELOG.md` เสมอ

---

```text
คุณคือผู้พัฒนาหลักของโปรเจกต์ "Auto Mouse & Keyboard Macro" — เครื่องมือ
อัตโนมัติเมาส์/คีย์บอร์ดภาษาไทย (Tkinter + pynput) เป้าหมายหลักคือ Windows
(รองรับ Linux/macOS) โค้ดทั้งหมดอยู่ในไฟล์เดียวตอนแจกจ่าย มีเทสต์ครบ
และคุณภาพต้องไม่ถอยหลัง

## สถาปัตยกรรม (สำคัญ — อ่านก่อนแก้โค้ด)

- `auto_macro.py` = โปรแกรมหลักไฟล์เดียวจบ (GUI + CLI) · ข้างในมีบล็อก
  ENGINE-BEGIN/ENGINE-END ที่ "สร้างจาก macro_engine.py โดยอัตโนมัติ"
  ⛔ ห้ามแก้โค้ดในบล็อกนี้ตรง ๆ — แก้ที่ `macro_engine.py` แล้วรัน
  `py build_singlefile.py` ทุกครั้ง (มีเทสต์ตรวจว่าซิงก์ตรงกัน)
- `macro_engine.py` = engine ล้วนไม่มี Tk: ค่าคงที่/parser/ActionRunner
  (execute แถวเดียว — แหล่งเดียวที่ GUI และ CLI ใช้ร่วมกัน)/Recorder/
  clipboard/Unicode typing/log/plugins นอกจากนี้ TR (ข้อความ i18n) ก็อยู่
  "ใน engine" — แก้ TR ใน auto_macro.py แล้วโดน sync ทับทิ้ง
- `engine_cli.py` = CLI ย่อยใช้ engine ตรง ๆ (พฤติกรรมต้องตรงกับ CLI หลัก)
- `plugins/*.py` = Custom Actions ประกาศ ACTION_NAME + run(ctx, row);
  ctx = {mouse, kb, log, cfg, vars, stop_check, ui{msg,beep}}
- `test_auto_macro.py` / `test_e2e.py` = unittest (ทุกคลาสต้องชื่อไม่ซ้ำ)
- เวอร์ชันแหล่งเดียว: `__version__` ใน macro_engine.py → APP_TITLE อิงจากนี้
  และมีเทสต์เช็คว่า CHANGELOG มี section ตรงเวอร์ชัน

## กฎเหล็ก (เรียนรู้จากบั๊กจริง — ฝ่าฝืนแล้วพังมาแล้วทุกข้อ)

1. เธรด player/recorder ห้ามเรียก Tk โดยตรง — สื่อสารผ่าน `_ui_state`
   ให้ poller (main thread) เป็นคนอัพเดตหน้าจอ; ไฮไลต์แถวส่ง iid มาตั้งแต่เริ่มเล่น
2. พิมพ์ข้อความ = `send_unicode_char()` (SendInput KEYEVENTF_UNICODE)
   ห้ามกลับไปพิมพ์ด้วย virtual key — layout ไทยจะเพี้ยน ("D" → "ิ")
3. คีย์ที่มี modifier ใช้ `parse_key_combo("Ctrl+W")`; ตัวอักษร A-Z/ตัวเลขเดี่ยว
   เป็นปุ่มกายภาพ (VK) — ไม่ผูกกับ layout
4. bind event ซ้ำกันได้เมื่อใช้ add="+": `<Button-1>` == `<ButtonPress-1>`
   — bind ทีหลัง "ไม่มี add" = เขียนทับของเดิม (เคยทำให้ลากแถวตายทั้งฟีเจอร์)
5. เงื่อนไขทุกตัว (If Image/Else/If Loop/If Time/If Pixel/If Variable):
   Repeat = จำนวนแถวที่ข้ามเมื่อเงื่อนไขไม่จริง · ตัดสินก่อน delay เสมอ ·
   If Variable ประเมินผ่าน evaluate_condition(..., variables=...) —
   ไม่มีตัวแปร = ไม่จริง → ข้าม N (กฎเดียวกันทั้ง GUI/CLI/engine_cli)
6. STOP ต้องใช้ได้เสมอ (หลักการข้อ 1): delay หารชิ้น 50ms ผ่าน stop_check,
   ปล่อยคีย์/ปุ่มค้างด้วย release_all, hotkey มี self-healing รีสตาร์ตเอง
7. ห้ามเพิ่ม dependency โดยไม่จำเป็น (stdlib + pynput; opencv/Pillow = optional)
8. ImageGrab/pixel/screenshot อาจล้มเหลวบน headless — โค้ดทนได้ (คืน None)
   และเทสต์ต้อง skip อย่างชัดเจน ไม่ assert ว่าอ่านสี/จับภาพสำเร็จ
9. คอลัมน์ตาราง COLS มี note (index 9) — ไม่ส่งเข้า runner; แถวที่ย่อ/สถานะ
   พิเศษ (หัวข้อ Section, marker กลุ่มย่อ) ต้องได้รับการดูแลใน serialize/
   undo/ลบ/เล่น ทุกจุดที่แตะตาราง
10. แก้อะไรในตาราง → เรียก refresh_nums() เสมอ

## ขั้นตอนมาตรฐานทุกครั้งที่แก้โค้ด

1. อ่าน `AGENTS.md` (บันทึกประวัติ/กับดักเฉพาะจุด) + `docs/CHANGELOG.md`
   และรัน `py -m unittest test_auto_macro -v` ก่อนเริ่มแก้ (ต้องเขียวก่อนอยู่แล้ว)
2. แก้ engine → `py build_singlefile.py` → แก้ GUI/CLI ที่เหลือ
3. เพิ่ม/ปรับเทสต์ให้ครอบฟีเจอร์ (GUI เทสต์ต้อง headless-safe และไม่แตะ
   เมาส์/คีย์/คลิปบอร์ดจริงโดยไม่ snapshot-restore)
4. ตรวจ: `py -m py_compile auto_macro.py macro_engine.py` +
   `py -m unittest test_auto_macro -v` + `py -m unittest test_e2e -v` +
   `timeout 6 py auto_macro.py` (เช็ค stderr ว่าง)
5. เอกสารพร้อมกันเสมอ: `docs/CHANGELOG.md` (เวอร์ชันใหม่ด้านบนสุด) +
   `AGENTS.md` (บันทึกกับดัก/บทเรียน) + bump `__version__` + ROADMAP ถ้าเกี่ยว
6. commit + push **ทั้ง main และ tag** (ระวัง: `git push origin main v2.x`
   ถ้า tag ยังไม่สร้าง = push ทั้งคำสั่งล้มเหลว main ไม่ขึ้นเลย — ตรวจด้วย
   `git ls-remote origin main` เทียบ HEAD)

## สไตล์

- คอมเมนต์/ข้อความ UI/เอกสาร = ภาษาไทย · ชื่อตัวแปร/ฟังก์ชัน = อังกฤษ
- อธิบายสิ่งที่ทำกับผู้ใช้เป็นภาษาไทย สรุปผลการรันเทสต์ตรงตามจริง
- ก่อนเสนอฟีเจอร์ใหม่: ตรวจ `docs/ROADMAP.md` ก่อนเสมอ (ของที่วางแผนไว้ต้องต่อเนื่อง)

## สิ่งที่ยังไม่ทำ (ต้องถามก่อนเริ่ม)

OCR / รันซับสคริปต์ / ตลาด plugin / เอกสารจีน-ญี่ปุ่น / แปลงจาก AutoHotkey
```

---

## 💡 เกร็ดการใช้

- งานเล็ก: วางพรอมต์ + อธิบายงาน 1-2 ประโยคพอ
- งานใหญ่: วางพรอมต์ + สั่ง "อ่าน AGENTS.md และ docs/CHANGELOG.md ก่อนแล้วเสนอแผนก่อนแก้"
- AI ที่ไม่มีสิทธิ์อ่านไฟล์: แนบ `AGENTS.md` และไฟล์ที่เกี่ยวข้องไปด้วย
- หลัง AI แก้เสร็จ: ตรวจ 4 ข้อเองเสมอ — (1) เทสต์เขียว (2) `py build_singlefile.py`
  ถ้าแก้ engine (3) CHANGELOG/เวอร์ชันตรง (4) `py auto_macro.py` เปิดได้ไม่มี error

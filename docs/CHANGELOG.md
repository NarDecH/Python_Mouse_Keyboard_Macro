# 📋 CHANGELOG — Auto Mouse & Keyboard Macro

รูปแบบอ้างอิง [Keep a Changelog](https://keepachangelog.com/) และใช้ [Semantic Versioning](https://semver.org/)

---

## [1.7.0] — 2026-09-27

### ✨ เพิ่มใหม่
- **🖼️ Search Area ให้ Image Click / Wait for Image** — ระบุกรอบค้นหาได้:
  ช่อง X,Y = มุมซ้ายบน, Mins = ความกว้าง, Secs = ความสูง (พิกเซล; เว้นว่าง = ค้นทั้งจอ)
  ลดเวลาค้นหาและลดโอกาสเจอภาพซ้ำผิดตำแหน่ง

### 🔄 CI/CD (GitHub Actions)
- **tests.yml** — รัน unit tests อัตโนมัติทุก push/PR บน Python 3.12–3.14 (Windows)
- **release.yml** — เมื่อ push tag `v*` จะ build .exe แล้วสร้าง GitHub Release
  พร้อมแนบไฟล์ให้โหลดอัตโนมัติ (รัน tests ก่อน build ทุกครั้ง)

### 📚 เอกสาร
- เพิ่มสกรีนช็อตหน้าตาโปรแกรมจริง (`docs/images/screenshot.png`)
- README เพิ่ม badge สถานะ tests + หัวข้อ CI/CD

### 🎬 สคริปต์เดโม่ + ชุดตัวอย่าง
- `demo_script.json` — เปิด Notepad พิมพ์ไทย เคาะ Enter บี๊บ คืนเมาส์ (โชว์ดีเลย์สุ่ม + Repeat)
  — **ทดสอบรันจริงผ่าน CLI แล้ว ทำงานครบทุกแถว**
- `demo_move_click.json` — เลื่อนเมาส์เป็นสี่เหลี่ยม + Scroll (ไม่คลิกอะไร ปลอดภัย)
- ใช้ได้ทั้งโหลดใน GUI (Load) และ CLI (`py auto_macro.py demo_script.json`)
- **examples/** — ชุดตัวอย่างสำเร็จรูป 4 ไฟล์ validate กับโค้ดจริงแล้ว:
  01_auto_typer / 02_form_filler / 03_image_click (พร้อม `target.png` + Search Area) /
  04_scroll_gallery + README ประกอบ
- 🔄 **ปรับปรุง Search Area:** เปลี่ยนจากการใช้ Mins/Secs เป็นขนาดกรอบ (ชนกับความหมาย
  ดีเลย์เดิม) มาเป็น syntax ใน Additional แทน: `ไฟล์.png@x,y,กว้าง,สูง`
  — Mins/Secs กลับมาเป็นดีเลย์ตามปกติทุกแถว และ X,Y กลับไปใช้กับพิกัดเมาส์ของ Action อื่น

### 🧪 ทดสอบ
- เพิ่ม 5 tests สำหรับ search area (รวม **51 tests**)
  พร้อมแก้บั๊ก falsy: พิกัด 0 ถูกมองเป็น "ค่าว่าง" ทำให้กรอบที่เริ่มที่ 0 ใช้ไม่ได้

---

## [1.6.0] — 2026-09-27

### 🐛 แก้บั๊กร้ายแรง
- **ลูปเล่นสคริปต์เป็น dead code** — จากการแก้โค้ดรอบ v1.5 ฟังก์ชัน `kb_ctrl_char`
  ถูกแทรกคั่นกลาง `_player` ทำให้ลูปเล่นทั้งหมดอยู่หลัง `return` → กด START แล้วไม่มีอะไรเล่น
  (เจอจากการ review ด้วย AST) — แก้เรียบร้อย พร้อมเพิ่ม progress ในตัว

### ✨ เพิ่มใหม่
- **⌨️ CLI mode** — เล่นสคริปต์โดยไม่เปิด GUI:
  `py auto_macro.py script.json [--loop] [--loops N] [--speed X]`
  - กด F8/Esc หยุดได้ (global hotkey) หรือ Ctrl+C
  - แสดงความคืบหน้ารายแถวในคอนโซล + ข้ามแถวที่ disabled
  - ตั้งคอนโซลเป็น UTF-8 อัตโนมัติ (พิมพ์ไทยไม่พังบน cp1252)
- **🖱️ Right-click menu บนตาราง** — คัดลอกแถว / แทรกแถวใหม่ด้านบน-ด้านล่าง / ลบแถว
- **📊 Progress bar + ตัวนับรอบ** ใน statusbar — แสดง `รอบ N • x/y (p%)` ขณะเล่น

### 🧪 ทดสอบ
- เพิ่ม 5 tests สำหรับ CLI (ไฟล์หาย/JSON พัง/ชนิดผิด/สคริปต์ว่าง/ข้ามแถว disabled)
  รวมเป็น **46 tests**

### 📚 เอกสาร
- อัพเดต README/RESEARCH/AGENTS ครอบคลุม v1.6

---

## [1.5.0] — 2026-09-27

> ฟีเจอร์ชุดนี้ศึกษาและคัดสรรจาก [automouseclick.com](https://www.automouseclick.com/)

### ✨ เพิ่มใหม่ — Action ชุดใหม่ในตาราง
- **Scroll Up / Scroll Down** — เลื่อนล้อเมาส์ตามจำนวนจังหวะ (ใส่ในช่อง Additional เช่น `3`)
- **Double Left Click / Double Right Click** — ดับเบิลคลิกที่พิกัด
- **คลิกแบบ Modifier** — Ctrl+Click, Shift+Click, Alt+Click, Ctrl+Right Click
- **Move Mouse** — ย้ายเมาส์ไปพิกัดโดยไม่คลิก
- **Move Mouse by Offset** — ย้ายแบบสัมพัทธ์จากตำแหน่งปัจจุบัน (X,Y = ระยะเปลี่ยนแปลง)
- **Save Cursor / Restore Cursor** — จำตำแหน่งเมาส์แล้วย้อนกลับมาภายหลัง
- **Type Text** — พิมพ์ข้อความ (รองรับภาษาไทย) ตรงช่อง Additional
- **Launch App** — เปิดโปรแกรม/ไฟล์/เว็บไซต์ (เช่น `https://example.com`)
- **Wait for Image** — รอจนกว่าภาพที่ระบุจะปรากฏบนจอ (timeout 30 วิ)
- **Beep** — เสียงเตือนจากสมาร์ต
- **อัด scroll ตอน RECORD** — บันทึกการเลื่อนล้อเมาส์เป็นแถว Scroll Up/Down อัตโนมัติ

### ✨ เพิ่มใหม่ — ตัวเลือกการเล่น
- **ดีเลย์สุ่ม** — ใส่ Secs แบบ `1-3` เพื่อสุ่มดีเลย์ 1–3 วิ (กันจังหวะเครื่องจักรจนเกินไป)
- **ตัวคูณความเร็ว** — 0.25× / 0.5× / 1× / 2× / 4×
- **จำนวนรอบของสคริปต์ทั้งชุด** — ช่อง "รอบ" (0 = ไม่จำกัด)
- **คืนเมาส์จุดเดิม** — ติ๊กแล้วเมื่อจบรอบ เมาส์จะกลับมาที่ตำแหน่งเริ่มเล่น

### 🧪 ทดสอบ
- เพิ่ม 12 unit tests (รวม 41): `delay_range`, ชุด action ใหม่ครบและไม่ซ้ำ

### 📚 เอกสาร
- อัพเดต README/RESEARCH ครอบคลุมฟีเจอร์ v1.5

---

## [1.4.0] — 2026-09-27

### ✨ เพิ่มใหม่
- **🌐 Global Hotkey** — F6/F8/F9/F10 กดได้แม้โปรแกรมไม่ได้โฟกัส
  (ใช้ `pynput.keyboard.GlobalHotKeys`; ถ้าคีย์ชนกับโปรแกรมอื่นจะแจ้งเตือนและ fallback
  ไปใช้แบบโฟกัสหน้าต่างเหมือนเดิม)
- **🖼️ คลิกตามภาพ (Image Click)** — Action ใหม่ในตาราง: ระบุไฟล์ .png ในช่อง Additional
  โปรแกรมจะจับภาพหน้าจอ หาตำแหน่งภาพด้วย OpenCV template matching (threshold 80%)
  แล้วคลิกที่จุดศูนย์กลาง — ใช้เมื่อพิกัดเลื่อนไม่แน่นอน
  (ติดตั้งเพิ่ม: `pip install opencv-python Pillow`; ถ้าไม่ติดตั้ง ฟีเจอร์อื่นยังใช้ได้ปกติ)
- **🎛️ ระบบโปรไฟล์** — แถบเลือกโปรไฟล์ใต้เมนู: สร้าง/เปลี่ยนชื่อ/ลบ/สลับได้หลายสคริปต์
  เก็บใน `macro_profiles.json` (ตัวอย่างเช่น "งานบ้าน", "เกม A", "เกม B")
- **⏰ เล่นอัตโนมัติตามเวลา (Schedule)** — ตั้งให้เล่นสคริปต์ "ทุก N นาที" หรือ
  "ทุกวัน เวลา HH:MM" — เธรดตรวจเวลาแยกจาก UI ปลอดภัยต่อเธรด (ผ่าน queue)

### 🧪 ทดสอบ
- เพิ่ม `test_auto_macro.py` — 29 unit tests สำหรับฟังก์ชันล้วน
  (`parse_key`, `delay_seconds`, `fmt_num`, `parse_int`, `re_match_hhmm`,
  ค่าคงที่ และ mapping ของ global hotkey) — รัน: `py -m unittest test_auto_macro -v`

### 📦 Build
- อัพเดท `requirements.txt` เพิ่ม opencv-python + Pillow (เป็น optional deps)
- อัพเดท `auto_macro.spec` — .exe ขนาด ~72 MB เพราะรวม OpenCV
  (ถ้าต้องการ .exe เล็กแบบเดิม ลบ opencv-python/Pillow ออกจาก requirements แล้ว build ใหม่)

### 📚 เอกสาร
- อัพเดท README/RESEARCH/AGENTS ให้ครอบคลุมฟีเจอร์ v1.4 ทั้งหมด

---

## [1.3.0] — 2026-09-27

### ✨ เพิ่มใหม่
- **โปรแกรมหลัก `auto_macro.py`** — GUI ภาษาไทยตามต้นแบบ Auto Mouse v1.3:
  ตารางคำสั่ง (# / X / Y / Button / Additional / Mins / Secs / Repeat) + ปุ่ม
  START / STOP / REPEAT / RECORD
- **โหมดบันทึกเรียลไทม์ (F9)** — จับการคลิกเมาส์และกดคีย์ พร้อมจับเวลาหน่วง (Secs) อัตโนมัติ
- **เล่นสคริปต์ (F6)** และ **เล่นวนซ้ำ (REPEAT)** พร้อมตัวเลือก "วนซ้ำไม่จำกัด" (F10)
- **คำสั่งคีย์บอร์ด** — Tap Key / Press Key / Release Key รองรับชื่อคีย์พิเศษ
  (space, enter, esc, ctrl, shift, alt, win, f1–f12, ลูกศร, pgup/pgdn, prtsc ฯลฯ)
  และรหัส virtual key ตัวเลข
- **จับพิกัดเมาส์อัตโนมัติ** — ดับเบิลคลิกช่อง X/Y นับถอยหลัง 3 วิ แล้วใส่ตำแหน่งเมาส์ปัจจุบัน
- **แก้ค่าในตาราง** — ดับเบิลคลิกช่องอื่นเปิดหน้าต่างแก้ค่า (Action เป็น dropdown)
- **Checkbox เปิด/ปิดรายแถว** (☑/☐) และเครื่องมือจัดการแถว: เพิ่ม / ลบ / เลื่อนขึ้นลง / ล้างทั้งหมด
- **Save / Load สคริปต์ .json** + autosave (`macro_conf.json`) ตอนปิดโปรแกรม
- **Live statusbar** — พิกัดเมาส์และคีย์ที่กดล่าสุดแบบสด + ไฮไลต์แถวที่กำลังเล่น
- **คีย์ลัดในโปรแกรม** — F6 / F8 / F9 / F10 / Delete
- **เมนูไอคอน** — Save, Load, Settings, About, Help, Exit (ภาษาไทยทั้งหมด)

### 📦 Build & การแจกจ่าย
- `build.bat` + `auto_macro.spec` — build ไฟล์เดียว `dist/AutoMouseMacro.exe` (~13 MB,
  onefile, ไม่มี console) ด้วย PyInstaller ทดสอบรันจริงแล้ว
- `run.bat` — รันจากซอร์สด้วย `py` launcher
- `requirements.txt` — pynput>=1.7.6 (ติดตั้งจริงเวอร์ชัน 1.8.2 บน Python 3.14.7)

### 📚 เอกสาร
- `AGENTS.md` — แนวทางสำหรับ AI agent / นักพัฒนา (เทคโนโลยี, สถาปัตยกรรม, ข้อตกลงโค้ด)
- โฟลเดอร์ `docs/` — README / RESEARCH / CHANGELOG ทั้ง **.md และ .html** ภาษาไทย
  ธีมสวยงาม เปิดออฟไลน์ได้ (CSS ฝังในไฟล์) พร้อมรูปประกอบใน `docs/images/`

---

## [Unreleased]

### 🎯 วางแผนไว้
- จับภาพตัวอย่าง (crop) จากในโปรแกรมโดยไม่ต้องใช้ editor ภายนอก
- CLI รองรับ Image Click / Wait for Image ด้วย
- เชื่อมต่อ Windows Task Scheduler ผ่าน CLI
- ปรับ threshold ความมั่นใจของ Image Click ได้รายแถว

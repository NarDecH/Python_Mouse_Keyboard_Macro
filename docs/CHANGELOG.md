# 📋 CHANGELOG — Auto Mouse & Keyboard Macro

รูปแบบอ้างอิง [Keep a Changelog](https://keepachangelog.com/) และใช้ [Semantic Versioning](https://semver.org/)

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
- ตัวคูณความเร็ว 0.5× / 1× / 2×
- แถบ progress และตัวนับรอบเวลาเล่นแบบวนซ้ำ
- โซนค้นหาภาพ (search area) แบบระบุพิกัดได้สำหรับ Image Click
- บันทึกภาพตัวอย่าง (crop) จากในโปรแกรมโดยไม่ต้องใช้ editor ภายนอก

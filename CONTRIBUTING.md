# 🤝 CONTRIBUTING — ชวนมาร่วมพัฒนา

ขอบคุณที่สนใจร่วมพัฒนา Auto Mouse & Keyboard Macro! เอกสารนี้สรุปวิธีเริ่มต้นและกติกาของโปรเจกต์

## 🚀 เริ่มต้นใน 3 นาที

```bash
git clone https://github.com/NarDecH/Python_Mouse_Keyboard_Macro.git
cd Python_Mouse_Keyboard_Macro
py -m pip install -r requirements.txt        # pynput + opencv-python + Pillow
py -m unittest test_auto_macro -v             # unit tests
py -m unittest test_e2e -v                    # E2E tests (สคริปต์ Beep ล้วน ปลอดภัย)
```

> เครื่อง Windows ใช้ `py` launcher เสมอ (`python` ใน PATH อาจเป็น stub ของ Windows Store)

## 🏗️ โครงสร้างที่ต้องรู้ก่อนแก้โค้ด

อ่าน **[AGENTS.md](AGENTS.md)** ก่อนเสมอ — สรุปสถาปัตยกรรมทั้งหมด สั้น ๆ คือ:

- **ไฟล์เดียวจบ `auto_macro.py`** — อย่าแยกโมดูลเว้นแต่ผู้ใช้ขอ
- **คอมเมนต์/ข้อความ UI เป็นไทย, ชื่อตัวแปร/ฟังก์ชัน เป็นอังกฤษ**
- **Tk แตะได้บน main thread เท่านั้น** — เธรด listener/player ต้องผลักงานผ่าน
  `self._ui_state` + poller หรือ `root.after(0, ...)` เท่านั้น (ดูรูปแบบในโค้ด)
- **อย่าใช้ `GlobalHotKeys`** — พิสูจน์แล้วว่าบน pynput 1.8.x บางเครื่องไม่ยิง
  ใช้ `keyboard.Listener` จับคู่คีย์เอง (ดู `_start_global_hotkeys`)
- **แก้ตารางเสร็จเรียก `refresh_nums()` เสมอ**

## ✅ เกณฑ์ก่อนส่ง PR

```bash
py -m py_compile auto_macro.py                       # syntax ผ่าน
py -m unittest test_auto_macro test_e2e -v           # เทสต์ผ่านทั้งหมด
timeout 6 py auto_macro.py                           # เปิดจริงไม่มี error ที่ stderr
```

- เพิ่มเทสต์สำหรับฟีเจอร์/บั๊กที่แก้ทุกครั้ง (เทสต์ต้องไม่คลิกเมาส์/กดคีย์จริง —
  ใช้ Beep/mock และ **อย่าตั้งชื่อคลาสเทสต์ซ้ำกัน** — คลาสหลังจะบังคลาสหน้า)
- อัพเดต `docs/CHANGELOG.md` + `.html` เพิ่มเวอร์ชันใหม่ด้านบนสุด
- ข้อความ UI ใหม่ใส่ใน `TR` **ทั้ง th/en** และใช้ `self._t("key")`
- ลิงก์ใน docs/*.md ที่อ้างข้ามโฟลเดอร์ต้องมี `../` นำหน้า (ตรวจลิงก์ก่อน push)
- อย่า commit ไฟล์ runtime: `macro_conf.json`, `macro_profiles.json`,
  `macro_log_*.txt`, `backups/`, `dist/` (ดู `.gitignore`)

## 🐛 รายงานบั๊ก / 💡 เสนอฟีเจอร์

ใช้แม่แบบที่ [.github/ISSUE_TEMPLATE/](.github/ISSUE_TEMPLATE/) — ยิ่งให้ข้อมูล
(เวอร์ชัน, ขั้นตอนทำซ้ำ, ไฟล์ log ของวันนั้น ตัดข้อมูลส่วนตัว) ยิ่งแก้เร็ว

## 🎯 ประเด็นที่ยินดีรับ PR มากเป็นพิเศษ

- แก้ FAQ/เอกสารให้ชัดขึ้น
- เพิ่มเทสต์ครอบฟีเจอร์ที่ยังบาง
- รองรับ Linux/macOS ให้จริง (ปัจจุบัน CLI มี msvcrt เฉพาะ Windows — ยินดีรับ macOS/Linux แทน)
- Action ใหม่ที่ stdlib + pynput ทำได้ (ไม่เพิ่ม dependency ใหม่โดยไม่จำเป็น)

## ⚖️ กติกา

- ใช้งานอย่างมีความรับผิดชอบ — อย่าใช้กับเกม/ระบบที่ห้าม bot
- จะไม่ยอมรับโค้ดที่มุ่งร้าย/เก็บข้อมูลผู้ใช้
- ทุก PR ผ่าน CI (Windows, Python 3.12/3.13/3.14) ก่อน merge

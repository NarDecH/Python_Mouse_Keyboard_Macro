# 📣 โพสต์แนะนำโปรแกรม (สำหรับโซเชียล)

> เวอร์ชันสั้นสำหรับ X/Twitter, Facebook, Discord, Reddit — เลือกใช้ตามแพลตฟอร์ม
> แนบรูป: `docs/images/screenshot.png` • ลิงก์ดาวน์โหลด: https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/releases/latest

---

## 🐦 X / Twitter (สั้นสุด)

```
เบื่องานซ้ำ ๆ บนคอม? ผมทำโปรแกรมอัดและเล่นซ้ำคลิกเมาส์+คีย์บอร์ดแบบอัตโนมัติฟรี ๆ 🖱️

✅ อัด 60 วิ เล่นซ้ำได้ไม่จำกัด
✅ คลิกตามภาพ + ปุ่มลัดทั้งจอ + ตั้งเวลาเล่นเอง
✅ ไฟล์ .exe เดียว ไม่ต้องติดตั้งอะไร

โหลดฟรี: https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/releases/latest

#automation #python #opensource
```

---

## 📘 Facebook (เล่าเรื่อง)

```
🖱️ ให้คอมทำงานแทนคุณ — โปรแกรม Auto Mouse & Keyboard Macro (ฟรี, โอเพนซอร์ส)

เคยไหม? ต้องคลิกปุ่มเดิม พิมพ์ข้อความเดิม ทุกวัน... ผมเลยทำโปรแกรมนี้ขึ้นมา
แค่กด "อัด" ทำงานตามปกติครั้งเดียว แล้วให้โปรแกรมเล่นซ้ำแทนได้ไม่จำกัด

ทำอะไรได้:
• อัดคลิก/พิมพ์/สกรอลล์ แล้วเล่นซ้ำ — แก้จังหวะทีละแถวได้ในตาราง
• คลิกตามภาพ (จับรูปปุ่มบนจอ โปรแกรมหาและคลิกให้เอง)
• ตั้งเวลาเล่นเองทุก N นาที หรือรายวันตอน HH:MM
• ปุ่มลัด F1–F10 กดได้แม้ไม่โฟกัสหน้าต่าง
• โหมดเฝ้าระบบ: จบแล้วเริ่มใหม่เอง วนไม่จำกัด
• มี log + กราฟสถิติ + backup อัตโนมัติทุกครั้งที่ปิด
• เงื่อนไขในสคริปต์ (If Image/Pixel Color/Variable) + ตัวแปร {ชื่อ} + ลากสลับแถวได้

ดาวน์โหลด: ไฟล์ .exe เดียว (Windows) ไม่ต้องติดตั้ง Python
ภาษาไทยทั้งโปรแกรมและคู่มือ 🇹🇭

⬇️ ฟรีทั้งหมด: https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/releases/latest
คู่มือใช้งาน: https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/blob/main/docs/TUTORIAL.md
```

---

## 💬 Discord / กลุ่ม (กึ่งทางการ)

```
แจกฟรี 🖱️ Auto Mouse & Keyboard Macro — อัดคลิก/คีย์แล้วเล่นซ้ำอัตโนมัติ (Windows)

• อัด 60 วิ เริ่มใช้ได้เลย | แก้รายการทีละแถวในตาราง | พิมพ์ข้อความไทยได้
• Image Click: จับรูปปุ่ม → โปรแกรมหาบนจอแล้วคลิกเอง (มีกรอบค้นหา+ปรับความไว)
• Schedule ทุก N นาที/รายวัน • Watchdog เริ่มใหม่เอง • CLI สำหรับ Task Scheduler
• Backup อัตโนมัติ 7 วัน • log + กราฟสถิติ • self-check ตอนเปิดโปรแกรม

ไฟล์เดียวจบ ไม่ต้องติดตั้ง | โอเพนซอร์ส (Python) | 373 unit + 15 E2E tests
⬇️ https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/releases/latest
⚠️ อย่าใช้กับเกม/ระบบที่ห้าม bot นะ
```

---

## 👽 Reddit r/python / r/software

**Title:** I built a free, open-source mouse & keyboard macro recorder (single .exe, Thai/English UI)

```
Hi! I've been building Auto Mouse & Keyboard Macro — a free, open-source Windows
automation tool: record once, replay forever, edit everything row-by-row.

Highlights:
- Record clicks/keys/scroll with automatic timing, edit everything row-by-row
  (drag to reorder, undo/redo, find & replace, notes per row)
- Image Click with search area + per-row confidence threshold (OpenCV)
- In-script conditions: If Image / If Pixel Color / If Variable / If Loop / If Time,
  variables `{name}`, clipboard actions, and 20+ built-in actions
- Plugin system: drop a small .py into plugins/ to add new Actions
  (13 built-ins: Screenshot, Toast, Webhook, Ask Input, Random Pause, Counter, Open URL, ...)
- Global hotkeys (F1–F10) that work even when unfocused, with self-healing listeners
- Scheduler (every N minutes / daily HH:MM — several daily times, comma-separated — each time
  can bind its own profile: `12:30=morning job`),
  random delays (anti-pattern), shuffle & row sampling, watchdog auto-restart mode, safety timeout
- CLI mode for Windows Task Scheduler with --stop-file / --validate for external control
- Daily play logs + in-app stats with charts, startup self-check,
  automatic 7-day backups, settings export/import

Tech: Python (Tkinter + pynput), optional opencv-python + Pillow, engine separated
from the GUI (macro_engine.py — embed it in your own project).
407 unit tests + 15 end-to-end tests, CI on Windows/Linux/macOS, auto releases via tag.
Docs in Thai, English, Chinese and Japanese.

Download (no Python needed): https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/releases/latest
Source: https://github.com/NarDecH/Python_Mouse_Keyboard_Macro

Feedback welcome! (Note: don't use it with games/services that prohibit bots.)
```

---

## 💡 เคล็ดลับตอนโพสต์

- แนบ `screenshot.png` หรือเปิด [LANDING.html](LANDING.html) เป็นลิงก์หลัก (สวย อ่านง่าย มี CTA)
- ช่วงเวลาโพสต์ดี: ค่ำวันธรรมดา / เช้าเสาร์ (คนไทยออนไลน์)
- ถ้ามีคนถามถึงความปลอดภัย: โอเพนซอร์สทั้งหมด ตรวจโค้ดได้ มี CI รันเทสต์ทุก push

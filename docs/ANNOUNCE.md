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

ไฟล์เดียวจบ ไม่ต้องติดตั้ง | โอเพนซอร์ส (Python) | 428 unit + 15 E2E tests
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
- Plugin system: drop a small .py into plugins/ to add new Actions AND Conditions
  (13 built-in actions: Screenshot, Toast, Webhook, Ask Input, Random Pause, Counter, Open URL, ...
   + condition plugins: File Exists, Internet Up, Process Running, Window Exists)
- Global hotkeys (F1–F10) that work even when unfocused, with self-healing listeners
- Scheduler (every N minutes / daily HH:MM — several daily times, comma-separated — each time
  can bind its own profile: `12:30=morning job`),
  random delays (anti-pattern), shuffle & row sampling, watchdog auto-restart mode, safety timeout
- CLI mode for Windows Task Scheduler with --stop-file / --validate for external control
- Collapse Block Start→End groups in the table (hidden rows still play) + a 🔍 Validate
  button that reports problem rows in-app; START pre-validates too (skips broken rows after
  a confirm) and a two-way .ahk bridge covers if/Loop/Until blocks in both directions
- Daily play logs + in-app stats with charts, startup self-check,
  automatic 7-day backups, settings export/import

Tech: Python (Tkinter + pynput), optional opencv-python + Pillow, engine separated
from the GUI (macro_engine.py — embed it in your own project).
506 unit tests + 20 end-to-end tests, CI on Windows/Linux/macOS, auto releases via tag.
Docs in Thai, English, Chinese and Japanese.

Download (no Python needed): https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/releases/latest
Source: https://github.com/NarDecH/Python_Mouse_Keyboard_Macro

Feedback welcome! (Note: don't use it with games/services that prohibit bots.)
```

---

## 🆕 ข่าวเวอร์ชัน v2.14 (โพสต์ต่อท้ายหรือโพสต์เดี่ยว)

```
🆕 v2.14 ออกแล้ว!

• เงื่อนไขใหม่ 3 ตัวจาก plugin: Internet Up / Process Running / Window Exists —
  เช่น เล่นต่อเมื่อเน็ตขึ้น หรือข้ามบล็อกเมื่อโปรแกรมปิดอยู่ (ผสม && กับเงื่อนไขอื่นได้)
• ปุ่ม 🧩 ในโปรแกรม: เลือกเงื่อนไข plugin + ใส่อาร์กิวเมนต์ แล้วแทรกแถวให้เลย
• CLI: --dry-report PATH เลือกไฟล์รายงาน Dry-run เอง ({date} = วันที่วันนี้)

โหลด: https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/releases/latest
```

## 🆕 ข่าวเวอร์ชัน v2.15 (โพสต์ต่อท้ายหรือโพสต์เดี่ยว)

```
🆕 v2.15 ออกแล้ว!

• เล่นเฉพาะกลุ่มหัวข้อ: คลิกขวาที่หัวข้อ Section → "▶ เล่นกลุ่มนี้อย่างเดียว" —
  สคริปต์ยาวแบ่งเป็นขั้น ๆ ทดสอบ/รันทีละกลุ่มได้ ไม่ต้องปิดแถวอื่นเอง
  (แถวที่ย่อไว้ก็เล่นครบ · ผ่าน player จริง — STOP/ไฮไลต์/log ครบ)
• CLI: --only-section ชื่อกลุ่ม เล่นเฉพาะกลุ่มนั้นจาก command line
• เปิด milestone v2.15 + issues แผนถัดไปแล้ว: ลากจัดลำดับกลุ่ม / .bat คู่สคริปต์ /
  ไทม์ไลน์เหตุการณ์ / ตลาด condition-plugin — เสนอไอเดียได้ที่ Issue #1

โหลด: https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/releases/latest
```

## 🆕 ข่าวเวอร์ชัน v2.15.1 (โพสต์ต่อท้ายหรือโพสต์เดี่ยว)

```
🆕 v2.15.1 ออกแล้ว!

• ย้ายกลุ่มทั้งก้อน: คลิกขวาที่หัวข้อ → "⬆ ย้ายกลุ่มขึ้น" / "⬇ ย้ายกลุ่มลง"
  (หรือ Alt+↑↓ บนหัวข้อ) — จัดลำดับการเล่นทีละกลุ่ม ไม่ต้องลากทีละแถว
• แถวที่ย่อไว้เดินตามกลุ่มของตัวเองเสมอ · Block คร่อมกลุ่ม = โปรแกรมกันไว้ให้
• ผิดพลาดกด Ctrl+Z ย้อนได้ตามปกติ

โหลด: https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/releases/latest
```

## 🆕 ข่าวเวอร์ชัน v2.16 (โพสต์ต่อท้ายหรือโพสต์เดี่ยว)

```
🆕 v2.16.0 ออกแล้ว! — ปิด milestone v2.15 ครบทุกข้อ

• 🚀 Launcher คู่สคริปต์: Save สคริปต์ → กดเมนู 🚀 → ได้ .bat + .lnk
  ดับเบิลคลิกเล่นสคริปต์นั้นทันที ไม่ต้องเปิดโปรแกรมหลัก งานประจำวันสบายขึ้น
• ⏱ ไทม์ไลน์การเล่น: ปุ่มใหม่ในหน้าต่าง 📝 Log — เห็นทุกแถวของรอบล่าสุด
  (เล่น/ข้าม/เหตุผล/เวลา) ดีบั๊กสคริปต์เงื่อนไขซ้อน ๆ ได้ในหน้าเดียว
• 🔌 เงื่อนไข plugin ใหม่ 3 ตัว: Window Focused · File Newer Than · HTTP Status
  เช่น "API พร้อมและหน้าต่างงานยังโฟกัส = ค่อยทำงานต่อ"

โหลด: https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/releases/latest
```

## 🆕 ข่าวเวอร์ชัน v2.17.1 (โพสต์ต่อท้ายหรือโพสต์เดี่ยว)

```
🔊 v2.17.1 — Beep ตั้งค่าได้แล้ว!

• แถว Beep ใส่ Additional ได้ เช่น freq=1000 dur=200 count=3
  (ความถี่ Hz / ระยะ ms / จำนวนครั้ง — ใส่บางส่วนก็ได้)
• ไม่ใส่ = เสียงเดิมเหมือนเดิม สคริปต์เก่าไม่ต้องแก้อะไร
• Windows ได้เสียงจริงผ่าน winsound (ไม่ใช่เสียง bell เงียบ ๆ)
  STOP กดระหว่างบี๊บหลายครั้งได้ทันที

โหลด: https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/releases/latest
```

## 🆕 ข่าวเวอร์ชัน v2.17 (โพสต์ต่อท้ายหรือโพสต์เดี่ยว)

```
🆕 v2.17.0 ออกแล้ว!

• 🧩 เงื่อนไข plugin ใหม่ 3 ตัว: Disk Space Low (ดิสก์เหลือน้อย = เตือนก่อนพัง)
  Process CPU (เฝ้าโปรเซสใช้ CPU เกินเกณฑ์) · Window Closed (ปิดหน้าต่างงานแล้ว = จบงาน)
• 📅 คู่มือตั้งเวลางานด้วย Task Scheduler + 🚀 Launcher (TUTORIAL บทที่ 21)
  ตั้งแล้วลืมได้ — หยุดด้วย --stop-file ตรวจย้อนหลังด้วย ⏱ ไทม์ไลน์
• ตัวอย่างใหม่ examples/17 ลองเล่นเงื่อนไขใหม่ได้ทันที

โหลด: https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/releases/latest
```

## 🆕 ข่าวเวอร์ชัน v2.16.1 (โพสต์ต่อท้ายหรือโพสต์เดี่ยว)

```
🛠 v2.16.1 — แก้บั๊กที่เจอจากการทดสอบ .exe จริง

• ใครใช้ AutoMouseMacro.exe: ตอนนี้ตั้งค่า/โปรไฟล์/log/รายงาน dry-run
  จะเก็บอยู่ข้างไฟล์ .exe ไม่หายอีกต่อไป (เดิมหายทุกครั้งที่ปิดโปรแกรม)
• แถม: ตัวอย่างใหม่ examples/16 ลองเล่นเงื่อนไข plugin ใหม่ 3 ตัว
  แล้วเปิด ⏱ ไทม์ไลน์ดูผลทีละแถว

โหลด: https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/releases/latest
```

---

## 🆕 ข่าวเวอร์ชัน v2.18 (โพสต์ต่อท้ายหรือโพสต์เดี่ยว)

```
🎲 v2.18 — ลำดับการเล่นระดับกลุ่ม + ซ้อมเล่นเฉพาะกลุ่ม

• สุ่มลำดับ "กลุ่มหัวข้อ" ทั้งก้อน (แถวภายในกลุ่มเรียงเดิมเสมอ)
  — GUI: ติ๊ก "สุ่มลำดับกลุ่ม" · CLI: --shuffle-groups
• --only-section รับหลายกลุ่มคั่น comma เช่น --only-section "เตรียม,ล้าง"
• คลิกขวาหัวข้อ → 🧪 Dry-run กลุ่มนี้ — ซ้อมเดินเฉพาะกลุ่ม ไม่แตะเมาส์/คีย์จริง
• ตัวอย่างใหม่ examples/18 ลองได้ทันที

โหลด: https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/releases/latest
```

---

## 🆕 ข่าวเวอร์ชัน v2.19 (โพสต์ต่อท้ายหรือโพสต์เดี่ยว)

```
🧠 v2.19 — รวมเงื่อนไขด้วย OR (||) ได้แล้ว — ปิดครบ 3 ชุดเงื่อนไข

• เงื่อนไขทุกชนิดคั่น || ได้
  If Variable / If Loop / If Time / If Pixel Color / If Image / Block Start
  เช่น `n > 5 || code = "A-1"` · `img.png || 300,300 #ffffff`
• สายใดจริงก่อน = จริงทั้งนิพจน์ (short-circuit — ไม่ค้นภาพ/ยิงเน็ต
  /วัด CPU ของสายที่เหลือ) · && แน่นกว่า || ตามมาตรฐาน
• โทเคน `>ชื่อ` เก็บผลรวมทั้งนิพจน์ (1 = มีสายใดจริง / 0 = ทุกสายไม่จริง) —
  แถวถัดไปใช้ `{ชื่อ}` ต่อได้เลย
• ครบทุกเส้นทาง: 🔍 Validate / ตรวจก่อน START / Dry-run / สีแถว / hint /
  .ahk สองทิศ (export/import if (a || b) และบล็อก if (a) { ... })
• ตัวอย่างใหม่ examples/19_or_conditions.json ลองได้ทันที

โหลด: https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/releases/latest
```

---

## 🆕 News version v2.19 (English — Reddit/Discord EN)

```
🆕 v2.19.0 — OR (||) in composite conditions!

Every condition type now accepts || — If Variable / If Loop / If Time /
If Pixel Color / If Image / Block Start (if/until). Examples:
- n > 5 || code = "A-1"
- img.png || 300,300 #ffffff
- Block Start: if (img.png || n > 5) { ... } — skip the block if none is true

Priorities: && binds tighter than ||, short-circuit evaluation (the first
true branch wins — no extra image search/HTTP/CPU checks for the rest),
and the `>name` token stores the overall result (1/0) for later rows.
Everything is covered: 🔍 Validate / START pre-check / Dry-run / row colors /
hints — and both-direction .ahk export+import for `if (a || b)` and
`if (a) { ... }` blocks.

Download: https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/releases/latest
Demo script: examples/19_or_conditions.json
```

---

## 💡 เคล็ดลับตอนโพสต์

- แนบ `screenshot.png` หรือเปิด [LANDING.html](LANDING.html) เป็นลิงก์หลัก (สวย อ่านง่าย มี CTA)
- ช่วงเวลาโพสต์ดี: ค่ำวันธรรมดา / เช้าเสาร์ (คนไทยออนไลน์)
- ถ้ามีคนถามถึงความปลอดภัย: โอเพนซอร์สทั้งหมด ตรวจโค้ดได้ มี CI รันเทสต์ทุก push

# ตัวอย่างสคริปต์ (examples/)

ตัวอย่างสคริปต์สำเร็จรูป โหลดผ่านเมนู **Load** ในโปรแกรม หรือรันผ่าน CLI:

```bash
py auto_macro.py examples/01_auto_typer.json
```

### ตัวอย่าง Custom Action plugins (v1.16+)

```bash
py auto_macro.py examples/06_plugin_demo.json
```

สาธิต plugin ที่มากับโปรเจกต์: **Message Box** (เด้งกล่องข้อความ) + **Sleep (plugin)**
(หน่วง) — เหมาะใช้เป็นแม่แบบเขียน plugin ของคุณเอง ดู `plugins/README.md`

### ตัวอย่างเงื่อนไข (v1.18+)

```bash
py auto_macro.py examples/07_conditions.json
```

สาธิต **If Image → กลุ่ม A/B** (Else If Image) และ **Wait for Pixel Color** —
ลองบัง/เลิกบังหน้าต่างที่มี target.png แล้วเล่นใหม่ เส้นทางจะเปลี่ยน
(แบบฝึกหัดเต็มอยู่ใน TUTORIAL บทที่ 5A)

### ตัวอย่างตัวแปรในสคริปต์ (v1.19+)

```bash
py auto_macro.py examples/08_variables.json
```

สาธิต **Set Variable** (`รอบ = 0`, `รอบ += 1`) และการเรียกใช้ด้วย `{รอบ}`
ในช่องอื่น — ตัวนับ/สรุปค่าระหว่างเล่น ไม่ต้องแก้สคริปต์ทุกรอบ

### ตัวอย่างงานเฝ้าระบบ (v1.10+)

```bash
py auto_macro.py examples/05_watchdog_monitor.json --watchdog 5
# จบรอบ → พัก 5 วิ → เริ่มใหม่เอง วนไม่จำกัด (หยุดถาวร: F8/Esc/Ctrl+C)
# หรือดับเบิลคลิก examples/run_watchdog.bat
```

ทุกการรีสตาร์ตบันทึก `[WATCHDOG]` ลง log — เปิดดูย้อนหลังได้ที่เมนู 📊 Stats

> ⚠️ สคริปต์ที่มีการคลิก (เช่น 02) ให้ตรวจสอบพิกัดกับหน้าจอของคุณก่อนเล่นเสมอ —
> พิกัดในตัวอย่างเป็นแค่ค่าตัวอย่าง

| ไฟล์ | สอนอะไร | ความปลอดภัย |
|---|---|---|
| `01_auto_typer.json` | Type Text ไทย/อังกฤษ, คีย์พิเศษ, ดีเลย์สุ่ม, Repeat, Save/Restore Cursor | ✅ ไม่คลิก |
| `02_form_filler.json` | เปิด Notepad, พิมพ์ลงฟอร์ม, Tab ระหว่างช่อง, Launch App | ✅ ไม่คลิก |
| `03_image_click.json` | **Image Click + Search Area** (`@x,y,w,h`), Wait for Image, Beep | ✅ ไม่คลิกจริง (ปิด enabled ไว้) |
| `04_scroll_gallery.json` | Scroll ดูรูป/เว็บ, Move Mouse, Double Click (ปิด enabled) | ⚠️ มีแถวคลิกที่ปิดไว้ |
| `05_watchdog_monitor.json` | งานเฝ้าระบบ: Beep + พิมพ์สถานะ + Save/Restore Cursor + Scroll | ✅ ไม่คลิก |
| `06_plugin_demo.json` | **Custom Action plugins**: Message Box + Sleep (plugin) — แม่แบบเขียน plugin | ✅ ไม่คลิก |
| `07_conditions.json` | **เงื่อนไข (v1.18)**: If Image → กลุ่ม A/B (Else If Image) + Wait for Pixel Color | ✅ ไม่คลิก |
| `08_variables.json` | **ตัวแปร (v1.19)**: Set Variable (`=`, `+=`) + เรียกใช้ `{รอบ}` ในช่องอื่น | ✅ ไม่คลิก |
| `run_watchdog.bat` | ดับเบิลคลิกรัน 05 แบบ watchdog (จบ = พัก 5 วิ = เริ่มใหม่เอง) | ✅ |

ทุกสคริปต์แถวแรกคือ `Save Cursor` และแถวสุดท้าย `Restore Cursor` เสมอ
(แนวปฏิบัติที่แนะนำ: เมาส์จะกลับมาที่เดิมหลังจบสคริปต์)

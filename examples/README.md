# ตัวอย่างสคริปต์ (examples/)

ตัวอย่างสคริปต์สำเร็จรูป โหลดผ่านเมนู **Load** ในโปรแกรม หรือรันผ่าน CLI:

```bash
py auto_macro.py examples/01_auto_typer.json
```

> ⚠️ สคริปต์ที่มีการคลิก (เช่น 02) ให้ตรวจสอบพิกัดกับหน้าจอของคุณก่อนเล่นเสมอ —
> พิกัดในตัวอย่างเป็นแค่ค่าตัวอย่าง

| ไฟล์ | สอนอะไร | ความปลอดภัย |
|---|---|---|
| `01_auto_typer.json` | Type Text ไทย/อังกฤษ, คีย์พิเศษ, ดีเลย์สุ่ม, Repeat, Save/Restore Cursor | ✅ ไม่คลิก |
| `02_form_filler.json` | เปิด Notepad, พิมพ์ลงฟอร์ม, Tab ระหว่างช่อง, Launch App | ✅ ไม่คลิก |
| `03_image_click.json` | **Image Click + Search Area** (`@x,y,w,h`), Wait for Image, Beep | ✅ ไม่คลิกจริง (ปิด enabled ไว้) |
| `04_scroll_gallery.json` | Scroll ดูรูป/เว็บ, Move Mouse, Double Click (ปิด enabled) | ⚠️ มีแถวคลิกที่ปิดไว้ |

ทุกสคริปต์แถวแรกคือ `Save Cursor` และแถวสุดท้าย `Restore Cursor` เสมอ
(แนวปฏิบัติที่แนะนำ: เมาส์จะกลับมาที่เดิมหลังจบสคริปต์)

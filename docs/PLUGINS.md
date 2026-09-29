# 🔌 ตลาด Plugin — PLUGINS.md (v2.1)

ขยายโปรแกรมด้วย **Custom Action** — เขียนไฟล์ Python สั้น ๆ วางใน `plugins/`
โปรแกรมโหลดอัตโนมัติตอนเปิด แล้วชื่อจะโผล่ใน dropdown คอลัมน์ **Action** ทันที (ทั้ง GUI และ CLI)

> เปิดโฟลเดอร์นี้จากในโปรแกรมได้เลย: ปุ่ม **🔌 plugins** บนแถบเครื่องมือ (v2.1)
> หลังเพิ่ม/แก้ไฟล์ รีสตาร์ตโปรแกรม 1 ครั้งเพื่อโหลดใหม่

## Plugin ที่มากับโปรเจกต์

| ไฟล์ | ชื่อ Action | ทำอะไร |
|---|---|---|
| `sleep_seconds.py` | Sleep (plugin) | หน่วง N วินาที (จาก Additional) — ตัวอย่างพื้นฐาน |
| `message_box.py` | Message Box | แสดงกล่องข้อความ (Additional = ข้อความ) |
| `_template.py` | — | แม่แบบคัดลอกไปแก้ต่อ (ไฟล์ขึ้นต้น `_` ไม่ถูกโหลด) |

## วิธีเขียน plugin ใน 30 วินาที

```python
# plugins/my_action.py
import time

ACTION_NAME = "เปิด Notepad แล้วรอ"      # ชื่อที่โชว์ในตาราง (ห้ามซ้ำกับ Action เดิม)

def run(ctx, row):
    import os
    os.startfile("notepad.exe")
    time.sleep(1.5)
```

## Plugin API v2 — ctx ที่ฟังก์ชัน `run(ctx, row)` ได้รับ

| คีย์ | ชนิด | ความหมาย |
|---|---|---|
| `ctx["mouse"]` | pynput Mouse Controller | ควบคุมเมาส์ (position / click / scroll) |
| `ctx["kb"]` | pynput Keyboard Controller | ควบคุมคีย์บอร์ด (press / release / tap) |
| `ctx["log"](ข้อความ)` | function | เขียนข้อความลง log การเล่น (โหมด `[PLUGIN]`) |
| `ctx["cfg"]` | dict | `{"lang": "th"/"en"}` ภาษาของโปรแกรม |
| `ctx["stop_check"]()` | function | **คืน `False` เมื่อผู้ใช้กด STOP** — ลูปยาวต้องเช็คและออกเอง |
| `ctx["ui"]["msg"](text, color)` | function | แสดงข้อความใน statusbar (GUI) หรือ print (CLI) |
| `ctx["ui"]["beep"]()` | function | ส่งเสียงเตือน |

`row` คือ dict ของแถวที่กำลังเล่น: `x, y, additional, mins, secs, repeat, enabled`
(ค่า `{ตัวแปร}` ถูกแทนค่าให้ก่อนส่งเข้ามาแล้ว)

## กฎของ plugin

1. **ไฟล์ล้ม = โปรแกรมไม่พัง** — ไฟล์ที่ import ล้มเหลว / ไม่มี `ACTION_NAME` /
   ชื่อซ้ำกับ Action เดิม จะถูก**ข้าม**พร้อมบันทึกสาเหตุไว้ใน `load_plugins.last_failed`
2. ไฟล์ขึ้นต้น `_` ไม่ถูกโหลด — ใช้เป็นแม่แบบ/ไฟล์ช่วยได้
3. เรียงโหลดตามชื่อไฟล์ (a-z) · ชื่อ Action ต้องไม่ซ้ำกันและไม่ซ้ำกับของโปรแกรม
4. กับ `.exe`: วางโฟลเดอร์ `plugins/` ข้างไฟล์ `AutoMouseMacro.exe` (ปุ่ม 🔌 เปิดให้ถูกที่เอง)

## แนวคิด plugin ที่อยากเห็น (ชวนเขียน!)

- 🔊 เสียงแจ้งเตือนจริง (ไฟล์ .wav) แทนบี๊บ
- 📸 OCR อ่านข้อความบนจอแล้วเก็บเป็นตัวแปร
- 🌐 เรียก webhook/HTTP แจ้งสถานะสคริปต์
- 🖼️ ค้นภาพหลายไฟล์พร้อมกันแล้วคลิกตัวที่เจอก่อน
- ⌨️ ฟอร์มกรอกข้อความชุดจากไฟล์ CSV

ส่ง PR มาที่ [CONTRIBUTING.md](../CONTRIBUTING.md) — plugin ดี ๆ จะถูกเพิ่มในตารางข้างบน

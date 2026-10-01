# 🔌 ตลาด Plugin — PLUGINS.md (v2.7)

ขยายโปรแกรมด้วย **Custom Action** — เขียนไฟล์ Python สั้น ๆ วางใน `plugins/`
โปรแกรมโหลดอัตโนมัติตอนเปิด แล้วชื่อจะโผล่ใน dropdown คอลัมน์ **Action** ทันที (ทั้ง GUI และ CLI)

> เปิดโฟลเดอร์นี้จากในโปรแกรมได้เลย: ปุ่ม **🔌 plugins** บนแถบเครื่องมือ (v2.1)
> หลังเพิ่ม/แก้ไฟล์ รีสตาร์ตโปรแกรม 1 ครั้งเพื่อโหลดใหม่

## Plugin ที่มากับโปรเจกต์

| ไฟล์ | ชื่อ Action | ทำอะไร |
|---|---|---|
| `sleep_seconds.py` | Sleep (plugin) | หน่วง N วินาที (จาก Additional) — ตัวอย่างพื้นฐาน |
| `message_box.py` | Message Box | แสดงกล่องข้อความ (Additional = ข้อความ) |
| `play_sound.py` | Play Sound | บี๊บเสียงจริง (winsound) ตามจำนวนครั้งใน Additional — fallback bell บน OS อื่น |
| `webhook.py` | Webhook | ยิง POST JSON ไป URL ใน Additional (timeout 5 วิ) — แจ้งทีม/ระบบอื่นเมื่อสคริปต์ถึงจุดสำคัญ |
| `multi_image_click.py` | Multi Image Click | คลิกภาพหลายไฟล์ตามลำดับ คั่น `|` รองรับ @กรอบ#threshold — ไฟล์ไหนไม่เจอข้ามให้ |
| `screenshot.py` | Screenshot | ถ่ายหน้าจอเก็บไฟล์พร้อมเวลา (หลักฐานงานเฝ้าระบบ) |
| `toast.py` | Toast | แจ้งเตือน Windows 10/11 ไม่บล็อกการเล่น (ส่งไม่ได้/OS อื่น → statusbar+log แทน) |
| `write_log.py` | Write Log | เขียนข้อความของผู้ใช้ลง log การเล่น (ใช้ `{ตัวแปร}` ได้) |
| `ask_input.py` | Ask Input | ถามค่าผู้ใช้ตอนเล่นเก็บเป็นตัวแปร — Additional `ชื่อ|หัวข้อ|ค่าเริ่มต้น` |
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
| `ctx["vars"]` | dict | **ชี้ dict ตัวแปรเดียวกับของสคริปต์** — plugin เขียนค่าแล้วแถวถัดไปใช้ `{ชื่อ}` ต่อได้ (v2.5) |

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
- 📸 OCR อ่านข้อความบนจอแล้วเก็บเป็นตัวแปร (ผ่าน `ctx["vars"]`)
- ⌨️ ฟอร์มกรอกข้อความชุดจากไฟล์ CSV (อ่านแถวแล้วเขียน `ctx["vars"]["row"]` ทีละบรรทัด)
- 🖼️ ค้นภาพหลายไฟล์พร้อมกันแล้วคลิกตัวที่เจอก่อน (มีตัวอย่างแล้ว: multi_image_click.py)

ส่ง PR มาที่ [CONTRIBUTING.md](../CONTRIBUTING.md) — plugin ดี ๆ จะถูกเพิ่มในตารางข้างบน

## 📝 เกณฑ์รีวิว plugin จากชุมชน (v2.7)

PR plugin ใหม่ต้องผ่านครบทั้ง 6 ข้อ (ผู้รีวิวใช้ checklist นี้):

1. **โครงไฟล์ถูก** — ไฟล์เดียวใน `plugins/`, ขึ้นต้นด้วยตัวอักษร (ขึ้นต้น `_` จะไม่ถูกโหลด),
   ประกาศ `ACTION_NAME` (ไม่ซ้ำกับ Action เดิมและ plugin ที่มีอยู่) + `run(ctx, row)`
2. **dependency ตามหลักโปรเจกต์** — stdlib + pynput เท่านั้น (ต้องการ opencv/Pillow =
   ต้องกันกรณีไม่มีติดตั้งเอง ทนได้ไม่ crash)
3. **ทน error ทุกจุด** — input พัง (`additional` เป็น None/ข้อความมั่ว/ติดลบ),
   ctx ขาดคีย์ (ไม่มี `ui`/`vars`), และไฟล์ล้มตอน import = โปรแกรมต้องยังเปิดได้
   (เรียก `run` ด้วย input ที่พังทุกแบบในเทสต์ก่อน merge)
4. **มีเทสต์ใน PR** — อย่างน้อย: เรียก `run` จริงด้วย ctx จำลอง / ทน input พัง /
   ทน ctx ขาด / เขียน `ctx["vars"]` ได้ (ถ้ามี) — ก๊อปแม่แบบจากท้าย
   [`plugins/_template.py`](../plugins/_template.py) ไปแก้ได้เลย
   (ตัวอย่างเต็ม: `TestPluginsComplete` ใน test_auto_macro.py)
5. **STOP ต้องหยุดมันได้** — ลูป/หน่วงยาวต้องเช็ค `ctx["stop_check"]()` เป็นระยะ
   (กฎความปลอดภัยข้อ 1 ของโปรเจกต์: ห้ามทำให้ STOP ใช้ไม่ได้)
6. **เอกสารครบ** — เพิ่มแถวในตาราง "Plugin ที่มากับโปรเจกต์" ด้านบน + ตัวอย่าง
   การใช้งาน (ค่าที่ใส่ช่อง Additional) ใน PR description

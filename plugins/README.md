# 🔌 Custom Action Plugins (v1.16)

ขยายโปรแกรมด้วย Action ของคุณเอง — **เขียนไฟล์ Python สั้น ๆ วางในโฟลเดอร์นี้**
โปรแกรมโหลดอัตโนมัติตอนเปิด แล้วชื่อจะโผล่ใน dropdown คอลัมน์ **Action** ทันที
(ทั้ง GUI และ CLI)

## โครงแบบ plugin

```python
# plugins/my_action.py
import time

ACTION_NAME = "ชื่อที่โชว์ในตาราง"     # ห้ามซ้ำกับ Action เดิม

def run(ctx, row):
    os.startfile("notepad.exe")       # ทำอะไรก็ได้ที่ Python ทำได้
    time.sleep(1.5)
```

- `row` = dict ของแถวนั้น: `x, y, additional, mins, secs, repeat, ...`
  (ค่าที่พิมพ์ในตาราง เช่น Additional = `"hello"` → `row["additional"]`)
- `ctx["mouse"]` / `ctx["kb"]` = controller ของ pynput (ขยับเมาส์/กดคีย์ได้เลย)
- `ctx["log"](ข้อความ)` = เขียนลง `macro_log_วันที่.txt` (แสดงเป็น `[PLUGIN]`)
- `ctx["cfg"]["lang"]` = `"th"` หรือ `"en"` (ถ้า plugin อยากแสดงข้อความสองภาษา)

## กติกา

- ไฟล์ลงท้าย `.py` วางในโฟลเดอร์นี้ → โหลดอัตโนมัติ (เรียงตามชื่อไฟล์)
- ไฟล์ขึ้นต้น `_` = **ไม่ถูกโหลด** (ใช้เก็บ utility ส่วนตัวได้)
- ไฟล์ไหนพัง โปรแกรม**ข้ามไฟล์นั้น**แล้วทำงานต่อปกติ (ชื่อไฟล์โชว์ใน statusbar ตอนเปิด)
- ชื่อ `ACTION_NAME` ห้ามซ้ำกับ Action เดิม/ plugin อื่น

## ตัวอย่างในโฟลเดอร์นี้

| ไฟล์ | Action | หน้าที่ |
|---|---|---|
| `sleep_seconds.py` | Sleep (plugin) | หน่วงตามวินาทีใน Additional (รองรับทศนิยม) |
| `message_box.py` | Message Box | เด้งกล่องข้อความจาก Additional (ถ้าแสดงไม่ได้ → เขียน log) |
| `_template.py` | — | แม่แบบว่างให้ก๊อปไปแก้ (ขึ้นต้น `_` จึงไม่ถูกโหลด) |

## ทดสอบ plugin

```bash
# GUI: เปิดโปรแกรม → dropdown คอลัมน์ Action จะมี "Sleep (plugin)" / "Message Box"
# CLI:
py auto_macro.py my_script.json
# หัวโปรแกรมจะบอกว่า:  •  plugins: Message Box, Sleep (plugin)
```

> ⚠️ โค้ด plugin รันด้วยสิทธิ์ของโปรแกรม — วางเฉพาะไฟล์ที่คุณเขียน/อ่านแล้วเข้าใจเท่านั้น

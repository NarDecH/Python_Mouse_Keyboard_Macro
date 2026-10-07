# 🔌 ตลาด Plugin — PLUGINS.md (v2.16)

ขยายโปรแกรมด้วย **Custom Action** และ (ตั้งแต่ v2.13) **เงื่อนไข plugin (Condition)** —
เขียนไฟล์ Python สั้น ๆ วางใน `plugins/` โปรแกรมโหลดอัตโนมัติตอนเปิด แล้วชื่อจะโผล่ใน dropdown
คอลัมน์ **Action** ทันที (ทั้ง GUI และ CLI)

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
| `random_pause.py` | Random Pause | สุ่มพักช่วงเวลากันจังหวะเครื่องจักร — Additional `1.5-4` (วินาที) พักเป็นชิ้นสั้นเช็ค STOP ระหว่างทาง |
| `counter.py` | Counter | นับ/ตั้งตัวแปร — `ชื่อ` = +1, `ชื่อ += 5`, `ชื่อ = rand 1-10` — คู่ If Variable เป็นลูปนับรอบได้ |
| `open_url.py` | Open URL | เปิดลิงก์เว็บด้วย webbrowser ของ stdlib — แทน `{ตัวแปร}` ก่อนเปิด, ไม่มี scheme เติม https:// ให้ |
| `file_exists.py` | **File Exists** (เงื่อนไข) | **Condition plugin ตัวอย่าง (v2.13)** — ไฟล์ใน Additional มีจริง = จริง, ไม่มี = ข้าม N แถว (N = Repeat) ใช้ `{ตัวแปร}` ได้ |
| `internet_up.py` | **Internet Up** (เงื่อนไข v2.14) | เช็คเน็ตด้วย socket ล้วน stdlib — Additional ว่าง = 1.1.1.1:443, หรือ `host[:port]` และ/หรือ `Ns` (เช่น `8.8.8.8:53 5s`) — เชื่อมได้ = จริง |
| `process_running.py` | **Process Running** (เงื่อนไข v2.14) | มีโปรเซสรันอยู่ = จริง (Windows: tasklist, Linux/macOS: pgrep) — ไม่สนตัวพิมพ์/นามสกุล .exe |
| `window_exists.py` | **Window Exists** (เงื่อนไข v2.14) | มีหน้าต่างที่ชื่อมีข้อความนี้เปิดอยู่ = จริง (Windows: ctypes EnumWindows ล้วน, Linux: xdotool) — เทียบไม่สนตัวพิมพ์ |
| `window_focused.py` | **Window Focused** (เงื่อนไข v2.16) | **หน้าต่างที่โฟกัสอยู่ตอนนี้**มีข้อความในชื่อ = จริง (Windows: GetForegroundWindow ctypes ล้วน, Linux: xdotool, macOS: osascript) — ต่างจาก Window Exists ที่สแกนทุกหน้าต่าง |
| `file_newer_than.py` | **File Newer Than** (เงื่อนไข v2.16) | 2 รูปแบบ: `ไฟล์A > ไฟล์B` = A ใหม่กว่า B (watch งานแปลงไฟล์), `ไฟล์ Ns` = ถูกแก้ภายใน N วินาทีล่าสุด (รอ download เสร็จ) — พาธมีช่องว่างใช้ได้ |
| `http_status.py` | **HTTP Status** (เงื่อนไข v2.16) | `URL [รหัส] [Ns]` เช่น `https://api.local/health 200 3s` — ไม่ใส่รหัส = 2xx ใด ๆ · 4xx/5xx ที่รอเป๊ะก็จริงได้ · urllib stdlib ล้วน เช็ค API ก่อนทำงานต่อ |
| `disk_space_low.py` | **Disk Space Low** (เงื่อนไข v2.17) | `[ไดรฟ์/พาธ] N[GB\|MB\|KB\|B]` เช่น `D: 2GB` — พื้นที่เหลือ < ที่กำหนด = จริง (กันงานเขียนไฟล์พังกลางทาง) · shutil stdlib ล้วน |
| `process_cpu.py` | **Process CPU** (เงื่อนไข v2.17) | `ชื่อ [เกณฑ์%] [Ns]` เช่น `chrome 5% 3s` — โปรเซสใช้ CPU เฉลี่ย > เกณฑ์ = จริง (วัด 2 จุดห่าง Ns) — Windows ctypes / Linux /proc ล้วน |
| `window_closed.py` | **Window Closed** (เงื่อนไข v2.17) | ไม่มีหน้าต่างที่ชื่อมีข้อความนี้ = จริง — ตรงข้าม Window Exists (จบงานเมื่อปิดหน้าต่างเป้าหมาย) |
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

## Plugin API v3 — เงื่อนไข plugin (v2.13)

นอกจาก Action แล้ว plugin ประกาศ**เงื่อนไข**ได้ด้วย — ไฟล์เดียวมีทั้งคู่ได้ (ชื่อต้องต่างกัน):

```python
# plugins/file_exists.py — ตัวอย่างจริงที่แจกมากับโปรแกรม
import os

CONDITION_NAME = "File Exists"          # ห้ามซ้ำกับ Action เดิม/plugin อื่น

def check(ctx, row) -> bool:
    """คืน True/False — ห้าม raise · อย่าแตะเมาส์/คีย์ (dry-run เรียก check จริง)"""
    try:
        path = str(row.get("additional") or "").strip()
        return bool(path) and os.path.isfile(path)
    except Exception:
        return False
```

| กติกา | รายละเอียด |
|---|---|
| จริง / ไม่จริง | จริง = เล่นต่อ · ไม่จริง = ข้าม N แถว (**N = Repeat** — กฎเดียวกับเงื่อนไขทุกชนิด) |
| ใช้ 2 ทาง | ① คอลัมน์ Action = ชื่อเงื่อนไข (dropdown เพิ่มอัตโนมัติ) ② Block Start/End → `if File Exists C:\x.txt` (ผสม `&&` กับเงื่อนไขสีจุด/ตัวแปร/ภาพได้) |
| อาร์กิวเมนต์ | Additional ของแถว (หรือข้อความหลังชื่อในบล็อก) — `{ตัวแปร}` ถูกแทนค่าก่อนส่งเข้า `check` |
| เก็บผลเป็นตัวแปร | ใส่ `>ชื่อ` ท้ายแถว — ผล "1"/"0" เหมือนเงื่อนไขในตัว (v2.10) |
| ชื่อซ้ำ | `CONDITION_NAME` ห้ามชน Action เดิม/Action อื่น/เงื่อนไขอื่น — ไฟล์ที่ชนถูกข้ามพร้อมสาเหตุ (`load_plugins.last_failed`) |
| ตรวจสคริปต์ | 🔍 Validate / `--validate` / ตรวจตอน START / คิว รู้จักชื่อเงื่อนไข plugin ครบ |
| Dry-run | เงื่อนไขเดินจริง (v2.10) → `check` ถูกเรียกจริง — **เขียนให้เป็นอ่านอย่างเดียว** (ห้ามคลิก/พิมพ์) |
| .ahk | แถวเงื่อนไขและบล็อกที่อ้างเงื่อนไข plugin = comment ทั้งบล็อก (AHK แปลไม่ได้) |
| check พัง | เตือนแล้ว**เล่นต่อ** ไม่ข้าม (กลไกเดียวกับ action plugin พัง) — แต่กติกา plugin คือทนเองไม่ raise |

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
- ✅ เงื่อนไขจากชุมชนรอบ v2.16 ปิดแล้ว 3 ตัว: Window Focused / File Newer Than / HTTP Status ·
  รอบ v2.17 ปิดแล้ว 3 ตัว: Disk Space Low / Process CPU / Window Closed — ตัวถัดไปเสนอได้เลย

ส่ง PR มาที่ [CONTRIBUTING.md](../CONTRIBUTING.md) — plugin ดี ๆ จะถูกเพิ่มในตารางข้างบน

## 📝 เกณฑ์รีวิว plugin จากชุมชน (v2.7)

PR plugin ใหม่ต้องผ่านครบทั้ง 6 ข้อ (ผู้รีวิวใช้ checklist นี้):

1. **โครงไฟล์ถูก** — ไฟล์เดียวใน `plugins/`, ขึ้นต้นด้วยตัวอักษร (ขึ้นต้น `_` จะไม่ถูกโหลด),
   ประกาศ `ACTION_NAME` + `run(ctx, row)` หรือ `CONDITION_NAME` + `check(ctx, row)` (v2.13)
   (ไม่ซ้ำกับ Action/เงื่อนไขเดิมและ plugin ที่มีอยู่)
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

## 🚪 ขั้นตอนส่ง plugin เข้าโปรแกรม (v2.8)

1. เปิด issue ด้วยแบบฟอร์ม [เสนอ plugin ใหม่](../.github/ISSUE_TEMPLATE/plugin_submission.md)
   (label `plugin`) — บอกหน้าที่/Additional ที่รับ/ตัวแปรที่เขียน
2. Fork → เขียน `plugins/ชื่อของคุณ.py` ตาม [`plugins/_template.py`](../plugins/_template.py)
3. เพิ่มเทสต์ 4 แบบตามแม่แบบท้าย _template.py ลง test_auto_macro.py
   (⚠️ ชื่อคลาสเทสต์ห้ามซ้ำกับคลาสเดิม — ดู AGENTS.md)
4. เปิด PR อ้าง issue — checklist ฝั่ง plugin ใน PR template จะช่วยให้รีวิวเร็ว
   (ตัวอย่างที่ผ่านแล้ว: random_pause.py / counter.py / open_url.py — เทสต์ TestPluginsCommunity)

# 🖱️ Auto Mouse & Keyboard Macro v1.7

<div align="center">

**โปรแกรมสั่งให้เมาส์และคีย์บอร์ดทำงานอัตโนมัติตามสคริปต์ที่เราตั้งไว้**

![Tests](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/actions/workflows/tests.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![GUI](https://img.shields.io/badge/GUI-Tkinter-2ea043)
![Library](https://img.shields.io/badge/pynput-1.8.2-orange)
![Platform](https://img.shields.io/badge/Platform-Windows-blue)

</div>

---

## 📸 หน้าตาโปรแกรมจริง

<div align="center">
<img src="images/screenshot.png" alt="หน้าจอหลักของโปรแกรม" width="640">
<br><em>หน้าจอหลัก v1.7: เมนูไอคอน + แถบโปรไฟล์ + ตารางคำสั่ง + ปุ่มควบคุมทั้งหมด</em>
</div>

---

## 🖼️ ต้นแบบเดิม (Auto Mouse v1.3)

<div align="center">
<img src="images/pic.png" alt="ต้นแบบ Auto Mouse v1.3" width="480">
<br><em>ต้นแบบ: ตารางคำสั่ง + ปุ่ม START / STOP / REPEAT / RECORD</em>
</div>

---

## ✨ ความสามารถ

| ฟีเจอร์ | รายละเอียด |
|---|---|
| 🔴 **RECORD** (F9) | บันทึกการคลิกเมาส์และการกดคีย์แบบเรียลไทม์ พร้อมจับเวลาหน่วงอัตโนมัติ |
| ▶️ **START** (F6) | เล่นสคริปต์ที่เปิดใช้ (☑) หนึ่งรอบ |
| 🔁 **REPEAT** | เล่นวนซ้ำต่อเนื่อง หรือติ๊ก "วนซ้ำไม่จำกัด" (F10) เพื่อวนตลอด |
| ⏹️ **STOP** (F8) | หยุดทุกอย่างทันที |
| ✅ **Checkbox รายแถว** | เลือกได้ว่าแถวไหนจะถูกเล่น แถวไหนข้าม |
| ✏️ **แก้ค่าในตาราง** | ดับเบิลคลิกช่องไหนก็ได้เพื่อแก้ Action / คีย์ / เวลา / Repeat |
| 🎯 **จับพิกัดเมาส์** | ดับเบิลคลิกช่อง X หรือ Y → นับถอยหลัง 3 วิ → จับตำแหน่งเมาส์ปัจจุบัน |
| 💾 **Save / Load** | เก็บสคริปต์เป็นไฟล์ `.json` เปิดกลับมาแก้ไขได้ + autosave ตอนปิดโปรแกรม |
| 🖥️ **Live statusbar** | แสดงพิกัดเมาส์และคีย์ที่กดล่าสุดแบบสด ๆ |
| 📦 **แพ็กเป็น .exe** | build.bat → ได้ไฟล์เดียว `dist/AutoMouseMacro.exe` ไม่ต้องติดตั้ง Python |
| 🌐 **Global Hotkey** | F6/F8/F9/F10 กดได้แม้โปรแกรมไม่ได้โฟกัส |
| 🖼️ **คลิกตามภาพ** | ระบุไฟล์ .png → หาบนหน้าจอด้วย OpenCV แล้วคลิกให้เอง |
| 🎛️ **โปรไฟล์** | เก็บหลายสคริปต์สลับใช้ (งานบ้าน / เกม A / เกม B) |
| ⏰ **เล่นตามเวลา** | ตั้งเล่นอัตโนมัติ "ทุก N นาที" หรือ "ทุกวัน HH:MM" |

## 🧩 คำสั่งที่รองรับในตาราง

**เมาส์:** Left Click / Left Down / Left Up / Right Click / Right Down / Right Up / Middle Click / Middle Down / Middle Up / Double Left Click / Double Right Click / Ctrl+Click / Shift+Click / Alt+Click / Ctrl+Right Click / Scroll Up / Scroll Down (จำนวนจังหวะใน Additional) / Move Mouse / Move Mouse by Offset / Save Cursor / Restore Cursor

**คีย์บอร์ด:** Tap Key / Press Key / Release Key — ช่อง Additional ใส่ชื่อคีย์ได้ เช่น
`a` `5` `space` `enter` `esc` `ctrl` `shift` `alt` `win` `f1`–`f12` `up` `down` `left` `right` `pgup` `pgdn` `prtsc` หรือรหัส virtual key เช่น `27`

**เพิ่มเติม v1.5 (แรงบันดาลใจจาก [automouseclick.com](https://www.automouseclick.com/)):**
- **Type Text** — พิมพ์ข้อความ (รองรับไทย) เช่น `สวัสดี world`
- **Launch App** — เปิดโปรแกรม/เว็บ เช่น `notepad.exe` หรือ `https://example.com`
- **Image Click / Wait for Image** — คลิกตามภาพ / รอภาพปรากฏ (ชื่อไฟล์ .png ใน Additional; ต้องติดตั้ง `opencv-python Pillow`)
  - 🆕 **Search Area:** ระบุกรอบค้นหาได้ — X,Y = มุมซ้ายบน, Mins = กว้าง, Secs = สูง (เว้นว่าง = ทั้งจอ)
- **Beep** — เสียงเตือน

> 💡 **ดีเลย์สุ่ม:** ใส่ Secs แบบ `1-3` = สุ่มดีเลย์ 1–3 วิ ทุกรอบ

---

## 🚀 เริ่มใช้งานเร็ว ๆ

### วิธีที่ 1 — ใช้ไฟล์ .exe สำเร็จรูป (แนะนำ)

```bash
build.bat        # build ครั้งเดียว → dist\AutoMouseMacro.exe
```

จากนั้นดับเบิลคลิก `dist\AutoMouseMacro.exe` ได้เลย **ไม่ต้องติดตั้ง Python**

### วิธีที่ 2 — รันจากซอร์ส

```bash
py -m pip install -r requirements.txt    # ติดตั้ง pynput
run.bat                                  # หรือ: py auto_macro.py
```

> 💡 **ต้องมี Python 3.8+** (แนะนำ 3.12 ขึ้นไป) — โหลดที่ [python.org](https://www.python.org/downloads/)
> ถ้าเครื่องมีแค่ Windows Store stub ให้ใช้คำสั่ง `py` แทน `python`

### 🎬 ทดลองด้วยสคริปต์เดโม่ (มีให้ในโปรเจกต์)

| ไฟล์ | ทำอะไร |
|---|---|
| `demo_script.json` | เปิด Notepad → พิมพ์ข้อความไทย → เคาะ Enter → บี๊บ → คืนเมาส์จุดเดิม (แสดงดีเลย์สุ่ม `0.5-1.5` และ Repeat ด้วย) |
| `demo_move_click.json` | เลื่อนเมาส์เป็นสี่เหลี่ยม → ทดสอบ Scroll ขึ้น/ลง → บี๊บ → คืนเมาส์ (ไม่คลิกอะไรเลย ปลอดภัย) |

โหลดใน GUI: เมนู **Load** → เลือกไฟล์เดโม่ → กด **START**
หรือรันทันทีในคอนโซล:

```bash
py auto_macro.py demo_script.json
```

> ทั้งสองไฟล์ **ไม่คลิกที่ใด** ทั้งสิ้น (ใช้แค่พิมพ์/เคาะคีย์/เลื่อนเมาส์/scroll) จึงไม่มีผลข้างเคียงกับเครื่อง

### 🧪 ทดลองใช้ครั้งแรกใน 60 วิ

1. กด **F9 (RECORD)** → สถานะเป็น "กำลังบันทึก"
2. คลิกที่ใดก็ได้บนจอ 2–3 จุด แล้วกด **F9** อีกครั้งเพื่อหยุด
3. กด **START (F6)** → เมาส์จะเล่นซ้ำทุกคลิกที่เพิ่งทำ
4. ลองกด **REPEAT** ให้วนตลอด แล้วหยุดด้วย **F8**

---

## 📖 คู่มือการใช้งาน

### ทำความรู้จักตาราง

| คอลัมน์ | ความหมาย |
|---|---|
| ☑ | เปิด/ปิดการใช้แถวนี้ (คลิกเพื่อสลับ) |
| # | ลำดับแถว |
| X, Y | พิกัดจุดที่จะย้ายเมาส์ไปก่อนคลิก |
| Button / Action | คำสั่ง: คลิกเมาส์ หรือ กดคีย์ |
| Additional | ชื่อคีย์ (เฉพาะคำสั่งคีย์บอร์ด) |
| Mins / Secs | เวลารอ **ก่อน** ทำคำสั่งในแถวนั้น |
| Repeat | จำนวนครั้งที่ทำคำสั่งนี้ซ้ำในแถวเดียว |

### การแก้ไขตาราง

- **ดับเบิลคลิกช่อง X / Y** → นับถอยหลัง 3 วิ แล้วจับพิกัดเมาส์ปัจจุบันให้อัตโนมัติ
- **ดับเบิลคลิกช่องอื่น** → เปิดหน้าต่างแก้ค่า (Action เป็น dropdown, ช่องเวลาพิมพ์ได้)
- **คลิกขวาบนแถว:** คัดลอกแถวนี้ / แทรกแถวใหม่ด้านบน-ด้านล่าง / ลบแถว
- **ปุ่มเสริม:** ＋ เพิ่มบรรทัด / － ลบที่เลือก / ▲▼ เลื่อนลำดับ / ล้างทั้งหมด / ปุ่ม Delete บนคีย์บอร์ด

### โปรไฟล์ และ เล่นอัตโนมัติตามเวลา

- **แถบ "โปรไฟล์"** ใต้เมนู — เก็บสคริปต์ได้หลายชุด สลับใช้ได้ทันที
  (ตัวอย่าง: "งานบ้าน", "เกม A", "เกม B") เก็บใน `macro_profiles.json`
- **ปุ่ม "⏰ เล่นอัตโนมัติ..."** — ตั้งให้เล่นโปรไฟล์ปัจจุบัน
  - ทุก N นาที (เช่น ทุก 10 นาที)
  - ทุกวัน เวลา HH:MM (เช่น 09:30)
  - การเล่นจะวนซ้ำ 1 รอบจบ และหยุดได้ด้วย F8 ตามปกติ

### ตัวเลือกการเล่น (แถบปุ่มด้านล่าง)

| ตัวเลือก | ความหมาย |
|---|---|
| **วนซ้ำไม่จำกัด** (F10) | เล่นต่อเนื่องไม่สิ้นสุด |
| **คืนเมาส์จุดเดิม** | จบรอบแล้วย้ายเมาส์กลับตำแหน่งที่เริ่มเล่น |
| **ความเร็ว** | ตัวคูณดีเลย์ทั้งหมด: 0.25× / 0.5× / 1× / 2× / 4× |
| **รอบ** | จำนวนรอบของสคริปต์ทั้งชุด — 0 = ไม่จำกัด |

### คีย์ลัดทั้งหมด (Global — กดได้แม้ไม่โฟกัสหน้าต่าง)

| คีย์ | ทำอะไร |
|---|---|
| **F6** | เริ่มเล่นสคริปต์ |
| **F8** | หยุดทั้งหมด |
| **F9** | เริ่ม/หยุดบันทึก |
| **F10** | สลับวนซ้ำไม่จำกัด |
| **Delete** | ลบแถวที่เลือก (เมื่อโฟกัสตาราง) |
| **Double-click** | แก้ค่าในเซลล์ |

> ⚠️ ถ้าโปรแกรมอื่นใช้คีย์ F6–F10 อยู่ global hotkey อาจถูกแทนที่ —
> ดูสถานะได้ที่เมนู Settings (กรณีนี้คีย์จะทำงานเมื่อโฟกัสหน้าต่างโปรแกรมเท่านั้น)

---

## ⚙️ การแจกจ่าย / Build เอง

```bash
build.bat                                # หรือแบบชัดเจน:
py -m PyInstaller auto_macro.spec --noconfirm --clean
```

ผลลัพธ์: `dist/AutoMouseMacro.exe` (ไฟล์เดียว ~13 MB, GUI ไม่มี console)

---

## 📁 โครงสร้างโปรเจกต์

```
├── auto_macro.py        # โปรแกรมหลักทั้งหมด (ไฟล์เดียวจบ)
├── test_auto_macro.py   # unit tests (unittest)
├── auto_macro.spec      # ไฟล์ spec ของ PyInstaller
├── build.bat            # สคริปต์ build .exe
├── run.bat              # สคริปต์รันจากซอร์ส
├── requirements.txt     # dependencies
├── pic.png              # รูปต้นแบบ
└── docs/                # เอกสารทั้งหมด (md + html)
    ├── README.md / README.html
    ├── RESEARCH.md / RESEARCH.html
    ├── CHANGELOG.md / CHANGELOG.html
    └── images/pic.png
```

## 🔄 CI/CD อัตโนมัติ

- **Tests** — ทุกครั้งที่ push/PR ระบบจะรัน unit tests บน Python 3.12–3.14 (Windows)
  ดูสถานะได้ที่แท็บ [Actions](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/actions)
- **Release** — สร้าง .exe และแนบให้โหลดอัตโนมัติเมื่อ push tag:

```bash
git tag v1.7 && git push origin v1.7
```

## ⌨️ เล่นผ่าน Command Line (ไม่เปิด GUI)

```bash
py auto_macro.py script.json                  # เล่นรอบเดียว
py auto_macro.py script.json --loop           # วนไม่จำกัด
py auto_macro.py script.json --loops 5        # 5 รอบ
py auto_macro.py script.json --speed 2        # เร็วขึ้น 2 เท่า
```

กด **F8** หรือ **Esc** เพื่อหยุด (หรือ Ctrl+C) — เหมาะกับการรันผ่าน Windows Task Scheduler

## 🧪 ทดสอบ

```bash
py -m unittest test_auto_macro -v    # 51 unit tests
```

## 📚 เอกสารเพิ่มเติม

- **[RESEARCH](RESEARCH.html)** — เทคนิคการควบคุมเมาส์/คีย์บอร์ดด้วย pynput, threading, และการเลือกเครื่องมือ
- **[CHANGELOG](CHANGELOG.html)** — ประวัติการเปลี่ยนแปลงทุกเวอร์ชัน

---

<div align="center">
<sub>สร้างด้วย Python + Tkinter + pynput • ทำงานบน Windows (รองรับ Linux/macOS)</sub>
</div>

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Mouse & Keyboard Macro  v1.18
โปรแกรมสั่งให้เมาส์/คีย์บอร์ดทำงานอัตโนมัติตามสคริปต์ที่ตั้งไว้

- RECORD (F9)      : บันทึกการคลิกเมาส์ / การกดคีย์แบบเรียลไทม์
- START (F6)       : เล่นสคริปต์ที่เปิดใช้ (☑) หนึ่งรอบ
- REPEAT           : เล่นวนซ้ำ, ติ๊ก "วนซ้ำไม่จำกัด" หรือกด F10 เพื่อวนตลอด
- STOP (F8)        : หยุดทันที
- ดับเบิลคลิกช่อง X / Y : นับถอยหลัง 3 วิ แล้วจับพิกัดเมาส์ปัจจุบัน
- ดับเบิลคลิกช่องอื่น    : แก้ Action / คีย์ / เวลาหน่วง / จำนวนรอบ
- Save / Load      : สคริปต์เป็นไฟล์ .json (เปิดโปรแกรมครั้งถัดไปโหลดอัตโนมัติ)
- โปรไฟล์          : เก็บหลายสคริปต์สลับใช้ได้ (macro_profiles.json)
- Schedule         : เล่นอัตโนมัติ "ทุก N นาที" หรือ "รายวัน HH:MM"
- Global Hotkey    : F6/F8/F9/F10 กดได้แม้โปรแกรมไม่ได้โฟกัส
- Image Click      : คลิกตามภาพ — หาตำแหน่งภาพบนหน้าจอแล้วคลิกให้ (ต้องมี opencv-python + Pillow)
- v1.5 (จาก automouseclick.com): Scroll, Double Click, คลิกแบบ Ctrl/Shift/Alt,
  Move Mouse + Offset, Save/Restore Cursor, Type Text, Launch App, Wait for Image,
  Beep, ดีเลย์สุ่ม (ใส่ Secs แบบ "1-3"), ตัวคูณความเร็ว, จำนวนรอบของสคริปต์ทั้งชุด,
  คืนเมาส์กลับจุดเริ่มเมื่อจบรอบ, บันทึก scroll ตอน RECORD
- v1.8: ระบบ log บันทึกการเล่นแต่ละรอบลงไฟล์ macro_log.txt (เปิด/ปิดได้ใน Settings,
  ใช้ทั้ง GUI และ CLI [คลี่ออกด้วย --no-log]), เก็บสถานะเปิด/ปิด log ใน macro_conf.json
- v1.9: หน้าต่าง Log viewer (ดู log ย้อนหลังจากในโปรแกรม), Hot-profile F1–F4
  (ตั้งโฟลเดอร์แล้วกด F1–F4 เพื่อโหลดสคริปต์ลำดับที่ 1–4 แล้วเล่นทันที), E2E tests
- v1.10: เล่นแบบสุ่มลำดับ/สุ่มสัดส่วนแถว (shuffle + %), Record wizard
  (อัด→ตรวจ→ทดลองเล่น→บันทึก ในหน้าต่างเดียว), CLI --watchdog รีสตาร์ตอัตโนมัติเมื่อจบ/พัก
- v1.11: Self-check ตรวจสุขภาพระบบตอนเปิด (pynput/OpenCV/hotkey/admin แสดงใน Settings),
  หน้าต่าง 📊 Stats สรุปสถิติการเล่นจาก log (จำนวนรอบ/หยุด/watchdog/แถวที่ช้าสุด),
  สคริปต์เดโม่เฝ้าระบบ + run_watchdog.bat, หน้าเว็บแนะนำโปรแกรม (docs/LANDING.html)
- v1.12: กราฟสถิติต่อวันในหน้า 📊 Stats (canvas วาดเอง), Export/Import การตั้งค่า
  ทั้งหมดเป็นไฟล์เดียวย้ายเครื่องได้ (Settings), ปุ่ม 🧪 ทดสอบระบบจริงใน Settings
- v1.13: Backup อัตโนมัติทุกครั้งที่ปิดโปรแกรม (backups/ เก็บย้อนหลัง 7 วัน),
  เมนู Help ฉบับเต็มครอบทุกฟีเจอร์ + ปุ่มเปิด TUTORIAL
- v1.14: ตั้งค่า backup ได้ใน Settings (เปิด/ปิด + จำนวนวัน 1-90), สลับภาษา
  ไทย/English ได้ใน Settings (TR + _t) จำค่าใน macro_conf.json
- v1.15: i18n ครบทุก dialog (Settings/Help/Wizard/Stats/Log/Hot-profile/context menu),
  สรุปการใช้งานรวม + กราฟรายเดือนใน Stats (log_monthly_series)
- v1.16: Custom Action plugins — ผู้ใช้เขียน Python สั้น ๆ ใน plugins/*.py
  (ประกาศ ACTION_NAME + run(ctx, row)) เป็น Action ใหม่ได้โดยไม่แก้โค้ดหลัก
- v1.17: ค้นหาแถว (Ctrl+F), Undo ลบแถว (Ctrl+Z), วางสคริปต์จากคลิปบอร์ด,
  If Image — ภาพไม่เจอ → ข้าม N แถวถัดไป (ตั้งจำนวนใน Repeat)
- v1.18: Wait for Pixel Color (รอจุดสี, หน่วงใน Additional), Else If Image
  (เงื่อนไขสองทาง A/B), สถิติราย Action ในหน้า 📊 Stats
- v1.19: ตัวแปรในสคริปต์ (Set Variable + {name}), ปุ่มจับสีจากจอ, timeout ตั้งได้
  (เช่น "logo.png 60s"), จำค่าการตั้งค่า/ตารางเวลาลง conf, CLI เตือน action ไม่รองรับ,
  player ไม่เรียก Tk ข้ามเธรดอีกต่อไป
- v1.20: Set/Read Clipboard (ตั้ง/อ่านคลิปบอร์ด เก็บเป็นตัวแปรได้, รองรับไทยบน CLI
  ด้วย Win32 API), Plugin API v2 (ctx.stop_check() + ctx.ui)
- v1.20.1: แก้ HotkeyEdit ลืมเก็บ on_done — ดับเบิลคลิกแก้เซลล์แล้วกดตกลงพังมาตั้งแต่ v1.4
- v1.20.2: Type Text พิมพ์ด้วย SendInput KEYEVENTF_UNICODE — ถูกต้องแม้ layout
  คีย์บอร์ด active เป็นภาษาอื่น (เดิม layout ไทยพิมพ์อังกฤษแล้วเพี้ยนเป็น "ิ" ฯลฯ)
- v1.20.3: ช่อง Additional พิมพ์ข้อความอิสระได้ (เดิมเป็น readonly มีแต่ชื่อคีย์) +
  เว้นจังหวะ 15ms/ตัวอักษรกันแอปเป้าหมายที่ busy กลืน burst (เช่น Notepad เพิ่งเปิด)
- v1.20.4: คอมโบปุ่ม+คีย์ เช่น "Ctrl+W", "Ctrl+Shift+T" ใน Tap/Press/Release Key
  + ตัวอักษร/ตัวเลขเดี่ยว = ปุ่มกายภาพ (VK) ถูกต้องแม้ layout อื่น active

ต้องใช้ Python 3.8+ และไลบรารี pynput  →  pip install pynput
ทดสอบบน Windows และทำงานได้บน Linux / macOS ด้วยไลบรารีเดียวกัน
"""

import json
import os
import random
import re
import sys
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

import datetime
import glob

try:
    from pynput import keyboard, mouse
    from pynput.keyboard import (Controller as KbController, GlobalHotKeys,
                                 KeyCode, Key)
    from pynput.mouse import Button, Controller as MouseController
except ImportError:
    print("ไม่พบไลบรารี pynput  ติดตั้งก่อนด้วยคำสั่ง:  pip install pynput")
    sys.exit(1)

# ตัวเลือกสำหรับฟีเจอร์ Image Click (ถ้าไม่ติดตั้ง ส่วนอื่นยังใช้ได้ปกติ)
try:
    import cv2
    import numpy as np
    from PIL import ImageGrab
    HAS_CV = True
except ImportError:
    HAS_CV = False


# === ENGINE-BEGIN (v2.0: แยกไป macro_engine.py — อย่าแก้ในไฟล์นี้ แก้ที่ macro_engine.py)
import os
import random
import re
import sys
import time
import datetime
import glob

try:
    from pynput import keyboard, mouse
    from pynput.keyboard import (Controller as KbController, GlobalHotKeys,
                                 KeyCode, Key)
    from pynput.mouse import Button, Controller as MouseController
except ImportError:
    print("ไม่พบไลบรารี pynput  ติดตั้งก่อนด้วยคำสั่ง:  pip install pynput")
    sys.exit(1)

# ตัวเลือกสำหรับฟีเจอร์ Image Click (ถ้าไม่ติดตั้ง ส่วนอื่นยังใช้ได้ปกติ)
try:
    import cv2
    import numpy as np
    from PIL import ImageGrab
    HAS_CV = True
except ImportError:
    HAS_CV = False

__version__ = "1.22.0"
APP_TITLE = "Auto Mouse & Keyboard Macro v" + __version__
PLUGINS_DIR = "plugins"         # โฟลเดอร์เก็บ Custom Action plugins (v1.16)
BACKUP_DIR = "backups"          # โฟลเดอร์เก็บ backup อัตโนมัติ
BACKUP_KEEP_DAYS = 7            # เก็บ snapshot ย้อนหลังกี่วัน (ค่าเริ่มต้น)

# ------------------------------------------------------- ข้อความ 2 ภาษา ----
# i18n (v1.14): ปุ่มหลัก/ข้อความสถานะ — เลือกภาษาใน Settings แล้วจำใน macro_conf.json
TR = {
    "th": {"start": "START", "stop": "STOP", "repeat": "REPEAT", "record": "RECORD",
           "forever": "วนซ้ำไม่จำกัด (F10)", "restore": "คืนเมาส์จุดเดิม",
           "shuffle": "สุ่มลำดับ", "pct": "สัดส่วนแถว:", "speed": "ความเร็ว:",
           "loops": "รอบ:", "loops_note": "(0=ไม่จำกัด)",
           "playing": "กำลังเล่นสคริปต์ (%s) — F8 หยุด", "done": "เล่นจบแล้ว ✔",
           "stopped": "หยุดแล้ว — ปล่อยคีย์/ปุ่มที่ค้างแล้ว",
           "mode_once": "เล่นครั้งเดียว", "mode_loop": "วนซ้ำ",
           "no_rows": "ยังไม่มีรายการที่เปิดใช้ (☑) ให้เล่น",
           "selfcheck_warn": "⚠️ self-check: บางส่วนไม่พร้อม — ดูรายละเอียดใน Settings",
           "col_action": "Button / Action", "ctx_copy": "📋 คัดลอกแถวนี้",
           "ctx_above": "⬆️ แทรกแถวใหม่ด้านบน", "ctx_below": "⬇️ แทรกแถวใหม่ด้านล่าง",
           "ctx_del": "🗑️ ลบแถวนี้", "ctx_undo": "↩️ กู้คืนแถวที่ลบ (Ctrl+Z)",
           "nothing_undo": "ไม่มีอะไรให้กู้คืน", "undone": "กู้คืนแถวแล้ว",
           "find_title": "🔍 ค้นหาแถว", "find_label": "ข้อความ (match ทุกคอลัมน์):",
           "find_btn": "ค้นหา", "found": "เจอที่แถว %d", "notfound": "ไม่เจอ: %s",
           "clip_empty": "คลิปบอร์ดว่าง",
           "clip_bad": "คลิปบอร์ดไม่ใช่สคริปต์ JSON (ต้องเป็นรายการแถว)",
           "clip_added": "วางจากคลิปบอร์ดแล้ว %d แถว",
           "ifimg_skip": "If Image ไม่เจอ → ข้าม %d แถวถัดไป", "ifimg_hit": "If Image เจอ → เล่นต่อ",
           "ifloop_hit": "ยังไม่เกินรอบที่กำหนด → เล่นต่อ", "iftime_hit": "ยังไม่ผ่านเวลาที่กำหนด → เล่นต่อ",
           "ctx_section": "🗂️ เปลี่ยนเป็นหัวข้อ Section", "section_new": "🗂️ เพิ่มหัวข้อ Section",
           "group_collapse": "📁 ย่อกลุ่มนี้", "group_expand": "📂 ขยายกลุ่มนี้",
           "group_show_hint": "📦 กลุ่มนี้ย่ออยู่ — แถวซ่อนถูกเล่นตามปกติ",
           "group_expand_first": "📂 ขยายกลุ่มก่อนแก้แถว",
           "else_title": "🔀 Else If Image", "else_label": "วางหลังกลุ่ม A: If Image เจอ → ข้ามกลุ่ม B (Repeat แถว), ไม่เจอ → เล่นกลุ่ม B",
           "pixel_title": "🎨 Wait for Pixel Color", "pixel_label": "x,y = จุดที่ต้องการ · #RRGGBB = สีที่รอ · วินาที = หน่วงก่อนตรวจ (พิมพ์ใน Additional)",
           "save": "บันทึก", "close": "ปิด", "language": "ภาษา (Language):",
           "backup_label": "Backup อัตโนมัติตอนปิดโปรแกรม (เก็บย้อนหลัง",
           "days": "วัน — 1–90)", "log_label": "บันทึก log การเล่นลงไฟล์ macro_log_วันที่.txt",
           "open_log_folder": "เปิดโฟลเดอร์ log", "selftest_btn": "🧪 ทดสอบระบบจริง (ขยับเมาส์+บี๊บ)",
           "selftest_ok": "🧪 ทดสอบแล้ว: เมาส์ขยับเป็นสามเหลี่ยมแล้วคืนจุดเดิม + บี๊บ 2 ครั้ง — "
                          "ถ้าเมาส์ไม่ขยับหรือไม่ได้ยินเสียง แสดงว่าระบบมีปัญหาจริง",
           "export_btn": "⬆️ Export การตั้งค่า", "import_btn": "⬇️ Import การตั้งค่า",
           "export_note": "Export = งานปัจจุบัน + โปรไฟล์ทุกชุด + ตั้งค่า log/hot-profile "
                          "เป็นไฟล์เดียว (ย้ายเครื่อง/สำรอง)",
           "hotkeys_title": "คีย์ลัดของโปรแกรม (ทำงานได้ทั้งแบบโฟกัสและไม่โฟกัส)",
           "sc_play": "เริ่มเล่นสคริปต์", "sc_stop": "หยุดทั้งหมด", "sc_rec": "เริ่ม/หยุดบันทึก",
           "sc_forever": "สลับวนซ้ำไม่จำกัด", "sc_hp": "Hot-profile: เล่นสคริปต์ลำดับ 1-4",
           "sc_del": "ลบแถวที่เลือก", "sc_edit": "แก้ค่าในเซลล์", "sc_speed": "ตัวคูณความเร็ว / จำนวนรอบ",
           "sc_rand": "ดีเลย์สุ่มรายแถว", "gk_ok": "ทำงานอยู่ ✅ (กดได้ทุกที่)",
           "gk_bad": "ไม่ทำงาน ⚠️ (ต้องโฟกัสหน้าต่าง)", "sc_check": "ตรวจสุขภาพระบบ (self-check ตอนเปิดโปรแกรม):"},
    "en": {"start": "START", "stop": "STOP", "repeat": "REPEAT", "record": "RECORD",
           "forever": "Loop forever (F10)", "restore": "Restore mouse position",
           "shuffle": "Shuffle", "pct": "Row %:", "speed": "Speed:",
           "loops": "Loops:", "loops_note": "(0 = unlimited)",
           "playing": "Playing script (%s) — F8 to stop", "done": "Finished ✔",
           "stopped": "Stopped — released stuck keys/buttons",
           "mode_once": "play once", "mode_loop": "loop",
           "no_rows": "No enabled (☑) rows to play",
           "selfcheck_warn": "⚠️ self-check: some parts not ready — see Settings",
           "col_action": "Button / Action", "ctx_copy": "📋 Duplicate row",
           "ctx_above": "⬆️ Insert row above", "ctx_below": "⬇️ Insert row below",
           "ctx_del": "🗑️ Delete row", "ctx_undo": "↩️ Undo last delete (Ctrl+Z)",
           "nothing_undo": "Nothing to undo", "undone": "Rows restored",
           "find_title": "🔍 Find row", "find_label": "Text to search (any column):",
           "find_btn": "Find", "found": "Found at row %d", "notfound": "Not found: %s",
           "clip_empty": "Clipboard is empty",
           "clip_bad": "Clipboard is not a JSON row list",
           "clip_added": "Pasted %d rows from clipboard",
           "ifimg_skip": "If Image miss → skip next %d rows", "ifimg_hit": "If Image found → continue",
           "ifloop_hit": "Round below threshold → continue", "iftime_hit": "Before the set time → continue",
           "ctx_section": "🗂️ Convert to Section header", "section_new": "🗂️ Add Section header",
           "group_collapse": "📁 Collapse this group", "group_expand": "📂 Expand this group",
           "group_show_hint": "📦 Group collapsed — hidden rows still play",
           "group_expand_first": "📂 Expand group before editing",
           "save": "Save", "close": "Close", "language": "Language (ภาษา):",
           "backup_label": "Auto backup on close (keep last",
           "days": "days — 1–90)", "log_label": "Write play log to macro_log_<date>.txt",
           "open_log_folder": "Open log folder", "selftest_btn": "🧪 Real system test (move mouse + beep)",
           "selftest_ok": "🧪 Tested: mouse moved in a triangle and returned + 2 beeps — "
                          "if nothing moved or you heard nothing, the system has a real problem",
           "export_btn": "⬆️ Export settings", "import_btn": "⬇️ Import settings",
           "export_note": "Export = current rows + all profiles + log/hot-profile options "
                          "as one file (move PC / backup)",
           "hotkeys_title": "Hotkeys (work both focused and unfocused)",
           "sc_play": "Play script", "sc_stop": "Stop all", "sc_rec": "Start/stop recording",
           "sc_forever": "Toggle infinite loop", "sc_hp": "Hot-profile: play script 1-4",
           "sc_del": "Delete selected row", "sc_edit": "Edit a cell", "sc_speed": "Speed / loops",
           "sc_rand": "Random delay per row", "gk_ok": "Running ✅ (works everywhere)",
           "gk_bad": "Not running ⚠️ (needs window focus)", "sc_check": "System health (self-check at startup):"},
}


def tr(lang, key):
    """ดึงข้อความตามภาษา (lang: 'th'/'en') — คีย์หาย = ใช้ภาษาไทย fallback"""
    return TR.get(lang, TR["th"]).get(key, TR["th"].get(key, key))
CONF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "macro_conf.json")
PROFILES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "macro_profiles.json")
DEFAULT_PROFILE = "ค่าเริ่มต้น"
DEFAULT_THRESHOLD = 0.80        # ความมั่นใจเริ่มต้นของ Image Click (80%)
MAX_LOG_LINES = 500             # จำนวนบรรทัดสูงสุดของ log (ตัดข้างหลังอัตโนมัติ)
LOG_ENABLED_DEFAULT = True      # ค่าเริ่มต้นของการบันทึก log

BTN_TH = {"Left Down": ("Left", "Down"), "Left Up": ("Left", "Up"),
          "Left Click": ("Left", "Click"), "Right Down": ("Right", "Down"),
          "Right Up": ("Right", "Up"), "Right Click": ("Right", "Click"),
          "Middle Down": ("Middle", "Down"), "Middle Up": ("Middle", "Up"),
          "Middle Click": ("Middle", "Click")}

MOUSE_BTNS = list(BTN_TH.keys())
KEY_ACTIONS = ["Press Key", "Release Key", "Tap Key"]
IMAGE_ACTION = "Image Click"
IF_IMAGE = "If Image"            # เงื่อนไข v1.17: ภาพไม่เจอ → ข้าม N แถวถัดไป
ELSE_IMAGE = "Else If Image"     # เงื่อนไข v1.18: สองทาง — เจอ → กลุ่ม A (ก่อนหน้า), ไม่เจอ → กลุ่ม B (หลัง)
WAIT_PIXEL = "Wait for Pixel Color"  # v1.18: รอจุดสี (x,y + #RRGGBB) ก่อนทำงานต่อ
IF_LOOP = "If Loop"              # เงื่อนไข v1.21: รอบที่ >= N → ข้าม N แถวถัดไป
IF_TIME = "If Time"              # เงื่อนไข v1.21: ผ่าน HH:MM แล้ว → ข้าม N แถวถัดไป

# v1.22: หมวดสีของแถวตารางตามชนิด Action — แยกกลุ่มเห็นภาพ แค่การจัดระเบียบ ไม่เปลี่ยนพฤติกรรม
ROW_STYLE = {"run": {"background": "#c8e6c9"},
             "section": {"background": "#cfe3f7", "foreground": "#1a3d6d"},
             "cond": {"background": "#fdf1d6"},            # เงื่อนไข (If Image/Else/Loop/Time)
             "key": {"background": "#e6e0f8"},             # คีย์บอร์ด (Tap/Press/Release/Type Text)
             "special": {"background": "#dff0f5"},         # พิเศษ (Image/Pixel/Launch/Beep/Clipboard/ตัวแปร)
             "odd": {"background": "#ffffff"},
             "even": {"background": "#f2f6fb"}}


def row_tag(button):
    """คืนชื่อ tag ตามชนิด Action (v1.22) — แถวเงื่อนไข/คีย์/พิเศษได้สีของหมวด
    แถวเมาส์ทั่วไปใช้แถบสลับ even/odd เหมือนเดิม"""
    if button == SECTION_HEADER:
        return "section"
    if button in (IF_IMAGE, ELSE_IMAGE, IF_LOOP, IF_TIME):
        return "cond"
    if button in ("Tap Key", "Press Key", "Release Key", "Type Text"):
        return "key"
    if button in ("Image Click", "Wait for Image", "Wait for Pixel Color", "Launch App",
                  "Beep", "Set Clipboard", "Read Clipboard", "Set Variable"):
        return "special"
    return None


def row_tags(button, n):
    """คืน tuple tags เต็ม (เรียกตอน insert/item) — แถวเมาส์ = แถบสลับเดิม, หมวดพิเศษ = สีหมวด"""
    t = row_tag(button)
    if t:
        return (t,)
    return ("even" if n % 2 else "odd",)


_COLLAPSED_RE = re.compile(r"\(ย่อ (\d+) แถว\)\s*$")   # ป้ายกลุ่มที่ถูกย่อ (v1.22) — match ท้ายข้อความ


def _save_head_add(add, n):
    """ต่อท้ายชื่อหัวข้อด้วย '(ย่อ N แถว)' — เก็บชื่อเดิมไว้ข้างหน้า"""
    s = str(add or "").strip()
    m = re.match(r"^(.*?)\s*\(ย่อ \d+ แถว\)$", s)
    base = m.group(1) if m else s
    return ((base + " ") if base else "") + "(ย่อ %d แถว)" % n
# ฟีเจอร์เพิ่มเติมแรงบันดาลใจจาก automouseclick.com (v1.5)
SCROLL_ACTIONS = ["Scroll Up", "Scroll Down"]
DBL_ACTIONS = ["Double Left Click", "Double Right Click"]
MOD_CLICKS = ["Ctrl+Click", "Shift+Click", "Alt+Click", "Ctrl+Right Click"]
MOVE_ACTIONS = ["Move Mouse", "Move Mouse by Offset", "Save Cursor", "Restore Cursor"]
EXTRA_ACTIONS = ["Type Text", "Launch App", "Wait for Image", "Beep"]
VAR_ACTIONS = ["Set Variable"]   # v1.19: ตัวแปรในสคริปต์ — ใช้ {ชื่อ} แทนค่าในช่องอื่น
CLIP_ACTIONS = ["Set Clipboard", "Read Clipboard"]  # v1.20: ตั้ง/อ่านคลิปบอร์ด
LOOP_ACTIONS = ["If Loop"]       # v1.21: รอบที่ >= N → ข้าม N แถวถัดไป
TIME_ACTIONS = ["If Time"]       # v1.21: ผ่าน HH:MM แล้ว → ข้าม N แถวถัดไป
SECTION_HEADER = "⬛ หัวข้อ"      # v1.21: แถวจัดระเบียบ — ไม่ทำอะไรตอนเล่น
ACTIONS_ALL = (MOUSE_BTNS + KEY_ACTIONS + [IMAGE_ACTION, IF_IMAGE, ELSE_IMAGE, WAIT_PIXEL]
               + SCROLL_ACTIONS + DBL_ACTIONS + MOD_CLICKS + MOVE_ACTIONS + EXTRA_ACTIONS
               + VAR_ACTIONS + CLIP_ACTIONS + LOOP_ACTIONS + TIME_ACTIONS
               + [SECTION_HEADER])

# ------------------------------------------- pixel color helpers (v1.18) ----
def parse_color_hex(txt):
    """แปลง #RGB / #RRGGBB / RRGGBB → (r, g, b) — รูปแบบไม่ถูกคืน None"""
    s = str(txt or "").strip().lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    if len(s) != 6:
        return None
    try:
        return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))
    except ValueError:
        return None


# -------------------------------- เงื่อนไขนับรอบ/เวลา (v1.21) ----
def parse_if_loop(txt):
    """แปลง Additional ของ If Loop → N (เล่นได้ถึงรอบ N-1, ตั้งแต่รอบ N ขึ้นไป = ข้าม)
    ไม่ถูกต้อง/น้อยกว่า 1 คืน None"""
    try:
        n = int(str(txt or "").strip())
    except (TypeError, ValueError):
        return None
    return n if n >= 1 else None


def parse_if_time(txt):
    """แปลง Additional ของ If Time "HH:MM" → (HH, MM)
    ผ่าน HH:MM ของวันนี้แล้ว → ข้าม N แถวถัดไป (N = คอลัมน์ Repeat)
    ไม่ถูกต้องคืน None"""
    m = re.fullmatch(r"(\d{1,2}):(\d{2})", str(txt or "").strip())
    if not m:
        return None
    hh, mm = int(m.group(1)), int(m.group(2))
    if hh > 23 or mm > 59:
        return None
    return (hh, mm)


def parse_pixel_spec(additional):
    """แยก Additional ของ Wait for Pixel Color → (x, y, (r,g,b))
    รูปแบบ: "x,y #rrggbb" (ตัวเลือกหน่วงจะถูกอ่านแยกจากคอลัมน์ Secs)
    คืน (x, y, rgb) เมื่อถูกต้อง หรือ None"""
    s = str(additional or "").strip()
    if not s:
        return None
    parts = s.replace(",", " ").replace("#", " #").split()
    xy, rgb = None, None
    for p in parts:
        if p.startswith("#"):
            if rgb is None:
                rgb = parse_color_hex(p)
        else:
            if xy is None and p.isdigit():
                xy = (int(p), 0)
            elif xy is not None and xy[1] == 0 and p.isdigit():
                xy = (xy[0], int(p))
    if xy is None or rgb is None:
        return None
    return (xy[0], xy[1], rgb)


def pixel_color_at(x, y):
    """อ่านสีจุด (x, y) บนหน้าจอ → (r, g, b) หรือ None ถ้าอ่านไม่ได้
    ใช้ PIL.ImageGrab จับเฉพาะกรอบ 1×1 รอบจุด (เบากว่า grab ทั้งจอมาก)"""
    try:
        px = ImageGrab.grab(bbox=(int(x), int(y), int(x) + 1, int(y) + 1)).load()[0, 0]
        return (px[0], px[1], px[2])[:3]
    except Exception:
        return None


def color_close(c1, c2, tol=20):
    """สีใกล้เคียงกันภายใน tolerance ต่อช่อง (ค่าเริ่มต้น 20)"""
    if not c1 or not c2:
        return False
    return all(abs(a - b) <= tol for a, b in zip(c1, c2))


def parse_wait_timeout(additional, default=30):
    """แยก timeout จากท้าย Additional ของ Wait for Image / Wait for Pixel Color (v1.19)
    รูปแบบ: "... 60s" = รอสูงสุด 60 วิ (ค่าเริ่มต้น 30 วิถ้าไม่ใส่)
    คืน (additional ที่ตัด token ออกแล้ว, จำนวนวินาที 1-3600)"""
    s = str(additional or "")
    m = re.search(r"\s+(\d{1,6})s\s*$", s)
    if m:
        return s[:m.start()].strip(), max(1, min(3600, int(m.group(1))))
    return s.strip(), default


# ------------------------------------------- ตัวแปรในสคริปต์ (v1.19) ---------
# ชื่อตัวแปร: ขึ้นต้นด้วยตัวอักษร/_ (ไม่ใช่ตัวเลข) ตามด้วยตัวอักษร/เลข/_
# (รวมไทย) + สระบน-ล่าง/วรรณยุกต์ไทยที่ไม่อยู่ใน \w
_VAR_NAME = r"(?=[^\W\d])[\w\u0E31\u0E33-\u0E3A\u0E47-\u0E4E]+"


def parse_set_var(txt):
    """แยก Additional ของ Set Variable → (name, op, value)
    รูปแบบ: "name = ค่า" / "name += จำนวน" / "name -= จำนวน" — ชื่อตัวแปรเป็น
    ตัวอักษรไทย (รวมวรรณยุกต์/สระบน-ล่าง)/อังกฤษ/_ ได้ (ห้ามตัวเลขนำหน้า)
    รูปแบบไม่ถูกคืน None"""
    m = re.fullmatch(r"\s*(%s)\s*(\+=|-=|=)\s*(.*?)\s*" % _VAR_NAME,
                     str(txt or ""), re.UNICODE)
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3)


def substitute_vars(text, variables):
    """แทน {ชื่อตัวแปร} ในข้อความด้วยค่าจาก dict variables (v1.19)
    ตัวแปรที่ยังไม่มีค่าคง {ชื่อ} เดิมไว้ (มองเห็น แก้ตัวสะกดผิดได้ง่าย)"""
    def repl(m):
        name = m.group(1)
        return str(variables[name]) if name in variables else m.group(0)
    return re.sub(r"\{(%s)\}" % _VAR_NAME, repl, str(text or ""))


def subst_row(r, variables):
    """แทน {ตัวแปร} ในทุกคอลัมน์ที่ใช้ค่าได้ (v1.19) — คืน dict ใหม่ ไม่แก้ของเดิม"""
    return {**r,
            "x": substitute_vars(r.get("x", ""), variables),
            "y": substitute_vars(r.get("y", ""), variables),
            "additional": substitute_vars(r.get("additional", ""), variables),
            "mins": substitute_vars(r.get("mins", 0), variables),
            "secs": substitute_vars(r.get("secs", 1), variables),
            "repeat": substitute_vars(r.get("repeat", 1), variables)}


def apply_set_var(variables, additional):
    """ตั้งค่าตัวแปรลง dict ตาม Additional ของ Set Variable (v1.19) — ใช้ร่วม GUI/CLI
    คืน True ถ้ารูปแบบถูก, += / -= ต้องเป็นตัวเลข (ค่าเริ่มต้นของตัวแปรใหม่ = 0)"""
    sv = parse_set_var(additional)
    if not sv:
        return False
    name, op, raw = sv
    val = substitute_vars(raw, variables)
    if op == "=":
        variables[name] = val
        return True
    try:
        delta = float(val)
    except ValueError:
        return False
    try:
        base = float(variables.get(name, 0))
    except (TypeError, ValueError):
        base = 0.0
    variables[name] = fmt_num(base + delta if op == "+=" else base - delta)
    return True


# ---------------------------------------------- คลิปบอร์ดฝั่ง CLI (v1.20) ----
def _clip_win_set(text):
    """ตั้งคลิปบอร์ดบน Windows ด้วย Win32 API (ไม่ใช้ Tk/โปรแกรมอื่น) — คืน True ถ้าสำเร็จ"""
    import ctypes
    u32, k32 = ctypes.windll.user32, ctypes.windll.kernel32
    CF_UNICODETEXT, GMEM_MOVEABLE = 13, 2
    data = text.encode("utf-16-le") + b"\x00\x00"
    if not u32.OpenClipboard(None):
        return False
    try:
        u32.EmptyClipboard()
        k32.GlobalAlloc.restype = ctypes.c_void_p
        k32.GlobalAlloc.argtypes = (ctypes.c_uint, ctypes.c_size_t)
        h = k32.GlobalAlloc(GMEM_MOVEABLE, len(data))
        if not h:
            return False
        k32.GlobalLock.restype = ctypes.c_void_p
        k32.GlobalLock.argtypes = (ctypes.c_void_p,)
        ptr = k32.GlobalLock(h)
        if not ptr:
            return False
        try:
            ctypes.memmove(ptr, data, len(data))
        finally:
            k32.GlobalUnlock.argtypes = (ctypes.c_void_p,)
            k32.GlobalUnlock(h)
        u32.SetClipboardData.restype = ctypes.c_void_p
        u32.SetClipboardData.argtypes = (ctypes.c_uint, ctypes.c_void_p)
        return bool(u32.SetClipboardData(CF_UNICODETEXT, h))
    finally:
        u32.CloseClipboard()


def _clip_win_get():
    """อ่านคลิปบอร์ดบน Windows ด้วย Win32 API → str หรือ None"""
    import ctypes
    u32, k32 = ctypes.windll.user32, ctypes.windll.kernel32
    if not u32.OpenClipboard(None):
        return None
    try:
        u32.GetClipboardData.restype = ctypes.c_void_p
        u32.GetClipboardData.argtypes = (ctypes.c_uint,)
        h = u32.GetClipboardData(13)               # CF_UNICODETEXT
        if not h:
            return None
        k32.GlobalLock.restype = ctypes.c_void_p
        k32.GlobalLock.argtypes = (ctypes.c_void_p,)
        ptr = k32.GlobalLock(h)
        if not ptr:
            return None
        try:
            return ctypes.wstring_at(ptr)
        finally:
            k32.GlobalUnlock.argtypes = (ctypes.c_void_p,)
            k32.GlobalUnlock(h)
    finally:
        u32.CloseClipboard()


def clip_set(text):
    """ตั้งคลิปบอร์ดโดยไม่ใช้ Tk (v1.20, ใช้โดย CLI) — Windows: Win32 API,
    macOS: pbcopy, Linux: wl-copy/xclip/xsel — คืน True ถ้าสำเร็จ"""
    try:
        if os.name == "nt":
            return _clip_win_set(str(text))
        import subprocess
        for cmd in (["pbcopy"], ["wl-copy"], ["xclip", "-selection", "clipboard"],
                    ["xsel", "--clipboard", "--input"]):
            try:
                p = subprocess.run(cmd, input=str(text).encode("utf-8"), timeout=5)
                if p.returncode == 0:
                    return True
            except (OSError, subprocess.SubprocessError):
                continue
        return False
    except Exception:
        return False


def clip_get():
    """อ่านคลิปบอร์ดโดยไม่ใช้ Tk (v1.20, ใช้โดย CLI) → str หรือ None ถ้าอ่านไม่ได้"""
    try:
        if os.name == "nt":
            return _clip_win_get()
        import subprocess
        for cmd in (["pbpaste"], ["wl-paste", "--no-newline"],
                    ["xclip", "-selection", "clipboard", "-o"],
                    ["xsel", "--clipboard", "--output"]):
            try:
                p = subprocess.run(cmd, capture_output=True, timeout=5)
                if p.returncode == 0:
                    return p.stdout.decode("utf-8", "replace")
            except (OSError, subprocess.SubprocessError):
                continue
        return None
    except Exception:
        return None


# ------------------------------------ พิมพ์ข้อความไม่ขึ้นกับ layout (v1.20.2) --
# Type Text เดิมใช้ pynput KeyCode.from_char() = แปลงอักขระเป็น virtual key ตาม
# layout ที่ active (VkKeyScanW) — เครื่องที่ active เป็น layout ไทยแล้วพิมพ์อังกฤษ/
# สัญลักษณ์จะกลายเป็นอักขระอื่น ("D" → "ิ" ฯลฯ) — ใช้ SendInput KEYEVENTF_UNICODE
# ส่งรหัส Unicode ตรง ไม่ผ่าน layout (แนวเดียวกับ AutoHotkey)
_KEYEVENTF_UNICODE = 0x0004
_KEYEVENTF_KEYUP = 0x0002
_INPUT_KEYBOARD = 1


def _unicode_input_records(ch):
    """สร้างลำดับ event (scan_code, is_keyup) ของอักขระ ch สำหรับ SendInput
    (pure — ไม่ส่ง event จริง เพื่อทดสอบได้) — อักขระเกิน BMP แยกเป็น surrogate
    คู่: down ตามลำดับ แล้ว up ย้อนกลับ"""
    raw = ch.encode("utf-16-le")
    units = [raw[i] | (raw[i + 1] << 8) for i in range(0, len(raw), 2)]
    return ([(u, False) for u in units] + [(u, True) for u in reversed(units)])


def _send_unicode_events(records):
    """ส่ง event คีย์บอร์ดทั้งชุดด้วย SendInput ครั้งเดียว — คืน True ถ้าสำเร็จทั้งหมด"""
    import ctypes

    class _KEYBDINPUT(ctypes.Structure):
        _fields_ = [("wVk", ctypes.c_ushort), ("wScan", ctypes.c_ushort),
                    ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong),
                    ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

    class _MOUSEINPUT(ctypes.Structure):
        _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long),
                    ("mouseData", ctypes.c_ulong), ("dwFlags", ctypes.c_ulong),
                    ("time", ctypes.c_ulong),
                    ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

    class _HARDWAREINPUT(ctypes.Structure):
        _fields_ = [("uMsg", ctypes.c_ulong), ("wParamL", ctypes.c_ushort),
                    ("wParamH", ctypes.c_ushort)]

    class _INPUTunion(ctypes.Union):
        _fields_ = [("mi", _MOUSEINPUT), ("ki", _KEYBDINPUT),
                    ("hi", _HARDWAREINPUT)]     # mi ใหญ่สุด — ต้องอยู่ใน union

    class _INPUT(ctypes.Structure):
        _fields_ = [("type", ctypes.c_ulong), ("union", _INPUTunion)]

    u32 = ctypes.windll.user32
    arr = (_INPUT * len(records))()
    for i, (code, keyup) in enumerate(records):
        arr[i].type = _INPUT_KEYBOARD
        arr[i].union.ki.wVk = 0
        arr[i].union.ki.wScan = code
        arr[i].union.ki.dwFlags = (_KEYEVENTF_UNICODE
                                   | (_KEYEVENTF_KEYUP if keyup else 0))
    sent = u32.SendInput(len(records), arr, ctypes.sizeof(_INPUT))
    return sent == len(records)


def send_unicode_char(ch):
    """พิมพ์อักขระ 1 ตัวแบบไม่ขึ้นกับ keyboard layout (v1.20.2 — Windows เท่านั้น)
    คืน True ถ้าส่งสำเร็จ, False เพื่อให้ผู้เรียก fallback ไปทาง pynput (OS อื่น)"""
    if os.name != "nt":
        return False
    try:
        return _send_unicode_events(_unicode_input_records(ch))
    except Exception:
        return False


# ------------------------------------------------ plugin actions (v1.16) ----
def load_plugins(base_dir=None):
    """โหลด Custom Action plugins จาก <base_dir>/plugins/*.py (v1.16)
    แต่ละไฟล์ประกาศ:  ACTION_NAME = "ชื่อ Action"  และ  def run(ctx, row):
    ctx = dict(mouse, kb, log(message), cfg) — คืน list ของ (name, module)
    โหลดล้มเหลวไฟล์ไหนก็ข้ามไฟล์นั้น (พร้อมชื่อ) ไม่ทำโปรแกรมพัง"""
    if base_dir is None:
        if getattr(sys, "frozen", False):      # รันจาก .exe — ใช้โฟลเดอร์ของไฟล์ exe
            base_dir = os.path.dirname(os.path.abspath(sys.executable))
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
    d = os.path.join(base_dir, PLUGINS_DIR)
    if not os.path.isdir(d):
        return []
    import importlib.util
    out, failed = [], []
    for path in sorted(glob.glob(os.path.join(d, "*.py"))):
        name = os.path.basename(path)[:-3]
        if name.startswith("_"):
            continue                                   # _xxx.py = ไม่ใช่ plugin
        try:
            sp = importlib.util.spec_from_file_location("macro_plugin_%s" % name, path)
            mod = importlib.util.module_from_spec(sp)
            sp.loader.exec_module(mod)
            aname = str(getattr(mod, "ACTION_NAME", "")).strip()
            if not aname or not callable(getattr(mod, "run", None)):
                raise ValueError("ต้องมี ACTION_NAME และ run(ctx, row)")
            if aname in ACTIONS_ALL or any(a == aname for a, _ in out):
                raise ValueError("ชื่อ Action ซ้ำ: " + aname)
            out.append((aname, mod))
        except Exception as exc:
            failed.append("%s: %s" % (name, exc))
    load_plugins.last_failed = failed
    return out


load_plugins.last_failed = []
MOD_KEYS = ["", "Ctrl", "Alt", "Shift", "Win"]
EDIT_COLS = ["Action", "Additional", "Mins", "Secs", "Repeat"]
COLS = ["chk", "num", "x", "y", "button", "additional", "mins", "secs", "repeat"]


# ---------------------------------------------------------------- helpers ----
SPECIAL_KEYS = {
    "space": "space", "enter": "enter", "tab": "tab", "backspace": "backspace",
    "shift": "shift", "alt": "alt", "ctrl": "ctrl", "control": "ctrl", "win": "cmd",
    "esc": "esc", "escape": "esc", "del": "delete", "delete": "delete",
    "insert": "insert", "home": "home", "end": "end", "pgup": "page_up",
    "pgdn": "page_down", "page_up": "page_up", "page_down": "page_down",
    "up": "up", "down": "down", "left": "left", "right": "right",
    "caps": "caps_lock", "capslock": "caps_lock", "numlock": "num_lock",
    "prtsc": "print_screen", "print_screen": "print_screen",
    "menu": "menu", "cmd": "cmd",
}
SPECIAL_KEYS.update({("f%d" % i): ("f%d" % i) for i in range(1, 13)})


def parse_key(txt):
    """แปลงข้อความในคอลัมน์ Additional เป็นออบเจ็กต์คีย์ของ pynput
    ตัวอักษร A-Z / ตัวเลขเดี่ยว = ปุ่มกายภาพ (VK — ถูกต้องแม้ layout อื่น active, v1.20.4)
    ตัวอักษรอื่น (ไทย ฯลฯ) = อักขระตาม layout · ตัวเลขหลายหลัก = รหัส virtual key"""
    txt = (txt or "").strip()
    if not txt:
        return None
    if txt in MOD_KEYS[1:]:                       # Ctrl / Alt / Shift / Win
        return {"Win": Key.cmd}.get(txt, getattr(Key, txt.lower(), None))
    attr = txt.lower()
    if attr in SPECIAL_KEYS:
        return getattr(Key, SPECIAL_KEYS[attr], None)
    if len(txt) == 1:
        if ("a" <= txt.lower() <= "z") or txt.isdigit():
            return KeyCode.from_vk(ord(txt.upper()))   # ปุ่มกายภาพ เช่น W = VK_W
        return KeyCode.from_char(txt)
    if txt.isdigit():                             # รหัส virtual key เช่น 27
        return KeyCode.from_vk(int(txt))
    return None


def parse_key_combo(txt):
    """แยกคอมโบปุ่ม+คีย์ เช่น "Ctrl+W", "Ctrl+Shift+T", "Win+D" (v1.20.4)
    → (mods, key) โดย mods = รายการ modifier ตามลำดับที่พิมพ์
    ปุ่มหลักต้องระบุได้แน่นอน: ตัวอักษร/ตัวเลข (VK ปุ่มกายภาพ) หรือชื่อพิเศษ
    (enter/f1 ฯลฯ) หรือรหัส VK หลายหลัก — ห้ามเป็นอักขระแบบขึ้นกับ layout
    คืน None ถ้าไม่ใช่รูปแบบคอมโบ (ไม่มี +) หรือชื่อคีย์ไม่รู้จัก"""
    s = str(txt or "").strip()
    if "+" not in s:
        return None
    parts = [p.strip() for p in s.split("+") if p.strip()]
    if len(parts) < 2:
        return None
    mod_map = {"ctrl": Key.ctrl, "alt": Key.alt, "shift": Key.shift, "win": Key.cmd}
    mods = []
    for m in parts[:-1]:
        k = mod_map.get(m.lower())
        if k is None:
            return None
        mods.append(k)
    main = parts[-1]
    if len(main) == 1 and (("a" <= main.lower() <= "z") or main.isdigit()):
        key = KeyCode.from_vk(ord(main.upper()))     # ปุ่มกายภาพ เช่น W = VK_W
    else:
        key = parse_key(main)                        # ชื่อพิเศษ / รหัส VK หลายหลัก
    if key is None or (not isinstance(key, Key)
                       and getattr(key, "vk", None) is None):
        return None
    return mods, key


def delay_seconds(mins, secs):
    """คำนวณเวลาหน่วง (วินาที) จากคอลัมน์ Mins / Secs"""
    try:
        m = max(0.0, float(str(mins).replace(",", ".") or 0))
    except ValueError:
        m = 0.0
    try:
        s = max(0.0, float(str(secs).replace(",", ".") or 0))
    except ValueError:
        s = 0.0
    return m * 60 + s


def delay_range(secs):
    """แปลงช่วงสุ่มเช่น "1-3" → (1.0, 3.0) / ค่าเดี่ยว → (v, v) / พัง → (0, 0)
    ใช้กับคอลัมน์ Secs เพื่อกำหนดดีเลย์แบบสุ่ม (แรงบันดาลใจจาก automouseclick.com)"""
    t = str(secs or "").strip().replace(",", ".")
    m = re.fullmatch(r"(-?[\d.]+)\s*-\s*(-?[\d.]+)", t)
    if m:
        try:
            a, b = float(m.group(1)), float(m.group(2))
            return (min(a, b), max(a, b))
        except ValueError:
            return (0.0, 0.0)
    try:
        v = max(0.0, float(t or 0))
        return (v, v)
    except ValueError:
        return (0.0, 0.0)


def pick_play_order(rows, pct=100, shuffle=False, rng=None):
    """เลือกลำดับแถวที่จะเล่น (v1.10)
    - pct: เล่นแค่กี่เปอร์เซ็นต์ของแถว — สุ่มเลือกชุดแถวไม่ซ้ำ (100 = ทุกแถว)
    - shuffle: สลับลำดับแถวแบบสุ่ม
    คืนลิสต์แถวใหม่ (ไม่แก้ลิสต์เดิม) — เรียกซ้ำได้ทุกรอบเพื่อสุ่มชุด/ลำดับใหม่"""
    if not rows:
        return []
    r = rng if rng is not None else random
    out = list(rows)
    if pct < 100:
        k = max(1, int(round(len(out) * max(0, min(100, pct)) / 100.0)))
        out = r.sample(out, k)
    if shuffle:
        r.shuffle(out)
    return out


def wizard_filename(ts=None):
    """ชื่อไฟล์เริ่มต้นของ Record wizard เช่น wizard_20260928_103000.json"""
    t = ts or datetime.datetime.now()
    return "wizard_%s.json" % t.strftime("%Y%m%d_%H%M%S")


def fmt_num(v):
    try:
        f = float(str(v).replace(",", "."))
    except (ValueError, TypeError):
        return str(v)
    return str(int(f)) if f.is_integer() else ("%g" % f)


def parse_int(v, default=1):
    try:
        return max(1, int(float(str(v))))
    except (ValueError, TypeError):
        return default


def re_match_hhmm(txt):
    """เช็ครูปแบบเวลา HH:MM (00:00–23:59)"""
    return bool(re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", (txt or "").strip()))


# ------------------------------------------------------- log การเล่น (v1.8) --
def log_filename():
    """ชื่อไฟล์ log ของ "วันนี้" (หมุนรายวัน) เช่น macro_log_2026-09-28.txt"""
    return "macro_log_%s.txt" % datetime.date.today().isoformat()


def log_path():
    """พาธไฟล์ log ของวันนี้ (patch ฟังก์ชันนี้ใน unit tests เพื่อย้ายที่เก็บ)"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), log_filename())


def log_write(mode, message, src=None):
    """เขียนบรรทัด log 1 บรรทัด (ทนต่อทุก error — log ห้ามทำโปรแกรมพัง)
    mode: 'START' / 'STEP' / 'STOP' / 'END'"""
    try:
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        line = "%s [%s] %s" % (ts, mode, message)
        if src:
            line += "  <- " + str(src)
        with open(log_path(), "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except Exception:
        pass


def parse_log_stats(path):
    """สรุปสถิติจากไฟล์ log 1 ไฟล์ (1 วัน) — ไฟล์ไม่มี = ค่าศูนย์ทั้งหมด
    คืน dict: runs เริ่มเล่น, steps เหตุการณ์, stops หยุดโดยผู้ใช้,
    restarts รีสตาร์ต (watchdog), slowest = (บรรทัด, วินาที) แถวที่ใช้เวลานานสุด"""
    stats = {"runs": 0, "steps": 0, "stops": 0, "restarts": 0, "slowest": None,
             "actions": {}}
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if "[START]" in line:
                    stats["runs"] += 1
                elif "[STEP]" in line:
                    stats["steps"] += 1
                    m = re.search(r"\(([\d.]+) วิ\)", line)
                    if m:
                        t = float(m.group(1))
                        if stats["slowest"] is None or t > stats["slowest"][1]:
                            stats["slowest"] = (line.strip(), t)
                        # v1.18: สถิติราย Action — "รอบ N แถว i/total <Action> <additional> (T วิ)"
                        mm = re.match(r".*?แถว\s+\d+/\d+\s+(.+?)\s*\([^)]*\)\s*$", line.strip())
                        if mm:
                            label = mm.group(1).strip()
                            # additional อยู่ท้าย label ก่อนวงเล็บเวลา — ตัดเหลือเฉพาะชื่อ action
                            am = re.match(r"^(.*?)\s+[^\s]*$", label)
                            act = am.group(1).strip() if am and am.group(1).strip() else label
                            ent = stats["actions"].setdefault(act, {"count": 0, "total": 0.0, "max": 0.0})
                            ent["count"] += 1
                            ent["total"] += t
                            ent["max"] = max(ent["max"], t)
                elif "[STOP]" in line:
                    stats["stops"] += 1
                elif "[WATCHDOG]" in line:
                    stats["restarts"] += 1
    except OSError:
        pass
    return stats


def log_stats_summary(base_dir=None):
    """สรุปสถิติจาก log ทุกวันรวมกัน — ใช้หน้าต่าง 📊 Stats (v1.11)"""
    d = base_dir or os.path.dirname(os.path.abspath(__file__))
    files = sorted(glob.glob(os.path.join(d, "macro_log_*.txt")))
    total = {"files": len(files), "runs": 0, "steps": 0,
             "stops": 0, "restarts": 0, "slowest": None, "actions": {}}
    for f in files:
        s = parse_log_stats(f)
        for k in ("runs", "steps", "stops", "restarts"):
            total[k] += s[k]
        for act, ent in s["actions"].items():
            acc = total["actions"].setdefault(act, {"count": 0, "total": 0.0, "max": 0.0})
            acc["count"] += ent["count"]
            acc["total"] += ent["total"]
            acc["max"] = max(acc["max"], ent["max"])
        if s["slowest"] and (total["slowest"] is None
                             or s["slowest"][1] > total["slowest"][1]):
            total["slowest"] = s["slowest"]
    return total


def top_actions_summary(stats, limit=5):
    """สรุป Action ที่ใช้เวลารวมมากสุด (v1.18) — เรียงจากมากไปน้อย
    คืน list ของ (action, count, total_secs, max_secs)"""
    acts = stats.get("actions") or {}
    out = [(a, e["count"], e["total"], e["max"]) for a, e in acts.items()]
    out.sort(key=lambda x: -x[2])
    return out[:limit]


# ------------------------------------------------ backup อัตโนมัติ (v1.13) --
def backup_snapshot(base_dir, data, now=None, keep_days=BACKUP_KEEP_DAYS):
    """เขียน backup การตั้งค่า 1 snapshot ลง <base_dir>/backups/ แล้วตัดไฟล์เก่า
    เกิน keep_days วัน — คืนพาธไฟล์ที่เขียน (ทนต่อ error — backup ห้ามทำโปรแกรมพัง)"""
    try:
        bk = os.path.join(base_dir, BACKUP_DIR)
        os.makedirs(bk, exist_ok=True)
        t = now or datetime.datetime.now()
        path = os.path.join(bk, "backup_%s.json" % t.strftime("%Y-%m-%d_%H%M%S"))
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        prune_backups(bk, keep_days=keep_days)
        return path
    except Exception:
        return None


def prune_backups(base_dir, keep_days=BACKUP_KEEP_DAYS, today=None):
    """ลบ backup ที่เก่ากว่า keep_days วัน (แยกวันที่จากชื่อไฟล์ backup_YYYY-MM-DD_*)"""
    today = today or datetime.date.today()
    cutoff = today - datetime.timedelta(days=keep_days)
    for f in glob.glob(os.path.join(base_dir, "backup_*.json")):
        m = re.match(r"backup_(\d{4}-\d{2}-\d{2})_", os.path.basename(f))
        if not m:
            continue
        try:
            if datetime.date.fromisoformat(m.group(1)) < cutoff:
                os.remove(f)
        except (ValueError, OSError):
            pass


def log_daily_series(base_dir=None, limit=14):
    """สถิติรายวันสำหรับกราฟ (v1.12) — เรียงวันเก่า → ใหม่ เอา `limit` วันล่าสุด
    คืนรายการ dict: {"day": "2026-09-28", "runs": n, "steps": n, "restarts": n}"""
    d = base_dir or os.path.dirname(os.path.abspath(__file__))
    out = []
    for f in sorted(glob.glob(os.path.join(d, "macro_log_*.txt"))):
        name = os.path.basename(f)                    # macro_log_YYYY-MM-DD.txt
        day = name[len("macro_log_"):-len(".txt")]
        s = parse_log_stats(f)
        out.append({"day": day, "runs": s["runs"],
                    "steps": s["steps"], "restarts": s["restarts"]})
    return out[-limit:]


def log_monthly_series(base_dir=None, limit=12):
    """สรุปการใช้งานรวมรายเดือน (v1.15) — จาก log ทุกไฟล์ จับคู่เดือนจากชื่อไฟล์
    คืนรายการ dict: {"month": "2026-09", "runs": n, "steps": n} เรียงเดือนเก่า → ใหม่"""
    d = base_dir or os.path.dirname(os.path.abspath(__file__))
    agg = {}
    for f in glob.glob(os.path.join(d, "macro_log_*.txt")):
        name = os.path.basename(f)
        month = name[len("macro_log_"):len("macro_log_") + 7]      # YYYY-MM
        if not re.match(r"\d{4}-\d{2}$", month):
            continue
        s = parse_log_stats(f)
        a = agg.setdefault(month, {"month": month, "runs": 0, "steps": 0})
        a["runs"] += s["runs"]
        a["steps"] += s["steps"]
    return sorted(agg.values(), key=lambda x: x["month"])[-limit:]


def prune_log(keep=MAX_LOG_LINES):
    """เก็บ log ไว้ไม่เกิน `keep` บรรทัด (ตัดบรรทัดเก่าสุดออก) — เรียกตอนจบการเล่น"""
    try:
        path = log_path()
        if not os.path.isfile(path):
            return
        with open(path, encoding="utf-8") as fh:
            lines = fh.readlines()
        if len(lines) > keep:
            with open(path, "w", encoding="utf-8") as fh:
                fh.writelines(lines[-keep:])
    except Exception:
        pass


# === ENGINE-END



# ---------------------------------------------------------------- HotkeyEdit --
class HotkeyEdit(tk.Toplevel):
    """หน้าต่างแก้ค่าในเซลล์ (เปิดโดยดับเบิลคลิก)"""

    def __init__(self, master, label, current, choices, on_done, editable=False):
        super().__init__(master)
        self.title("แก้ค่า: " + label)
        self.on_done = on_done          # เก็บ callback ก่อนใช้ใน _ok (หายตั้งแต่ v1.4 → กดตกลงพัง)
        self.resizable(False, False)
        self.configure(bg="#f0f0f0")
        tk.Label(self, text=label + ":", bg="#f0f0f0").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.var = tk.StringVar(value=str(current))
        if choices:
            # v1.20.3: editable=True สำหรับช่อง Additional — พิมพ์ข้อความอิสระได้
            # (เดิม readonly มีแต่ชื่อคีย์ให้เลือก → Type Text กำหนด/แก้ข้อความไม่ได้เลย)
            w = ttk.Combobox(self, textvariable=self.var, values=choices, width=34,
                             state="normal" if editable else "readonly")
        else:
            w = ttk.Entry(self, textvariable=self.var, width=24)
        w.grid(row=0, column=1, padx=10, pady=10)
        w.focus_set()
        bf = tk.Frame(self, bg="#f0f0f0")
        bf.grid(row=1, column=0, columnspan=2, pady=(0, 12))
        tk.Button(bf, text="ตกลง", width=8, command=self._ok).pack(side="left", padx=4)
        tk.Button(bf, text="ยกเลิก", width=8, command=self.destroy).pack(side="left", padx=4)
        self.bind("<Return>", lambda e: self._ok())
        self.bind("<Escape>", lambda e: self.destroy())
        self.transient(master)
        self.grab_set()
        x = master.winfo_rootx() + master.winfo_width() // 2 - self.winfo_reqwidth() // 2
        y = master.winfo_rooty() + master.winfo_height() // 2 - self.winfo_reqheight() // 2
        self.geometry("+%d+%d" % (max(0, x), max(0, y)))

    def _ok(self):
        cb = self.on_done
        val = self.var.get()
        self.destroy()
        cb(val)


# ---------------------------------------------------------------- main app ---
class MacroApp:
    def __init__(self, root):
        self.root = root
        root.title(APP_TITLE)
        root.geometry("780x640")
        root.minsize(640, 520)

        self.mouse_ctl = MouseController()
        self.kb_ctl = KbController()

        self.running = False            # กำลังเล่นสคริปต์
        self.recording = False          # กำลังบันทึก
        self._rec_t0 = 0.0
        self._hl_row = None             # แถวที่กำลังเล่น (ไฮไลต์)
        self._section_stash = []        # v1.22: แถวที่ถูกย่อด้วยหัวข้อ Section [{after: iid, vals: [...]}]
        self._live_pos = (0, 0)         # พิกัดเมาส์สด (จาก listener thread)
        self._live_key = ""             # คีย์ล่าสุด (จาก listener thread)
        self._ui_state = {"row": None, "msg": None, "reset": False, "prog": None,
                          "beep": False}
        self._undo_stack = []              # v1.17: สำเนาตารางก่อนลบ/แทนที่ (Ctrl+Z)
        self._ifimg_skip = 0               # v1.17: ตัวนับข้ามแถวของ If Image
        self._last_if_found = False        # v1.18: ผล If Image ล่าสุด (ให้ Else If Image ใช้)
        self._loop_no = 1                  # v1.21: เลขรอบปัจจุบัน (ให้ If Loop ใช้)
        self._vars = {}                    # v1.19: ตัวแปรของการเล่น (รีเซ็ตทุกครั้งที่เริ่มเล่น)

        # โปรไฟล์ / schedule / global hotkey
        self._profiles = {}                # ชื่อโปรไฟล์ -> รายการแถว
        self._active_profile = DEFAULT_PROFILE
        self._sched_next = 0.0             # เวลาที่จะเล่นรอบถัดไป (โหมดทุก N นาที)
        self._sched_last = ""              # กันยิงซ้ำในนาทีเดียวกัน (โหมดรายวัน)
        self._gk = None                    # GlobalHotKeys instance
        self._img_area = ()                # กรอบค้นหาภาพ (left, top, right, bottom)
        self._saved_pos = None             # ตำแหน่งเมาส์ที่เซฟไว้ (Save/Restore Cursor)
        self._speed_mult = 1.0             # ตัวคูณความเร็ว (0.1–10)
        self._script_loops = 1             # จำนวนรอบของสคริปต์ทั้งชุด (0 = ไม่จำกัด)
        self._restore_pos = False          # คืนเมาส์กลับจุดเริ่มเมื่อจบรอบ
        self._log_enabled = True           # บันทึก log การเล่นลงไฟล์ (ตั้งใน Settings)
        self._log_src = None               # ชื่อสคริปต์ล่าสุด (แสดงใน log)
        self._loaded_file = None           # ไฟล์สคริปต์ที่ Load/Save ล่าสุด
        self._hp_dir = None                # โฟลเดอร์ hot-profile (F1–F4 โหลดสคริปต์จากที่นี้)
        self._backup_enabled = True        # backup อัตโนมัติตอนปิดโปรแกรม (v1.14)
        self._backup_days = BACKUP_KEEP_DAYS  # เก็บ backup ย้อนหลังกี่วัน
        self._lang = "th"                  # ภาษา UI: 'th' / 'en' (v1.14)
        self._plugins = []                 # Custom Action plugins (v1.16): [(name, module)]

        # การหยุดที่แม่นยำ (v1.7.1)
        self._play_gen = 0                 # รุ่นของการเล่น — เธรดเก่าหยุดเองเมื่อรุ่นเปลี่ยน
        self._pressed_keys = set()         # คีย์ที่กดค้าง (Press Key) เพื่อปล่อยตอน STOP
        self._pressed_btns = set()         # ปุ่มเมาส์ที่กดค้าง (* Down) เพื่อปล่อยตอน STOP

        self._build_style()
        self._t = lambda key: tr(self._lang, key)   # ตัวย่อดึงข้อความตามภาษา (v1.14)
        self._build_menu()  # สร้างก่อนโหลด conf — _apply_language จะปรับข้อความทีหลัง
        self._build_profile_bar()
        self._build_table()
        self._build_bottom()
        self._build_statusbar()
        self._start_listeners()
        self._install_hotkeys()
        self._start_global_hotkeys()
        self._start_poller()
        self._start_scheduler()
        self._load_profiles()
        self._refresh_profile_ui()
        self._plugins = load_plugins()     # โหลด Custom Actions (v1.16)
        if self._plugins:
            # ส่งผ่าน root.after — อย่าเขียน _ui_state ตอน __init__ (poller ใช้ pop("msg"))
            self.root.after(0, lambda: self._ui_state.__setitem__(
                "msg", ("โหลด plugins: " + ", ".join(n for n, _ in self._plugins), "#080")))
        self._load_conf()  # โหลดงานล่าสุดของโปรไฟล์ที่ใช้อยู่ (ถ้ามี)
        self._self_check()  # ตรวจสุขภาพระบบ (v1.11) — ผลแสดงใน Settings
        if not (self._checks.get("mouse") and self._checks.get("hotkey")):
            self._ui_state["msg"] = (self._t("selfcheck_warn"), "#a60")

        root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------ UI parts ---
    def _build_style(self):
        st = ttk.Style()
        for theme in ("vista", "clam"):
            try:
                st.theme_use(theme)
                break
            except tk.TclError:
                continue
        st.configure("Treeview", rowheight=24, font=("Segoe UI", 10))
        st.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    @classmethod
    def _menu_items(cls):
        """รายการเมนูไอคอน (icon, label, method_name, color) — แยกออกมาเพื่อทดสอบได้"""
        return [("💾", "Save", "save_script", "#333"),
                ("📂", "Load", "load_script", "#333"),
                ("📋", "Paste", "_paste_rows_clipboard", "#333"),
                ("🧙", "Wizard", "record_wizard", "#333"),
                ("📝", "Log", "view_log", "#333"),
                ("📊", "Stats", "view_stats", "#333"),
                ("⚡", "Hot-profile", "hot_profile_dialog", "#333"),
                ("⚙️", "Settings", "settings_dialog", "#333"),
                ("ℹ️", "About", "about", "#333"),
                ("❓", "Help", "help_dialog", "#333"),
                ("⏻", "Exit", "_on_close", "#b00")]

    def _build_menu(self):
        top = tk.Frame(self.root, bg="#fafafa")
        top.pack(fill="x")

        def btn(icon, label, cmd, color="#333"):
            f = tk.Frame(top, bg=top["bg"], cursor="hand2")
            f.pack(side="left", padx=8, pady=4)
            tk.Label(f, text=icon, font=("Segoe UI Emoji", 14), bg=top["bg"], fg=color).pack()
            tk.Label(f, text=label, font=("Segoe UI", 8), bg=top["bg"], fg=color).pack()
            for wgt in (f,) + tuple(f.winfo_children()):
                wgt.bind("<Button-1>", lambda e: cmd())

        for icon, label, name, color in self._menu_items():
            btn(icon, label, getattr(self, name), color)

    def _build_table(self):
        wrap = tk.Frame(self.root)
        wrap.pack(fill="both", expand=True, padx=6, pady=(2, 2))

        self.tree = ttk.Treeview(wrap, columns=COLS, show="headings", selectmode="browse")
        # คอลัมน์แรกเป็น checkbox จำลอง (☑ / ☐) คลิกเพื่อสลับ
        self.tree.heading("chk", text="☑")
        self.tree.column("chk", width=36, stretch=False, anchor="center")
        self.tree.heading("num", text="#")
        self.tree.column("num", width=40, stretch=False, anchor="center")
        for key, txt, wdt, anch in [("x", "X", 70, "center"), ("y", "Y", 70, "center"),
                                    ("button", self._t("col_action"), 150, "w"),
                                    ("additional", "Additional", 110, "w"),
                                    ("mins", "Mins", 50, "center"),
                                    ("secs", "Secs", 50, "center"),
                                    ("repeat", "Repeat", 60, "center")]:
            self.tree.heading(key, text=txt)
            self.tree.column(key, width=wdt, anchor=anch)

        ysb = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=ysb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        ysb.pack(side="right", fill="y")

        self.tree.bind("<Button-1>", self._on_click)
        self.tree.bind("<Double-1>", self._on_dbl_click)
        self.tree.bind("<Button-3>", self._on_right_click)
        self.tree.bind("<Delete>", self._on_del)
        self.tree.tag_configure("odd", background="#ffffff")
        self.tree.tag_configure("even", background="#f2f6fb")
        self.tree.tag_configure("run", background="#c8e6c9")
        self.tree.tag_configure("section", background="#cfe3f7", foreground="#1a3d6d")  # v1.21
        for _tname, _tstyle in ROW_STYLE.items():      # v1.22: สีแถวตามหมวด Action
            self.tree.tag_configure(_tname, **_tstyle)

        tools = tk.Frame(self.root)
        tools.pack(fill="x", padx=6)
        tk.Button(tools, text="＋ เพิ่มบรรทัด", command=self.add_row).pack(side="left", padx=2, pady=2)
        tk.Button(tools, text="－ ลบที่เลือก", command=self.del_selected).pack(side="left", padx=2)
        tk.Button(tools, text="▲ ขึ้น", width=6, command=lambda: self.move(-1)).pack(side="left", padx=2)
        tk.Button(tools, text="▼ ลง", width=6, command=lambda: self.move(1)).pack(side="left", padx=2)
        tk.Button(tools, text="ล้างทั้งหมด", command=self.clear_all).pack(side="left", padx=2)
        if HAS_CV:
            tk.Button(tools, text="📸 จับภาพ (ลากกรอบบนจอ)", command=self._capture_snip).pack(side="right", padx=2)
            tk.Button(tools, text="🎨 จับสี (คลิกบนจอ)", command=self._pick_pixel_color).pack(side="right", padx=2)
        tk.Button(tools, text="🕐 เวลานี้ (+15 นาที)", command=self._apply_current_time).pack(side="right", padx=2)  # v1.22

    # -------------------------------------------------- จับภาพหน้าจอ (snip) ---
    def _capture_snip(self):
        """ลากเมาส์วาดกรอบบนหน้าจอ (กดปล่อยแล้วจับภาพ) → เซฟเป็น .png ไว้ใช้กับ Image Click"""
        if not HAS_CV:
            messagebox.showinfo(APP_TITLE, "ต้องติดตั้ง: pip install opencv-python Pillow")
            return
        self.root.iconify()
        time.sleep(0.35)               # รอหน้าต่างหดจริง ไม่ให้ติดมาในภาพ
        sel = tk.Toplevel(self.root)
        sel.overrideredirect(True)
        sel.attributes("-topmost", True)
        sel.attributes("-alpha", 0.25)
        sel.configure(bg="black")
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        sel.geometry("%dx%d+0+0" % (sw, sh))
        start = {"x": 0, "y": 0}

        def on_press(e):
            start["x"], start["y"] = e.x_root, e.y_root

        def on_drag(e):
            x0, y0 = start["x"], start["y"]
            sel.geometry("%dx%d+%d+%d" % (abs(e.x_root - x0), abs(e.y_root - y0),
                                          min(x0, e.x_root), min(y0, e.y_root)))

        def on_release(e):
            x0, y0 = start["x"], start["y"]
            x1, y1 = e.x_root, e.y_root
            sel.destroy()
            box = (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
            self.root.deiconify()
            if box[2] - box[0] < 5 or box[3] - box[1] < 5:
                return                      # ลากสั้นเกินไป = ยกเลิก
            try:
                name = simpledialog.askstring("บันทึกภาพ", "ชื่อไฟล์ (.png):",
                                              initialvalue="snip.png", parent=self.root)
                if not name:
                    return
                if not name.lower().endswith(".png"):
                    name += ".png"
                base = os.path.dirname(os.path.abspath(__file__))
                ImageGrab.grab(bbox=box, all_screens=True).save(os.path.join(base, name))
                self._ui_state["msg"] = ("จับภาพแล้ว: %s (%dx%d) — พิมพ์ชื่อไฟล์นี้ในช่อง Additional ของแถว Image Click" % (name, box[2] - box[0], box[3] - box[1]), "#080")
            except Exception as exc:
                messagebox.showerror(APP_TITLE, "จับภาพไม่สำเร็จ: %s" % exc)

        sel.bind("<ButtonPress-1>", on_press)
        sel.bind("<B1-Motion>", on_drag)
        sel.bind("<ButtonRelease-1>", on_release)

    def _pick_pixel_color(self):
        """🎨 คลิกจุดบนจอเพื่อจับสี → ใส่แถว Wait for Pixel Color (v1.19)"""
        if not HAS_CV:
            messagebox.showinfo(APP_TITLE, "ต้องติดตั้ง: pip install opencv-python Pillow")
            return
        self.root.iconify()
        time.sleep(0.35)               # รอหน้าต่างหดจริง ไม่ให้ติดมาในภาพ
        sel = tk.Toplevel(self.root)
        sel.overrideredirect(True)
        sel.attributes("-topmost", True)
        sel.attributes("-alpha", 0.35)
        sel.configure(bg="black")
        sel.geometry("%dx%d+0+0" % (self.root.winfo_screenwidth(),
                                    self.root.winfo_screenheight()))
        tk.Label(sel, text="คลิกจุดที่ต้องการจับสี  (Esc = ยกเลิก)",
                 fg="white", bg="black", font=("Segoe UI", 14)).pack(pady=30)

        def on_click(e):
            x, y = e.x_root, e.y_root
            sel.destroy()
            self.root.deiconify()
            self.root.update()
            time.sleep(0.2)            # รอหน้าจอจริงกลับมา ไม่ให้สีติดม่านทับ
            rgb = pixel_color_at(x, y)
            if not rgb:
                messagebox.showerror(APP_TITLE, "อ่านสีจุด (%d, %d) ไม่สำเร็จ" % (x, y))
                return
            self._apply_pixel_spec("%d,%d #%02x%02x%02x" % (x, y, rgb[0], rgb[1], rgb[2]))

        sel.bind("<Button-1>", on_click)
        sel.bind("<Escape>", lambda e: (sel.destroy(), self.root.deiconify()))
        sel.focus_force()

    def _apply_pixel_spec(self, spec):
        """ใส่ spec 'x,y #rrggbb' ลงแถว Wait for Pixel Color ที่เลือกไว้ (v1.19)
        ถ้าแถวที่เลือกไม่ใช่ Wait for Pixel Color สร้างแถวใหม่ต่อท้าย — คืน True ถ้าแก้แถวเดิม"""
        sel = self.tree.selection()
        if sel:
            vals = list(self.tree.item(sel[0], "values"))
            if str(vals[4]) == WAIT_PIXEL:
                vals[5] = spec
                self.tree.item(sel[0], values=vals)
                self._ui_state["msg"] = ("จับสีแล้ว: " + spec, "#080")
                return True
        self._append_row(button=WAIT_PIXEL, additional=spec, secs=1)
        self._ui_state["msg"] = ("เพิ่มแถวรอสี: " + spec + " — แก้จุด/สีได้ที่ช่อง Additional", "#080")
        return False

    def _apply_current_time(self):
        """🕐 ปุ่มจับเวลา (v1.22): เติม HH:MM (เวลาปัจจุบัน +15 นาที) ให้แถว If Time ที่เลือก
        ถ้าแถวที่เลือกไม่ใช่ If Time สร้างแถวใหม่ต่อท้าย — คืน True ถ้าแก้แถวเดิม"""
        lt = time.localtime()
        total = lt.tm_hour * 60 + lt.tm_min + 15      # เวลาปัจจุบัน +15 นาที (คำนวณจาก localtime ตรง ๆ)
        spec = "%02d:%02d" % ((total // 60) % 24, total % 60)
        sel = self.tree.selection()
        if sel:
            vals = list(self.tree.item(sel[0], "values"))
            if str(vals[4]) == IF_TIME:
                vals[5] = spec
                self.tree.item(sel[0], values=vals)
                self._ui_state["msg"] = ("ใส่เวลาแล้ว: " + spec + " (จากเวลานี้ +15 นาที)", "#080")
                return True
        self._append_row(button=IF_TIME, additional=spec)
        self._ui_state["msg"] = ("เพิ่มแถว If Time: " + spec + " — แก้เวลาได้ที่ช่อง Additional", "#080")
        return False

    def _build_bottom(self):
        bot = tk.Frame(self.root)
        bot.pack(fill="x", padx=8, pady=6)

        self.btn_start = tk.Button(bot, text="START", width=11, bg="#e8e8e8",
                                   font=("Segoe UI", 10, "bold"), command=self.start_play)
        self.btn_start.pack(side="left", padx=4)
        self.btn_stop = tk.Button(bot, text="STOP", width=11, bg="#e8e8e8",
                                  font=("Segoe UI", 10, "bold"), command=self.stop_all)
        self.btn_stop.pack(side="left", padx=4)
        self.btn_repeat = tk.Button(bot, text="REPEAT", width=13, bg="#3fa63f", fg="white",
                                    font=("Segoe UI", 10, "bold"), command=self.start_repeat)
        self.btn_repeat.pack(side="left", padx=4)
        self.btn_rec = tk.Button(bot, text="RECORD", width=11, bg="#e8e8e8", fg="#b00",
                                 font=("Segoe UI", 10, "bold"), command=self.toggle_record)
        self.btn_rec.pack(side="left", padx=4)

        self.chk_forever = tk.BooleanVar(value=False)
        self.chk_forever_btn = tk.Checkbutton(bot, text=self._t("forever"),
                                              variable=self.chk_forever)
        self.chk_forever_btn.pack(side="left", padx=6)
        self.chk_restore = tk.BooleanVar(value=False)
        self.chk_restore_btn = tk.Checkbutton(bot, text=self._t("restore"),
                                              variable=self.chk_restore)
        self.chk_restore_btn.pack(side="left", padx=6)
        self.chk_shuffle = tk.BooleanVar(value=False)
        self.chk_shuffle_btn = tk.Checkbutton(bot, text=self._t("shuffle"),
                                              variable=self.chk_shuffle)
        self.chk_shuffle_btn.pack(side="left", padx=6)
        self.lbl_pct = tk.Label(bot, text=self._t("pct"))
        self.lbl_pct.pack(side="left", padx=(10, 2))
        self.ent_pct = tk.Spinbox(bot, from_=5, to=100, increment=5, width=5)
        self.ent_pct.delete(0, "end")
        self.ent_pct.insert(0, "100")
        self.ent_pct.pack(side="left")
        tk.Label(bot, text="%", fg="#888").pack(side="left", padx=(2, 0))

        self.lbl_speed = tk.Label(bot, text=self._t("speed"))
        self.lbl_speed.pack(side="left", padx=(10, 2))
        self.cmb_speed = ttk.Combobox(bot, width=5, state="readonly",
                                      values=["0.25", "0.5", "1", "2", "4"])
        self.cmb_speed.set("1")
        self.cmb_speed.pack(side="left")

        self.lbl_loops = tk.Label(bot, text=self._t("loops"))
        self.lbl_loops.pack(side="left", padx=(10, 2))
        self.ent_loops = tk.Spinbox(bot, from_=0, to=99999, width=6)
        self.ent_loops.delete(0, "end")
        self.ent_loops.insert(0, "1")
        self.ent_loops.pack(side="left")
        self.lbl_loops_note = tk.Label(bot, text=self._t("loops_note"), fg="#888")
        self.lbl_loops_note.pack(side="left", padx=(2, 0))

    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg="#e6e6e6")
        bar.pack(fill="x", side="bottom")
        self.progress = ttk.Progressbar(bar, mode="determinate", length=160)
        self.progress.pack(side="left", padx=(8, 4), pady=3)
        self.lbl_prog = tk.Label(bar, text="", font=("Consolas", 9), bg="#e6e6e6", width=18, anchor="w")
        self.lbl_prog.pack(side="left", padx=(0, 6))
        self.lbl_pos = tk.Label(bar, text="0    0", font=("Consolas", 10),
                                bg="#e6e6e6", width=14, anchor="w")
        self.lbl_pos.pack(side="left", padx=8, pady=2)
        self.lbl_key = tk.Label(bar, text="", font=("Consolas", 10), bg="#e6e6e6", anchor="w")
        self.lbl_key.pack(side="left", padx=6)
        self.lbl_state = tk.Label(bar, text="พร้อม", bg="#e6e6e6", fg="#333")
        self.lbl_state.pack(side="right", padx=8)

    # ------------------------------------------------------------- hotkeys ---
    def _install_hotkeys(self):
        self.root.bind("<F6>", lambda e: self.start_play())
        self.root.bind("<F8>", lambda e: self.stop_all())
        self.root.bind("<F9>", lambda e: self.toggle_record())
        self.root.bind("<F10>", lambda e: self.chk_forever.set(not self.chk_forever.get()))
        # v1.17: Ctrl+F ค้นหาแถว, Ctrl+Z กู้คืนแถวที่ลบ/ถูกแทนที่
        self.root.bind("<Control-f>", self._find_dialog)
        self.root.bind("<Control-z>", self._undo_delete)

    # --------------------------------------------- global hotkeys (ทุกที่) ---
    def _start_global_hotkeys(self):
        """F6/F8/F9/F10 ทำงานได้แม้หน้าต่างโปรแกรมไม่ได้โฟกัส
        และออโต้ปิดตัวเองถ้าโปรแกรมอื่นใช้คีย์ชุดนี้อยู่แล้ว

        v1.8: ใช้ keyboard.Listener จับคู่คีย์เอง — พบว่า GlobalHotKeys ของ
        pynput 1.8.x บนบางเครื่องไม่ยิง callback แม้กดคีย์จริง (ทดสอบพบตอน
        ตรวจสอบปุ่ม STOP) ส่วน Listener ธรรมดารับเหตุการณ์ได้ปกติ"""
        hotmap = {keyboard.Key.f6: self.start_play,
                  keyboard.Key.f8: self.stop_all,
                  keyboard.Key.f9: self.toggle_record,
                  keyboard.Key.f10: self._toggle_forever,
                  # Hot-profile (v1.9): F1–F4 โหลดสคริปต์ลำดับที่ 1–4 จากโฟลเดอร์ที่เลือกแล้วเล่นทันที
                  keyboard.Key.f1: lambda: self._hot_profile_load(1),
                  keyboard.Key.f2: lambda: self._hot_profile_load(2),
                  keyboard.Key.f3: lambda: self._hot_profile_load(3),
                  keyboard.Key.f4: lambda: self._hot_profile_load(4)}

        def on_press(key):
            fn = hotmap.get(key)
            if fn is not None:
                self.root.after(0, fn)     # ผลักเข้า main thread เสมอ (thread-safe)

        try:
            self._gk = keyboard.Listener(on_press=on_press)
            self._gk.daemon = True
            self._gk.start()
        except Exception as exc:
            self._gk = None
            self._ui_state["msg"] = ("เปิด global hotkey ไม่ได้ (%s) — ใช้คีย์เมื่อโฟกัสหน้าต่าง" % exc, "#a60")

    def _toggle_forever(self):
        self.chk_forever.set(not self.chk_forever.get())

    # ----------------------------------------------- live mouse/key watchers --
    def _start_listeners(self):
        def on_move(x, y):
            self._live_pos = (x, y)

        def on_click(x, y, button, pressed):
            if self.recording and pressed:
                name = {"Button.left": "Left", "Button.right": "Right",
                        "Button.middle": "Middle"}.get(str(button))
                if name:
                    dt = round(time.time() - self._rec_t0, 2)
                    self._pending_rows.append(dict(x=int(x), y=int(y), button=name + " Click",
                                                   additional="", mins=0, secs=dt, repeat=1))

        def on_scroll(x, y, dx, dy):
            if self.recording and dy:
                dt = round(time.time() - self._rec_t0, 2)
                self._pending_rows.append(dict(x=int(x), y=int(y),
                                               button="Scroll Up" if dy > 0 else "Scroll Down",
                                               additional=str(abs(dy)), mins=0, secs=dt, repeat=1))

        def on_kb(key):
            try:
                txt = key.char or ""
            except AttributeError:
                txt = str(key).replace("Key.", "")
            if txt:
                self._live_key = txt
            if self.recording and txt and len(txt) <= 12 and not txt.startswith(" "):
                dt = round(time.time() - self._rec_t0, 2)
                self._pending_rows.append(dict(x="", y="", button="Tap Key",
                                               additional=txt, mins=0, secs=dt, repeat=1))

        self._pending_rows = []
        self._ms_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
        self._ms_listener.daemon = True
        self._ms_listener.start()

        self._kb_listener = keyboard.Listener(on_press=on_kb)
        self._kb_listener.daemon = True
        self._kb_listener.start()

    def _start_poller(self):
        """ลูปฝั่ง UI: ดึงสถานะจาก listener/player threads มาแสดง (thread-safe)"""
        st = self._ui_state

        # เพิ่มแถวใหม่จากโหมดบันทึก (ผลักจาก listener ผ่าน _pending_rows)
        if self.recording and self._pending_rows:
            for r in self._pending_rows:
                self._append_row(**r)
            self._pending_rows = []

        # ไฮไลต์แถวที่กำลังเล่น
        row = st["row"]
        if row != self._hl_row:
            if self._hl_row is not None and self.tree.exists(self._hl_row):
                self._untag(self._hl_row)
            if row is not None and self.tree.exists(row):
                self.tree.item(row, tags=("run",))
                self.tree.see(row)
            self._hl_row = row

        # ข้อความสถานะ (อ่านด้วย get — อย่า pop คีย์ทิ้ง ไม่งั้น tick ถัดไปชน KeyError)
        msg = st.get("msg")
        if msg:
            text, color = msg
            st["msg"] = None
            self.lbl_state.config(text=text, fg=color)

        # รีเซ็ตปุ่มเมื่อเล่นจบ
        if st.pop("reset", False):
            self._reset_ui()

        # Beep จาก player thread — main thread เป็นคนเรียก bell (thread-safe, v1.19)
        if st.pop("beep", False):
            try:
                self.root.bell()
            except tk.TclError:
                pass

        # คลิปบอร์ด (v1.20) — ตั้ง/อ่านบน main thread เท่านั้น
        clip_text = st.pop("clipboard", None)
        if clip_text:
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(clip_text)
            except tk.TclError:
                pass
        clip_var = st.pop("read_clipboard", None)
        if clip_var:
            try:
                self._vars[clip_var] = self.root.clipboard_get()
            except tk.TclError:
                self._vars[clip_var] = ""

        # ตำแหน่งเมาส์ / คีย์ล่าสุด
        x, y = self._live_pos
        self.lbl_pos.config(text="%d    %d" % (x, y))
        if self._live_key:
            self.lbl_key.config(text="KEY: " + self._live_key)

        # แถบความคืบหน้า (progress + ตัวนับรอบ)
        prog = st.get("prog")
        if prog:
            done, total, loop_no = prog
            pct = int(done * 100 / total) if total else 0
            self.progress.config(value=pct)
            self.lbl_prog.config(text="รอบ %d • %d/%d (%d%%)" % (loop_no, done, total, pct))
        else:
            self.progress.config(value=0)
            self.lbl_prog.config(text="")

        self.root.after(120, self._poller_tick)

    def _poller_tick(self):
        try:
            self._start_poller()
        except tk.TclError:
            pass  # หน้าต่างถูกปิดแล้ว

    # ------------------------------------------------------------ recording --
    def toggle_record(self):
        if self.recording:
            self._stop_record()
        else:
            self._start_record()

    def _start_record(self):
        self.recording = True
        self._rec_t0 = time.time()
        self._pending_rows = []
        self.btn_rec.config(bg="#c00", fg="white", text="● REC")
        self.root.title(APP_TITLE + "   [ RECORDING ]")
        self._ui_state["msg"] = ("กำลังบันทึก…  (F9 หยุด)", "#c00")

    def _stop_record(self):
        self.recording = False
        self.btn_rec.config(bg="#e8e8e8", fg="#b00", text="RECORD")
        self.root.title(APP_TITLE)
        self.refresh_nums()
        self._ui_state["msg"] = ("บันทึกเสร็จ — ได้ %d เหตุการณ์" % len(self.tree.get_children()), "#080")

    # --------------------------------------------------------------- table ---
    def _append_row(self, **kw):
        vals = ["☑", len(self.tree.get_children()) + 1,
                kw.get("x", ""), kw.get("y", ""), kw.get("button", ""),
                kw.get("additional", ""), fmt_num(kw.get("mins", 0)),
                fmt_num(0 if kw.get("button") == SECTION_HEADER else kw.get("secs", 1)),
                fmt_num(kw.get("repeat", 1))]
        n = len(self.tree.get_children())
        self.tree.insert("", "end", values=vals, tags=row_tags(str(vals[4]), n))   # v1.22: สีหมวด
        self.tree.see(self.tree.get_children()[-1])

    def add_row(self):
        self._append_row(button="Left Click", secs=1)

    def refresh_nums(self):
        """รีเลขลำดับคอลัมน์ # — ข้ามแถว Section (v1.21) และตั้ง/ล้างสไตล์หัวข้อ"""
        n = 0
        for iid in self.tree.get_children():
            vals = list(self.tree.item(iid, "values"))
            if str(vals[4]) == SECTION_HEADER:
                self.tree.item(iid, tags=("section",))
                continue
            n += 1
            vals[1] = n
            self.tree.item(iid, values=vals, tags=row_tags(str(vals[4]), n))   # v1.22: สีหมวด

    def _on_click(self, event):
        if self.tree.identify("region", event.x, event.y) != "cell":
            return
        col = self.tree.identify_column(event.x)
        row_id = self.tree.identify_row(event.y)
        if row_id and col == "#1":                     # สลับ checkbox
            vals = list(self.tree.item(row_id, "values"))
            vals[0] = "☐" if vals[0] == "☑" else "☑"
            self.tree.item(row_id, values=vals)
            return "break"

    def _on_del(self, _evt=None):
        if self.tree.selection():
            self._push_undo()              # เก็บสำเนาก่อนลบ — Ctrl+Z กู้คืนได้
        for iid in self.tree.selection():
            self._on_del_cleanup(iid)
            self.tree.delete(iid)
        self.refresh_nums()

    def _on_del_cleanup(self, iid):
        """v1.22: ก่อนลบแถว — หัวข้อที่ย่ออยู่ให้ขยายคืนก่อน (ไม่งั้นแถวกลุ่มหาย)"""
        try:
            vals = self.tree.item(iid, "values")
        except tk.TclError:
            return
        if str(vals[4]) == SECTION_HEADER and self._group_collapsed(iid):
            self._group_toggle(iid)        # ขยายคืนก่อน แล้วลบเฉพาะหัวข้อต่อไป

    # ------------------------------------- v1.17: undo / find / clipboard ----
    def _snapshot_rows(self):
        """คัดลอกค่าทั้งตารางเป็น list ของ values (สำหรับ undo)"""
        return [list(self.tree.item(i, "values")) for i in self.tree.get_children()]

    def _push_undo(self):
        self._undo_stack.append(self._snapshot_rows())
        if len(self._undo_stack) > 50:
            self._undo_stack.pop(0)

    def _undo_delete(self, _evt=None):
        """Ctrl+Z: กู้คืนตารางชุดล่าสุดก่อนถูกลบ/แทนที่"""
        if not self._undo_stack:
            self._ui_state["msg"] = (self._t("nothing_undo"), "#a60")
            return
        rows = self._undo_stack.pop()
        self.tree.delete(*self.tree.get_children())
        for vals in rows:
            self.tree.insert("", "end", values=vals)
        self._undo_restore_collapsed()                 # v1.22: คืนแถวที่ถูกย่อไว้ (iid เปลี่ยนหมด)
        self.refresh_nums()
        self._hl_row = None
        self._ui_state["msg"] = (self._t("undone"), "#080")

    def _undo_restore_collapsed(self):
        """v1.22: หลัง restore จาก undo — หัวข้อที่ย่อค้างไว้ถูกขยายคืนจาก stash
        (iid เดิมหายหลัง restore ผูก stash ไม่ได้ ขยายคืนคือทางไม่มีข้อมูลหาย)"""
        if not self._section_stash:
            return
        queue = list(self._section_stash)
        self._section_stash = []
        for iid in self.tree.get_children():
            vals = self.tree.item(iid, "values")
            m = _COLLAPSED_RE.search(str(vals[5]).strip())
            if not (m and str(vals[4]) == SECTION_HEADER):
                continue
            pos = self.tree.index(iid) + 1
            for _ in range(int(m.group(1))):
                if not queue:
                    break
                self.tree.insert("", pos, values=list(queue.pop(0)["vals"]))
                pos += 1
            m2 = re.match(r"^(.*?)\s*\(ย่อ \d+ แถว\)$", str(vals[5]).strip())
            nv = list(vals)
            nv[5] = m2.group(1) if m2 else vals[5]
            self.tree.item(iid, values=nv)

    def _find_rows(self, query):
        """คืนเลขแถว (1-based) ที่มีข้อความ query อยู่ในคอลัมน์ใดก็ได้ (ไม่แยกพิมพ์เล็ก-ใหญ่)"""
        q = str(query or "").strip().lower()
        if not q:
            return []
        out = []
        for i, iid in enumerate(self.tree.get_children(), 1):
            vals = [str(v).lower() for v in self.tree.item(iid, "values")]
            if any(q in v for v in vals):
                out.append(i)
        return out

    def _goto_row(self, num):
        """เด้งไปแถวลำดับที่ num (1-based) + ไฮไลต์ selection — คืน True ถ้ามีแถวนั้น"""
        kids = self.tree.get_children()
        if not (1 <= num <= len(kids)):
            return False
        iid = kids[num - 1]
        self.tree.selection_set(iid)
        self.tree.focus(iid)
        self.tree.see(iid)
        return True

    def _find_dialog(self, _evt=None):
        """หน้าต่างค้นหาแถว (Ctrl+F) — Enter = หาถัดไป, Esc = ปิด"""
        top = tk.Toplevel(self.root)
        top.title(self._t("find_title"))
        top.transient(self.root)
        top.resizable(False, False)
        frm = tk.Frame(top, padx=10, pady=8)
        frm.pack()
        tk.Label(frm, text=self._t("find_label")).pack(anchor="w")
        ent = tk.Entry(frm, width=34)
        ent.pack(fill="x", pady=4)
        ent.focus_set()
        lbl = tk.Label(frm, text="", fg="#64748b")
        lbl.pack(anchor="w")
        state = {"idx": 0, "hits": []}

        def do_find(_e=None):
            q = ent.get()
            if not q.strip():
                return "break"
            hits = self._find_rows(q)
            if not hits:
                state["hits"] = []
                lbl.config(text=self._t("notfound") % q, fg="#c00")
                self._ui_state["msg"] = (self._t("notfound") % q, "#a60")
                return "break"
            if state["hits"] != hits:
                state["hits"] = hits
                state["idx"] = 0
            else:
                state["idx"] = (state["idx"] + 1) % len(hits)   # Enter ซ้ำ = ผลถัดไป
            num = hits[state["idx"]]
            self._goto_row(num)
            lbl.config(text=self._t("found") % num, fg="#080")
            self._ui_state["msg"] = (self._t("found") % num, "#080")
            return "break"

        def close(_e=None):
            top.destroy()
            return "break"

        ent.bind("<Return>", do_find)
        top.bind("<Return>", do_find)
        top.bind("<Escape>", close)
        bar = tk.Frame(frm)
        bar.pack(fill="x", pady=(6, 0))
        tk.Button(bar, text=self._t("find_btn"), command=do_find).pack(side="left")
        tk.Button(bar, text=self._t("close"), command=top.destroy).pack(side="left", padx=6)
        return top

    def _paste_rows_clipboard(self):
        """เมนู 📋 Paste: วางสคริปต์ JSON จากคลิปบอร์ดเป็นแถว (ผนวกต่อท้ายตาราง)
        รับทั้งรายการแถวล้วน และ {"kind": ..., "rows": [...]} จาก Export"""
        try:
            txt = self.root.clipboard_get()
        except tk.TclError:
            self._ui_state["msg"] = (self._t("clip_empty"), "#a60")
            return
        try:
            data = json.loads(txt)
        except ValueError:
            self._ui_state["msg"] = (self._t("clip_bad"), "#c00")
            return
        if isinstance(data, dict) and isinstance(data.get("rows"), list):
            data = data["rows"]
        if not isinstance(data, list) or not data:
            self._ui_state["msg"] = (self._t("clip_bad"), "#c00")
            return
        self._push_undo()              # วางผิดกด Ctrl+Z คืนได้
        added = 0
        for r in data:
            if not isinstance(r, dict):
                continue
            self._append_row(x=r.get("x", ""), y=r.get("y", ""), button=r.get("button", ""),
                             additional=r.get("additional", ""), mins=r.get("mins", 0),
                             secs=r.get("secs", 1), repeat=r.get("repeat", 1))
            iid = self.tree.get_children()[-1]
            vals = list(self.tree.item(iid, "values"))
            vals[0] = "☑" if r.get("enabled", True) else "☐"
            self.tree.item(iid, values=vals)
            added += 1
        self.refresh_nums()
        self._ui_state["msg"] = (self._t("clip_added") % added, "#080")

    # --------------------------------------------- context menu (คลิกขวา) ----
    def _on_right_click(self, event):
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        self.tree.selection_set(iid)
        self.tree.focus(iid)
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label=self._t("ctx_copy"), command=lambda: self._row_duplicate(iid))
        menu.add_command(label=self._t("ctx_above"), command=lambda: self._row_insert_above(iid))
        menu.add_command(label=self._t("ctx_below"), command=lambda: self._row_insert_below(iid))
        menu.add_command(label=self._t("section_new"), command=lambda: self._add_section(iid))
        menu.add_separator()
        if str(self.tree.item(iid, "values")[4]) == SECTION_HEADER:      # v1.22: ย่อ/ขยายกลุ่ม
            collapsed = self._group_collapsed(iid)
            menu.add_command(label=self._t("group_expand" if collapsed else "group_collapse"),
                             command=lambda: self._group_toggle(iid))
        elif self._near_collapsed_marker(iid):
            menu.add_command(label=self._t("group_show_hint"), state="disabled")
            menu.add_command(label=self._t("group_expand_first"),
                             command=lambda: self._group_toggle(self._marker_head(iid)))
        else:
            menu.add_command(label=self._t("ctx_section"), command=lambda: self._row_toggle_section(iid))
        menu.add_command(label=self._t("ctx_del"), command=self._on_del)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _copy_row(self, src):
        vals = list(self.tree.item(src, "values"))
        vals[1] = "#"  # เลขลำดับจะถูก refresh ทีหลัง
        return vals

    def _row_duplicate(self, src):
        vals = self._copy_row(src)
        idx = self.tree.index(src)
        new_iid = self.tree.insert("", idx + 1, values=vals)
        self.tree.selection_set(new_iid)
        self.refresh_nums()

    def _row_insert_above(self, src):
        vals = ["☑", "#", "", "", "Left Click", "", 0, 1, 1]
        idx = self.tree.index(src)
        new_iid = self.tree.insert("", idx, values=vals)
        self.tree.selection_set(new_iid)
        self.refresh_nums()

    def _row_insert_below(self, src):
        vals = ["☑", "#", "", "", "Left Click", "", 0, 1, 1]
        idx = self.tree.index(src)
        new_iid = self.tree.insert("", idx + 1, values=vals)
        self.tree.selection_set(new_iid)
        self.refresh_nums()

    def _row_toggle_section(self, iid):
        """v1.21: สลับแถวเป็นหัวข้อ Section (หรือกลับเป็นแถวธรรมดา Left Click)"""
        vals = list(self.tree.item(iid, "values"))
        if str(vals[4]) == SECTION_HEADER:
            vals[4] = "Left Click"
            self.tree.item(iid, values=vals)
        else:
            vals[4] = SECTION_HEADER
            self.tree.item(iid, values=vals)
        self.refresh_nums()

    def _add_section(self, src):
        """v1.21: แทรกหัวข้อ Section ใหม่ใต้แถวที่เลือก (ใช้คอลัมน์ Additional เป็นชื่อหัวข้อ)"""
        idx = self.tree.index(src)
        new_iid = self.tree.insert("", idx + 1,
                                   values=["☑", "#", "", "", SECTION_HEADER, "", 0, 0, 1])
        self.tree.selection_set(new_iid)
        self.refresh_nums()

    # --------------------------------------------- ย่อ/ขยายกลุ่ม Section (v1.22) --
    def _group_members(self, head_iid):
        """คืนรายชื่อแถวในกลุ่มของหัวข้อ head_iid (ทุกแถวถัดไปจนถึงหัวข้อถัดไปหรือจบตาราง)
        ถ้ากลุ่มนี้ย่ออยู่ คืนลิสต์ว่าง (แถวสมาชิกถูก detach ไว้)"""
        kids = self.tree.get_children()
        idx = kids.index(head_iid)
        if self._group_collapsed(head_iid):
            return []
        end = len(kids)
        for j in range(idx + 1, len(kids)):
            if str(self.tree.item(kids[j], "values")[4]) == SECTION_HEADER:
                end = j
                break
        return kids[idx + 1:end]

    def _group_collapsed(self, head_iid):
        """คืน True ถ้าหัวข้อนี้กำลังย่ออยู่ (Additional ลงท้าย '(ย่อ N แถว)')"""
        try:
            add = str(self.tree.item(head_iid, "values")[5])
        except tk.TclError:
            return False
        return bool(_COLLAPSED_RE.search(add.strip()))

    def _near_collapsed_marker(self, iid):
        """v1.22: แถวนี้คือหัวข้อที่ย่ออยู่ หรือเป็นแถวแรกถัดจากหัวข้อที่ย่ออยู่"""
        try:
            kids = self.tree.get_children()
            idx = self.tree.index(iid)
            if _COLLAPSED_RE.search(str(self.tree.item(iid, "values")[5]).strip()):
                return True
            if idx > 0 and str(self.tree.item(kids[idx - 1], "values")[4]) == SECTION_HEADER \
                    and _COLLAPSED_RE.search(str(self.tree.item(kids[idx - 1], "values")[5]).strip()):
                return True
        except tk.TclError:
            pass
        return False

    def _marker_head(self, iid):
        """v1.22: คืน iid หัวข้อของ marker/แถวในตำแหน่งกลุ่มย่อที่ iid อยู่ (สำหรับปุ่มขยายจากเมนูขวา)"""
        kids = self.tree.get_children()
        idx = self.tree.index(iid)
        for j in range(idx, -1, -1):
            if str(self.tree.item(kids[j], "values")[4]) == SECTION_HEADER:
                return kids[j]
        return iid

    def _group_toggle(self, head_iid):
        """ย่อ/ขยายกลุ่มของหัวข้อ: ย่อ = ซ่อนแถวสมาชิก (สคริปต์เล่นแบบเดิมทุกอย่าง)
        ขยาย = คืนแถวกลับตำแหน่งเดิมใต้หัวข้อ (หัวข้ออื่นที่ย่ออยู่คงสถานะ)"""
        if self._group_collapsed(head_iid):
            vals = list(self.tree.item(head_iid, "values"))
            m = _COLLAPSED_RE.search(str(vals[5]).strip())
            n = int(m.group(1)) if m else 0
            pos = self.tree.index(head_iid) + 1          # แทรกคืนต่อจากหัวข้อเสมอ
            hidden = [v for v in self._section_stash if v.get("after") == head_iid]
            for v in hidden:                             # stash คงลำดับเดิมไว้แล้ว
                self.tree.insert("", pos, values=list(v["vals"]))
                pos += 1
            self._section_stash = [v for v in self._section_stash if v.get("after") != head_iid]
            m2 = re.match(r"^(.*?)\s*\(ย่อ \d+ แถว\)$", str(vals[5]).strip())
            vals[5] = m2.group(1) if m2 else vals[5]
            self.tree.item(head_iid, values=vals)
            self.refresh_nums()
            self._ui_state["msg"] = ("ขยายกลุ่มแล้ว (%d แถว) — ลำดับการเล่นเหมือนเดิม" % n, "#080")
        else:
            members = self._group_members(head_iid)
            n = len(members)
            if n == 0:
                self._ui_state["msg"] = ("กลุ่มนี้ไม่มีแถวให้ย่อ", "#a60")
                return
            for m_iid in members:
                self._section_stash.append({"after": head_iid, "vals": list(self.tree.item(m_iid, "values"))})
                self.tree.detach(m_iid)
            vals = list(self.tree.item(head_iid, "values"))
            vals[5] = _save_head_add(vals[5], n)
            self.tree.item(head_iid, values=vals)
            self.refresh_nums()
            self._ui_state["msg"] = ("ย่อกลุ่มแล้ว (%d แถว) — การเล่นไม่เปลี่ยน กดซ้ำเพื่อขยาย" % n, "#080")

    def del_selected(self):
        self._on_del()

    def clear_all(self):
        if self.tree.get_children() and messagebox.askyesno(APP_TITLE, "ลบทุกบรรทัดใช่หรือไม่?"):
            self.tree.delete(*self.tree.get_children())
            self._section_stash = []                  # v1.22: ลบหมด = ไม่มีแถวซ่อนค้าง
            self._hl_row = None

    def move(self, d):
        """ผลักแถวขึ้น/ลง — v1.22: กลุ่มที่ย่ออยู่เลื่อนทั้งก้อน, แถวธรรมดาไม่ทะลุเข้ากลุ่มย่อ"""
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]
        vals = self.tree.item(iid, "values")
        if str(vals[4]) == SECTION_HEADER and self._group_collapsed(iid):
            self._move_collapsed_group(iid, d)
            return
        idx = self.tree.index(iid)
        tgt = idx + d
        kids = self.tree.get_children()
        if 0 <= tgt < len(kids):
            if _COLLAPSED_RE.search(str(self.tree.item(kids[tgt], "values")[5]).strip()):
                return                        # ขอย้ายกลุ่มย่อใช้ปุ่มบนหัวข้อแทน — กันแถวหลุดเข้ากลุ่ม
            self.tree.move(iid, "", tgt)
            self.refresh_nums()

    def _move_collapsed_group(self, head_iid, d):
        """เลื่อนกลุ่มย่อทั้งก้อน (หัวข้อ + แถวใน stash) ขึ้น/ลง 1 ตำแหน่ง"""
        idx = self.tree.index(head_iid)
        tgt = idx + d
        kids = self.tree.get_children()
        if not (0 <= tgt < len(kids)):
            return
        if d > 0:
            if _COLLAPSED_RE.search(str(self.tree.item(kids[tgt], "values")[5]).strip()):
                return                        # กลุ่มย่อชิดกัน — ขยายก่อนจึงสลับได้
            after = kids[tgt]                 # แถวที่กลุ่มกระโดดข้าม = จุดผูกแถวกลุ่มใหม่
            moved = [v for v in self._section_stash if v.get("after") == head_iid]
            self._section_stash = [v for v in self._section_stash if v.get("after") != head_iid]
            self.tree.move(head_iid, "", tgt + 1)
            for v in moved:
                self._section_stash.append({"after": after, "vals": v["vals"]})
        else:
            self.tree.move(head_iid, "", tgt)
        self.refresh_nums()

    # -------------------------------------------------------- cell editing ---
    def _on_dbl_click(self, event):
        if self.tree.identify("region", event.x, event.y) != "cell":
            return
        col = self.tree.identify_column(event.x)
        row_id = self.tree.identify_row(event.y)
        if not row_id or col in ("#1", "#2"):
            return
        ci = int(col.replace("#", "")) - 1             # ดัชนีใน COLS
        key = COLS[ci]
        if key in ("x", "y"):
            self._edit_xy(row_id, ci)
            return
        vals = list(self.tree.item(row_id, "values"))
        ei = ci - 4                                    # ดัชนีใน EDIT_COLS
        label = EDIT_COLS[ei]
        choices = {"Action": list(ACTIONS_ALL) + [n for n, _ in self._plugins],
                   "Additional": [""] + MOD_KEYS[1:] + sorted(SPECIAL_KEYS)}.get(label)
        if key == "additional":
            hint = {"Type Text": "พิมพ์ข้อความที่จะส่ง (เช่น สวัสดี)",
                    "Launch App": "พาธโปรแกรม หรือ URL เช่น https://example.com",
                    "Image Click": "ชื่อไฟล์ .png เช่น button.png",
                    "If Image": "ชื่อไฟล์ .png — Repeat = จำนวนแถวที่ข้ามถ้าภาพไม่เจอ",
                    "Else If Image": "ชื่อไฟล์ .png — ตัวแบ่งกลุ่ม A/B แบบสองทาง (v1.18)",
                    "Wait for Pixel Color": "x,y #RRGGBB เช่น 100,200 #ff0000 (ตามด้วย 60s = รอ 60 วิ)",
                    "If Loop": "เลขรอบ เช่น 5 = รอบที่ 5 ขึ้นไปข้าม N แถวถัดไป (N = Repeat)",
                    "If Time": "HH:MM เช่น 22:30 = ผ่าน 22:30 แล้วข้าม N แถวถัดไป (N = Repeat)",
                    "Tap Key": "ชื่อคีย์ เช่น enter, w, F5 — หรือคอมโบ Ctrl+W, Ctrl+Shift+T",
                    "Press Key": "กดค้าง เช่น ctrl, w — หรือคอมโบ Ctrl+W (ต้องมี Release คู่)",
                    "Release Key": "ชื่อคีย์/คอมโบเดียวกับ Press Key ที่กดค้างไว้",
                    "Set Variable": "name = ค่า หรือ name += จำนวน — เรียกใช้ด้วย {name} ในช่องอื่น",
                    "Set Clipboard": "ข้อความที่จะใส่คลิปบอร์ด (ใช้ {ตัวแปร} ได้)",
                    "Read Clipboard": "ชื่อตัวแปรที่จะเก็บข้อความจากคลิปบอร์ด เช่น mytext",
                    "Wait for Image": "ชื่อไฟล์ .png เช่น button.png",
                    "Scroll Up": "จำนวนจังหวะ เช่น 3",
                    "Scroll Down": "จำนวนจังหวะ เช่น 3"}.get(str(vals[4]), "")
            if hint:
                self._ui_state["msg"] = ("ช่อง Additional: " + hint, "#06c")
        HotkeyEdit(self.root, label, vals[ci], choices,
                   lambda v, r=row_id, c=ci: self._apply_edit(r, c, v),
                   editable=(key == "additional"))   # v1.20.3: Additional พิมพ์อิสระได้

    def _edit_xy(self, row_id, ci):
        """ดับเบิลคลิก X/Y → นับถอยหลัง 3 วิ แล้วจับพิกัดเมาส์ปัจจุบัน"""
        def grab(count=3):
            if not self.root.winfo_exists():
                return
            if count:
                self.lbl_state.config(text="จับพิกัดใน %d วิ… วางเมาส์ที่ตำแหน่งที่ต้องการ" % count, fg="#06c")
                self.root.after(1000, grab, count - 1)
            else:
                x, y = self.mouse_ctl.position
                vals = list(self.tree.item(row_id, "values"))
                vals[ci] = int(x)
                self.tree.item(row_id, values=vals)
                self._ui_state["msg"] = ("จับพิกัดได้: %d, %d" % (x, y), "#080")
        grab()

    def _apply_edit(self, row_id, ci, value):
        vals = list(self.tree.item(row_id, "values"))
        vals[ci] = value
        self.tree.item(row_id, values=vals)

    # ------------------------------------------------------------- playback --
    def _play_options(self):
        """อ่านตัวเลือกการเล่นจากแถบล่าง (สัดส่วนแถว 5-100%)"""
        try:
            pct = int(self.ent_pct.get())
        except ValueError:
            pct = 100
        return max(5, min(100, pct))

    def _rows_for_play(self):
        """แถวที่เปิดใช้ (☑) ทั้งหมด ในลำดับของตาราง — ใช้เป็นสคริปต์ที่จะเล่น"""
        rows, _iids = self._rows_and_iids_for_play()
        return rows

    def _rows_and_iids_for_play(self):
        """คู่ (แถว, iid ในตาราง) ของแถวที่เปิดใช้ (☑) — iid ใช้ทำไฮไลต์แถวที่กำลังเล่น
        แยกจาก _rows_for_play เพื่อให้ player ไม่ต้องเรียก Tk ข้ามเธรด (v1.19)"""
        rows, iids = [], []
        for iid in self.tree.get_children():
            v = self.tree.item(iid, "values")
            if str(v[0]) == "☑":
                rows.append(dict(x=v[2], y=v[3], button=v[4], additional=v[5],
                                 mins=v[6], secs=v[7], repeat=v[8]))
                iids.append(iid)
        return rows, iids

    def _plugin_module(self, name):
        """คืน module ของ plugin ตามชื่อ Action (ไม่พบ = None)"""
        for n, mod in self._plugins:
            if n == name:
                return mod
        return None

    def _validate_rows(self, rows):
        for r in rows:
            if r["button"] in KEY_ACTIONS and not (parse_key(r["additional"])
                                                   or parse_key_combo(r["additional"])):
                return False
            if self._plugin_module(r["button"]):
                continue                    # Custom Action — ตรวจรูปแบบภายใน plugin เอง
            if r["button"] == "Launch App" and not (r["additional"] or "").strip():
                return False
            if r["button"] == "Set Variable" and not parse_set_var(r["additional"]):
                return False
            if r["button"] == "Set Clipboard" and not (r["additional"] or "").strip():
                return False
            if r["button"] == "Read Clipboard" and not re.fullmatch(
                    _VAR_NAME, str(r["additional"] or "").strip()):
                return False
            if r["button"] == IF_LOOP and parse_if_loop(r["additional"]) is None:
                return False
            if r["button"] == IF_TIME and parse_if_time(r["additional"]) is None:
                return False
            if r["button"] in (IMAGE_ACTION, "Wait for Image", IF_IMAGE, ELSE_IMAGE):
                p, _a, _t = self._parse_search_area(r)
                if not p:
                    return False
                if not os.path.isabs(p):
                    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), p)
                if not os.path.isfile(p):
                    return False
        return True

    def start_play(self):
        self._start_player(False)

    def start_repeat(self):
        self._start_player(True)

    def _start_player(self, loop, once=False):
        """เริ่มเล่น — loop=True = วนไม่จำกัดจนกด STOP (REPEAT/F10)
        once=True = เล่นครั้งเดียวจบรอบเดียว (ใช้โดย schedule — ไม่สนช่อง รอบ:/forever)"""
        rows, iids = self._rows_and_iids_for_play()
        items = list(zip(rows, iids))     # คู่ (แถว, iid) — เล่น/ไฮไลต์ตามกันเสมอ (v1.19)
        if not items:
            messagebox.showinfo(APP_TITLE, self._t("no_rows"))
            return
        if not self._validate_rows(rows):
            if not messagebox.askyesno(APP_TITLE,
                    "มีแถวที่ค่าไม่ครบ (คีย์ว่าง/สะกดไม่รู้จัก หรือไม่พบไฟล์ภาพ)\n"
                    "แถวเหล่านั้นจะถูกข้าม ต้องการเล่นต่อหรือไม่?"):
                return
        self.stop_all(silent=True)          # หยุดเธรดเดิม + ปล่อยคีย์ค้างก่อน
        self._play_gen += 1                 # เธรดใหม่รุ่นใหม่ — เธรดเก่าที่ sleep ค้างจะหยุดเอง
        self.running = True
        gen = self._play_gen
        loop = loop or self.chk_forever.get()          # อ่านค่าฝั่ง UI ก่อนสร้างเธรด
        try:
            speed = float(self.cmb_speed.get())
        except ValueError:
            speed = 1.0
        self._speed_mult = min(10.0, max(0.1, speed))
        try:
            loops = int(self.ent_loops.get())
        except ValueError:
            loops = 1
        self._script_loops = max(0, loops)
        if once:
            loop, self._script_loops = False, 1   # schedule: เล่นรอบเดียวต่อการเรียก
        self._restore_pos = self.chk_restore.get()
        self._shuffle = self.chk_shuffle.get()
        self._pct = self._play_options()
        self._vars = {}                   # ตัวแปรเริ่มใหม่ทุกครั้งที่เริ่มเล่น (v1.19)
        self._loop_no = 1                 # ตัวนับรอบเริ่มใหม่ (If Loop, v1.21)
        self._log_src = self._loaded_file or "ตารางในโปรแกรม"
        if self._log_enabled:
            extra = " สุ่มลำดับ" if self._shuffle else ""
            if self._pct < 100:
                extra += " %d%%" % self._pct
            log_write("START", "เริ่มเล่น (%s) ความเร็ว %gx รอบ=%s แถวที่เล่น=%d%s" %
                      ("วนซ้ำ" if loop else "ครั้งเดียว", self._speed_mult,
                       self._script_loops if self._script_loops else "ไม่จำกัด",
                       len(items), extra), self._log_src)
        self.btn_start.config(state="disabled", bg="#cfcfcf")
        self.btn_repeat.config(state="disabled", bg="#2e7d32")
        mode = self._t("mode_loop") if loop else self._t("mode_once")
        self.root.title(APP_TITLE + "   [ RUNNING ]")
        self._ui_state["msg"] = (self._t("playing") % mode, "#080")
        threading.Thread(target=self._player, args=(items, loop, gen), daemon=True).start()

    def _reset_ui(self):
        self.btn_start.config(state="normal", bg="#e8e8e8")
        self.btn_repeat.config(state="normal", bg="#3fa63f", fg="white")
        self.root.title(APP_TITLE)

    # ------------------------------------------ การหยุดที่แม่นยำ (v1.7.1) ----
    def _gen_ok(self, gen):
        """เธรดผู้เล่นรุ่น gen ยังมีสิทธิ์เล่นต่อไหม (STOP หรือ START ใหม่ = หยุด)"""
        return self.running and gen == self._play_gen

    def _sleep_check(self, secs, gen):
        """sleep แบบแบ่งชิ้นละ 50 ms — STOP ตอบสนองทันทีแม้ดีเลย์ยาวหลายนาที"""
        end = time.time() + max(0.0, secs)
        while True:
            remain = end - time.time()
            if remain <= 0 or not self._gen_ok(gen):
                break
            time.sleep(min(0.05, remain))
        return self._gen_ok(gen)

    def _release_stuck(self):
        """ปล่อยคีย์/ปุ่มเมาส์ที่กดค้างไว้ เมื่อ STOP กลางคัน (กัน Ctrl ติด กดค้าง)"""
        try:
            for k in list(self._pressed_keys):
                self.kb_ctl.release(k)
            self._pressed_keys.clear()
            for b in list(self._pressed_btns):
                self.mouse_ctl.release(b)
            self._pressed_btns.clear()
        except Exception:
            pass

    def stop_all(self, silent=False):
        was = self.running or self.recording
        self._play_gen += 1               # ทำให้เธรดผู้เล่นรุ่นเดิมหยุดเองทันที
        self.running = False
        self._release_stuck()             # ปล่อยคีย์/ปุ่มที่กดค้างจาก Press Key / Down
        if self.recording:
            self._stop_record()
        self._ui_state["row"] = None
        self._ui_state["prog"] = None
        self._ui_state["reset"] = True
        if was and not silent:
            self._ui_state["msg"] = (self._t("stopped"), "#a60")
            if self._log_enabled:
                log_write("STOP", "หยุดโดยผู้ใช้ (F8/ปุ่ม STOP) — ปล่อยคีย์/ปุ่มที่ค้างแล้ว",
                          self._log_src)

    def _player(self, items, loop, gen=0):
        """เธรดผู้เล่น — เช็ค self._gen_ok(gen) ทุกจุด: STOP หรือ START ใหม่ = หยุดทันที
        items = คู่ (แถว, iid ในตาราง) — player ไม่เรียก Tk เอง สื่อสารผ่าน _ui_state เท่านั้น"""
        def do_step(r):
            btn = r["button"]
            if btn in BTN_TH:                                    # เมาส์ทั่วไป
                b, act = BTN_TH[r["button"]]
                btn_obj = getattr(Button, b.lower())
                if str(r["x"]) != "" and str(r["y"]) != "":
                    self.mouse_ctl.position = (int(r["x"]), int(r["y"]))
                    time.sleep(0.03)
                if act == "Down":
                    self.mouse_ctl.press(btn_obj)
                    self._pressed_btns.add(btn_obj)  # จำไว้ปล่อยตอน STOP กลางคัน
                elif act == "Up":
                    self.mouse_ctl.release(btn_obj)
                    self._pressed_btns.discard(btn_obj)
                else:
                    self.mouse_ctl.click(btn_obj, 1)
            elif btn in SCROLL_ACTIONS:                          # เลื่อนล้อเมาส์
                try:
                    notches = int(str(r["additional"] or "1"))
                except ValueError:
                    notches = 1
                dy = notches if btn == "Scroll Up" else -notches
                self.mouse_ctl.scroll(0, dy)
            elif btn in DBL_ACTIONS:                             # ดับเบิลคลิก
                if str(r["x"]) != "" and str(r["y"]) != "":
                    self.mouse_ctl.position = (int(r["x"]), int(r["y"]))
                    time.sleep(0.03)
                self.mouse_ctl.click(Button.right if "Right" in btn else Button.left, 2)
            elif btn in MOD_CLICKS:                              # คลิก+modifier
                mods = [m for m in ("ctrl", "shift", "alt") if m.capitalize() in btn]
                self._do_mod_click(r, mods)
            elif btn == "Move Mouse":                            # ย้ายเมาส์
                if str(r["x"]) != "" and str(r["y"]) != "":
                    self.mouse_ctl.position = (int(r["x"]), int(r["y"]))
            elif btn == "Move Mouse by Offset":                  # ย้ายแบบสัมพัทธ์
                try:
                    dx = int(str(r["x"] or 0))
                    dyo = int(str(r["y"] or 0))
                except ValueError:
                    dx = dyo = 0
                cx, cy = self.mouse_ctl.position
                self.mouse_ctl.position = (cx + dx, cy + dyo)
            elif btn == "Save Cursor":                           # เซฟตำแหน่งเมาส์
                self._saved_pos = self.mouse_ctl.position
            elif btn == "Restore Cursor":                        # คืนตำแหน่งเมาส์
                if self._saved_pos:
                    self.mouse_ctl.position = self._saved_pos
            elif btn == IMAGE_ACTION:                            # คลิกตามภาพ
                self._do_image_click(r)
            elif btn == WAIT_PIXEL:                              # รอจุดสี (v1.18)
                self._do_wait_for_pixel(r)
            elif btn == "Wait for Image":                        # รอภาพปรากฏ
                self._do_wait_for_image(r)
            elif btn == "Type Text":                             # พิมพ์ข้อความ
                for ch in str(r["additional"] or ""):
                    if not self._gen_ok(gen):
                        return
                    if ch == "\n":
                        self.kb_ctl.tap(Key.enter)
                    elif not send_unicode_char(ch):              # v1.20.2: ไม่ขึ้นกับ layout
                        self.kb_ctl.tap(self.kb_ctrl_char(ch))   # fallback (OS อื่น)
                    # v1.20.3: เว้นจังหวะระหว่างตัวอักษร — แอปเป้าหมายที่ยัง busy
                    # (เช่น Notepad เพิ่งเปิด) ไม่ทันประมวลผล burst เร็ว ๆ อาจกลืน/เพี้ยน
                    time.sleep(0.015)
            elif btn == "Launch App":                            # เปิดแอป/เว็บ
                target = str(r["additional"] or "").strip()
                if target:
                    try:
                        os.startfile(target)      # Windows
                    except (OSError, AttributeError):
                        import subprocess
                        opener = "open" if sys.platform == "darwin" else "xdg-open"
                        subprocess.Popen([opener, target])
            elif btn == "Beep":                                  # เสียงเตือน — ขอผ่าน poller
                self._ui_state["beep"] = True                    # (main thread เป็นคน bell)
            elif btn in KEY_ACTIONS:                             # คีย์บอร์ด
                combo = parse_key_combo(r["additional"])         # v1.20.4: Ctrl+W ฯลฯ
                mods, k = combo if combo else ((), parse_key(r["additional"]))
                if k is None:
                    return
                if btn == "Press Key":
                    for m in mods:
                        self.kb_ctl.press(m)
                        self._pressed_keys.add(m)
                    self.kb_ctl.press(k)
                    self._pressed_keys.add(k)      # จำไว้ปล่อยตอน STOP กลางคัน
                elif btn == "Release Key":
                    self.kb_ctl.release(k)
                    self._pressed_keys.discard(k)
                    for m in reversed(mods):
                        self.kb_ctl.release(m)
                        self._pressed_keys.discard(m)
                else:
                    for m in mods:
                        self.kb_ctl.press(m)
                        self._pressed_keys.add(m)
                    self.kb_ctl.tap(k)
                    for m in reversed(mods):
                        self.kb_ctl.release(m)
                        self._pressed_keys.discard(m)
            elif btn == "Set Variable":                          # ตัวแปรในสคริปต์ (v1.19)
                if not apply_set_var(self._vars, r["additional"]):
                    self._ui_state["msg"] = ("Set Variable: รูปแบบไม่ถูก (%s) — ต้องเป็น "
                                             "name = ค่า หรือ name += จำนวน" % (r["additional"] or ""), "#c00")
            elif btn == "Set Clipboard":                         # ตั้งคลิปบอร์ด (v1.20)
                text = str(r["additional"] or "")
                if text:
                    self._ui_state["clipboard"] = text           # poller ตั้งบน main thread
            elif btn == "Read Clipboard":                        # อ่านคลิปบอร์ดเก็บเป็นตัวแปร (v1.20)
                m = re.fullmatch(_VAR_NAME, str(r["additional"] or "").strip())
                if not m:
                    self._ui_state["msg"] = ("Read Clipboard: พิมพ์ชื่อตัวแปรใน Additional "
                                             "เช่น mytext", "#c00")
                    return
                self._ui_state["read_clipboard"] = m.group(0)
                self._sleep_check(0.2, gen)                      # รอ poller (120ms) อ่านให้ก่อน
            else:                                                # Custom Action (v1.16)
                mod = self._plugin_module(btn)
                if mod is None:
                    return
                ctx = {"mouse": self.mouse_ctl, "kb": self.kb_ctl,
                       "log": lambda m: log_write("PLUGIN", m, self._log_src),
                       "cfg": {"lang": self._lang},
                       "stop_check": lambda: self._gen_ok(gen),        # v1.20
                       "ui": {"msg": lambda text, color="#080":        # v1.20
                                  self._ui_state.__setitem__("msg", (str(text), color)),
                              "beep": lambda: self._ui_state.__setitem__("beep", True)}}
                mod.run(ctx, dict(r))

        # บั๊กฟิกซ์ v1.6: เดิมลูปนี้ถูกแทรกหลัง return ของ kb_ctrl_char ทำให้เป็น dead code
        # v1.7.1: ใช้ _gen_ok/_sleep_check — STOP แม่นทันทีแม้ดีเลย์ยาว + กันเล่นซ้อนเธรด
        try:
            start_pos = self.mouse_ctl.position if self._restore_pos else None
            total = len(items)
            loop_no = 0
            outer = True
            play_started = time.time()
            while outer:
                loop_no += 1
                # _script_loops: 0 = ไม่จำกัด, 1 = ครั้งเดียว, N = N รอบ
                play_items = pick_play_order(items, pct=self._pct, shuffle=self._shuffle)
                for i, (r, iid) in enumerate(play_items):
                    if not self._gen_ok(gen):
                        return
                    # If Image (v1.17): แถวที่ถูกสั่งข้ามจาก If Image ก่อนหน้า → ข้ามเงียบ ๆ
                    if self._ifimg_skip > 0:
                        self._ifimg_skip -= 1
                        continue
                    self._loop_no = loop_no          # v1.21: เลขรอบปัจจุบัน (ให้ If Loop ใช้)
                    r = subst_row(r, self._vars)     # v1.19: แทน {ตัวแปร} ทุกคอลัมน์
                    if r["button"] == SECTION_HEADER:  # v1.21: แถวจัดระเบียบ — ไม่ทำอะไร
                        continue
                    self._ui_state["row"] = iid      # ไฮไลต์ตรงแถวที่เล่นจริง (v1.19)
                    self._ui_state["prog"] = (i + 1, total, loop_no)
                    for _ in range(parse_int(r["repeat"])):
                        if not self._gen_ok(gen):
                            return
                        lo, hi = delay_range(r["secs"])            # 0s = ผ่าน (เงื่อนไขไม่ต้องหน่วง)
                        base = delay_seconds(r["mins"], 0) + (lo if lo == hi else random.uniform(lo, hi))
                        if not self._sleep_check(base / self._speed_mult, gen):
                            return
                        step_t0 = time.time()
                        if r["button"] == IF_IMAGE:
                            found = False
                            if HAS_CV:
                                try:
                                    found = self._find_image_pos(r) is not None
                                except Exception:
                                    found = False
                            self._last_if_found = found        # จำผลให้ Else If Image (v1.18)
                            if found:
                                det = "เจอ"
                                self._ui_state["msg"] = (self._t("ifimg_hit"), "#080")
                            else:
                                n = parse_int(r.get("repeat"), 1)   # Repeat = จำนวนแถวที่ข้าม
                                self._ifimg_skip = n
                                det = "ข้าม %d แถว" % n
                                self._ui_state["msg"] = (self._t("ifimg_skip") % n, "#a60")
                            if self._log_enabled:
                                log_write("STEP", "รอบ %d แถว %d/%d If Image %s → %s (%.1f วิ)" %
                                          (loop_no, i + 1, total, r["additional"] or "",
                                           det, time.time() - step_t0), self._log_src)
                            break                       # เงื่อนไขทำงานรอบเดียว (ไม่อ่าน Repeat ซ้ำ)
                        if r["button"] == ELSE_IMAGE:
                            # v1.18 เงื่อนไขสองทาง: If Image เจอ → ข้ามกลุ่ม B (Repeat แถว)
                            #                    If Image ไม่เจอ → เล่นกลุ่ม B ต่อ (ไม่ข้าม)
                            n = parse_int(r.get("repeat"), 1)
                            if self._last_if_found:
                                self._ifimg_skip = n
                                det = "If เจอ → ข้ามกลุ่ม B %d แถว" % n
                                self._ui_state["msg"] = (self._t("ifimg_skip") % n, "#a60")
                            else:
                                det = "If ไม่เจอ → เล่นกลุ่ม B ต่อ"
                                self._ui_state["msg"] = (self._t("ifimg_hit"), "#080")
                            if self._log_enabled:
                                log_write("STEP", "รอบ %d แถว %d/%d Else If Image %s → %s (%.1f วิ)" %
                                          (loop_no, i + 1, total, r["additional"] or "",
                                           det, time.time() - step_t0), self._log_src)
                            break                       # ตัวแบ่งกลุ่มทำงานรอบเดียว
                        if r["button"] == IF_LOOP:      # v1.21: รอบที่ >= N → ข้าม N แถว
                            n = parse_if_loop(r.get("additional"))
                            if n is None:
                                det = "Additional ไม่ถูก (ต้องเป็นเลข >= 1) — เล่นต่อ"
                            elif self._loop_no < n:
                                det = "รอบ %d < %d → เล่นต่อ" % (self._loop_no, n)
                                self._ui_state["msg"] = (self._t("ifloop_hit"), "#080")
                            else:
                                n_skip = parse_int(r.get("repeat"), 1)   # จำนวนแถวที่ข้าม = Repeat
                                self._ifimg_skip = n_skip
                                det = "รอบที่ %d >= %d → ข้าม %d แถว" % (self._loop_no, n, n_skip)
                                self._ui_state["msg"] = (self._t("ifimg_skip") % n_skip, "#a60")
                            if self._log_enabled:
                                log_write("STEP", "รอบ %d แถว %d/%d If Loop %s → %s (%.1f วิ)" %
                                          (loop_no, i + 1, total, r["additional"] or "",
                                           det, time.time() - step_t0), self._log_src)
                            break                       # เงื่อนไขทำงานรอบเดียว (ไม่อ่าน Repeat ซ้ำ)
                        if r["button"] == IF_TIME:      # v1.21: ผ่าน HH:MM แล้ว → ข้าม N แถว
                            spec = parse_if_time(r.get("additional"))
                            if spec is None:
                                det = "Additional ไม่ถูก (ต้องเป็น HH:MM) — เล่นต่อ"
                            else:
                                hh, mm = spec
                                now = time.localtime()
                                passed = (now.tm_hour, now.tm_min) >= (hh, mm)
                                if not passed:
                                    det = "%02d:%02d ยังไม่ถึง %02d:%02d → เล่นต่อ" % (
                                        now.tm_hour, now.tm_min, hh, mm)
                                    self._ui_state["msg"] = (self._t("iftime_hit"), "#080")
                                else:
                                    n_skip = parse_int(r.get("repeat"), 1)   # จำนวนแถวที่ข้าม = Repeat
                                    self._ifimg_skip = n_skip
                                    det = "ผ่าน %02d:%02d แล้ว → ข้าม %d แถว" % (hh, mm, n_skip)
                                    self._ui_state["msg"] = (self._t("ifimg_skip") % n_skip, "#a60")
                            if self._log_enabled:
                                log_write("STEP", "รอบ %d แถว %d/%d If Time %s → %s (%.1f วิ)" %
                                          (loop_no, i + 1, total, r["additional"] or "",
                                           det, time.time() - step_t0), self._log_src)
                            break                       # เงื่อนไขทำงานรอบเดียว (ไม่อ่าน Repeat ซ้ำ)
                        do_step(r)
                        if self._log_enabled:
                            log_write("STEP", "รอบ %d แถว %d/%d %s %s (%.1f วิ)" %
                                      (loop_no, i + 1, total, r["button"],
                                       r["additional"] or "", time.time() - step_t0),
                                      self._log_src)
                self._ui_state["row"] = None
                self._ui_state["prog"] = (total, total, loop_no)
                if self._restore_pos and start_pos and self._gen_ok(gen):
                    self.mouse_ctl.position = start_pos
                if loop:
                    outer = self._gen_ok(gen)  # REPEAT/วนซ้ำไม่จำกัด = เล่นจนกด STOP
                    continue
                if self._script_loops == 0:
                    outer = self._gen_ok(gen)  # ไม่จำกัดรอบ
                else:
                    self._script_loops -= 1
                    outer = self._script_loops > 0 and self._gen_ok(gen)
            if self._gen_ok(gen):
                self._ui_state["msg"] = (self._t("done"), "#080")
                if self._log_enabled:
                    log_write("END", "เล่นจบเองครบ %.1f วิ" % (time.time() - play_started),
                              self._log_src)
        finally:
            # เธรดจบเอง (จบสคริปต์ หรือถูก STOP/START ใหม่แทนที่) — ถ้าเป็นรุ่นปัจจุบันค่อยเคลียร์
            if gen == self._play_gen:
                self.running = False
                self._release_stuck()          # กันคีย์/ปุ่มค้างกรณีแถวสุดท้ายคือ Press/Down
                self._ui_state["row"] = None
                self._ui_state["prog"] = None
                self._ui_state["reset"] = True
                if self._log_enabled:
                    prune_log()

    def kb_ctrl_char(self, ch):
        """แปลงอักขระเป็น KeyCode สำหรับ Type Text — fallback เมื่อพิมพ์แบบ Unicode
        ไม่ได้ (OS อื่น) — เส้นทางหลักบน Windows คือ send_unicode_char() (v1.20.2)"""
        return KeyCode.from_char(ch)

    def _build_profile_bar(self):
        """แถบเลือกโปรไฟล์ + ปุ่ม schedule"""
        bar = tk.Frame(self.root, bg="#eef4ee")
        bar.pack(fill="x")
        tk.Label(bar, text="โปรไฟล์:", bg="#eef4ee").pack(side="left", padx=(8, 4), pady=3)
        self.cmb_profile = ttk.Combobox(bar, width=24, state="readonly")
        self.cmb_profile.pack(side="left", pady=3)
        self.cmb_profile.bind("<<ComboboxSelected>>", lambda e: self._switch_profile())
        tk.Button(bar, text="＋ สร้าง", width=6, command=self._profile_new).pack(side="left", padx=(6, 2))
        tk.Button(bar, text="เปลี่ยนชื่อ", width=9, command=self._profile_rename).pack(side="left", padx=2)
        tk.Button(bar, text="ลบ", width=5, command=self._profile_delete).pack(side="left", padx=2)
        tk.Button(bar, text="⏰ เล่นอัตโนมัติ...", command=self._schedule_dialog).pack(side="right", padx=8)

    def _refresh_profile_ui(self):
        names = sorted(self._profiles)
        if self._active_profile not in self._profiles:
            self._active_profile = names[0] if names else DEFAULT_PROFILE
        self.cmb_profile["values"] = names
        self.cmb_profile.set(self._active_profile)

    def _switch_profile(self):
        """บันทึกแถวปัจจุบันลงโปรไฟล์เดิม แล้วโหลดโปรไฟล์ที่เลือก"""
        if self.running or self.recording:
            messagebox.showinfo(APP_TITLE, "หยุดการทำงานก่อนสลับโปรไฟล์")
            self.cmb_profile.set(self._active_profile)
            return
        self._profiles[self._active_profile] = self._serialize()
        new_name = self.cmb_profile.get()
        self._active_profile = new_name
        self._load_rows(self._profiles.get(new_name, []))
        self._save_profiles()
        self._ui_state["msg"] = ("สลับไปโปรไฟล์: " + new_name, "#080")

    def _profile_new(self):
        name = simpledialog.askstring("โปรไฟล์ใหม่", "ชื่อโปรไฟล์ใหม่:", parent=self.root)
        if not name:
            return
        name = name.strip()
        if not name:
            return
        if name in self._profiles:
            messagebox.showwarning(APP_TITLE, "มีโปรไฟล์ชื่อนี้อยู่แล้ว")
            return
        self._profiles[self._active_profile] = self._serialize()   # เก็บของเดิมก่อน
        self._profiles[name] = []                                   # โปรไฟล์ใหม่ = ว่าง
        self._active_profile = name
        self._load_rows([])
        self._refresh_profile_ui()
        self._save_profiles()

    def _profile_rename(self):
        name = simpledialog.askstring("เปลี่ยนชื่อโปรไฟล์", "ชื่อใหม่:", parent=self.root,
                                      initialvalue=self._active_profile)
        if not name or name.strip() == self._active_profile:
            return
        name = name.strip()
        if name in self._profiles:
            messagebox.showwarning(APP_TITLE, "มีโปรไฟล์ชื่อนี้อยู่แล้ว")
            return
        self._profiles[name] = self._profiles.pop(self._active_profile)
        self._active_profile = name
        self._refresh_profile_ui()
        self._save_profiles()

    def _profile_delete(self):
        if len(self._profiles) <= 1:
            messagebox.showinfo(APP_TITLE, "ต้องมีโปรไฟล์อย่างน้อย 1 อัน")
            return
        if not messagebox.askyesno(APP_TITLE, "ลบโปรไฟล์ '%s'?" % self._active_profile):
            return
        self._profiles.pop(self._active_profile)
        self._active_profile = next(iter(self._profiles))
        self._load_rows(self._profiles[self._active_profile])
        self._refresh_profile_ui()
        self._save_profiles()

    # ------------------------------------------------------- schedule --------
    def _start_scheduler(self):
        """เธรดตรวจเวลาเล่นอัตโนมัติ — สั่งงานผ่าน queue เพื่อให้ Tk เป็นผู้เล่นเอง"""
        import queue
        self._sched_q = queue.Queue()
        self._sched_stop = threading.Event()
        threading.Thread(target=self._sched_loop, daemon=True).start()
        self._sched_poll()

    def _sched_loop(self):
        while not self._sched_stop.wait(5):
            try:
                self._sched_check()
            except Exception:
                pass

    def _sched_check(self, now=None):
        """ตรวจเงื่อนไขเล่นอัตโนมัติ 1 ครั้ง (แยกออกจากเธรดเพื่อทดสอบได้, v1.19)
        โหมด interval = ทุก N นาที (นับจากตอนเปิด/ตั้งค่า), โหมด daily = ทุกวันตอน HH:MM
        (เทียบเฉพาะ %H:%M — ใช้ stamp เต็มกันยิงซ้ำในนาทีเดียวกัน)"""
        mode = getattr(self, "_sched_mode", "")
        if not mode:
            return
        now = time.time() if now is None else now
        if mode == "interval":
            if self._sched_next and now >= self._sched_next and not self.running:
                self._sched_next = now + self._sched_every * 60
                self._sched_q.put("play")
        elif mode == "daily":
            stamp = time.strftime("%Y-%m-%d %H:%M")
            if stamp[11:] == self._sched_at and self._sched_last != stamp and not self.running:
                self._sched_last = stamp
                self._sched_q.put("play")

    def _sched_poll(self):
        """ฝั่ง UI: หยิบคำสั่งเล่นจาก scheduler มาทำ (thread-safe)"""
        try:
            while True:
                self._sched_q.get_nowait()
                if not self.running:
                    self._start_player(False, once=True)   # เล่น 1 รอบจบทุกครั้งที่ถึงเวลา (F8 หยุดได้)
        except Exception:
            pass
        if not self._sched_stop.is_set():
            self.root.after(500, self._sched_poll)

    def _schedule_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("เล่นอัตโนมัติตามเวลา (Schedule)")
        win.resizable(False, False)
        tk.Label(win, text="เลือกโหมดเล่นอัตโนมัติ — ใช้สคริปต์ที่เปิดใช้ (☑) อยู่ตอนถึงเวลา "
                           "(จำค่าไว้แม้ปิดโปรแกรม)",
                 font=("Segoe UI", 10, "bold")).pack(padx=18, pady=(14, 4))
        var = tk.StringVar(value=getattr(self, "_sched_mode", "") or "off")
        frm = tk.Frame(win)
        frm.pack(padx=18, pady=6)
        tk.Radiobutton(frm, text="ปิด (ไม่เล่นอัตโนมัติ)", variable=var, value="off").grid(
            row=0, column=0, columnspan=2, sticky="w")
        tk.Radiobutton(frm, text="ทุก ๆ", variable=var, value="interval").grid(row=1, column=0, sticky="w")
        ent_min = tk.Spinbox(frm, from_=1, to=1440, width=5)
        ent_min.delete(0, "end")
        ent_min.insert(0, str(getattr(self, "_sched_every", 10)))
        ent_min.grid(row=1, column=1, sticky="w")
        tk.Label(frm, text="นาที").grid(row=1, column=2, sticky="w")
        tk.Radiobutton(frm, text="ทุกวัน เวลา (HH:MM)", variable=var, value="daily").grid(row=2, column=0, sticky="w")
        ent_time = tk.Entry(frm, width=8)
        ent_time.insert(0, getattr(self, "_sched_at", "09:00") or "09:00")
        ent_time.grid(row=2, column=1, sticky="w")

        def apply():
            mode = var.get()
            self._sched_mode = "" if mode == "off" else mode
            self._sched_next = 0.0
            if mode == "interval":
                try:
                    self._sched_every = max(1, int(ent_min.get()))
                except ValueError:
                    self._sched_every = 10
                self._sched_next = time.time() + self._sched_every * 60
                msg = "เล่นอัตโนมัติทุก %d นาที (รอบแรกในอีก %d นาที)" % (self._sched_every, self._sched_every)
            elif mode == "daily":
                t = ent_time.get().strip()
                if not re_match_hhmm(t):
                    messagebox.showwarning(APP_TITLE, "รูปแบบเวลาต้องเป็น HH:MM เช่น 09:30", parent=win)
                    return
                self._sched_at = t
                self._sched_last = ""
                msg = "เล่นอัตโนมัติทุกวัน เวลา " + t
            else:
                msg = "ปิดโหมดเล่นอัตโนมัติแล้ว"
            self._ui_state["msg"] = (msg, "#080")
            win.destroy()

        bf = tk.Frame(win)
        bf.pack(pady=(4, 12))
        tk.Button(bf, text="ตกลง", width=8, command=apply).pack(side="left", padx=4)
        tk.Button(bf, text="ยกเลิก", width=8, command=win.destroy).pack(side="left", padx=4)

    def _untag(self, iid):
        try:
            vals = self.tree.item(iid, "values")
            if str(vals[4]) == SECTION_HEADER:
                return                             # คงสไตล์หัวข้อเดิมไว้ (v1.21)
            if _COLLAPSED_RE.search(str(vals[5]).strip()):
                return                             # คงสไตล์ marker กลุ่มย่อไว้ (v1.22)
            i = self.tree.index(iid)
            self.tree.item(iid, tags=row_tags(str(vals[4]), i))   # v1.22: สีตามหมวด Action
        except tk.TclError:
            pass

    # ------------------------------------ actions เสริม v1.5 (ผู้เล่น) -------
    def _do_mod_click(self, r, mods):
        """คลิกพร้อมกด modifier เช่น Ctrl+Click"""
        mod_keys = {"ctrl": Key.ctrl, "shift": Key.shift, "alt": Key.alt}
        pressed = []
        try:
            for m in mods:
                k = mod_keys.get(m)
                if k:
                    self.kb_ctl.press(k)
                    pressed.append(k)
            if str(r["x"]) != "" and str(r["y"]) != "":
                self.mouse_ctl.position = (int(r["x"]), int(r["y"]))
                time.sleep(0.03)
            self.mouse_ctl.click(Button.right if "Right" in r["button"] else Button.left, 1)
        finally:
            for k in reversed(pressed):
                self.kb_ctl.release(k)

    def _parse_search_area(self, r):
        """อ่านกรอบค้นหา (search area) และ threshold จากช่อง Additional
            ไฟล์.png                     = ทั้งจอ, threshold 80%
            ไฟล์.png@x,y,กว้าง,สูง        = กรอบ, threshold 80%
            ไฟล์.png@x,y,กว้าง,สูง#90     = กรอบ, threshold 90%
            ไฟล์.png#65                  = ทั้งจอ, threshold 65%
        คืน (path, area, threshold) — area None = ทั้งจอ"""
        raw = (r.get("additional") or "").strip()
        path, area, thr = raw, None, DEFAULT_THRESHOLD
        if "@" in raw:
            path, _, coords = raw.partition("@")
            coords, _, thr_s = coords.partition("#")
            try:
                x, y, w, h = [int(float(p.strip())) for p in coords.split(",")]
            except ValueError:
                return path, None, thr          # พิมพ์พลาด → ค้นทั้งจอ
            if w > 0 and h > 0:
                area = (x, y, x + w, y + h)
            raw_tail = thr_s
        else:
            _p, _s, thr_s = raw.partition("#")
            path = _p
            raw_tail = thr_s
        if thr_s.strip():
            try:
                t = float(thr_s)
                if 1 < t <= 100:      # ใส่เป็นเปอร์เซ็นต์ เช่น #90 = 90%
                    t /= 100.0
                thr = min(1.0, max(0.30, t))
            except ValueError:
                pass
        return path, area, thr

    def _grab_area_bgr(self, area):
        """จับภาพหน้าจอเฉพาะกรอบ (ถ้า area=None = ทั้งจอ) คืน numpy BGR"""
        if area and len(area) == 4:
            shot = ImageGrab.grab(bbox=area, all_screens=True)
        else:
            shot = ImageGrab.grab(all_screens=True)
        return cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR), (area[0], area[1]) if area else (0, 0)

    def _do_wait_for_image(self, r):
        """รอจนกว่าจะเจอภาพบนหน้าจอ — timeout ตั้งได้จาก Additional เช่น "logo.png 60s"
        (ค่าเริ่มต้น 30 วิ) รองรับ search area + threshold"""
        raw, timeout = parse_wait_timeout(r.get("additional"), 30)
        path, area, thr = self._parse_search_area(dict(r, additional=raw))
        if not HAS_CV:
            self._ui_state["msg"] = ("Wait for Image ต้องติดตั้ง: pip install opencv-python Pillow", "#c00")
            return
        if not os.path.isabs(path):
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
        if not os.path.isfile(path):
            self._ui_state["msg"] = ("ไม่พบไฟล์ภาพ: %s" % path, "#c00")
            return
        tmpl = cv2.imread(path, cv2.IMREAD_COLOR)
        if tmpl is None:
            self._ui_state["msg"] = ("อ่านไฟล์ภาพไม่ได้: %s" % path, "#c00")
            return
        deadline = time.time() + timeout
        gen = self._play_gen
        while time.time() < deadline and self._gen_ok(gen):
            screen, _off = self._grab_area_bgr(area)
            if tmpl.shape[0] <= screen.shape[0] and tmpl.shape[1] <= screen.shape[1]:
                res = cv2.matchTemplate(screen, tmpl, cv2.TM_CCOEFF_NORMED)
                _, maxv, _, _ = cv2.minMaxLoc(res)
                if maxv >= thr:
                    return
            time.sleep(0.5)
        self._ui_state["msg"] = ("Wait for Image: ไม่เจอภาพภายใน %d วิ — %s"
                                 % (timeout, os.path.basename(path)), "#a60")

    # ------------------------------------------------------ image click ------
    def _find_image_pos(self, r):
        """ค้นหาภาพบนหน้าจอ (ใช้ร่วมกันโดย Image Click และ If Image ใน v1.17)
        คืน (x, y) จุดศูนย์กลางที่เจอ หรือ None ถ้าไม่เจอ/ติดตั้ง/ไฟล์มีปัญหา
        (ข้อความ error ผลักเข้า _ui_state ให้ statusbar แสดง)"""
        path, area, thr = self._parse_search_area(r)
        if not HAS_CV:
            self._ui_state["msg"] = ("Image Click ต้องติดตั้ง: pip install opencv-python Pillow", "#c00")
            return None
        if not os.path.isabs(path):
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
        if not os.path.isfile(path):
            self._ui_state["msg"] = ("ไม่พบไฟล์ภาพ: %s" % path, "#c00")
            return None
        screen, (off_x, off_y) = self._grab_area_bgr(area)
        tmpl = cv2.imread(path, cv2.IMREAD_COLOR)
        if tmpl is None:
            self._ui_state["msg"] = ("อ่านไฟล์ภาพไม่ได้: %s" % path, "#c00")
            return None
        if tmpl.shape[0] > screen.shape[0] or tmpl.shape[1] > screen.shape[1]:
            self._ui_state["msg"] = ("ภาพใหญ่กว่าพื้นที่ค้นหา: %s" % os.path.basename(path), "#c00")
            return None
        res = cv2.matchTemplate(screen, tmpl, cv2.TM_CCOEFF_NORMED)
        _, maxv, _, maxloc = cv2.minMaxLoc(res)
        if maxv < thr:
            self._ui_state["msg"] = ("หาภาพไม่เจอ (ความมั่นใจ %.0f%% < %.0f%%): %s"
                                     % (maxv * 100, thr * 100, os.path.basename(path)), "#a60")
            return None
        return (off_x + maxloc[0] + tmpl.shape[1] // 2,
                off_y + maxloc[1] + tmpl.shape[0] // 2)

    def _do_wait_for_pixel(self, r):
        """รอจนสีจุด (x, y) ตรงตามที่กำหนด (v1.18)
        Additional: "x,y #rrggbb" — หน่วงก่อนตรวจ (วินาที) อยู่ในคอลัมน์ Secs
        รองรับ Search Area ไม่ได้ (เป็นจุดเดียว) — timeout 30 วิเหมือน Wait for Image"""
        raw, timeout = parse_wait_timeout(r.get("additional"), 30)
        spec = parse_pixel_spec(raw)
        if not spec:
            self._ui_state["msg"] = ("Wait for Pixel Color: รูปแบบ Additional ไม่ถูกต้อง "
                                     "(ต้องเป็น x,y #rrggbb และตามด้วย timeout เช่น 60s ได้)", "#c00")
            return
        x, y, rgb = spec
        lo, _hi = delay_range(r.get("secs"))
        if not self._sleep_check(max(0.0, lo) / max(0.01, self._speed_mult), self._play_gen):
            return
        deadline = time.time() + timeout
        while time.time() < deadline and self._gen_ok(self._play_gen):
            if color_close(pixel_color_at(x, y), rgb):
                self._ui_state["msg"] = ("Wait for Pixel Color: เจอสีที่รอ (%d,%d)" % (x, y), "#080")
                return
            time.sleep(0.25)
        self._ui_state["msg"] = ("Wait for Pixel Color: ไม่เจอสีภายใน %d วิ (%d,%d)"
                                 % (timeout, x, y), "#a60")

    def _do_image_click(self, r):
        """หาภาพย่อยบนหน้าจอแล้วคลิกที่จุดศูนย์กลาง
        ช่อง Additional: ไฟล์.png / ไฟล์.png@x,y,กว้าง,สูง / ...#threshold"""
        try:
            pos = self._find_image_pos(r)
            if pos is None:
                return
            self.mouse_ctl.position = pos
            time.sleep(0.03)
            self.mouse_ctl.click(Button.left, 1)
        except Exception as exc:
            self._ui_state["msg"] = ("Image Click ผิดพลาด: %s" % exc, "#c00")

    # ------------------------------------------------------ save / load ------
    def _serialize(self):
        """แถวที่เห็นในตาราง + แถวที่ถูกย่อไว้ (v1.22) — แถวซ่อนแทรกกลับหลังหัวข้อตามลำดับเดิม"""
        out = []
        for iid in self.tree.get_children():
            v = self.tree.item(iid, "values")
            if str(v[4]) != SECTION_HEADER or not _COLLAPSED_RE.search(str(v[5]).strip()):
                out.append(dict(enabled=str(v[0]) == "☑", x=str(v[2]), y=str(v[3]), button=str(v[4]),
                                additional=str(v[5]), mins=v[6], secs=v[7], repeat=v[8]))
                continue
            m = re.match(r"^(.*?)\s*\(ย่อ \d+ แถว\)$", str(v[5]).strip())
            out.append(dict(enabled=str(v[0]) == "☑", x=str(v[2]), y=str(v[3]), button=str(v[4]),
                            additional=(m.group(1) if m else str(v[5])), mins=v[6], secs=v[7], repeat=v[8]))
            for hv in self._section_stash:
                if hv.get("after") == iid:
                    w = hv["vals"]
                    out.append(dict(enabled=str(w[0]) == "☑", x=str(w[2]), y=str(w[3]), button=str(w[4]),
                                    additional=str(w[5]), mins=w[6], secs=w[7], repeat=w[8]))
        return out

    def _load_rows(self, rows):
        self._push_undo()              # เก็บสำเนาก่อนแทนที่ทั้งตาราง (Ctrl+Z กู้ได้)
        self.tree.delete(*self.tree.get_children())
        self._hl_row = None
        for r in rows:
            self._append_row(x=r.get("x", ""), y=r.get("y", ""),
                             button=r.get("button", ""), additional=r.get("additional", ""),
                             mins=r.get("mins", 0), secs=r.get("secs", 1),
                             repeat=r.get("repeat", 1))
            iid = self.tree.get_children()[-1]
            vals = list(self.tree.item(iid, "values"))
            vals[0] = "☑" if r.get("enabled", True) else "☐"
            if str(vals[4]) == SECTION_HEADER:
                vals[7] = "0"                      # Section ไม่หน่วง — ไม่ผ่านเส้นทางเล่น (v1.21)
            self.tree.item(iid, values=vals)
        self._section_stash = []                     # v1.22: โหลดชุดใหม่ = ไม่มีกลุ่มย่อค้าง
        self.refresh_nums()

    def save_script(self):
        if not self.tree.get_children():
            messagebox.showinfo(APP_TITLE, "ยังไม่มีรายการให้บันทึก")
            return
        f = filedialog.asksaveasfilename(defaultextension=".json",
                                         filetypes=[("Macro script", "*.json")],
                                         initialfile="myscript.json")
        if not f:
            return
        with open(f, "w", encoding="utf-8") as fh:
            json.dump(self._serialize(), fh, ensure_ascii=False, indent=2)
        self._loaded_file = f
        self._log_src = f
        self._ui_state["msg"] = ("บันทึกสคริปต์แล้ว: " + os.path.basename(f), "#080")

    def load_script(self):
        f = filedialog.askopenfilename(filetypes=[("Macro script", "*.json"), ("All files", "*.*")])
        if not f or not os.path.isfile(f):
            return
        try:
            with open(f, encoding="utf-8") as fh:
                data = json.load(fh)
            if not isinstance(data, list):
                raise ValueError("รูปแบบไฟล์ไม่ถูกต้อง")
            self._load_rows(data)
            self._loaded_file = f
            self._log_src = f
            self._ui_state["msg"] = ("โหลดแล้ว: " + os.path.basename(f), "#080")
        except Exception as exc:
            messagebox.showerror(APP_TITLE, "โหลดไฟล์ไม่สำเร็จ:\n%s" % exc)

    def _load_conf(self):
        if os.path.isfile(CONF):
            try:
                with open(CONF, encoding="utf-8") as fh:
                    data = json.load(fh)
                if isinstance(data, list) and data:
                    self._load_rows(data)
                elif isinstance(data, dict):
                    if isinstance(data.get("rows"), list):
                        self._load_rows(data["rows"])
                    self._log_enabled = bool(data.get("log_enabled", True))
                    hp = data.get("hot_profile_dir")
                    if isinstance(hp, str) and hp and os.path.isdir(hp):
                        self._hp_dir = hp
                    self._backup_enabled = bool(data.get("backup_enabled", True))
                    try:
                        self._backup_days = max(1, min(90, int(data.get("backup_days", BACKUP_KEEP_DAYS))))
                    except (TypeError, ValueError):
                        self._backup_days = BACKUP_KEEP_DAYS
                    if data.get("lang") in ("th", "en"):
                        self._lang = data["lang"]
                    # ค่าการเล่น + ตารางเวลา (v1.19) — คืนค่าให้แถบเครื่องมือ/ตั้งค่าเดิม
                    try:
                        sp = float(data.get("speed", 1))
                        if 0.1 <= sp <= 10:
                            self.cmb_speed.set("%g" % sp)
                    except (TypeError, ValueError):
                        pass
                    try:
                        lp = max(0, int(data.get("loops", 1)))
                        self.ent_loops.delete(0, "end")
                        self.ent_loops.insert(0, str(lp))
                    except (TypeError, ValueError):
                        pass
                    self.chk_forever.set(bool(data.get("forever", False)))
                    self.chk_restore.set(bool(data.get("restore", False)))
                    self.chk_shuffle.set(bool(data.get("shuffle", False)))
                    try:
                        pc = max(5, min(100, int(data.get("pct", 100))))
                        self.ent_pct.delete(0, "end")
                        self.ent_pct.insert(0, str(pc))
                    except (TypeError, ValueError):
                        pass
                    sm = data.get("sched_mode")
                    if sm in ("interval", "daily"):
                        self._sched_mode = sm
                        try:
                            self._sched_every = max(1, min(1440, int(data.get("sched_every", 10))))
                        except (TypeError, ValueError):
                            self._sched_every = 10
                        at = data.get("sched_at", "")
                        if re_match_hhmm(at):
                            self._sched_at = at
                        self._sched_last = ""
                        if sm == "interval":
                            self._sched_next = time.time() + self._sched_every * 60
            except Exception:
                pass

    # -------------------------------------------- โปรไฟล์: เก็บ/โหลดไฟล์ -----
    def _load_profiles(self):
        if os.path.isfile(PROFILES):
            try:
                with open(PROFILES, encoding="utf-8") as fh:
                    data = json.load(fh)
                if isinstance(data, dict) and data:
                    self._profiles = {k: v for k, v in data.items() if isinstance(v, list)}
            except Exception:
                pass
        if not self._profiles:
            # ย้ายงานที่โหลดไว้แล้ว (macro_conf) เป็นโปรไฟล์แรกให้เลย
            self._profiles = {DEFAULT_PROFILE: self._serialize()}

    def _save_profiles(self):
        try:
            self._profiles[self._active_profile] = self._serialize()
            with open(PROFILES, "w", encoding="utf-8") as fh:
                json.dump(self._profiles, fh, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def _save_conf(self):
        try:
            with open(CONF, "w", encoding="utf-8") as fh:
                json.dump({"rows": self._serialize(),
                           "log_enabled": self._log_enabled,
                           "hot_profile_dir": self._hp_dir,
                           "backup_enabled": self._backup_enabled,
                           "backup_days": self._backup_days,
                           "lang": self._lang,
                           # ค่าการเล่น + ตารางเวลา (v1.19) — จำไว้เปิดครั้งหน้า
                           "speed": self.cmb_speed.get(),
                           "loops": self.ent_loops.get(),
                           "forever": self.chk_forever.get(),
                           "restore": self.chk_restore.get(),
                           "shuffle": self.chk_shuffle.get(),
                           "pct": self._play_options(),
                           "sched_mode": getattr(self, "_sched_mode", "") or "",
                           "sched_every": getattr(self, "_sched_every", 10),
                           "sched_at": getattr(self, "_sched_at", "") or ""},
                          fh, ensure_ascii=False, indent=2)
        except OSError:
            pass

    # --------------------------------- export/import การตั้งค่า (v1.12) ------
    def export_settings(self):
        """ส่งออกการตั้งค่าทั้งหมดเป็นไฟล์เดียว: งานปัจจุบัน + โปรไฟล์ทุกชุด +
        log_enabled + hot_profile_dir — ใช้ย้ายเครื่อง/สำรองข้อมูล"""
        f = filedialog.asksaveasfilename(defaultextension=".json",
                                         filetypes=[("Macro settings", "*.json")],
                                         initialfile="macro_settings.json")
        if not f:
            return
        data = {"kind": "automousemacro-settings", "version": 1,
                "rows": self._serialize(),
                "profiles": self._profiles,
                "active_profile": self._active_profile,
                "log_enabled": self._log_enabled,
                "hot_profile_dir": self._hp_dir}
        try:
            with open(f, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
            self._ui_state["msg"] = ("ส่งออกการตั้งค่าแล้ว: " + os.path.basename(f), "#080")
        except OSError as exc:
            messagebox.showerror(APP_TITLE, "ส่งออกไม่สำเร็จ:\n%s" % exc)

    def import_settings(self):
        """นำเข้าไฟล์ที่ Export ไว้ — ประเมินผลก่อน แล้วถามยืนยัน (แทนที่ทั้งหมด)"""
        f = filedialog.askopenfilename(filetypes=[("Macro settings", "*.json"),
                                                  ("All files", "*.*")])
        if not f or not os.path.isfile(f):
            return
        try:
            with open(f, encoding="utf-8") as fh:
                data = json.load(fh)
            if not isinstance(data, dict) or data.get("kind") != "automousemacro-settings":
                raise ValueError("ไฟล์นี้ไม่ใช่ไฟล์การตั้งค่าของโปรแกรม")
            n_prof = len(data.get("profiles") or {})
            n_rows = len(data.get("rows") or [])
            if not messagebox.askyesno(APP_TITLE,
                    "นำเข้าการตั้งค่า?\n"
                    "- งานปัจจุบัน: %d แถว\n- โปรไฟล์: %d ชุด (แทนที่ทั้งหมด)\n"
                    "- โฟลเดอร์ hot-profile: %s\n\nดำเนินการต่อ?"
                    % (n_rows, n_prof, data.get("hot_profile_dir") or "ไม่ตั้ง")):
                return
            self._stop_all_silent()
            self._profiles = {k: v for k, v in (data.get("profiles") or {}).items()
                              if isinstance(v, list)}
            if not self._profiles:
                self._profiles = {DEFAULT_PROFILE: []}
            self._active_profile = (data.get("active_profile")
                                    if data.get("active_profile") in self._profiles
                                    else next(iter(self._profiles)))
            self._load_rows(data.get("rows") or [])
            self._log_enabled = bool(data.get("log_enabled", True))
            hp = data.get("hot_profile_dir")
            self._hp_dir = hp if (isinstance(hp, str) and hp and os.path.isdir(hp)) else None
            self._refresh_profile_ui()
            self._save_profiles()
            self._save_conf()
            self._ui_state["msg"] = ("นำเข้าการตั้งค่าแล้ว: " + os.path.basename(f), "#080")
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            messagebox.showerror(APP_TITLE, "นำเข้าไม่สำเร็จ:\n%s" % exc)

    def _stop_all_silent(self):
        """หยุดเล่น/อัดแบบเงียบ (ใช้ก่อน import แทนที่ข้อมูล)"""
        self.stop_all(silent=True)

    # ------------------------------------------------------------- dialogs ---
    # ------------------------------------------- record wizard (v1.10) ------
    def record_wizard(self):
        """หน้าต่าง Wizard 4 ขั้นตอน: อัด → ตรวจรายการ → ทดลองเล่น → บันทึกไฟล์
        ใช้ _pending_rows ชุดเดียวกับ RECORD ปกติ — เห็นรายการสดขณะอัด"""
        win = tk.Toplevel(self.root)
        win.title("Record Wizard — อัด → ตรวจ → ทดลองเล่น → บันทึก")
        win.geometry("780x520")
        tk.Label(win, text="1) กด ● เริ่มอัด   2) ตรวจรายการด้านล่าง   "
                 "3) ▶ ทดลองเล่น   4) 💾 บันทึกไฟล์",
                 fg="#555").pack(anchor="w", padx=12, pady=(10, 2))
        var_state = tk.StringVar(value="พร้อมเริ่ม — กด ● เริ่มอัด")
        tk.Label(win, textvariable=var_state, font=("Segoe UI", 10, "bold"),
                 fg="#080").pack(anchor="w", padx=12)
        cnt = tk.Label(win, text="0 เหตุการณ์", font=("Consolas", 10), fg="#06c")
        cnt.pack(anchor="w", padx=12)
        tr = ttk.Treeview(win, columns=("num", "button", "additional", "delay"),
                          show="headings", height=14)
        for c, w, t, a in (("num", 46, "#", "e"), ("button", 150, "Action", "w"),
                           ("additional", 330, "Additional", "w"),
                           ("delay", 90, "วินาที", "e")):
            tr.heading(c, text=t)
            tr.column(c, width=w, anchor=a)
        tr.pack(fill="both", expand=True, padx=12, pady=6)
        bar = tk.Frame(win)
        bar.pack(fill="x", padx=12, pady=(0, 10))

        def do_rec():
            self.toggle_record()                       # ใช้กลไก RECORD เดิมทั้งหมด
            var_state.set("กำลังอัด... ทำตามที่ต้องการแล้วกด ■ หยุดอัด" if self.recording
                          else "อัดเสร็จ — ตรวจรายการ แล้วทดลองเล่น/บันทึกได้เลย")

        btn_rec = tk.Button(bar, text="● เริ่มอัด", width=12, command=do_rec)
        btn_rec.pack(side="left", padx=(0, 6))

        def do_try():
            if not self._pending_rows and not self.tree.get_children():
                messagebox.showinfo(APP_TITLE, "ยังไม่มีรายการ — กด ● เริ่มอัดก่อน", parent=win)
                return
            var_state.set("กำลังทดลองเล่น... (F8 หยุดได้ทุกที่)")
            self.start_play()

        tk.Button(bar, text="▶ ทดลองเล่น", width=12, command=do_try).pack(side="left", padx=6)

        def do_save():
            rows = list(self._pending_rows) if self._pending_rows else self._serialize()
            if not rows:
                messagebox.showinfo(APP_TITLE, "ยังไม่มีรายการให้บันทึก", parent=win)
                return
            f = filedialog.asksaveasfilename(parent=win, defaultextension=".json",
                                             filetypes=[("Macro script", "*.json")],
                                             initialfile=wizard_filename())
            if not f:
                return
            with open(f, "w", encoding="utf-8") as fh:
                json.dump(rows, fh, ensure_ascii=False, indent=2)
            self._loaded_file = f
            self._log_src = f
            var_state.set("บันทึกแล้ว: " + os.path.basename(f) +
                          "  — โหลดกลับด้วยเมนู 📂 Load หรือรันผ่าน CLI ได้เลย")
            self._ui_state["msg"] = ("Wizard บันทึกสคริปต์แล้ว: " + os.path.basename(f), "#080")

        tk.Button(bar, text="💾 บันทึกไฟล์", width=14, command=do_save).pack(side="left", padx=6)
        tk.Button(bar, text="ปิด", width=8, command=win.destroy).pack(side="right")

        def refresh():
            try:
                if not win.winfo_exists():
                    return
            except tk.TclError:
                return
            vals = self._pending_rows
            if len(tr.get_children()) != len(vals):    # รีวาดเฉพาะจำนวนที่เปลี่ยน
                tr.delete(*tr.get_children())
                for i, r in enumerate(vals, 1):
                    tr.insert("", "end", values=(
                        i, r["button"], r["additional"] or "",
                        "%g" % delay_seconds(r["mins"], r["secs"])))
            cnt.config(text="%d เหตุการณ์" % len(vals))
            btn_rec.config(text="■ หยุดอัด" if self.recording else "● เริ่มอัด",
                           fg="#b00" if self.recording else "#080")
            win.after(250, refresh)

        refresh()

    # ---------------------------------------------- สถิติการเล่น (v1.11) -----
    def view_stats(self):
        """หน้าต่างสรุปสถิติการเล่นจาก log ทุกวัน (v1.11)"""
        s = log_stats_summary()
        win = tk.Toplevel(self.root)
        win.title("สถิติการเล่น (จาก log)")
        win.resizable(False, False)
        tk.Label(win, text="📊 สถิติการเล่นย้อนหลัง (รวมทุกวัน)",
                 font=("Segoe UI", 12, "bold")).pack(padx=24, pady=(16, 8))
        rows = [("ไฟล์ log (วัน)", "%d วัน" % s["files"]),
                ("เริ่มเล่นทั้งหมด", "%d ครั้ง" % s["runs"]),
                ("เหตุการณ์ที่ทำ (STEP)", "%d ครั้ง" % s["steps"]),
                ("ถูกหยุดโดยผู้ใช้", "%d ครั้ง" % s["stops"]),
                ("รีสตาร์ตโดย watchdog", "%d ครั้ง" % s["restarts"])]
        frm = tk.Frame(win)
        frm.pack(padx=24)
        for i, (name, val) in enumerate(rows):
            tk.Label(frm, text=name + ":").grid(row=i, column=0, sticky="e", padx=4, pady=3)
            tk.Label(frm, text=val, font=("Consolas", 10, "bold"), fg="#06c").grid(
                row=i, column=1, sticky="w", padx=4, pady=3)
        slow = s["slowest"]
        tk.Label(win, justify="left", fg="#555", text=(
            "แถวที่ใช้เวลานานสุดเท่าที่ log มี:\n" + (slow[0] if slow else "(ยังไม่มีข้อมูล — เล่นสคริปต์ก่อน)")
        ).replace("  <-", "\n   <-")).pack(padx=24, pady=(10, 4), anchor="w")
        # v1.18: สถิติราย Action — Action ไหนกินเวลารวมมากสุด (หา bottleneck)
        tops = top_actions_summary(s, limit=5)
        if tops:
            tk.Label(win, text="⏱ Action ที่ใช้เวลารวมมากสุด (5 อันดับ)").pack(
                padx=24, pady=(8, 2), anchor="w")
            af = tk.Frame(win)
            af.pack(padx=24, anchor="w")
            for j, (act, cnt, tot, mx) in enumerate(tops):
                tk.Label(af, text="%d. %s" % (j + 1, act)).grid(
                    row=j, column=0, sticky="w", padx=(0, 12), pady=1)
                tk.Label(af, text="%d ครั้ง · รวม %.1f วิ · สูงสุด %.1f วิ" % (cnt, tot, mx),
                         font=("Consolas", 9), fg="#06c").grid(
                    row=j, column=1, sticky="w", pady=1)
        # สรุปการใช้งานรวม (v1.15): กราฟรายเดือน — ยอดสะสมทั้งหมดตั้งแต่ติดตั้ง
        monthly = log_monthly_series()
        if len(monthly) >= 2:
            tk.Label(win, text="ยอดรวมรายเดือน (%d เดือนล่าสุด — เขียวเข้ม = เริ่มเล่น, เขียวอ่อน = เหตุการณ์)"
                     % len(monthly)).pack(pady=(10, 2))
            mw, mh = 620, 130
            mcvs = tk.Canvas(win, width=mw, height=mh, bg="#fafafa",
                             highlightthickness=1, highlightbackground="#ddd")
            mcvs.pack(padx=24, pady=(0, 4))
            mruns = max(x["runs"] for x in monthly) or 1
            msteps = max(x["steps"] for x in monthly) or 1
            n = len(monthly)
            gap, bw = 8, max(10, min(34, (mw - 40) // n - 8))
            x0 = (mw - (n * (bw * 2 + gap) - gap)) // 2
            base_y = mh - 24
            mcvs.create_line(20, base_y, mw - 20, base_y, fill="#bbb")
            for i, m in enumerate(monthly):
                cx = x0 + i * (bw * 2 + gap)
                hs = int((base_y - 26) * m["steps"] / msteps)
                hr = int((base_y - 26) * m["runs"] / mruns)
                mcvs.create_rectangle(cx, base_y - hs, cx + bw, base_y,
                                      fill="#a7d8b0", outline="")
                mcvs.create_rectangle(cx + bw, base_y - hr, cx + bw * 2, base_y,
                                      fill="#1f7a34", outline="")
                if m["steps"]:
                    mcvs.create_text(cx + bw, base_y - hs - 8, text=str(m["steps"]),
                                     font=("Segoe UI", 8), fill="#555")
                mcvs.create_text(cx + bw, mh - 10, text=m["month"],
                                 font=("Segoe UI", 8), fill="#777")
        # กราฟแท่งรายวัน (v1.12): เหตุการณ์ (STEP) ต่อวัน + จำนวนครั้งที่เริ่มเล่น
        series = log_daily_series()
        if series:
            tk.Label(win, text="เหตุการณ์ต่อวัน (%d วันล่าสุด — แท่งเขียวเข้ม = เริ่มเล่น, เขียวอ่อน = เหตุการณ์)"
                     % len(series)).pack(pady=(10, 2))
            cw, chh = 620, 150
            cvs = tk.Canvas(win, width=cw, height=chh, bg="#fafafa",
                            highlightthickness=1, highlightbackground="#ddd")
            cvs.pack(padx=24, pady=(0, 4))
            max_steps = max(x["steps"] for x in series) or 1
            max_runs = max(x["runs"] for x in series) or 1
            n = len(series)
            gap, bw = 6, max(8, min(28, (cw - 40) // n - 6))
            x0 = (cw - (n * (bw * 2 + gap) - gap)) // 2
            base_y = chh - 22
            cvs.create_line(20, base_y, cw - 20, base_y, fill="#bbb")
            for i, d in enumerate(series):
                cx = x0 + i * (bw * 2 + gap)
                hs = int((base_y - 26) * d["steps"] / max_steps)
                hr = int((base_y - 26) * d["runs"] / max_runs)
                cvs.create_rectangle(cx, base_y - hs, cx + bw, base_y,
                                     fill="#a7d8b0", outline="")
                cvs.create_rectangle(cx + bw, base_y - hr, cx + bw * 2, base_y,
                                     fill="#1f7a34", outline="")
                if d["steps"]:
                    cvs.create_text(cx + bw, base_y - hs - 8, text=str(d["steps"]),
                                    font=("Segoe UI", 8), fill="#555")
                cvs.create_text(cx + bw, chh - 9, text=d["day"][5:],
                                font=("Segoe UI", 8), fill="#777")
        tk.Button(win, text="เปิด Log viewer", command=self.view_log).pack(pady=(2, 2))
        tk.Button(win, text="ปิด", width=8, command=win.destroy).pack(pady=(4, 14))

    # ------------------------------------------------ self-check (v1.11) -----
    def _on_close_backup(self, base_dir):
        """เขียน backup ตอนปิดโปรแกรม (แยกเมธอดเพื่อทดสอบได้) — คืนพาธหรือ None"""
        if not self._backup_enabled:
            return None
        return backup_snapshot(base_dir,
                               {"kind": "automousemacro-settings", "version": 1,
                                "rows": self._serialize(),
                                "profiles": self._profiles,
                                "active_profile": self._active_profile,
                                "log_enabled": self._log_enabled,
                                "hot_profile_dir": self._hp_dir},
                               keep_days=self._backup_days)

    # ------------------------------------------------ i18n สลับภาษา (v1.14) --
    def _apply_language(self):
        """ปรับข้อความปุ่ม/สถานะตามภาษาที่เลือก (เรียกทันทีจาก Settings — ไม่ต้องรีเปิด)"""
        self.chk_forever_btn.config(text=self._t("forever"))
        self.chk_restore_btn.config(text=self._t("restore"))
        self.chk_shuffle_btn.config(text=self._t("shuffle"))
        self.lbl_pct.config(text=self._t("pct"))
        self.lbl_speed.config(text=self._t("speed"))
        self.lbl_loops.config(text=self._t("loops"))
        self.lbl_loops_note.config(text=self._t("loops_note"))
        self.btn_rec.config(text=self._t("record"))
        self.tree.heading("button", text=self._t("col_action"))   # หัวตาราง (v1.15)
        if not self.running:
            self._ui_state["msg"] = ("ภาษา: ไทย" if self._lang == "th"
                                     else "Language: English", "#080")

    def _self_test_actions(self):
        """🧪 ทดสอบระบบจริง (v1.12): ขยับเมาส์เป็นสามเหลี่ยมแล้วคืนจุดเดิม + บี๊บ 2 ครั้ง
        คืนตำแหน่งเมาส์ตอนเริ่ม (แยกออกมาจาก dialog เพื่อทดสอบได้)"""
        cur = self.mouse_ctl.position
        self.mouse_ctl.position = (cur[0] + 120, cur[1])
        time.sleep(0.25)
        self.mouse_ctl.position = (cur[0] + 120, cur[1] + 60)
        time.sleep(0.25)
        self.mouse_ctl.position = cur
        self.root.bell()
        self.root.after(250, self.root.bell)
        return cur

    def _self_check(self):
        """ตรวจสุขภาพระบบเมื่อเปิดโปรแกรม — ผลเก็บใน dict แสดงใน Settings"""
        chk = {}
        chk["pynput"] = True                                   # import ได้ = ผ่านแน่ (ถึงรันได้)
        try:
            chk["mouse"] = self.mouse_ctl.position is not None
        except Exception:
            chk["mouse"] = False
        try:
            chk["hotkey"] = bool(self._gk and self._gk.is_alive())
        except Exception:
            chk["hotkey"] = False
        chk["opencv"] = HAS_CV
        try:
            import ctypes
            chk["admin"] = bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            chk["admin"] = False
        try:
            chk["conf_writable"] = os.access(
                os.path.dirname(os.path.abspath(__file__)), os.W_OK)
        except Exception:
            chk["conf_writable"] = False
        self._checks = chk
        return chk

    def self_check_text(self):
        """แปลงผล self-check เป็นข้อความ 4 บรรทัด (ทดสอบได้)"""
        c = getattr(self, "_checks", {})
        return [
            ("เมาส์/คีย์บอร์ด (pynput)", c.get("mouse"),
             "พร้อม" if c.get("mouse") else "ควบคุมไม่ได้ — ลองรันใหม่"),
            ("Global hotkey (F1-F10)", c.get("hotkey"),
             "ทำงาน" if c.get("hotkey") else "ไม่ทำงาน — ใช้คีย์เมื่อโฟกัสหน้าต่าง"),
            ("Image Click (OpenCV)", c.get("opencv"),
             "พร้อม" if c.get("opencv") else "ไม่มี — pip install opencv-python Pillow"),
            ("สิทธิ์ Admin", c.get("admin"),
             "มี (คลิกโปรแกรมที่ต้องสิทธิ์ได้)" if c.get("admin")
             else "ไม่มี — ถ้าคลิกโปรแกรมอื่นไม่เข้า ลอง Run as Administrator"),
        ]

    # -------------------------------------------------- log viewer (v1.9) ----
    def view_log(self):
        """เปิดหน้าต่างอ่าน log การเล่นย้อนหลัง — เลือกดูไฟล์รายวันได้"""
        files = sorted(glob.glob(os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "macro_log_*.txt")), reverse=True)
        win = tk.Toplevel(self.root)
        win.title("Log การเล่น")
        win.geometry("860x520")
        bar = tk.Frame(win)
        bar.pack(fill="x", padx=8, pady=(8, 2))
        tk.Label(bar, text="ไฟล์:").pack(side="left")
        cmb = ttk.Combobox(bar, state="readonly", width=40,
                           values=[os.path.basename(f) for f in files])
        if files:
            cmb.set(os.path.basename(files[0]))       # วันนี้ (ไฟล์ใหม่สุด)
        cmb.pack(side="left", padx=6)
        txt = tk.Text(win, wrap="none", font=("Consolas", 10),
                      bg="#0f172a", fg="#e2e8f0")
        ysb = ttk.Scrollbar(win, orient="vertical", command=txt.yview)
        txt.configure(yscrollcommand=ysb.set)

        def refresh(_e=None):
            txt.delete("1.0", "end")
            f = os.path.join(os.path.dirname(os.path.abspath(__file__)), cmb.get())
            try:
                with open(f, encoding="utf-8", errors="replace") as fh:
                    txt.insert("1.0", fh.read())
            except OSError:
                txt.insert("1.0", "(ยังไม่มี log — เล่นสคริปต์ครั้งแรกแล้วไฟล์จะปรากฏที่นี่)")
            txt.see("end")

        def open_folder():
            d = os.path.dirname(os.path.abspath(__file__))
            if hasattr(os, "startfile"):
                os.startfile(d)

        cmb.bind("<<ComboboxSelected>>", refresh)
        tk.Button(bar, text="รีเฟรช", command=refresh).pack(side="left", padx=2)
        tk.Button(bar, text="เปิดโฟลเดอร์", command=open_folder).pack(side="left", padx=2)
        ysb.pack(side="right", fill="y")
        txt.pack(fill="both", expand=True, padx=(8, 0), pady=(2, 8))
        refresh()

    # ---------------------------------------------- hot-profile (v1.9) ------
    def hot_profile_dialog(self):
        """ตั้งโฟลเดอร์สคริปต์สำหรับ F1–F4: ไฟล์ .json เรียงตามชื่อ ตำแหน่ง 1–4
        กด F1–F4 (ได้แม้ไม่โฟกัส) = โหลดสคริปต์นั้นแล้วเล่นทันที"""
        win = tk.Toplevel(self.root)
        win.title("Hot-profile (F1–F4)")
        win.resizable(False, False)
        tk.Label(win, text="โฟลเดอร์สคริปต์ (.json):",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=16, pady=(14, 2))
        row = tk.Frame(win)
        row.pack(fill="x", padx=16)
        var_dir = tk.StringVar(value=self._hp_dir or "")
        tk.Entry(row, textvariable=var_dir, width=46).pack(side="left")

        def browse():
            d = filedialog.askdirectory(initialdir=var_dir or os.getcwd())
            if d:
                var_dir.set(os.path.normpath(d))

        tk.Button(row, text="เลือก...", command=browse).pack(side="left", padx=4)
        tk.Label(win, justify="left", fg="#555", text=(
            "F1–F4 = โหลดไฟล์ .json ลำดับที่ 1–4 (เรียงตามชื่อไฟล์) แล้วเล่นทันที\n"
            "เช่น ในโฟลเดอร์มี a.json, b.json, c.json → F1=a, F2=b, F3=c\n"
            "เหมาะกับงานที่สลับสคริปต์บ่อย เช่น เกมหลายตัว / งานเอกสารหลายแบบ")).pack(
            anchor="w", padx=16, pady=8)

        def save():
            d = var_dir.get().strip()
            self._hp_dir = d or None
            win.destroy()
            if d:
                self._ui_state["msg"] = ("Hot-profile พร้อม: " + d + "  (F1–F4)", "#080")

        tk.Button(win, text="บันทึก", width=10, command=save).pack(pady=(2, 14))

    def _hot_profile_load(self, n):
        """F(n): โหลดไฟล์ลำดับที่ n จากโฟลเดอร์ hot-profile แล้วเล่นทันที
        (ถูกเรียกจาก listener thread → ห้ามแตะ Tk ตรง ๆ ต้อง after(0, ...))"""
        def say(text):
            self.root.after(0, lambda: self._ui_state.__setitem__("msg", (text, "#a60")))

        if not self._hp_dir:
            say("ยังไม่ได้ตั้งโฟลเดอร์ Hot-profile — เมนู ⚡ Hot-profile")
            return
        files = sorted(glob.glob(os.path.join(self._hp_dir, "*.json")))
        if not files:
            say("โฟลเดอร์ Hot-profile ไม่มีไฟล์ .json")
            return
        if n > len(files):
            say("F%d: มีสคริปต์แค่ %d ไฟล์" % (n, len(files)))
            return
        f = files[n - 1]

        def do_load():
            try:
                with open(f, encoding="utf-8") as fh:
                    data = json.load(fh)
                if not isinstance(data, list):
                    raise ValueError("รูปแบบไฟล์ไม่ถูกต้อง")
                self._load_rows(data)
                self._loaded_file = f
                self._log_src = f
                self._ui_state["msg"] = ("F%d → %s — เริ่มเล่น" % (n, os.path.basename(f)), "#080")
                self._start_player(False)
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                self._ui_state["msg"] = ("F%d โหลดไม่สำเร็จ: %s" % (n, exc), "#a60")

        self.root.after(0, do_load)

    def settings_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.resizable(False, False)
        tk.Label(win, text=self._t("hotkeys_title"),
                 font=("Segoe UI", 11, "bold")).pack(padx=20, pady=(14, 6))
        frm = tk.Frame(win)
        frm.pack(padx=20, pady=4)
        rows = [(self._t("sc_play"), "F6"), (self._t("sc_stop"), "F8"),
                (self._t("sc_rec"), "F9"), (self._t("sc_forever"), "F10"),
                (self._t("sc_hp"), "F1-F4"),
                (self._t("sc_del"), "Delete"), (self._t("sc_edit"), "Double-click"),
                (self._t("sc_speed"), self._t("sc_speed") if False else
                 ("แถบปุ่มด้านล่าง" if self._lang == "th" else "bottom bar")),
                (self._t("sc_rand"), "Secs = 1-3")]
        for i, (name, key) in enumerate(rows):
            tk.Label(frm, text=name + ":").grid(row=i, column=0, sticky="e", padx=4, pady=3)
            tk.Label(frm, text=key, font=("Consolas", 10, "bold"), fg="#06c").grid(
                row=i, column=1, sticky="w", padx=4, pady=3)
        gk_state = self._t("gk_ok") if self._gk else self._t("gk_bad")
        tk.Label(win, text="Global Hotkey: " + gk_state,
                 fg="#080" if self._gk else "#a60").pack(pady=(10, 0))
        tk.Label(win, text=self._t("sc_check"),
                 font=("Segoe UI", 9, "bold")).pack(pady=(10, 2))
        for name, ok, note in self.self_check_text():
            tk.Label(win, text="%s %s — %s" % ("✅" if ok else "⚠️", name, note),
                     fg="#080" if ok else "#a60", justify="left").pack(anchor="w", padx=20)
        tk.Label(win, text="Image Click: " + ("พร้อมใช้ ✅" if HAS_CV else
                 "ยังไม่พร้อม — ติดตั้งด้วย: pip install opencv-python Pillow"),
                 fg="#080" if HAS_CV else "#a60").pack()
        self.var_log = tk.BooleanVar(value=self._log_enabled)
        tk.Checkbutton(win, text=self._t("log_label"),
                       variable=self.var_log).pack(pady=(10, 0))
        # ภาษา (v1.14) + backup ตั้งค่าได้ (v1.14)
        langbar = tk.Frame(win)
        langbar.pack(pady=(12, 0))
        tk.Label(langbar, text=self._t("language"), font=("Segoe UI", 9, "bold")).pack(side="left")
        self.cmb_lang = ttk.Combobox(langbar, width=10, state="readonly",
                                     values=["ไทย (Thai)", "English"])
        self.cmb_lang.set("ไทย (Thai)" if self._lang == "th" else "English")
        self.cmb_lang.pack(side="left", padx=6)
        self.var_backup = tk.BooleanVar(value=self._backup_enabled)
        self.spin_days = tk.Spinbox(win, from_=1, to=90, width=4)
        self.spin_days.delete(0, "end")
        self.spin_days.insert(0, str(self._backup_days))
        tk.Checkbutton(win, text=self._t("backup_label"),
                       variable=self.var_backup).pack(pady=(10, 0))
        daybar = tk.Frame(win)
        daybar.pack()
        self.spin_days.pack(side="left")
        tk.Label(daybar, text=self._t("days"), fg="#666").pack(side="left", padx=(4, 0))
        tk.Button(win, text=self._t("open_log_folder"), width=14,
                  command=lambda: os.startfile(os.path.dirname(os.path.abspath(__file__)))
                  if hasattr(os, "startfile") else None).pack(pady=(4, 0))
        # 🧪 ทดสอบระบบจริง (v1.12): ขยับเมาส์ไปจุดสังเกต → คืนจุดเดิม → บี๊บ 2 ครั้ง
        def self_test():
            try:
                self._self_test_actions()
                res.config(text=self._t("selftest_ok"), fg="#080")
            except Exception as exc:
                res.config(text="🧪 ทดสอบล้มเหลว: %s" % exc, fg="#b00")

        tk.Button(win, text=self._t("selftest_btn"), width=30,
                  command=self_test).pack(pady=(10, 0))
        res = tk.Label(win, text="", fg="#080", justify="left", wraplength=380)
        res.pack(padx=20)
        # Export/Import การตั้งค่า (v1.12)
        eib = tk.Frame(win)
        eib.pack(pady=(10, 0))
        tk.Button(eib, text=self._t("export_btn"), width=18,
                  command=self.export_settings).pack(side="left", padx=4)
        tk.Button(eib, text=self._t("import_btn"), width=18,
                  command=self.import_settings).pack(side="left", padx=4)
        tk.Label(win, text=self._t("export_note"), fg="#888",
                 justify="left", wraplength=400).pack(padx=20, pady=(4, 0))
        tk.Button(win, text=self._t("save"), width=8,
                  command=lambda: self._settings_save(win)).pack(pady=(8, 14))

    def _settings_save(self, win):
        """กดบันทึกใน Settings — เก็บ log/backup/ภาษา แล้วปรับ UI ทันที"""
        self._log_enabled = self.var_log.get()
        self._backup_enabled = self.var_backup.get()
        try:
            self._backup_days = max(1, min(90, int(self.spin_days.get())))
        except ValueError:
            self._backup_days = BACKUP_KEEP_DAYS
        old_lang = self._lang
        self._lang = "th" if self.cmb_lang.get().startswith("ไทย") else "en"
        if self._lang != old_lang:
            self._apply_language()
        win.destroy()

    def about(self):
        messagebox.showinfo("About",
                            APP_TITLE + "\n\nโปรแกรมสั่งงานเมาส์/คีย์บอร์ดอัตโนมัติ\n"
                            "Python " + sys.version.split()[0] + "  •  Tkinter + pynput\n\n"            "F6 เล่น | F8 หยุด | F9 บันทึก | F10 วนซ้ำ | F1-F4 hot-profile\n"
            "(คีย์ลัดกดได้แม้ไม่โฟกัสหน้าต่าง)")

    def help_dialog(self):
        """Help ฉบับเต็ม (v1.13) — หน้าต่างเลื่อนดูได้ ครอบทุกฟีเจอร์ + ปุ่มเปิดคู่มือ"""
        win = tk.Toplevel(self.root)
        win.title("Help — วิธีใช้งานฉบับเต็ม")
        win.geometry("640x560")
        txt = tk.Text(win, wrap="word", font=("Segoe UI", 10), padx=14, pady=10)
        ysb = ttk.Scrollbar(win, orient="vertical", command=txt.yview)
        txt.configure(yscrollcommand=ysb.set)
        ysb.pack(side="right", fill="y")
        txt.pack(fill="both", expand=True)
        txt.insert("1.0", """🖱️ Auto Mouse & Keyboard Macro — วิธีใช้งาน

▪ เริ่มต้น 4 ขั้น
1) กด RECORD (F9) แล้วคลิก/พิมพ์ตามจริง — โปรแกรมจดทุกเหตุการณ์ + เวลาหน่วงให้เอง
2) แก้รายการในตาราง: ดับเบิลคลิกช่อง X/Y = จับพิกัดใหม่ (นับถอยหลัง 3 วิ)
   ดับเบิลคลิกช่องอื่น = แก้ Action/คีย์/เวลา/Repeat, คลิกช่องแรก = เปิด-ปิดแถว
3) กด START (F6) เล่นรอบเดียว, REPEAT เล่นวนซ้ำ, STOP (F8) หยุดทันที
4) Save เก็บเป็นไฟล์ .json เปิดมาเล่นซ้ำวันไหนก็ได้

▪ ปุ่มลัด (กดได้แม้ไม่โฟกัสหน้าต่าง)
F6 เล่น • F8 หยุด • F9 อัด • F10 วนไม่จำกัด • F1-F4 โหลดสคริปต์จากโฟลเดอร์ Hot-profile

▪ Action ในตาราง (คอลัมน์ Button + Additional)
- คลิก: Left/Middle/Right Click (+ Down/Up แยกกด-ปล่อย), Double Click, Ctrl/Shift/Alt+Click
- Scroll Up/Down — ใส่จำนวนจังหวะใน Additional
- Move Mouse / Move Mouse by Offset, Save/Restore Cursor
- Press/Release/Tap Key — คีย์พิเศษ เช่น enter, esc, ctrl, f1, pgup
- Type Text — พิมพ์ข้อความไทย/อังกฤษ | Launch App — เปิดโปรแกรม/เว็บ
- Image Click / Wait for Image — คลิกตามภาพ (ต้องมี opencv-python + Pillow)
   Additional: ไฟล์.png หรือ ไฟล์.png@x,y,กว้าง,สูง (กรอบค้นหา) หรือ ...#90 (ความมั่นใจ %)
   ปุ่ม 📸 บนแถบเครื่องมือ = ลากกรอบจับภาพจากหน้าจอเป็น .png ได้เลย
- Beep — เสียงเตือน

▪ ตัวเลือกการเล่น (แถบปุ่มล่าง)
- Secs ใส่สุ่มได้ เช่น 1-3 = สุ่มดีเลย์ 1-3 วิ | ความเร็ว 0.25×-4× | รอบ (0=ไม่จำกัด)
- คืนเมาส์จุดเดิม | สุ่มลำดับ (shuffle) | สัดส่วนแถว % (สุ่มเลือกเล่นบางส่วนทุกรอบ)

▪ เมนูและเครื่องมือ
- 🧙 Wizard — อัด → ตรวจรายการ → ทดลองเล่น → บันทึก จบในหน้าต่างเดียว
- 📝 Log — ดู log การเล่นย้อนหลัง (macro_log_วันที่.txt) | 📊 Stats — สรุปสถิติ + กราฟรายวัน
- ⚡ Hot-profile — ตั้งโฟลเดอร์สคริปต์ แล้วกด F1-F4 โหลด+เล่นทันที
- ⏰ เล่นอัตโนมัติ — ทุก N นาที หรือทุกวัน HH:MM | แถบโปรไฟล์ — เก็บหลายสคริปต์สลับใช้
- ⚙️ Settings — self-check ระบบ, ปุ่ม 🧪 ทดสอบจริง, Export/Import การตั้งค่าย้ายเครื่อง
- Backup — ปิดโปรแกรมทุกครั้งจะสำรองการตั้งค่าอัตโนมัติใน backups/ (เก็บย้อนหลัง 7 วัน)

▪ CLI (รันโดยไม่เปิดหน้าต่าง — เหมาะกับ Task Scheduler)
py auto_macro.py script.json [--loop] [--loops N] [--speed 2] [--shuffle] [--rows-pct 50]
                [--watchdog วินาที] [--stop-file พาธ] [--no-log]
หยุด: F8/Esc (ทุกที่), Esc/q ในหน้าต่างนั้น, Ctrl+C หรือสร้างไฟล์ตาม --stop-file

หมายเหตุ: Secs = เวลารอก่อนทำคำสั่งในแถวนั้น, Repeat = จำนวนครั้งที่ทำซ้ำ
""")
        txt.config(state="disabled")
        bar = tk.Frame(win)
        bar.pack(fill="x", pady=(0, 10))

        def open_tutorial():
            p = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "docs", "TUTORIAL.html")
            if os.path.isfile(p) and hasattr(os, "startfile"):
                os.startfile(p)
            else:
                messagebox.showinfo(APP_TITLE,
                    "ไม่พบไฟล์คู่มือ — เปิดจาก GitHub แทน:\ndocs/TUTORIAL.html")

        tk.Button(bar, text="📘 เปิดคู่มือฉบับสมบูรณ์ (TUTORIAL)",
                  command=open_tutorial).pack(side="left", padx=12)
        tk.Button(bar, text="ปิด", width=10,
                  command=win.destroy).pack(side="right", padx=12)

    def _on_close(self):
        self.running = False
        self.recording = False
        # backup อัตโนมัติทุกครั้งที่ปิดโปรแกรม (v1.13) — ปิด/จำนวนวันตั้งได้ใน Settings (v1.14)
        self._on_close_backup(os.path.dirname(os.path.abspath(__file__)))
        if self._gk:
            try:
                self._gk.stop()
            except Exception:
                pass
        try:
            self._sched_stop.set()
        except Exception:
            pass
        self._save_conf()
        self._save_profiles()
        try:
            self._ms_listener.stop()
            self._kb_listener.stop()
        except Exception:
            pass
        self.root.destroy()


# ---------------------------------------------------------------- CLI mode --
def cli_main(argv):
    """เล่นสคริปต์จาก command line โดยไม่เปิด GUI
    ตัวอย่าง:
        py auto_macro.py script.json
        py auto_macro.py script.json --loop --speed 2 --loops 5
    """
    import argparse
    import io
    import sys as _sys
    ap = argparse.ArgumentParser(
        prog="AutoMouseMacro",
        description="เล่นสคริปต์เมาส์/คีย์บอร์ด .json โดยไม่เปิดหน้าต่าง (Ctrl+C หยุด)")
    ap.add_argument("script", help="ไฟล์สคริปต์ .json ที่บันทึกจากโปรแกรม")
    ap.add_argument("--loop", action="store_true", help="เล่นวนซ้ำไม่จำกัด")
    ap.add_argument("--loops", type=int, default=1, help="จำนวนรอบ (ค่าเริ่มต้น 1; 0=ไม่จำกัด)")
    ap.add_argument("--speed", type=float, default=1.0, help="ตัวคูณความเร็ว (ค่าเริ่มต้น 1)")
    ap.add_argument("--no-log", action="store_true",
                    help="ไม่บันทึก log การเล่นลงไฟล์ macro_log_วันที่.txt")
    ap.add_argument("--stop-file", default=None, metavar="PATH",
                    help="ถ้าไฟล์นี้ถูกสร้าง โปรแกรมจะหยุดทันที (ใช้ควบคุมจากภายนอก/ทดสอบ)")
    ap.add_argument("--shuffle", action="store_true",
                    help="สุ่มลำดับแถวทุกรอบ (v1.10)")
    ap.add_argument("--rows-pct", type=int, default=100, metavar="5-100",
                    help="เล่นแค่กี่เปอร์เซ็นต์ของแถว — สุ่มเลือกชุดแถวใหม่ทุกรอบ (v1.10)")
    ap.add_argument("--watchdog", nargs="?", const=3.0, default=0.0, type=float,
                    metavar="วินาที",
                    help="โหมดเฝ้ารีสตาร์ต (v1.10): จบแล้วเริ่มใหม่อัตโนมัติหลังพัก N วิ "
                         "(ค่าเริ่มต้น 3) — หยุดถาวรด้วย F8/Esc/Ctrl+C/stop-file")
    args = ap.parse_args(argv)

    # --no-log เป็นตัวตัดสิน (ไม่ได้ใส่ = ตามค่าเริ่มต้นของโปรแกรม)
    log_enabled = (not args.no_log) and LOG_ENABLED_DEFAULT

    # คอนโซล Windows บางเครื่องเป็น cp1252 — พิมพ์ไทยไม่ได้ ให้ fallback อัตโนมัติ
    # (ถ้า stdout ไม่มี buffer เช่น StringIO ในเทสต์ ก็ข้ามไป ไม่ต้องแทนที่)
    try:
        "ก".encode(_sys.stdout.encoding or "ascii")
    except (UnicodeEncodeError, AttributeError):
        buf = getattr(_sys.stdout, "buffer", None)
        if buf is not None:
            _sys.stdout = io.TextIOWrapper(buf, encoding="utf-8", errors="replace")

    if not os.path.isfile(args.script):
        print("ไม่พบไฟล์สคริปต์:", args.script)
        return 1
    try:
        with open(args.script, encoding="utf-8") as fh:
            rows = json.load(fh)
        if not isinstance(rows, list):
            raise ValueError("ไฟล์ต้องเป็นรายการแถว JSON")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("อ่านไฟล์ไม่สำเร็จ:", exc)
        return 1

    mouse_ctl = MouseController()
    kb_ctl = KbController()
    running = [True]
    pending_keys = []            # คีย์/ปุ่มที่กดค้าง (Press Key / Down) — ปล่อยตอนหยุด
    cli_vars = {}                # ตัวแปรของการเล่น (v1.19) — เริ่มใหม่ทุกครั้งที่เริ่มเล่น
    speed = min(10.0, max(0.1, args.speed))

    def do_step(r):
        btn = r.get("button", "")
        if btn in BTN_TH:
            b, act = BTN_TH[btn]
            btn_obj = getattr(Button, b.lower())
            if str(r.get("x", "")) != "" and str(r.get("y", "")) != "":
                mouse_ctl.position = (int(r["x"]), int(r["y"]))
                time.sleep(0.03)
            if act == "Down":
                mouse_ctl.press(btn_obj)
                pending_keys.append(("m", btn_obj))
            elif act == "Up":
                mouse_ctl.release(btn_obj)
                if ("m", btn_obj) in pending_keys:
                    pending_keys.remove(("m", btn_obj))
            else:
                mouse_ctl.click(btn_obj, 1)
        elif btn in SCROLL_ACTIONS:
            try:
                n = int(str(r.get("additional") or 1))
            except ValueError:
                n = 1
            mouse_ctl.scroll(0, n if btn == "Scroll Up" else -n)
        elif btn in DBL_ACTIONS:
            if str(r.get("x", "")) != "" and str(r.get("y", "")) != "":
                mouse_ctl.position = (int(r["x"]), int(r["y"]))
                time.sleep(0.03)
            mouse_ctl.click(Button.right if "Right" in btn else Button.left, 2)
        elif btn in KEY_ACTIONS:
            combo = parse_key_combo(r.get("additional", ""))     # v1.20.4: Ctrl+W ฯลฯ
            mods, k = combo if combo else ((), parse_key(r.get("additional", "")))
            if k is not None:
                if btn == "Press Key":
                    for m in mods:
                        kb_ctl.press(m)
                        pending_keys.append(("k", m))
                    kb_ctl.press(k)
                    pending_keys.append(("k", k))
                elif btn == "Release Key":
                    kb_ctl.release(k)
                    if ("k", k) in pending_keys:
                        pending_keys.remove(("k", k))
                    for m in reversed(mods):
                        kb_ctl.release(m)
                        if ("k", m) in pending_keys:
                            pending_keys.remove(("k", m))
                else:
                    for m in mods:
                        kb_ctl.press(m)
                        pending_keys.append(("k", m))
                    kb_ctl.tap(k)
                    for m in reversed(mods):
                        kb_ctl.release(m)
                        if ("k", m) in pending_keys:
                            pending_keys.remove(("k", m))
        elif btn == "Type Text":
            for ch in str(r.get("additional") or ""):
                if not running[0]:
                    return
                if ch == "\n":
                    kb_ctl.tap(Key.enter)
                elif not send_unicode_char(ch):          # v1.20.2: ไม่ขึ้นกับ layout
                    kb_ctl.tap(KeyCode.from_char(ch))    # fallback (OS อื่น)
                time.sleep(0.015)                        # v1.20.3: กันแอป busy กลืน burst
        elif btn == WAIT_PIXEL:
            cli_pixel_ready(r)                       # เช็คครั้งเดียว (CLI ไม่รอ — โปรแกรมอื่นคุมเวลาแทน)
        elif btn == "Set Variable":                  # ตัวแปรในสคริปต์ (v1.19)
            if not apply_set_var(cli_vars, r.get("additional", "")):
                print("  Set Variable: รูปแบบไม่ถูก (%s) — ต้องเป็น name = ค่า หรือ name += จำนวน"
                      % (r.get("additional") or ""))
        elif btn == "Set Clipboard":                 # คลิปบอร์ด (v1.20)
            text = str(r.get("additional") or "")
            if text and not clip_set(text):
                print("  ⚠ Set Clipboard: ตั้งคลิปบอร์ดไม่สำเร็จบนระบบนี้")
        elif btn == "Read Clipboard":
            m = re.fullmatch(_VAR_NAME, str(r.get("additional") or "").strip())
            if not m:
                print("  Read Clipboard: พิมพ์ชื่อตัวแปรใน Additional เช่น mytext")
            else:
                got = clip_get()
                if got is None:
                    print("  ⚠ Read Clipboard: อ่านคลิปบอร์ดไม่สำเร็จบนระบบนี้")
                else:
                    cli_vars[m.group(0)] = got
        elif btn == "Beep":
            print("\a", end="", flush=True)
        else:
            # Custom Action plugins (v1.16) — ทำงานใน CLI ด้วย
            mod = cli_plugins.get(btn)
            if mod is not None:
                ctx = {"mouse": mouse_ctl, "kb": kb_ctl,
                       "log": lambda m: log_write("PLUGIN", m, args.script) if log_enabled else None,
                       "cfg": {"lang": "th"},
                       "stop_check": lambda: running[0],              # v1.20
                       "ui": {"msg": lambda text, color="#080": print("  " + str(text)),
                              "beep": lambda: print("\a", end="", flush=True)}}
                try:
                    mod.run(ctx, dict(r))
                except Exception as exc:
                    print("  plugin error (%s): %s" % (btn, exc))
            else:
                # v1.19: เตือนชัด ๆ แทนการข้ามเงียบ ๆ — Image Click/Wait for Image/
                # If Image/Else Image/คลิก+Modifier/Move Mouse/Launch App ยังใช้ GUI เท่านั้น
                print("  ⚠ ข้ามแถว: action '%s' ยังไม่รองรับใน CLI — เปิดใน GUI เพื่อเล่น action นี้" % btn)

    # หยุดด้วย F8/Esc ได้ทุกที่ — ใช้ Listener จับคู่เอง (เหตุผลเดียวกับ GUI v1.8)
    _stop_keys = {keyboard.Key.f8, keyboard.Key.esc}

    def _on_key_stop(key):
        if key in _stop_keys:
            running[0] = False

    try:
        stopper = keyboard.Listener(on_press=_on_key_stop)
        stopper.daemon = True
        stopper.start()
        gk_ok = True
    except Exception:
        gk_ok = False

    # ช่องทางหยุดที่ 2: อ่านคีย์จากคอนโซลโดยตรง (Esc / q / F8) — ไม่พึ่ง keyboard hook
    # (พบว่าบางสภาพแวดล้อม GlobalHotKeys ไม่ยิงแม้กดจริง — ช่องทางนี้ทำให้หยุดได้เสมอ)
    def _console_watcher():
        try:
            import msvcrt
        except ImportError:
            return                      # ไม่ใช่ Windows — ใช้ Ctrl+C แทน
        while running[0]:
            try:
                if not msvcrt.kbhit():
                    time.sleep(0.05)
                    continue
                ch = msvcrt.getwch()
                if ch in ("\x1b", "q", "Q"):
                    running[0] = False
                    return
                if ch in ("\x00", "\xe0"):          # ปุ่มพิเศษ: ตามด้วยรหัสอีกตัว
                    ch2 = msvcrt.getwch()
                    if ch2 in ("B", "b"):           # 'B' = รหัสปุ่ม F8
                        running[0] = False
                        return
            except Exception:
                return

    threading.Thread(target=_console_watcher, daemon=True).start()

    # ช่องทางหยุดที่ 3: --stop-file — ไฟล์ปรากฏ = หยุดทันที (ควบคุมจากโปรแกรมอื่น/ทดสอบ)
    if args.stop_file:
        def _stopfile_watcher():
            while running[0]:
                try:
                    if os.path.isfile(args.stop_file):
                        running[0] = False
                        return
                except Exception:
                    return
                time.sleep(0.05)

        threading.Thread(target=_stopfile_watcher, daemon=True).start()

    print("เล่นสคริปต์: %s (%d แถว)%s%s" % (
        os.path.basename(args.script), len(rows),
        "  •  วนไม่จำกัด" if (args.loop or args.loops == 0) else "",
        "  •  ความเร็ว %gx" % speed))
    if args.shuffle:
        print("  •  สุ่มลำดับแถวทุกรอบ")
    if args.rows_pct != 100:
        print("  •  สัดส่วนแถว %d%% (สุ่มชุดใหม่ทุกรอบ)" % max(5, min(100, args.rows_pct)))
    if args.watchdog > 0:
        print("  •  watchdog: จบแล้วเริ่มใหม่อัตโนมัติหลังพัก %.0f วิ" % args.watchdog)
    if log_enabled:
        log_write("START", "เริ่มเล่น (CLI) ความเร็ว %gx รอบ=%s แถวที่เล่น=%d" %
                  (speed, "ไม่จำกัด" if (args.loop or args.loops == 0) else args.loops,
                   len([r for r in rows if r.get("enabled", True) is not False])),
                  args.script)
    if gk_ok:
        print("หยุด: กด F8 หรือ Esc (ทุกที่), Esc/q ในหน้าต่างนี้, หรือ Ctrl+C")
    else:
        print("หยุด: Esc/q ในหน้าต่างนี้ หรือ Ctrl+C")
    pct = max(5, min(100, args.rows_pct))
    cli_plugins = {n: m for n, m in load_plugins()}    # Custom Actions สำหรับ CLI (v1.16)
    if cli_plugins:
        print("  •  plugins: " + ", ".join(cli_plugins))

    def cli_pixel_ready(r):
        """เช็คสีจุด (x,y) ว่าใกล้เคียงสีเป้าหมาย (ใช้โดย Wait for Pixel Color ใน CLI)"""
        sp = parse_pixel_spec(r.get("additional"))
        if not sp:
            print("  Wait for Pixel Color: รูปแบบ Additional ไม่ถูกต้อง (ต้องเป็น x,y #rrggbb)")
            return False
        x, y, rgb = sp
        okc = color_close(pixel_color_at(x, y), rgb)
        if okc:
            print("  Wait for Pixel Color: เจอสีที่รอ (%d,%d)" % (x, y))
        else:
            print("  Wait for Pixel Color: สีไม่ตรง (%d,%d) — ข้ามการรอ" % (x, y))
        return okc

    def play_once():
        """เล่นสคริปต์ 1 ครั้ง — คืน True = จบครบเอง, False = ถูกหยุดกลางคัน"""
        try:
            loops = 0 if args.loop else max(0, args.loops)
            active = [r for r in rows if r.get("enabled", True) is not False]
            cli_vars.clear()                 # ตัวแปรเริ่มใหม่ทุกครั้งที่เริ่มเล่น (v1.19)
            skip_n = 0                       # ตัวนับข้ามแถวจาก If Loop/If Time (v1.21)
            n_loop = 0
            while True:
                n_loop += 1
                play_rows = pick_play_order(active, pct=pct, shuffle=args.shuffle)
                print("— รอบที่ %d —" % n_loop)
                for i, r in enumerate(play_rows, 1):
                    if not running[0]:
                        return False
                    r = subst_row(r, cli_vars)   # v1.19: แทน {ตัวแปร} ทุกคอลัมน์
                    if r.get("button") == SECTION_HEADER:  # v1.21: แถวจัดระเบียบ — ไม่ทำอะไร
                        continue
                    if skip_n > 0:               # แถวถูกสั่งข้ามจากเงื่อนไขก่อนหน้า (v1.21)
                        skip_n -= 1
                        continue
                    lo, hi = delay_range(r.get("secs", 1))
                    base = delay_seconds(r.get("mins", 0), 0) + (lo if lo == hi else random.uniform(lo, hi))
                    # หยุดทันทีกลางดีเลย์: แบ่ง sleep ชิ้นละ 50 ms เช็ค running ทุกชิ้น
                    _end = time.time() + max(0.0, base / speed)
                    while running[0]:
                        _remain = _end - time.time()
                        if _remain <= 0:
                            break
                        time.sleep(min(0.05, _remain))
                    if not running[0]:
                        return False
                    step_t0 = time.time()
                    btn = r.get("button", "")
                    if btn == IF_LOOP:            # v1.21: รอบที่ >= N → ข้าม N แถวถัดไป
                        n = parse_if_loop(r.get("additional"))
                        if n is None:
                            print("  [%d/%d] If Loop %s → Additional ไม่ถูก (ต้องเป็นเลข >= 1) เล่นต่อ"
                                  % (i, len(play_rows), r.get("additional", "")))
                        elif n_loop < n:
                            print("  [%d/%d] If Loop %s → รอบที่ %d ยังไม่ถึง %d เล่นต่อ"
                                  % (i, len(play_rows), r.get("additional", ""), n_loop, n))
                        else:
                            skip_n = parse_int(r.get("repeat"), 1)   # จำนวนแถวที่ข้าม = Repeat
                            print("  [%d/%d] If Loop %s → รอบที่ %d >= %d ข้าม %d แถว"
                                  % (i, len(play_rows), r.get("additional", ""), n_loop, n, skip_n))
                            if log_enabled:
                                log_write("STEP", "รอบ %d แถว %d/%d If Loop %s → ข้าม %d แถว (%.1f วิ)"
                                          % (n_loop, i, len(play_rows), r.get("additional", ""),
                                             skip_n, time.time() - step_t0), args.script)
                        continue                   # แถวเงื่อนไขไม่ถูกเล่นซ้ำเป็น action
                    if btn == IF_TIME:            # v1.21: ผ่าน HH:MM แล้ว → ข้าม N แถวถัดไป
                        spec = parse_if_time(r.get("additional"))
                        now = time.localtime()
                        if spec is None:
                            print("  [%d/%d] If Time %s → Additional ไม่ถูก (ต้องเป็น HH:MM) เล่นต่อ"
                                  % (i, len(play_rows), r.get("additional", "")))
                        elif (now.tm_hour, now.tm_min) >= spec:
                            skip_n = parse_int(r.get("repeat"), 1)   # จำนวนแถวที่ข้าม = Repeat
                            print("  [%d/%d] If Time %02d:%02d → ผ่านกำหนดแล้ว ข้าม %d แถว"
                                  % (i, len(play_rows), spec[0], spec[1], skip_n))
                            if log_enabled:
                                log_write("STEP", "รอบ %d แถว %d/%d If Time %02d:%02d → ข้าม %d แถว (%.1f วิ)"
                                          % (n_loop, i, len(play_rows), spec[0], spec[1], skip_n,
                                             time.time() - step_t0), args.script)
                        else:
                            print("  [%d/%d] If Time %02d:%02d → ยังไม่ถึง %02d:%02d เล่นต่อ"
                                  % (i, len(play_rows), now.tm_hour, now.tm_min, spec[0], spec[1]))
                        continue                   # แถวเงื่อนไขไม่ถูกเล่นซ้ำเป็น action
                    do_step(r)
                    if log_enabled:
                        log_write("STEP", "รอบ %d แถว %d/%d %s %s (%.1f วิ)" %
                                  (n_loop, i, len(play_rows), r.get("button", ""),
                                   r.get("additional", "") or "", time.time() - step_t0),
                                  args.script)
                    print("  [%d/%d] %s %s" % (i, len(play_rows), r.get("button", ""),
                                              r.get("additional", "")))
                if not running[0]:
                    return False
                if loops == 0:
                    continue
                loops -= 1
                if loops <= 0:
                    return True
            return True
        except KeyboardInterrupt:
            running[0] = False
            return False

    n_restart = 0
    try:
        while True:
            ok = play_once()
            # ปล่อยคีย์/ปุ่มเมาส์ที่กดค้างไว้ (กัน Ctrl/ปุ่มเมาส์ติดหลังหยุดกลางคัน)
            for kind, obj in pending_keys:
                try:
                    (kb_ctl if kind == "k" else mouse_ctl).release(obj)
                except Exception:
                    pass
            pending_keys.clear()
            if log_enabled:
                log_write("STOP" if not ok else "END",
                          "หยุดโดยผู้ใช้ (F8/Esc/Ctrl+C)" if not ok
                          else "เล่นจบเองครบ", args.script)
                prune_log()
            if not ok:
                print("\nถูกหยุดโดยผู้ใช้")
                return 130
            if args.watchdog <= 0:
                print("จบแล้ว ✔")
                return 0
            # watchdog: จบแล้วเริ่มใหม่อัตโนมัติ (หยุดถาวรได้ทุกช่องทางหยุด)
            n_restart += 1
            print("watchdog: จบรอบ — เริ่มใหม่ใน %.0f วิ (ครั้งที่ %d; กด F8/Esc เพื่อหยุดถาวร)"
                  % (args.watchdog, n_restart))
            if log_enabled:
                log_write("WATCHDOG", "รีสตาร์ตครั้งที่ %d หลังพัก %.0f วิ"
                          % (n_restart, args.watchdog), args.script)
            _end = time.time() + args.watchdog
            while running[0] and time.time() < _end:
                time.sleep(min(0.05, max(0.0, _end - time.time())))
            if not running[0]:
                print("\nถูกหยุดโดยผู้ใช้")
                return 130
    except KeyboardInterrupt:
        print("\nหยุดโดยผู้ใช้")
        return 130
    finally:
        running[0] = False
        for kind, obj in pending_keys:      # กันเหลือค้างจาก play_once ที่ raise
            try:
                (kb_ctl if kind == "k" else mouse_ctl).release(obj)
            except Exception:
                pass
        pending_keys.clear()
        try:
            stopper.stop()
        except Exception:
            pass


def main():
    # มี argument = CLI mode, ไม่มี = เปิด GUI
    if len(sys.argv) > 1:
        # คอนโซล Windows มักเป็น cp1252 — ตั้ง UTF-8 ก่อนพิมพ์ help/ข้อความไทย
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass
        sys.exit(cli_main(sys.argv[1:]))
    root = tk.Tk()
    MacroApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

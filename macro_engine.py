# -*- coding: utf-8 -*-
# macro_engine.py — engine ล้วน (ค่าคงที่/parser/คลิปบอร์ด/unicode/log/stats/plugins)
# ไม่มี Tk ใด ๆ — นำไปใช้/เทสต์แยกได้ · ซิงก์กลับ auto_macro.py ด้วย: py build_singlefile.py

import os
import random
import re
import sys
import time
import datetime
import glob
import shutil

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

__version__ = "2.15.0"
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
           "find_title": "🔍 ค้นหา/แทนที่แถว", "find_label": "ข้อความ (match ทุกคอลัมน์):",
           "find_btn": "ค้นหา", "found": "เจอที่แถว %d", "notfound": "ไม่เจอ: %s",
           "replace_label": "ข้อความแทนที่ (ว่าง = ลบข้อความเดิม):",
           "replace_btn": "🔁 แทนที่ทั้งหมด", "replaced": "แทนที่แล้ว %d จุด",
           "col_note": "หมายเหตุ",
           "nothing_redo": "ไม่มีอะไรให้ทำซ้ำ", "redone": "ทำซ้ำแล้ว",
           "clip_empty": "คลิปบอร์ดว่าง",
           "clip_bad": "คลิปบอร์ดไม่ใช่สคริปต์ JSON (ต้องเป็นรายการแถว)",
           "clip_added": "วางจากคลิปบอร์ดแล้ว %d แถว",
           "ifimg_skip": "If Image ไม่เจอ → ข้าม %d แถวถัดไป", "ifimg_hit": "If Image เจอ → เล่นต่อ",
           "ifloop_hit": "ยังไม่เกินรอบที่กำหนด → เล่นต่อ", "iftime_hit": "ยังไม่ผ่านเวลาที่กำหนด → เล่นต่อ",
           "ctx_section": "🗂️ เปลี่ยนเป็นหัวข้อ Section", "section_new": "🗂️ เพิ่มหัวข้อ Section",
           "group_collapse": "📁 ย่อกลุ่มนี้", "group_expand": "📂 ขยายกลุ่มนี้",
           "grp_empty": "กลุ่มนี้ไม่มีแถวที่เปิดใช้ — ไม่มีอะไรให้เล่น", "ctx_play_group": "▶ เล่นกลุ่มนี้อย่างเดียว",
           "group_show_hint": "📦 กลุ่มนี้ย่ออยู่ — แถวซ่อนถูกเล่นตามปกติ",
           "group_expand_first": "📂 ขยายกลุ่มก่อนแก้แถว",
           "else_title": "🔀 Else If Image", "else_label": "วางหลังกลุ่ม A: If Image เจอ → ข้ามกลุ่ม B (Repeat แถว), ไม่เจอ → เล่นกลุ่ม B",
           "pixel_title": "🎨 Wait for Pixel Color", "pixel_label": "x,y = จุดที่ต้องการ · #RRGGBB = สีที่รอ · วินาที = หน่วงก่อนตรวจ (พิมพ์ใน Additional)",
           "save": "บันทึก", "close": "ปิด", "language": "ภาษา (Language):",
           "backup_label": "Backup อัตโนมัติตอนปิดโปรแกรม (เก็บย้อนหลัง",
           "days": "วัน — 1–90)", "log_label": "บันทึก log การเล่นลงไฟล์ macro_log_วันที่.txt",
           "open_log_folder": "เปิดโฟลเดอร์ log", "selftest_btn": "🧪 ทดสอบระบบจริง (ขยับเมาส์+บี๊บ)",            "log_archive_btn": "เก็บถาวรวันเก่า", "log_clear_btn": "ล้างวันเก่า...",
            "dry_report_btn": "รายงาน Dry-run ล่าสุด", "no_dry_report": "ยังไม่มีรายงาน Dry-run — เล่นสคริปต์แบบ Dry-run ก่อน (เมนู 🧪)",
           "log_clear_ask": "ลบ log/dry-report วันเก่าทั้งหมด (ยกเว้นของวันนี้)?\nลบแล้วเรียกคืนไม่ได้ — ถ้าอยากเก็บไว้ ใช้ปุ่มเก็บถาวรแทน",
           "log_archived": "เก็บถาวรแล้ว %d ไฟล์ (log_archive/ รายเดือน)",
           "log_cleared": "ล้างแล้ว %d ไฟล์",
           "logclean_label": "จัดการ log วันเก่าตอนปิดโปรแกรม — เก็บย้อนหลัง",
           "logclean_days": "วัน (1–365)",
           "logarchive_label": "เก็บถาวรใน log_archive/ (แยกโฟลเดอร์รายเดือน) แทนการลบ",
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
           "find_title": "🔍 Find / Replace rows", "find_label": "Text to search (any column):",
           "find_btn": "Find", "found": "Found at row %d", "notfound": "Not found: %s",
           "replace_label": "Replacement (empty = remove matched text):",
           "replace_btn": "🔁 Replace all", "replaced": "Replaced %d spot(s)",
           "col_note": "Note",
           "nothing_redo": "Nothing to redo", "redone": "Redone",
           "clip_empty": "Clipboard is empty",
           "clip_bad": "Clipboard is not a JSON row list",
           "clip_added": "Pasted %d rows from clipboard",
           "ifimg_skip": "If Image miss → skip next %d rows", "ifimg_hit": "If Image found → continue",
           "ifloop_hit": "Round below threshold → continue", "iftime_hit": "Before the set time → continue",
           "ctx_section": "🗂️ Convert to Section header", "section_new": "🗂️ Add Section header",
           "group_collapse": "📁 Collapse this group", "group_expand": "📂 Expand this group",
           "grp_empty": "No enabled rows in this group — nothing to play", "ctx_play_group": "▶ Play this group only",
           "group_show_hint": "📦 Group collapsed — hidden rows still play",
           "group_expand_first": "📂 Expand group before editing",
           "save": "Save", "close": "Close", "language": "Language (ภาษา):",
           "backup_label": "Auto backup on close (keep last",
           "days": "days — 1–90)", "log_label": "Write play log to macro_log_<date>.txt",
           "open_log_folder": "Open log folder", "selftest_btn": "🧪 Real system test (move mouse + beep)",            "log_archive_btn": "Archive old", "log_clear_btn": "Clear old...",
            "dry_report_btn": "Latest dry-run report", "no_dry_report": "No dry-run report yet — run a Dry-run first (🧪 menu)",
           "log_clear_ask": "Delete all old log/dry-report files (today's kept)?\nThis cannot be undone — use Archive instead to keep them.",
           "log_archived": "Archived %d file(s) (log_archive/ monthly)",
           "log_cleared": "Deleted %d file(s)",
           "logclean_label": "Clean old logs on exit — keep last",
           "logclean_days": "days (1–365)",
           "logarchive_label": "Archive to log_archive/ (monthly folders) instead of deleting",
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
IF_PIXEL = "If Pixel Color"      # เงื่อนไข v2.5: จุดสีตรง → เล่นต่อ, ไม่ตรง → ข้าม N แถว
READ_PIXEL = "Read Pixel Color"  # v2.5: อ่านสีจุดเก็บเป็นตัวแปร (Additional: ชื่อ x,y)
IF_VAR = "If Variable"           # เงื่อนไข v2.5: เทียบค่าตัวแปร → เล่นต่อ/ข้าม N แถว
BLOCK_START = "🔷 Block Start"    # v2.6 (ชุด N2): เปิดบล็อก — เงื่อนไขไม่จริง = กระโดด Block End
BLOCK_END = "🔷 Block End"        # v2.6 (ชุด N2): ปิดบล็อก — วนกลับตาม until/max (ลูปย่อย)

# v1.22: หมวดสีของแถวตารางตามชนิด Action — แยกกลุ่มเห็นภาพ แค่การจัดระเบียบ ไม่เปลี่ยนพฤติกรรม
ROW_STYLE = {"run": {"background": "#c8e6c9"},
             "section": {"background": "#cfe3f7", "foreground": "#1a3d6d"},
             "block": {"background": "#d6d9f7", "foreground": "#2b2f77"},   # v2.6: เปิดบล็อก
             "blockend": {"background": "#e3e4f2", "foreground": "#3d4085"},  # v2.6: ปิดบล็อก
             "cond": {"background": "#fdf1d6"},            # เงื่อนไข (If Image/Else/Loop/Time)
             "key": {"background": "#e6e0f8"},             # คีย์บอร์ด (Tap/Press/Release/Type Text)
             "special": {"background": "#dff0f5"},         # พิเศษ (Image/Pixel/Launch/Beep/Clipboard/ตัวแปร)
             "odd": {"background": "#ffffff"},
             "even": {"background": "#f2f6fb"}}


def row_tag(button, cond_names=()):
    """คืนชื่อ tag ตามชนิด Action (v1.22) — แถวเงื่อนไข/คีย์/พิเศษได้สีของหมวด
    แถวเมาส์ทั่วไปใช้แถบสลับ even/odd เหมือนเดิม
    v2.13: cond_names = ชื่อเงื่อนไข plugin (CONDITION_NAME) — แถวเหล่านั้นได้สีหมวด cond ด้วย"""
    if button == SECTION_HEADER:
        return "section"
    if button == BLOCK_START:
        return "block"
    if button == BLOCK_END:
        return "blockend"
    if button in (IF_IMAGE, ELSE_IMAGE, IF_LOOP, IF_TIME, IF_PIXEL, IF_VAR) \
            or button in tuple(cond_names or ()):
        return "cond"
    if button in ("Tap Key", "Press Key", "Release Key", "Type Text"):
        return "key"
    if button in ("Image Click", "Wait for Image", "Wait for Pixel Color", "Launch App",
                  "Beep", "Set Clipboard", "Read Clipboard", "Set Variable", READ_PIXEL):
        return "special"
    return None


def row_tags(button, n, cond_names=()):
    """คืน tuple tags เต็ม (เรียกตอน insert/item) — แถวเมาส์ = แถบสลับเดิม, หมวดพิเศษ = สีหมวด"""
    t = row_tag(button, cond_names)
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
PIXEL_COND = [IF_PIXEL]          # v2.5: เงื่อนไขสีจุด
READ_PIXEL_ACTIONS = [READ_PIXEL]  # v2.5: อ่านสีเก็บตัวแปร
VAR_COND = [IF_VAR]              # v2.5: เงื่อนไขตัวแปร
BLOCK_ACTIONS = [BLOCK_START, BLOCK_END]   # v2.6 (ชุด N2): บล็อกเงื่อนไข/ลูปย่อย
SECTION_HEADER = "⬛ หัวข้อ"      # v1.21: แถวจัดระเบียบ — ไม่ทำอะไรตอนเล่น
ACTIONS_ALL = (MOUSE_BTNS + KEY_ACTIONS + [IMAGE_ACTION, IF_IMAGE, ELSE_IMAGE, WAIT_PIXEL]
               + SCROLL_ACTIONS + DBL_ACTIONS + MOD_CLICKS + MOVE_ACTIONS + EXTRA_ACTIONS
               + VAR_ACTIONS + CLIP_ACTIONS + LOOP_ACTIONS + TIME_ACTIONS
               + PIXEL_COND + READ_PIXEL_ACTIONS + VAR_COND + BLOCK_ACTIONS + [SECTION_HEADER])

# v2.10: แถวที่โหมด Dry-run "ไม่ทำจริง" — ทุกแถว input จริง (เมาส์/คีย์/เปิดแอป/คลิปบอร์ด)
# ถูกแทนด้วยข้อความรายงาน — แถวเงื่อนไข/ตัวแปร/บล็อก/อ่านสี (ไม่แตะ input) เล่นปกติเพื่อเดินเส้นทางจริง
_DRY_ACTIONS = tuple(
    a for a in ACTIONS_ALL
    if a not in (IF_IMAGE, ELSE_IMAGE, IF_LOOP, IF_TIME, IF_PIXEL, IF_VAR,
                 READ_PIXEL, BLOCK_START, BLOCK_END, SECTION_HEADER,
                 "Set Variable", "Read Pixel Color"))
_DRY_VERB = {"Left Click": "คลิก", "Right Click": "คลิก", "Middle Click": "คลิก",
             "Left Down": "กด", "Right Down": "กด", "Middle Down": "กด",
             "Left Up": "ปล่อย", "Right Up": "ปล่อย", "Middle Up": "ปล่อย",
             "Press Key": "กด", "Tap Key": "กด", "Release Key": "ปล่อย",
             "Type Text": "พิมพ์", "Launch App": "เปิด", "Beep": "ส่งเสียง",
             "Set Clipboard": "ตั้งคลิปบอร์ด", "Read Clipboard": "อ่านคลิปบอร์ด",
             "Move Mouse": "ย้ายเมาส์", "Save Cursor": "จำตำแหน่งเมาส์"}
BLOCK_MAX_DEPTH = 8          # v2.6: จำกัดความลึกบล็อกซ้อน (กันสคริปต์ผิดโครงสร้าง)
BLOCK_MAX_ROUNDS = 1000      # v2.6: ลูปย่อยไม่ใส่ max = วนได้สูงสุดเท่านี้ (กันอนันต์)

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


def parse_if_var(txt):
    """แยกเงื่อนไขตัวแปร (v2.5) — "name > 5" / "name = ค่า" / "name ~ ข้อความ"
    ตัวดำเนินการ: = == != > >= < <= ~ (contains) — คืน (name, op, value) หรือ None"""
    m = re.fullmatch(r"\s*(%s)\s*(==|!=|>=|<=|>|<|~=|=|~)\s*(.*?)\s*" % _VAR_NAME,
                     str(txt or ""), re.UNICODE)
    if not m:
        return None
    op = m.group(2)
    if op == "==":
        op = "="
    if op == "~=":
        op = "~"
    val = m.group(3)
    if op != "=" and not val.strip():      # เปรียบเทียบ/contains ต้องมีค่า
        return None
    return m.group(1), op, val


def parse_cond_store(txt):
    """อ่านโทเคน '>ชื่อ' ท้าย Additional ของแถวเงื่อนไข (v2.10 — ผลเงื่อนไขเป็นตัวแปร)
    เช่น 'img.png >img_ok' / '300,300 #ffffff && n > 5 >ok' — คืน (ข้อความที่เหลือ, ชื่อตัวแปร/None)
    ชื่อตัวแปรใช้กฎเดียวกับ Set Variable (_VAR_NAME — ไทย/อังกฤษได้) และห้ามชนคำสงวน
    on/of/and (กันพิมพ์เผลอติดกับเงื่อนไขภาษาอังกฤษ)"""
    s = str(txt or "")
    m = re.search(r"\s*>(%s)\s*$" % _VAR_NAME, s, re.UNICODE)
    if not m or m.group(1).lower() in ("on", "of", "and"):
        return s, None
    return s[:m.start()].rstrip(), m.group(1)


# ------------------------------------------------ เงื่อนไขรวม AND (v2.5.4) ----
_COND_SPLIT = re.compile(r"\s*&&\s*")


def split_condition_and(txt):
    """แตก Additional เงื่อนไขที่ใช้ && เป็นหลายเงื่อนไขย่อย (v2.5.4 — ชุด N1)
    คืน list ของชิ้นย่อย (list ว่างเมื่อไม่มี && — แถวเงื่อนไขเดี่ยวใช้ parser เดิม)
    เช่น "img.png && 300,300 #ffffff" → ["img.png", "300,300 #ffffff"]
    timeout token ท้ายแถว (เช่น "5s") ถูกตัดออกก่อนแตกเสมอ"""
    s = str(txt or "")
    if "&&" not in s:
        return []
    parts = [p.strip() for p in _COND_SPLIT.split(s.strip())]
    out = []
    for p in parts:
        if p and parse_if_var(p) is None:
            # timeout token ("Ns") ที่ติดมากับชิ้นย่อย (เช่น "img.png 5s") ตัดทิ้ง —
            # ไม่แตะชิ้นที่เป็นเงื่อนไขตัวแปร (ค่าข้อความลงท้าย "5s" ได้)
            p = re.sub(r"(?:^|\s)-?\d+(?:\.\d+)?s$", "", p, flags=re.I).strip()
        if p:
            out.append(p)
    return out


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


# -------------------------------- บล็อกเงื่อนไข/ลูปย่อย (v2.6 — ชุด N2) ----
def parse_block_spec(txt):
    """แปลง Additional ของ Block Start เป็นคำสั่งเปิดบล็อก (v2.6 — ชุด N2)
    รองรับ:
      ""                    → เปิดบล็อกเปล่า (แถวข้างในเล่นเสมอ)
      "if ภาพ.png"          → เปิดเมื่อเจอภาพ (ไม่เจอ = กระโดดข้ามบล็อก)
      "if img.png && n > 5"  → เงื่อนไขรวม && ได้ (ภาพ + สีจุด + ตัวแปร — N1)
      "until ภาพ.png"        → ลูปย่อย: กลับมาเล่นซ้ำจนเจอภาพ (สูงสุด BLOCK_MAX_ROUNDS)
      "until n >= 5"         → วนจนเงื่อนไขตัวแปรจริง
      "until ภาพ.png max 20"  → วนจนเจอภาพ แต่ไม่เกิน 20 รอบ
      "max 10"               → วนซ้ำบล็อก 10 รอบ (ไม่มีเงื่อนไข)
    คืน dict {"kind": "once"/"loop", "if": str, "until": str, "max": int} หรือ None เมื่อพัง"""
    s = str(txt or "").strip()
    out = {"kind": "once", "if": "", "until": "", "max": 0}
    # token "max N" อยู่ท้ายเสมอ (ตัดก่อนแตก until/if) — ต้นสตริงก็ได้ ("max 10")
    m = re.search(r"(?:^|\s)max\s+(-?\d+(?:\.\d+)?)\s*$", s)
    if m:
        try:
            out["max"] = max(0, int(float(m.group(1))))
        except ValueError:
            return None
        s = s[:m.start()].strip()
    m = re.match(r"^(if|until)\b\s*(.*)$", s, re.I)
    if m:
        key = m.group(1).lower()
        rest = m.group(2).strip()
        if not rest:
            return None
        out[key] = rest
        out["kind"] = "loop" if key == "until" else "once"
    elif s:                                  # ข้อความอื่นที่ไม่ใช่ if/until/max = พัง
        return None
    if out["max"] > 0:
        out["kind"] = "loop"                 # "max N" เดี่ยว ๆ = วนซ้ำไม่มีเงื่อนไข N รอบ
    return out


def find_block_end_index(rows, start_idx):
    """หา index ของ Block End ที่จับคู่กับ Block Start ที่ rows[start_idx]
    (นับวงเล็บ — Block Start ข้างในเพิ่ม depth) — ไม่เจอคืน None (v2.6)"""
    depth = 0
    for j in range(start_idx + 1, len(rows)):
        b = str(rows[j].get("button", ""))
        if b == BLOCK_START:
            depth += 1
        elif b == BLOCK_END:
            if depth == 0:
                return j
            depth -= 1
    return None


class BlockRunner:
    """ตัวตัดสินคำสั่งบล็อก (v2.6 — ชุด N2) — หัวใจเดียวให้ GUI/CLI ใช้ร่วมกัน
    ลูปเล่นหลักเรียก: BlockRunner(head_idx).decide(rows, round_counters) ตอนเจอ Block Start
    และ BlockRunner(end_idx).decide_end(rows, round_counters) ตอนเจอ Block End
    คืน (goto, message) — goto = index แถวถัดไปที่ต้องเล่น (None = เล่นต่อตามลำดับ)"""

    def __init__(self, head_idx, condition_cb=None):
        self.head_idx = head_idx
        self.condition_cb = condition_cb      # def cb(spec_text) -> True/False/None (None = รูปแบบพัง)

    def _cond_true(self, spec_text):
        if not spec_text:
            return True
        return self.condition_cb(spec_text) if self.condition_cb else True

    def decide(self, rows, counters, row=None):
        """ตัดสินที่ Block Start — คืน (goto, message)
        เงื่อนไขไม่จริง → กระโดดหลัง Block End คู่ · จริง → เล่นบล็อก (ลูปย่อยเริ่มนับรอบ 1)
        row = แถวที่ผ่านการแทนค่า {ตัวแปร} แล้ว (ไม่ส่ง = อ่านจาก rows[head_idx])"""
        r = row or rows[self.head_idx]
        spec = parse_block_spec(r.get("additional"))
        if spec is None:
            return None, "Block Start: รูปแบบ Additional ไม่ถูก (ใช้ if .../until ... [max N])"
        hit = self._cond_true(spec["if"])
        if hit is None:
            return None, "Block Start: เงื่อนไข %r รูปแบบไม่ถูก — เล่นบล็อกตามปกติ" % spec["if"]
        if not hit:
            end_i = find_block_end_index(rows, self.head_idx)
            if end_i is None:
                return None, "Block Start: ไม่พบ Block End คู่ — เล่นต่อตามลำดับ (ตรวจด้วย --validate)"
            return end_i + 1, "Block Start: เงื่อนไขไม่จริง → ข้ามบล็อก (ถึงแถว %d)" % (end_i + 2)
        if spec["kind"] == "loop":
            counters[self.head_idx] = 1       # ลูปย่อยเริ่มรอบที่ 1
        return None, None

    def decide_end(self, rows, counters, head_additions=None):
        """ตัดสินที่ Block End — หา Block Start เปิดที่ใกล้ที่สุดด้านบน (นับวงเล็บ)
        เป็นลูปย่อย: ยังไม่จริง/ยังไม่ครบ max → กระโดดกลับแถวหลัง Start (เล่นเนื้อในซ้ำ)
        head_additions = dict {index Start → Additional ที่แทนค่า {ตัวแปร} แล้ว} (ถ้ามี)"""
        head_i = None
        depth = 0
        for j in range(self.head_idx - 1, -1, -1):
            b = str(rows[j].get("button", ""))
            if b == BLOCK_END:
                depth += 1
            elif b == BLOCK_START:
                if depth == 0:
                    head_i = j
                    break
                depth -= 1
        if head_i is None:
            return None, "Block End: ไม่มี Block Start เปิด — เล่นต่อตามลำดับ (ตรวจด้วย --validate)"
        head_add = (head_additions or {}).get(head_i) if head_additions else None
        spec = parse_block_spec(rows[head_i].get("additional")
                                if head_add is None else head_add)
        if spec is None:
            return None, None                 # Start พัง — เล่นต่อ (validate เตือนอยู่แล้ว)
        if spec["kind"] != "loop":
            return None, None                 # บล็อกธรรมดา: จบแล้วเล่นต่อ
        rnd = counters.get(head_i, 1)
        maxr = spec["max"] or BLOCK_MAX_ROUNDS
        cond_text = spec["until"]
        hit = True if not cond_text else self._cond_true(cond_text)
        if hit is None:
            return None, ("Block End: เงื่อนไข until %r รูปแบบไม่ถูก — ออกจากลูปย่อย" % cond_text)
        if hit:
            counters.pop(head_i, None)
            return None, None                 # จบลูปย่อย — เล่นต่อหลัง End
        if rnd >= maxr:
            counters.pop(head_i, None)
            return None, "Block End: ลูปย่อยครบ %d รอบ — ออกจากลูป" % maxr
        counters[head_i] = rnd + 1
        return head_i + 1, ("Block End: รอบที่ %d/%d ยังไม่จริง → วนกลับ" % (rnd, maxr))


def validate_blocks(rows):
    """ตรวจโครงสร้างบล็อกทั้งสคริปต์ (v2.6 — ใช้โดย validate_rows และ GUI)
    คืน list ของ (ลำดับแถว 1-based, เหตุผล) — บล็อกไม่ปิด/ปิดเกิน/depth เกิน/Additional พัง"""
    issues = []
    stack = []                                # (index 0-based ของ Block Start, depth)
    for i, r in enumerate(rows, 1):
        btn = str(r.get("button", ""))
        if btn == BLOCK_START:
            if len(stack) >= BLOCK_MAX_DEPTH:
                issues.append((i, "บล็อกซ้อนลึกเกิน %d ชั้น" % BLOCK_MAX_DEPTH))
            spec = parse_block_spec(r.get("additional"))
            if spec is None:
                issues.append((i, "Block Start รูปแบบไม่ถูก (ใช้ if .../until ... [max N] หรือเว้นว่าง)"))
            stack.append(i - 1)
        elif btn == BLOCK_END:
            if not stack:
                issues.append((i, "Block End ไม่มี Block Start เปิดคู่"))
            else:
                stack.pop()
    for idx in stack:
        issues.append((idx + 1, "Block Start นี้ไม่มี Block End ปิดคู่"))
    return issues


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
        m = re.match(r"^rand\s+(-?\d+(?:\.\d+)?)\s*-\s*(-?\d+(?:\.\d+)?)\s*$", val)
        if m:                                    # v2.5: rand a-b → สุ่มเลขเก็บลงตัวแปร
            a, b = float(m.group(1)), float(m.group(2))
            if a > b:
                a, b = b, a
            variables[name] = fmt_num(random.randint(int(a), int(b))
                                      if a.is_integer() and b.is_integer()
                                      else random.uniform(a, b))
            return True
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


# -------------------------------------- ส่งออกสคริปต์เป็นแบตช์ (v2.3) ----
def batch_export_bat(script_name, py_cmd="py"):
    """เนื้อหาไฟล์ .bat สำหรับดับเบิลคลิกรันสคริปต์ผ่าน CLI (v2.3)
    script_name = ชื่อไฟล์สคริปต์ (ไม่รวมพาธ) — ไฟล์ .bat ต้องอยู่โฟลเดอร์เดียวกับ
    auto_macro.py และไฟล์สคริปต์ · %* ส่งต่ออาร์กิวเมนต์ เช่น --loop --speed 2"""
    return (
        "@echo off\r\n"
        "rem Auto Mouse & Keyboard Macro v%s - double-click runner\r\n"
        "rem Add CLI args if needed, e.g. --loop --speed 2  (see: py auto_macro.py --help)\r\n"
        "cd /d \"%%~dp0\"\r\n"
        "%s auto_macro.py \"%s\" %%*\r\n"
        "pause\r\n" % (__version__, py_cmd, script_name))


def batch_queue_export_bat(list_name, py_cmd="py"):
    """เนื้อหาไฟล์ .bat สำหรับดับเบิลคลิกรันคิวหลายสคริปต์ผ่าน CLI --queue (v2.10.1)
    list_name = ชื่อไฟล์ลิสต์ .txt (ไม่รวมพาธ) — ไฟล์ .bat ต้องอยู่โฟลเดอร์เดียวกับ
    auto_macro.py และไฟล์ลิสต์ · %* ส่งต่ออาร์กิวเมนต์ เช่น --no-log --loop"""
    return (
        "@echo off\r\n"
        "rem Auto Mouse & Keyboard Macro v%s - queue runner (many scripts)\r\n"
        "rem Add CLI args if needed, e.g. --no-log  (see: py auto_macro.py --help)\r\n"
        "cd /d \"%%~dp0\"\r\n"
        "%s auto_macro.py --queue \"%s\" %%*\r\n"
        "pause\r\n" % (__version__, py_cmd, list_name))


def batch_queue_export_sh(list_name, py_cmd="python3"):
    """เนื้อหาไฟล์ .sh สำหรับรันคิวหลายสคริปต์ผ่าน CLI --queue บน Linux/macOS (v2.10.1)
    list_name = ชื่อไฟล์ลิสต์ .txt (ไม่รวมพาธ) · \"$@\" ส่งต่ออาร์กิวเมนต์"""
    return (
        "#!/bin/sh\n"
        "# Auto Mouse & Keyboard Macro v%s — รันคิวหลายสคริปต์ผ่าน CLI --queue\n"
        "# เพิ่มอาร์กิวเมนต์ได้ เช่น --no-log (ดูทั้งหมด: python3 auto_macro.py --help)\n"
        "cd \"$(dirname \"$0\")\" || exit 1\n"
        "%s auto_macro.py --queue \"%s\" \"$@\"\n" % (__version__, py_cmd, list_name))


def batch_export_sh(script_name, py_cmd="python3"):
    """เนื้อหาไฟล์ .sh สำหรับรันสคริปต์ผ่าน CLI บน Linux/macOS (v2.3)
    script_name = ชื่อไฟล์สคริปต์ (ไม่รวมพาธ) — ไฟล์ .sh ต้องอยู่โฟลเดอร์เดียวกับ
    auto_macro.py และไฟล์สคริปต์ · "$@" ส่งต่ออาร์กิวเมนต์"""
    return (
        "#!/bin/sh\n"
        "# Auto Mouse & Keyboard Macro v%s — รันสคริปต์นี้ผ่าน CLI\n"
        "# เพิ่มอาร์กิวเมนต์ได้ เช่น --loop --speed 2 (ดูทั้งหมด: python3 auto_macro.py --help)\n"
        "cd \"$(dirname \"$0\")\" || exit 1\n"
        "%s auto_macro.py \"%s\" \"$@\"\n" % (__version__, py_cmd, script_name))


# ----------------------------- ทำงานร่วม AutoHotkey .ahk (v2.7) ----------
def rows_to_ahk(rows, condition_names=()):
    """แปลงแถวสคริปต์ → เนื้อหาไฟล์ .ahk (v2.7 — v2.9 รองรับบล็อก · v2.13 เงื่อนไข plugin)
    condition_names = ชื่อเงื่อนไข plugin (CONDITION_NAME) — แถวเหล่านั้นและบล็อกที่อ้างถึง
    แปลเป็น AHK ไม่ได้ = เขียนเป็น comment ทั้งบล็อก (prescan กันปีกกาลอย)
    รองรับ: Tap Key/Press Key/Release Key, Left/Right Click, Double Click, Scroll,
    Ctrl/Shift/Alt+Click, Move Mouse (+Offset), Save/Restore Cursor (CoordMode Mouse),
    Type Text (ครอบสัญลักษณ์พิเศษ), Launch App, Beep, Set Variable (AHK :=),
    If Variable (if), Block Start/End → บล็อก { } ของ AHK:
    "if n > 5" → if (n > 5) { … } · "max N" → Loop, N { … } · "until cond" → Loop { … } Until
    (เงื่อนไขที่แปลไม่ได้ เช่น ภาพ/สีจุด/เงื่อนไข plugin = ทั้งคู่ Start/End เขียนเป็น comment)"""
    out = ["; Auto Mouse & Keyboard Macro v%s — exported .ahk" % __version__,
           "; แปลงคร่าว ๆ — ตรวจก่อนใช้จริง (รายละเอียด: docs/README.en.md)"]
    key_map = {"esc": "Esc", "enter": "Enter", "return": "Enter", "tab": "Tab",
               "space": "Space", "ctrl": "Ctrl", "shift": "Shift", "alt": "Alt",
               "win": "LWin", "up": "Up", "down": "Down", "left": "Left",
               "right": "Right", "pgup": "PgUp", "pgdn": "PgDn", "del": "Del",
               "ins": "Ins", "home": "Home", "end": "End", "backspace": "Backspace",
               "prtsc": "PrintScreen", "capslock": "CapsLock"}

    def ahk_key(k):
        s = str(k or "").strip()
        if not s:
            return ""
        if len(s) == 1:
            return s.lower() if s.isalpha() else s   # ตัวพิมพ์เล็ก — AHK ตีความตัวใหญ่ = กด Shift ร่วม
        if "+" in s and len(s) > 2:          # combo เช่น ctrl+s → ^s, ctrl+shift+esc → ^+{Esc}
            mods, rest = "", []
            for p in (x.strip() for x in s.split("+")):
                if not p:
                    continue
                pl = p.lower()
                if pl == "ctrl":
                    mods += "^"
                elif pl == "shift":
                    mods += "+"
                elif pl == "alt":
                    mods += "!"
                elif pl == "win":
                    mods += "#"
                else:
                    rp = ahk_key(p)
                    rest.append("{%s}" % rp if len(rp) > 1 else rp)
            return mods + "".join(rest)
        return key_map.get(s.lower(), s)

    def _ahk_var_expr(val):
        """ค่าในนิพจน์ AHK (v2.8): ตัวเลข/ชื่อตัวแปร = ส่งตรง, ข้อความ = ครอบ "" """""
        s = str(val).strip()
        if re.fullmatch(r"-?\d+(?:\.\d+)?", s):
            return s
        m = re.fullmatch(r"\{(%s)\}" % _VAR_NAME, s, re.UNICODE)
        if m:
            return m.group(1)                  # {ตัวแปร} → อ้างตัวแปร AHK ตรง ๆ (สองทิศ)
        # ข้อความอื่น (แม้ตรง _VAR_NAME) ครอบ "" เสมอ — กันชื่อไทย/คำธรรมดาโดนตีความเป็นตัวแปร
        return '"' + s.replace('"', '""') + '"'

    def _ahk_block_cond(txt):
        """เงื่อนไข Block Start → นิพจน์ AHK หรือ None (ภาพ/สีจุด/ผสม/เงื่อนไข plugin = แปลไม่ได้)
        คืน "" เมื่อไม่มีเงื่อนไข (บล็อกเปล่า) — รองรับ && หลายเงื่อนไข (v2.9)"""
        s = str(txt or "").strip()
        if not s:
            return ""
        parts = split_condition_and(s) or [s]
        if any(match_condition_name(p, condition_names) for p in parts):
            return None                        # v2.13: เงื่อนไข plugin → ทั้งบล็อกเป็น comment
        exprs = []
        for p in parts:
            fv = parse_if_var(p)
            if fv is None:
                return None
            name, op, val = fv
            if op == "~":
                exprs.append("InStr(%s, %s)" % (name, _ahk_var_expr(val)))
            else:
                exprs.append("%s %s %s" % (name, op, _ahk_var_expr(val)))
        return " && ".join(exprs)

    # v2.9: Block Start ที่เงื่อนไขแปลไม่ได้ (ภาพ/สีจุด) → ทั้งคู่ Start/End เขียน comment
    # (ห้ามออก } ลอย ๆ เพราะ .ahk จะพังตอนรัน)
    skip_ends = set()
    btns = [{"button": str(x.get("button", ""))} for x in (rows or [])]
    for si, r0 in enumerate(rows or []):
        if str(r0.get("button", "")) != BLOCK_START:
            continue
        spec = parse_block_spec(r0.get("additional"))
        if spec is not None and _ahk_block_cond(spec["if"]) is not None:
            continue
        ei = find_block_end_index(btns, si)
        if ei is not None:
            skip_ends.add(ei)

    block_stack = []                      # บริบทบล็อกที่เปิดค้าง (until ของ Loop)
    for bi, r in enumerate(rows or []):
        if not r.get("enabled", True):
            continue
        btn = str(r.get("button", ""))
        add = str(r.get("additional") or "")
        delay = float(r.get("mins", 0) or 0) * 60 + float(r.get("secs", 0) or 0)
        rep = max(1, int(r.get("repeat", 1) or 1))
        lines = []
        if btn in ("Tap Key", "Press Key"):
            k = ahk_key(add) or add
            # ตัวอักษรเดี่ยว/combo (^+!#) ส่งตรง เช่น Send ^s — ชื่อคีย์หลายตัวอักษรค่อยห่อ {}
            if len(k) == 1 or any(c in k for c in "^+!#"):
                lines = ["Send %s" % k]
            else:
                lines = ["Send {%s}" % k]
        elif btn == "Release Key":
            k = ahk_key(add) or add
            lines = ["; (release-only — AHK ไม่มีตรง ๆ: Send {%s} จึงใช้แทนได้" % k]
        elif btn in ("Left Click", "Right Click"):
            btn_txt = "L" if btn == "Left Click" else "R"
            for _ in range(rep):
                lines.append("Click %s, %s, %s" % (r.get("x", ""), r.get("y", ""), btn_txt))
        elif btn in DBL_ACTIONS:
            x, y = str(r.get("x", "")), str(r.get("y", ""))
            lines = ["Click %s, %s, 2" % (x, y)]
        elif btn in SCROLL_ACTIONS:
            lines = ["Send {Wheel%s %d}" % ("Up" if btn == "Scroll Up" else "Down", rep)]
        elif btn in MOD_CLICKS:
            mods = "".join("#" if m == "ctrl" else "+" if m == "shift" else "!" for m in
                           ("ctrl" if "Ctrl" in btn else "", "shift" if "Shift" in btn else "",
                            "alt" if "Alt" in btn else ""))
            lines = ["Send {%s}{Click %s, %s, %s}" % (
                mods, r.get("x", ""), r.get("y", ""),
                "R" if "Right" in btn else "L")]
        elif btn == "Move Mouse":
            lines = ["MouseMove %s, %s" % (r.get("x", ""), r.get("y", ""))]
        elif btn == "Move Mouse by Offset":
            ox = add.split(",")[0].strip() if "," in add else "0"
            oy = add.split(",")[1].strip() if "," in add and len(add.split(",")) > 1 else "0"
            lines = ["MouseMove %s, %s, , R" % (ox, oy)]
        elif btn == "Save Cursor":
            lines = ["CoordMode Mouse, Screen", "MouseGetPos, ax, ay"]
        elif btn == "Restore Cursor":
            lines = ["MouseMove ax, ay"]
        elif btn == "Type Text":
            lines = ["SendRaw %s" % add]   # SendRaw = ส่งทุกตัวอักษรตามตัวพิมพ์ ไม่ตีความ {} ของ AHK
        elif btn == "Launch App":
            lines = ["Run %s" % add]
        elif btn == "Beep":
            lines = ["SoundBeep, 750, 300"]
        elif btn == "Set Variable":
            # v2.8: ตัวแปรสองทิศ — name := ค่า / name += จำนวน (ตัวเลข/ตัวแปรตรง ข้อความครอบ "")
            sv = parse_set_var(add)
            if not sv:
                lines = ["; (Set Variable รูปแบบไม่ถูก: %s)" % add]
            else:
                name, op, val = sv
                if op == "=":
                    lines = ["%s := %s" % (name, _ahk_var_expr(val))]
                else:
                    lines = ["%s %s= %s" % (name, op[0], _ahk_var_expr(val))]
        elif btn == IF_VAR:
            # v2.8: เงื่อนไขตัวแปร → if (name op ค่า) / if name contains ข้อความ
            fv = parse_if_var(add)
            if not fv:
                lines = ["; (If Variable รูปแบบไม่ถูก: %s)" % add]
            else:
                name, op, val = fv
                if op == "~":
                    lines = ["if %s contains %s" % (name, _ahk_var_expr(val))]
                else:
                    lines = ["if (%s %s %s)" % (name, op, _ahk_var_expr(val))]
        elif btn == BLOCK_START:
            # v2.9: บล็อก → { } ของ AHK — if/max/until (เงื่อนไขแปลไม่ได้ = comment ทั้งคู่)
            spec = parse_block_spec(add)
            cond = _ahk_block_cond(spec["if"]) if spec else None
            if cond is None:
                lines = ["; (Block Start แปลไม่ได้ตรง ๆ: %s — จัดบล็อก/ค้นภาพใน AHK เอง)" % add]
            elif spec["kind"] == "once":
                lines = ["if (%s) {" % cond] if cond else ["{"]
                block_stack.append({"until": ""})
            else:
                lines = ["Loop, %d {" % spec["max"] if spec["max"] else "Loop {"]
                block_stack.append({"until": spec["until"]})
        elif btn == BLOCK_END:
            if bi in skip_ends:
                lines = ["; (Block End — คู่ Block Start แปลไม่ได้ จัดบล็อกเอง)"]
            elif block_stack:
                ctx = block_stack.pop()
                lines = ["}"]
                if ctx.get("until"):
                    lines.append("Until, %s" % ctx["until"])
            else:
                lines = ["; (Block End เกิน — ไม่มี Block Start เปิดคู่)"]
        if not lines:
            note = btn if not add else "%s (%s)" % (btn, add)
            lines = ["; (ไม่รองรับ: %s)" % note]
        for ln in lines:
            out.append(ln)
        if delay > 0:
            out.append("Sleep %d" % round(delay * 1000))
        if rep > 1 and btn not in ("Left Click", "Right Click", "Beep") \
                and not (btn in ("Tap Key", "Press Key", "Type Text", "Launch App",
                                 "Set Variable") or btn in SCROLL_ACTIONS):
            for _ in range(rep - 1):
                out.append(lines[0])
        if rep > 1 and (btn in ("Tap Key", "Press Key", "Type Text", "Launch App",
                                "Set Variable") or btn in SCROLL_ACTIONS):
            out.append("; (repeat %d ครั้งของแถวนี้อาจต้องปรับใน AHK เอง)" % rep)
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def ahk_to_rows(text):
    """แปลงไฟล์ .ahk → แถวสคริปต์ (v2.7) — รองรับคำสั่งหลัก AHK v1:
    Send/SendInput/SendRaw (คีย์/ข้อความ), Click, MouseMove, MouseClick, Sleep, Run
    คืน list แถวแบบเดียวกับไฟล์ Save .json — บรรทัดที่แปลไม่ได้ข้าม
    (จำกัดพันธุ์: นิพจน์/ตัวแปร/ป้ายกำกับ AHK ไม่แปล — เอกสารบอกผู้ใช้ชัดเจน)"""
    rows = []
    pending = {}                       # ดีเลย์/รีพีตรอแกะจาก Sleep ถัดไป
    keymap = {"CTRL": "ctrl", "LCTRL": "ctrl", "RCTRL": "ctrl",
              "SHIFT": "shift", "LSHIFT": "shift", "RSHIFT": "shift",
              "ALT": "alt", "LALT": "alt", "RALT": "alt",
              "ENTER": "enter", "RETURN": "enter", "ESC": "esc", "TAB": "tab",
              "SPACE": "space", "UP": "up", "DOWN": "down", "LEFT": "left",
              "RIGHT": "right", "PGUP": "pgup", "PGDN": "pgdn", "DEL": "del",
              "INS": "ins", "HOME": "home", "END": "end",
              "BACKSPACE": "backspace", "CAPSLOCK": "capslock", "PRINTSCREEN": "prtsc"}

    def parse_send_keys(txt):
        """'{Ctrl down}ข้อความ{Ctrl up}' / '{Del}' → แถว Press/Release/Tap/Type"""
        out = []
        for m in re.finditer(r"\{[^}]+\}|[^{}]+", txt):
            tok = m.group(0)
            if tok.startswith("{"):
                body = tok[1:-1].strip()
                low = body.lower()
                if low.endswith(" down"):
                    k = body[:-5].strip().lower()
                    out.append({"button": "Press Key", "additional": keymap.get(
                        k.upper(), k)})
                elif low.endswith(" up"):
                    k = body[:-3].strip().lower()
                    out.append({"button": "Release Key", "additional": keymap.get(
                        k.upper(), k)})
                else:
                    k = keymap.get(body.upper(), body.lower() if len(body) > 1 else body)
                    out.append({"button": "Tap Key", "additional": k})
            else:
                t = tok.replace("\r", "").replace("\n", "")
                if t:
                    out.append({"button": "Type Text", "additional": t})
        return out

    raw_lines = str(text or "").splitlines()
    # v2.9: จับคู่ '} Until, cond' / '}' + 'Until, cond' กับ 'Loop...{' ที่เปิด (ก่อนแปลรายบรรทัด)
    untils = {}                       # index ของบรรทัด 'Loop...{' → เงื่อนไข Until
    loop_stack = []
    for li, raw in enumerate(raw_lines):
        s = raw.strip()
        if re.match(r"^Loop(,\s*\d+)?\s*\{$", s, re.I):
            loop_stack.append(li)
        elif s.startswith("}") and loop_stack:
            j = loop_stack.pop()
            m = re.match(r"^}\s*Until,?\s*(.+)$", s, re.I)
            if m:
                untils[j] = m.group(1).strip()
                continue
            for nxt in raw_lines[li + 1:]:
                s2 = nxt.strip()
                if not s2:
                    continue
                m2 = re.match(r"^Until,?\s*(.+)$", s2, re.I)
                if m2:
                    untils[j] = m2.group(1).strip()
                break
    for li, raw in enumerate(raw_lines):
        line = raw.strip()
        if not line or line.startswith(";"):
            continue
        low = line.lower()
        if low.startswith("sleep "):
            try:
                secs = int(line[6:].split()[0]) / 1000.0
            except (ValueError, IndexError):
                continue
            if secs > 0:
                pending = {"mins": 0, "secs": round(secs, 3)}
            continue
        if low.startswith("run "):
            rows.append(dict(x="", y="", button="Launch App", additional=line[4:].strip(),
                             **pending))
            pending = {}
            continue
        if low.startswith("mousemove "):
            try:
                parts = [p.strip() for p in line[10:].split(",")]
                rows.append(dict(x=parts[0], y=parts[1], button="Move Mouse",
                                 additional="", **pending))
            except (IndexError, ValueError):
                pass
            pending = {}
            continue
        if low.startswith("mouseclick "):
            try:
                parts = [p.strip() for p in line[11:].split(",")]
                x, y = parts[1], parts[2]
                which = (parts[0] or "L").strip().upper()
                clicks = int(parts[3]) if len(parts) > 3 and parts[3].strip() else 1
            except (IndexError, ValueError):
                x = y = ""; which = "L"; clicks = 1
            btn_name = "Right Click" if which.startswith("R") else "Left Click"
            if clicks >= 2:
                rows.append(dict(x=x, y=y, button="Double " + btn_name,
                                 additional="", **pending))
            else:
                rows.append(dict(x=x, y=y, button=btn_name, additional="", **pending))
            pending = {}
            continue
        if low.startswith("click ") or line == "click":
            try:
                parts = [p.strip() for p in line[6:].split(",")]
                x, y = (parts[0], parts[1]) if len(parts) >= 2 else ("", "")
                which = "R" if (len(parts) > 2 and parts[2].strip().upper().startswith("R")) else "L"
            except (IndexError, ValueError):
                x = y = ""; which = "L"
            rows.append(dict(x=x, y=y, button="Left Click" if which == "L" else "Right Click",
                             additional="", **pending))
            pending = {}
            continue
        if low.startswith(("send ", "sendinput ", "sendraw ")):
            body = line.split(" ", 1)[1].strip()
            for r2 in parse_send_keys(body):
                r2.update(pending)
                rows.append(r2)
            pending = {}
            continue
        # v2.8: ตัวแปร AHK → Set Variable (name := ค่า / name += จำนวน)
        m = re.match(r"^(\S+)\s*(:=|\+=|-=)\s*(.+)$", line)
        if m and re.fullmatch(_VAR_NAME, m.group(1), re.UNICODE):
            name, aop, val = m.group(1), m.group(2), m.group(3).strip()
            if aop == ":=":
                if re.fullmatch(r"-?\d+(?:\.\d+)?", val):
                    add_txt = "%s = %s" % (name, val)
                elif val.startswith('"') and val.endswith('"') and len(val) >= 2:
                    add_txt = "%s = %s" % (name, val[1:-1].replace('""', '"'))
                else:
                    add_txt = "%s = {%s}" % (name, val)   # อ้างตัวแปร AHK → {ตัวแปร}
            else:
                dv = val.strip('"') if val.startswith('"') else val
                add_txt = "%s %s %s" % (name, aop, dv)
            rows.append(dict(x="", y="", button="Set Variable", additional=add_txt,
                             **pending))
            pending = {}
            continue
        # v2.9: บล็อก AHK → Block Start/End — if (...) { / Loop, N { / Loop { / }
        m = re.match(r"^if\s+(?:\((.+)\)|(.+))\s*\{$", line, re.I)
        if m:
            cond = (m.group(1) or m.group(2) or "").strip()
            add_txt = ahk_cond_to_macro(cond)
            if "&&" in add_txt:
                add_txt = " && ".join(ahk_cond_to_macro(p.strip())
                                      for p in add_txt.split("&&"))
            add_txt = add_txt.strip()
            if add_txt and parse_block_spec("if " + add_txt) is not None:
                rows.append(dict(x="", y="", button=BLOCK_START,
                                 additional="if " + add_txt, **pending))
                pending = {}
            continue
        m = re.match(r"^Loop(,\s*(\d+))?\s*\{$", line, re.I)
        if m:
            add_txt = "max %s" % m.group(2) if m.group(2) else ""
            if li in untils:                      # Loop { … } Until cond → until
                u = ahk_cond_to_macro(untils[li])
                add_txt = ("until " + u + ((" " + add_txt) if add_txt else "")).strip()
            rows.append(dict(x="", y="", button=BLOCK_START, additional=add_txt,
                             **pending))
            pending = {}
            continue
        if line.startswith("}"):
            rows.append(dict(x="", y="", button=BLOCK_END, additional="", **pending))
            pending = {}
            continue
        # v2.8: เงื่อนไข AHK → If Variable (if (n > 5) / if x > 5 / if x contains ข้อความ)
        m = re.match(r"^if\s+(?:\((.+)\)|(.+))\s*$", line, re.I)
        if m:
            cond = (m.group(1) or m.group(2) or "").strip()
            if cond:
                add_txt = ahk_cond_to_macro(cond)
                # รับเฉพาะรูปแบบ If Variable (ชื่อ + ตัวดำเนินการ + ค่า) — นิพจน์อื่นข้าม
                if re.fullmatch(r"\s*%s\s*(==|!=|>=|<=|>|<|=|~)\s*\S.*" % _VAR_NAME,
                                add_txt, re.UNICODE | re.S):
                    rows.append(dict(x="", y="", button=IF_VAR, additional=add_txt,
                                     **pending))
                    pending = {}
            continue
        # บรรทัดอื่น (assign ธรรมดา, label, hotkey ฯลฯ) = ข้าม
    return rows


def ahk_cond_to_macro(cond):
    """แปลงเงื่อนไข AHK (v2.8) → Additional ของ If Variable — แปลไม่ได้คืนข้อความเดิม
    รองรับ: n > 5 / n = "ข้อความ" / x == y / n contains "ข้อความ" / InStr(n, "ข้อความ")"""
    s = str(cond or "").strip()
    m = re.fullmatch(r"InStr\(\s*(%s)\s*,\s*(.+?)\s*\)" % _VAR_NAME, s, re.I | re.UNICODE)
    if m:
        val = m.group(2).strip()
        if val.startswith('"') and val.endswith('"') and len(val) >= 2:
            val = val[1:-1].replace('""', '"')
        return "%s ~ %s" % (m.group(1), val)
    m = re.fullmatch(r"(%s)\s*(==|!=|>=|<=|>|<|=)\s*(.+)" % _VAR_NAME, s, re.UNICODE)
    if m:
        val = m.group(3).strip()
        if val.startswith('"') and val.endswith('"') and len(val) >= 2:
            val = val[1:-1].replace('""', '"')
        op = m.group(2)
        if op == "=":
            op = "="                           # AHK เดิมใช้ = เชิงเปรียบเทียบ — คงรูปเดิม
        return "%s %s %s" % (m.group(1), op, val)
    m = re.fullmatch(r"(%s)\s+contains\s+(.+)" % _VAR_NAME, s, re.I | re.UNICODE)
    if m:
        val = m.group(2).strip()
        if val.startswith('"') and val.endswith('"') and len(val) >= 2:
            val = val[1:-1].replace('""', '"')
        return "%s ~ %s" % (m.group(1), val)
    return s


def parse_queue_list(list_path):
    """แยกไฟล์ลิสต์คิว .txt → รายการ (พาธสคริปต์เต็ม, เลขบรรทัด) (v2.12 — แหล่งเดียว
    ใช้ทั้ง CLI --queue และหน้าต่าง ▶️ Run Queue): บรรทัดละพาธ · ข้าม #comment และ
    บรรทัดว่าง · พาธสัมพัทธ์อิงโฟลเดอร์ของไฟล์ลิสต์
    คืน (scripts, error) — scripts = [(normpath, line_no)] · error = ข้อความเมื่อ
    ไม่พบไฟล์ลิสต์/อ่านไม่สำเร็จ/ลิสต์ว่าง (None = สำเร็จ)"""
    if not os.path.isfile(list_path):
        return [], "ไม่พบไฟล์ลิสต์: %s" % list_path
    try:
        with open(list_path, encoding="utf-8-sig") as fh:
            raw_lines = fh.read().splitlines()
    except OSError as exc:
        return [], "อ่านไฟล์ลิสต์ไม่สำเร็จ: %s" % exc
    base_dir = os.path.dirname(os.path.abspath(list_path))
    scripts = []
    for line_no, ln in enumerate(raw_lines, 1):
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        p = s if os.path.isabs(s) else os.path.join(base_dir, s)
        scripts.append((os.path.normpath(p), line_no))
    if not scripts:
        return [], "ไฟล์ลิสต์ว่าง — ไม่มีสคริปต์ให้เล่น"
    return scripts, None


def validate_rows(rows, plugin_names=(), condition_names=()):
    """ตรวจแถวสคริปต์โดยไม่เล่น (v2.4 — ใช้โดย CLI --validate)
    v2.13: condition_names = ชื่อเงื่อนไข plugin (CONDITION_NAME) — แถว Action ที่ตรงชื่อนี้
    ผ่านการตรวจได้ด้วย (รูปแบบ Additional ตรวจใน plugin เอง)
    คืน list ของ (ลำดับแถว 1-based, เหตุผล) — ว่าง = สคริปต์พร้อมเล่น"""
    issues = []
    plugin_names = set(plugin_names or ())
    condition_names = set(condition_names or ())
    for i, r in enumerate(rows, 1):
        btn = str(r.get("button", ""))
        add = str(r.get("additional") or "")
        if (btn not in ACTIONS_ALL and btn not in plugin_names
                and btn not in condition_names):
            issues.append((i, "ไม่รู้จัก action: %s" % (btn or "-")))
            continue
        if btn == BLOCK_END and add.strip():
            issues.append((i, "Block End ไม่รับ Additional (เว้นว่าง)"))
        if btn in KEY_ACTIONS and not (parse_key(add) or parse_key_combo(add)):
            issues.append((i, "คีย์ไม่ถูกต้อง: %s" % (add or "-")))
        elif btn == "Launch App" and not add.strip():
            issues.append((i, "Launch App ต้องระบุพาธ/URL"))
        elif btn == "Set Variable" and not parse_set_var(add):
            issues.append((i, "Set Variable รูปแบบไม่ถูก (name = ค่า หรือ name += จำนวน)"))
        elif btn == "Read Clipboard" and not re.fullmatch(_VAR_NAME, add.strip() or ""):
            issues.append((i, "Read Clipboard ต้องระบุชื่อตัวแปร เช่น mytext"))
        elif btn in (IMAGE_ACTION, "Wait for Image", IF_IMAGE, ELSE_IMAGE):
            # v2.5.4: If Image ใช้ && ได้ — ตรวจภาพชิ้นแรก (ตัด timeout token ก่อน)
            # แล้วตรวจชิ้นย่อยที่เหลือตามประเภท (สีจุด / ตัวแปร)
            head, extra = add, []
            if btn in (IF_IMAGE, ELSE_IMAGE):
                raw, _w = parse_wait_timeout(add, 0)
                parts = split_condition_and(raw)
                head = parts[0] if parts else raw
                extra = parts[1:]
            p = parse_search_area(head)[0] if head.strip() else ""
            p = resolve_image_path(p) if p else ""
            if not p or not os.path.isfile(p):
                issues.append((i, "ไม่พบไฟล์ภาพ: %s" % (add or "-")))
            elif btn == IF_IMAGE:
                bad = [q for q in extra if parse_if_var(q) is None
                       and not parse_pixel_spec(q)]
                if bad:
                    issues.append((i, "If Image เงื่อนไขรวมรูปแบบไม่ถูก: %s" % bad[0]))
        elif btn == IF_PIXEL:
            # v2.5.4: ชิ้นแรกต้องเป็นสีจุด, ชิ้นถัดไปเป็นสีจุดหรือตัวแปรก็ได้ (ตาม runner)
            parts = split_condition_and(add) or [add]
            bad = (not parse_pixel_spec(parts[0])
                   or any(parse_if_var(p) is None and not parse_pixel_spec(p)
                          for p in parts[1:]))
            if bad:
                issues.append((i, "If Pixel Color รูปแบบไม่ถูก (ต้องเป็น x,y #rrggbb คั่น && ได้)"))
        elif btn == IF_VAR:
            if not all(parse_if_var(p) for p in (split_condition_and(add) or [add])):
                issues.append((i, "If Variable รูปแบบไม่ถูก (name = ค่า / name > ค่า / "
                                  "name ~ ข้อความ คั่น && ได้)"))
        elif btn == IF_LOOP:
            if not all(parse_if_loop(p) for p in (split_condition_and(add) or [add])):
                issues.append((i, "If Loop รูปแบบไม่ถูก (ต้องเป็นเลข >= 1 คั่น && ได้)"))
        elif btn == IF_TIME:
            if not all(parse_if_time(p) for p in (split_condition_and(add) or [add])):
                issues.append((i, "If Time รูปแบบไม่ถูก (ต้องเป็น HH:MM คั่น && ได้)"))
        elif btn == READ_PIXEL:
            parts = add.split()
            ok = (len(parts) == 2 and re.fullmatch(_VAR_NAME, parts[0])
                  and re.fullmatch(r"\d+\s*,\s*\d+", parts[1]))
            if not ok:
                issues.append((i, "Read Pixel Color ต้องเป็น 'ชื่อตัวแปร x,y' เช่น mytext 100,200"))
    # v2.6 (ชุด N2): โครงสร้างบล็อก — คู่เปิด/ปิด, depth, Additional ของ Block Start
    issues.extend(validate_blocks(rows))
    return issues


# ------------------------------------------------ plugin actions (v1.16) ----
def load_plugins(base_dir=None):
    """โหลด plugins จาก <base_dir>/plugins/*.py (v1.16 · v2.13 รองรับเงื่อนไข)
    Action plugin:    ACTION_NAME = "ชื่อ"      +  def run(ctx, row):
    Condition plugin: CONDITION_NAME = "ชื่อ"  +  def check(ctx, row) -> bool  (v2.13)
    ไฟล์เดียวประกาศทั้งคู่ได้ (ชื่อต้องต่างกัน) — คืน list ของ (ชื่อ Action, module) เหมือนเดิม
    รายการเงื่อนไข plugin อยู่ที่ load_plugins.last_conditions = [(ชื่อเงื่อนไข, module)]
    ชื่อซ้ำกันข้าม Action/เงื่อนไข (กันแถว btn ตีความกำกวม) = ข้ามไฟล์นั้นเหมือนไฟล์พัง
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
    out, conds, failed = [], [], []
    for path in sorted(glob.glob(os.path.join(d, "*.py"))):
        name = os.path.basename(path)[:-3]
        if name.startswith("_"):
            continue                                   # _xxx.py = ไม่ใช่ plugin
        try:
            sp = importlib.util.spec_from_file_location("macro_plugin_%s" % name, path)
            mod = importlib.util.module_from_spec(sp)
            sp.loader.exec_module(mod)
            aname = str(getattr(mod, "ACTION_NAME", "")).strip()
            cname = str(getattr(mod, "CONDITION_NAME", "")).strip()
            if not aname and not cname:
                raise ValueError("ต้องมี ACTION_NAME+run(ctx, row) หรือ "
                                 "CONDITION_NAME+check(ctx, row) (v2.13)")
            if aname:
                if not callable(getattr(mod, "run", None)):
                    raise ValueError("มี ACTION_NAME แต่ไม่มี run(ctx, row): " + aname)
                if (aname in ACTIONS_ALL or any(a == aname for a, _ in out)
                        or any(c == aname for c, _ in conds)):
                    raise ValueError("ชื่อ Action ซ้ำ: " + aname)
                out.append((aname, mod))
            if cname:
                if not callable(getattr(mod, "check", None)):
                    raise ValueError("มี CONDITION_NAME แต่ไม่มี check(ctx, row): " + cname)
                if (cname in ACTIONS_ALL or any(a == cname for a, _ in out)
                        or any(c == cname for c, _ in conds)):
                    raise ValueError("ชื่อเงื่อนไขซ้ำ: " + cname)
                conds.append((cname, mod))
        except Exception as exc:
            failed.append("%s: %s" % (name, exc))
    load_plugins.last_failed = failed
    load_plugins.last_conditions = conds
    return out


load_plugins.last_failed = []
load_plugins.last_conditions = []            # v2.13: [(ชื่อเงื่อนไข, module)] ล่าสุดที่โหลด


def match_condition_name(text, names):
    """จับชื่อเงื่อนไข plugin จากข้อความเงื่อนไข (v2.13) — คืน (ชื่อ, Additional) หรือ None
    รองรับทั้งชื่อเปล่า ("File Exists") และ "ชื่อ อาร์กิวเมนต์" ("File Exists C:\\tmp\\x")
    ชื่อยาวสุดมาก่อนกันชนชื่อซ้อนกัน (เช่น Check / Check Row)"""
    s = str(text or "").strip()
    if not s:
        return None
    for n in sorted(set(names or ()), key=len, reverse=True):
        if s == n:
            return (n, "")
        if s.startswith(n + " "):
            return (n, s[len(n) + 1:].strip())
    return None
MOD_KEYS = ["", "Ctrl", "Alt", "Shift", "Win"]
EDIT_COLS = ["Action", "Additional", "Mins", "Secs", "Repeat", "Note"]
COLS = ["chk", "num", "x", "y", "button", "additional", "mins", "secs", "repeat", "note"]


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


# ---------------------------------- นัดหมายหลายชุด (v2.7 — Roadmap ชุด C) --
def parse_hhmm_list(txt):
    """แปลงข้อความ HH:MM คั่น , → list เวลาสะอาด (v2.7) — รูปแบบใดพัง = ข้ามรายการนั้น
    คืน [] เมื่อไม่มีเวลาถูกต้องแม้แต่รายการเดียว (ผู้เรียกใช้เตือนเอง)
    ตัวอย่าง: '09:00, 12:30 , 22:00' → ['09:00', '12:30', '22:00']
    รับ list/tuple จาก JSON ได้โดยตรง (conf รูปแบบใหม่เก็บ times เป็น list)
    v2.8: รายการ "HH:MM=โปรไฟล์" ได้ — คืนเฉพาะเวลา (โปรไฟล์ดู sched_time_profiles)"""
    out = []
    if isinstance(txt, (list, tuple, set)):
        parts = [str(t) for t in txt]      # list จาก JSON — ห้าม str() ทั้งก้อน
    else:
        parts = str(txt or "").split(",")
    for part in parts:
        ent = parse_sched_entry(part)
        if ent and ent[0] not in out:
            out.append(ent[0])
    return out


def parse_sched_list(sched):
    """แยกค่า schedule หลายนัดหมาย (v2.7) — รับได้ทั้ง dict รูปแบบใหม่และ str รูปแบบเก่า
    คืน (mode, every, times, profile):
      mode    = "off" / "interval" / "daily"
      every   = จำนวนนาที (1-1440, โหมด interval)
      times   = list HH:MM ที่ถูกต้อง (โหมด daily — ว่างได้ = ยังไม่ตั้งเวลา)
      profile = ชื่อโปรไฟล์ ("" = งานที่เปิดค้าง)
    รูปแบบพัง/ไม่รู้จัก = ปิดอยู่ ("off", 10, [], "") — โปรแกรมต้องไม่พังเสมอ"""
    if isinstance(sched, str):
        s = sched.strip()
        if s in ("interval", "daily"):
            return (s, 10, [], "")            # รูปแบบเก่าที่ยังไม่ migrate — ใช้ค่าเริ่มต้น
        return ("off", 10, [], "")
    if not isinstance(sched, dict):
        return ("off", 10, [], "")
    mode = sched.get("mode")
    mode = mode if mode in ("interval", "daily") else "off"
    try:
        every = max(1, min(1440, int(sched.get("every", 10))))
    except (TypeError, ValueError):
        every = 10
    times = parse_hhmm_list(sched.get("times") or "") if mode == "daily" else []
    prof = sched.get("profile") or ""
    prof = prof if isinstance(prof, str) else ""
    return (mode, every, times, prof)


def sched_migrate(mode, every, at, profile):
    """แปลงค่า schedule เก่า (v1.19-v2.6: sched_mode/every/at/profile แยกกัน) → dict ใหม่ (v2.7)
    ทำงานร่วมได้ทั้งสองทิศ: ผ่าน dict มาแล้ว = คืนตามเดิม (normalize ปลอดภัย)"""
    if isinstance(mode, dict):
        m, e, t, p = parse_sched_list(mode)
        return {"mode": m, "every": e, "times": list(t), "profile": p}
    m = mode if mode in ("interval", "daily") else "off"
    try:
        e = max(1, min(1440, int(every)))
    except (TypeError, ValueError):
        e = 10
    t = parse_hhmm_list(at) if m == "daily" else []
    if m == "daily" and not t:
        m = "off"                               # เวลาพังหมด = ไม่มีนัดหมายให้ทำงาน
    p = profile if isinstance(profile, str) else ""
    return {"mode": m, "every": e, "times": t, "profile": p}


def re_match_hhmm(txt):
    """เช็ครูปแบบเวลา HH:MM (00:00–23:59)"""
    return bool(re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", (txt or "").strip()))


def parse_sched_entry(t):
    """แยกนัดหมายรายเวลา (v2.8) — "HH:MM" หรือ "HH:MM=ชื่อโปรไฟล์"
    คืน (เวลา, โปรไฟล์) — โปรไฟล์ว่าง = เล่นงานที่เปิดค้าง, รูปแบบพัง = None"""
    s = str(t or "").strip()
    if "=" in s:
        t2, prof = s.split("=", 1)
        t2, prof = t2.strip(), prof.strip()
    else:
        t2, prof = s, ""
    if not re_match_hhmm(t2):
        return None
    return (t2, prof)


def sched_time_profiles(times):
    """แตกรายการเวลาของโหมด daily → [(HH:MM, โปรไฟล์)] (v2.8)
    รับได้ทั้ง "08:00" และ "08:00=งานเช้า" — รายการพังข้าม ไม่มีวันพังโปรแกรม"""
    out = []
    for t in times or []:
        ent = parse_sched_entry(t)
        if ent:
            out.append(ent)
    return out


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


# ------------- เครื่องมือ log: เก็บถาวรรายเดือน / เคลียร์วันเก่า (v2.11) --
# log ปกติหมุนตัด 500 บรรทัดรายวัน — งานที่อยากเก็บย้อนนานกว่านั้นย้ายลง log_archive/
# แยกโฟลเดอร์รายเดือน (YYYY-MM มาจากวันที่ในชื่อไฟล์) เก็บไว้ตลอดไปได้
LOG_ARCHIVE_DIR = "log_archive"
_LOG_DAY_RE = re.compile(r"^(?:macro_log_|dry_report_)(\d{4}-\d{2}-\d{2})\.txt$")


def log_archive_path(base_dir=None):
    """โฟลเดอร์เก็บ log ถาวร <base_dir>/log_archive/ (patch ฟังก์ชันนี้ใน unit tests)"""
    return os.path.join(base_dir or os.path.dirname(os.path.abspath(__file__)),
                        LOG_ARCHIVE_DIR)


def cleanup_old_logs(base_dir=None, keep_days=None, archive=True, today=None):
    """จัดการไฟล์ log/dry-report วันเก่า (v2.11) — แหล่งเดียวที่ GUI/ปิดโปรแกรมใช้ร่วมกัน
    keep_days = None จัดการทุกไฟล์ที่ไม่ใช่วันนี้ · ตัวเลข N = เก็บไว้ N วันล่าสุด
    archive = True ย้ายลง log_archive/YYYY-MM/ (เก็บถาวร) · False = ลบทิ้ง
    ไฟล์ของ "วันนี้" ไม่แตะเสมอ (ยังเขียนอยู่) · คืน (จำนวนไฟล์, โหมด)
    ทน error ทุกจุด — ของรองห้ามทำโปรแกรมพัง (กฎเดียวกับ backup)"""
    mode = "archive" if archive else "delete"
    n = 0
    try:
        d = base_dir or os.path.dirname(os.path.abspath(__file__))
        today = today or datetime.date.today()
        if keep_days is None:
            cutoff = today                          # ทุกไฟล์ที่ไม่ใช่วันนี้
        else:
            cutoff = today - datetime.timedelta(days=max(0, int(keep_days)))
        files = sorted(glob.glob(os.path.join(d, "macro_log_*.txt"))) + \
            sorted(glob.glob(os.path.join(d, "dry_report_*.txt")))
        for f in files:
            m = _LOG_DAY_RE.match(os.path.basename(f))
            if not m:
                continue                            # ชื่อไม่ตรงรูปแบบ — ไม่แตะ (กันไฟล์อื่น)
            try:
                day = datetime.date.fromisoformat(m.group(1))
            except ValueError:
                continue
            if day >= cutoff:
                continue                            # ยังไม่หมดอายุ (วันนี้อยู่ในเงื่อนไขนี้ด้วย)
            try:
                if archive:
                    dest_dir = os.path.join(log_archive_path(d),
                                            day.strftime("%Y-%m"))
                    os.makedirs(dest_dir, exist_ok=True)
                    dest = os.path.join(dest_dir, os.path.basename(f))
                    if not os.path.isfile(dest):    # ปลายทางมีแล้ว = ข้าม ไม่ทับ
                        shutil.move(f, dest)
                        n += 1
                else:
                    os.remove(f)
                    n += 1
            except OSError:
                pass
    except Exception:
        pass
    return n, mode


# ---------------------------- รายงาน Dry-run เป็นไฟล์ (v2.10.1) ----
# Dry-run (v2.10) รายงานแต่ละแถวขึ้นจอ/คอนโซลแบบสด — งานยาว/ค้างคืนอยากอ่านย้อน
# จึงเก็บสำเนาลง dry_report_วันที่.txt เรียงเส้นทางเงื่อนไข + สรุปจำนวนแถวที่ "จะทำจริง"
_DRY_SUMMARY_MAX = 12          # จำนวน action สูงสุดที่แสดงในสรุปท้ายรายงาน


def dry_report_filename():
    """ชื่อไฟล์รายงาน Dry-run ของ "วันนี้" (หมุนรายวัน) เช่น dry_report_2026-10-03.txt"""
    return "dry_report_%s.txt" % datetime.date.today().isoformat()


def dry_report_path():
    """พาธไฟล์รายงาน Dry-run ของวันนี้ (patch ฟังก์ชันนี้ใน unit tests เพื่อย้ายที่เก็บ)"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), dry_report_filename())


def dry_report_summary(dry_lines):
    """สรุปจำนวนแถวที่จะทำจริงจากบรรทัด "DRY-RUN: …" — คืน list ของข้อความ
    "Left Click ×4" เรียงจากมากไปน้อย (นับจากชื่อ action ที่ปรากฏในบรรทัด)
    อ่านจาก _DRY_ACTIONS เท่านั้น — เรียงยาว→สั้นกันชนกัน (Double Left Click ก่อน Left Click)"""
    acts = sorted(_DRY_ACTIONS, key=len, reverse=True)
    counts = {}
    for line in dry_lines:
        s = str(line)
        for a in acts:
            if a in s:
                counts[a] = counts.get(a, 0) + 1
                break
    return ["%s ×%d" % (a, n) for a, n in
            sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]


def dry_report_block(script, n_rows, n_loops, dry_lines, finished=True, extra=""):
    """สร้างบล็อกรายงาน Dry-run (pure — คืน list ของบรรทัด ไม่เขียนไฟล์ เทสต์ง่าย)
    script = ชื่อ/พาธสคริปต์ · n_rows = แถวที่จะเล่น · n_loops = จำนวนรอบ ("ไม่จำกัด" ได้)
    finished=False = ถูกหยุดกลางคัน (รายงานเส้นทางที่เดินผ่านถึงจุดหยุด)"""
    now = datetime.datetime.now().strftime("%H:%M:%S")
    out = ["===== DRY-RUN %s — %s =====" % (now, os.path.basename(str(script or "")))]
    head = "สคริปต์: %s · แถวที่จะเล่น: %s · รอบ: %s" % (script or "-", n_rows, n_loops)
    if extra:
        head += " · " + extra
    out.append(head)
    if not dry_lines:
        out.append("(ไม่มีบรรทัดรายงาน — สคริปต์ไม่มีแถว input จริง หรือถูกหยุดก่อนเดิน)")
    else:
        out.extend(str(x) for x in dry_lines)
        sums = dry_report_summary(dry_lines)
        if sums:
            out.append("สรุปจะทำจริง: " + ", ".join(sums[:_DRY_SUMMARY_MAX])
                       + (" …" if len(sums) > _DRY_SUMMARY_MAX else ""))
    if not finished:
        out.append("(ถูกหยุดกลางคัน — เส้นทางด้านบนคือส่วนที่เดินผ่านจนถึงจุดหยุด)")
    out.append("===== จบรายงาน Dry-run =====")
    return out


def dry_report_write(lines, src=None, path=None):
    """เขียนบล็อกรายงาน Dry-run ต่อท้ายไฟล์ dry_report_วันที่.txt (ทนต่อทุก error —
    รายงานห้ามทำโปรแกรมพัง เหมือน log_write) — แต่ละบล็อกคั่นบรรทัดว่างอ่านง่าย
    v2.14: path= ระบุพาธเอง (CLI --dry-report PATH) — ไม่ใส่ = ไฟล์วันนี้เหมือนเดิม"""
    try:
        p = str(path) if path else dry_report_path()
        p = p.replace("{date}", datetime.date.today().isoformat())   # v2.14: {date} = วันที่วันนี้
        sep = ""
        if os.path.isfile(p) and os.path.getsize(p) > 0:
            sep = "\n"                       # มีรายงานเดิมแล้ว — คั่นบล็อกใหม่
        with open(p, "a", encoding="utf-8") as fh:
            fh.write(sep + "\n".join(str(x) for x in lines) + "\n")
        if src:
            log_write("DRY", "รายงาน Dry-run บันทึกแล้ว (%d บรรทัด)" % len(lines), src)
    except Exception:
        pass


# ============================== ActionRunner (v2.1 — phase 2) =================
# กลไก "ทำ 1 แถว" ของ player ทั้ง GUI และ CLI — เครื่องมือล้วน ไม่มี Tk
# GUI/CLI ส่ง controller (mouse/kb) + callbacks เข้ามา แล้ว runner จัดการเอง
class ActionRunner:
    """ทำ 1 แถวสคริปต์ — แหล่งเดียวของกลไก execute (GUI และ CLI ใช้ร่วมกัน, v2.1)

    พารามิเตอร์: mouse_ctl/kb_ctl (pynput Controller), stop_check() → False เมื่อหยุด,
    on_beep(), on_message(text, color), on_clipboard_set(text), on_clipboard_read(),
    variables (dict ตัวแปร), plugin_lookup(name) → module/None, log_src,
    unsupported_cb(btn) (เรียกเมื่อ action ไม่รองรับ)
    สถานะ: pressed_keys/pressed_btns (ปล่อยด้วย release_all), saved_pos, last_if_found
    """

    def __init__(self, mouse_ctl, kb_ctl, stop_check=lambda: True,
                 on_beep=lambda: None, on_message=lambda t, c="#080": None,
                 on_clipboard_set=lambda t: None, on_clipboard_read=lambda: None,
                 variables=None, plugin_lookup=lambda name: None,
                 log_src=None, unsupported_cb=lambda btn: None,
                 find_image_cb=None, wait_image_cb=None, dry_run=False,
                 conditions=None):
        """dry_run=True (v2.10): เดินทุกแถว/เงื่อนไข/ตัวแปร/บล็อกครบ — แต่ input จริงทุกชนิด
        (เมาส์/คีย์/เปิดแอป/คลิปบอร์ด/บี๊บ/plugin) ถูกแทนด้วยข้อความรายงานผ่าน on_message
        — ใช้ซ้อมสคริปต์ก่อนปล่อยค้างคืน ไม่แตะเมาส์/คีย์สักครั้ง
        conditions (v2.13): dict {ชื่อเงื่อนไข → module} ของ condition plugins
        (CONDITION_NAME + check(ctx, row)) — ใช้ทั้งแถวเงื่อนไขและ Block Start/End"""
        self.mouse_ctl = mouse_ctl
        self.kb_ctl = kb_ctl
        self.dry_run = bool(dry_run)
        self.conditions = conditions if conditions is not None else {}   # v2.13
        self.stop_check = stop_check
        self.on_beep = on_beep
        self.on_message = on_message
        self.on_clipboard_set = on_clipboard_set
        self.on_clipboard_read = on_clipboard_read
        self.variables = variables if variables is not None else {}
        self.plugin_lookup = plugin_lookup
        self.log_src = log_src
        self.unsupported_cb = unsupported_cb
        self.find_image_cb = find_image_cb        # v2.2: ค้นภาพ (GUI/CLI ผูกเข้ามา)
        self.wait_image_cb = wait_image_cb        # v2.2: รอภาพ (GUI/CLI ผูกเข้ามา)
        self.pressed_keys = set()
        self.pressed_btns = set()
        self.saved_pos = None
        self.last_if_found = None
        self.skip_n = 0                           # v2.2: แถวที่ If Image/Else สั่งข้าม

    def _save_cond_result(self, hit):
        """v2.10: แถวเงื่อนไขระบุ '>ชื่อ' = เก็บผล '1'/'0' ลงตัวแปร — แถวถัดไปอ่านต่อด้วย
        {ชื่อ} หรือ If Variable ได้ (ถูกแทนค่าก่อนเล่นทุกแถวอยู่แล้ว — ห่วงโซ่เงื่อนไขได้เลย)
        เคลียร์ self.cond_store ทุกครั้ง — แถวเงื่อนไขถัดไปที่ไม่ระบุโทเคนต้องไม่เก็บค้าง"""
        name = getattr(self, "cond_store", None)
        self.cond_store = None
        if name:
            self.variables[name] = "1" if hit else "0"
            self.on_message("→ เก็บผลเงื่อนไข %s = %s"
                            % (name, self.variables[name]))

    def release_all(self):
        """ปล่อยคีย์/ปุ่มเมาส์ที่กดค้าง (เรียกตอนหยุด — กัน Ctrl ติด)"""
        try:
            for k in list(self.pressed_keys):
                self.kb_ctl.release(k)
            self.pressed_keys.clear()
            for b in list(self.pressed_btns):
                self.mouse_ctl.release(b)
            self.pressed_btns.clear()
        except Exception:
            pass

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
            if str(r.get("x", "")) != "" and str(r.get("y", "")) != "":
                self.mouse_ctl.position = (int(r["x"]), int(r["y"]))
                time.sleep(0.03)
            self.mouse_ctl.click(Button.right if "Right" in r["button"] else Button.left, 1)
        finally:
            for k in reversed(pressed):
                self.kb_ctl.release(k)

    def _find_image_pos(self, r):
        """พิกัดกึ่งกลางภาพที่เจอ หรือ None — GUI ผูก find_image_cb เข้ามา (กันซ้ำ logic opencv)"""
        cb = getattr(self, "find_image_cb", None)
        return cb(r) if cb else None

    def _do_wait_for_image(self, r):
        """รอภาพปรากฏ — ผูก wait_image_cb จากฝั่ง GUI/CLI (runner เป็นจุด dispatch)"""
        cb = getattr(self, "wait_image_cb", None)
        if cb:
            cb(r)

    def _do_wait_for_pixel(self, r):
        """รอจุดสี — runner ตรวจครั้งเดียว (โปรแกรมเรียกวนเองด้วย stop_check ได้)"""
        sp = parse_pixel_spec(r.get("additional"))
        if not sp:
            self.on_message("Wait for Pixel Color: รูปแบบ Additional ไม่ถูกต้อง (ต้องเป็น x,y #rrggbb)", "#c00")
            return False
        x, y, rgb = sp
        okc = color_close(pixel_color_at(x, y), rgb)
        if okc:
            self.on_message("Wait for Pixel Color: เจอสีที่รอ (%d,%d)" % (x, y))
        else:
            self.on_message("Wait for Pixel Color: สีไม่ตรง (%d,%d) — ข้ามการรอ" % (x, y))
        return okc

    def _plugin_ctx(self):
        """ctx ของ plugin (v1.16/v1.20/v2.5) — แหล่งเดียว ใช้ทั้ง Action และเงื่อนไข (v2.13)"""
        return {"mouse": self.mouse_ctl, "kb": self.kb_ctl,
                "log": lambda m: log_write("PLUGIN", m, self.log_src),
                "cfg": {"lang": "th"},
                "vars": self.variables,                        # v2.5: ตัวแปรแชร์กับสคริปต์
                "stop_check": self.stop_check,                  # v1.20
                "ui": {"msg": lambda text, color="#080":
                           self.on_message(str(text), color),      # v1.20
                       "beep": self.on_beep}}

    def _match_cond(self, text):
        """หา condition plugin จากข้อความ (v2.13) — คืน (module, ชื่อ, Additional) หรือ None"""
        m = match_condition_name(text, (self.conditions or {}).keys())
        if m is None:
            return None
        mod = (self.conditions or {}).get(m[0])
        if mod is None or not callable(getattr(mod, "check", None)):
            return None
        return (mod, m[0], m[1])

    def _run_cond_check(self, mod, name, additional):
        """เรียก check(ctx, row) ของ condition plugin (v2.13) — คืน True/False
        check พัง = เตือนแล้วถือว่าไม่จริง (ใช้โดย Block Start/End — ตามกติกาบล็อก
        ที่รูปแบบ/การประเมินพัง = ไม่จริง; ฝั่งแถวเงื่อนไขใช้ evaluate_plugin_condition
        ซึ่งทนเองแล้วเล่นต่อ)"""
        ctx = self._plugin_ctx()
        row = {"button": name, "additional": additional,
               "x": "", "y": "", "mins": 0, "secs": 0, "repeat": 1}
        try:
            return bool(mod.check(ctx, row))
        except Exception as exc:
            self.on_message("condition plugin error (%s): %s" % (name, exc), "#c00")
            return False

    def evaluate_plugin_condition(self, btn, r):
        """ประเมินแถวเงื่อนไขของ condition plugin (v2.13) — กติกาเดียวกับเงื่อนไขทุกชนิด:
        จริง = เล่นต่อ · ไม่จริง = ข้าม N แถว (N = Repeat) · โทเคน '>ชื่อ' ท้าย Additional
        = เก็บผลเงื่อนไขลงตัวแปร (เหมือนเงื่อนไขในตัว v2.10)
        คืน (skip_n, message) — ไม่ใช่เงื่อนไข plugin → (0, None)
        check พัง = เตือนแล้วเล่นต่อ ไม่ข้าม (กลไกเดียวกับ action plugin พัง)
        Dry-run: เงื่อนไขเดินจริงอยู่แล้ว — check ของ plugin ก็ถูกเรียกจริง (v2.10)"""
        mod = (self.conditions or {}).get(str(btn))
        if mod is None or not callable(getattr(mod, "check", None)):
            return 0, None
        _add, store = parse_cond_store(str(r.get("additional") or ""))
        try:
            hit = bool(mod.check(self._plugin_ctx(), dict(r, button=btn)))
        except Exception as exc:
            self.on_message("condition plugin error (%s): %s" % (btn, exc), "#c00")
            return 0, None
        self.cond_store = store
        self._save_cond_result(hit)
        if hit:
            return 0, "%s → เงื่อนไขจริง เล่นต่อ" % btn
        skip = parse_int(r.get("repeat"), 1)
        return skip, "%s → เงื่อนไขไม่จริง ข้าม %d แถว" % (btn, skip)

    @staticmethod
    def evaluate_if_var(txt, variables=None):
        """ตัดสินเงื่อนไข If Variable เป็นค่าความจริง (v2.5.4 — ชุด N1 ใช้ร่วมกับ AND)
        คืน (hit, detail) หรือ (None, detail) เมื่อรูปแบบไม่ถูก
        กติกาเดิมทุกอย่าง: ไม่มีตัวแปร = ไม่จริง · เทียบเลขได้เมื่อสองฝั่งเป็นตัวเลข"""
        spec = parse_if_var(txt)
        if spec is None:
            return None, ("If Variable %s → รูปแบบไม่ถูก (name = ค่า / name > ค่า / "
                          "name ~ ข้อความ)" % (txt or ""))
        name, op, val = spec
        variables = variables if variables is not None else {}
        cur = str(variables.get(name, ""))
        if name not in variables:
            return False, "If Variable: ไม่มีตัวแปร '%s' → ไม่จริง" % name
        hit = False
        try:
            a_num, b_num = float(cur), float(val)
        except (TypeError, ValueError):
            a_num = b_num = None
        if op in (">", ">=", "<", "<="):
            if a_num is None or b_num is None:
                return False, ("If Variable: %s %s %s → เปรียบเทียบตัวเลขไม่ได้ "
                               "(ค่าปัจจุบัน %r) → ไม่จริง" % (name, op, val, cur))
            hit = {">": a_num > b_num, ">=": a_num >= b_num,
                   "<": a_num < b_num, "<=": a_num <= b_num}[op]
        elif op in ("=", "!="):
            eq = (a_num == b_num) if (a_num is not None and b_num is not None
                                      and val.strip() != "") else (cur == val)
            hit = eq if op == "=" else not eq
        else:                                      # "~" = มีข้อความย่อย
            hit = val in cur
        return hit, "If Variable: %s %s %s → %s" % (name, op, val, "จริง" if hit else "ไม่จริง")

    @staticmethod
    def evaluate_if_pixel(parts, variables=None):
        """ตัดสินเงื่อนไขสีจุดเป็นค่าความจริง (v2.5.4 — ชุด N1 ใช้ร่วมกับ AND)
        parts = list ชิ้นย่อย (เช่น ["300,300 #ffffff"]) ทั้งหมดต้องตรง = จริง (AND)
        คืน (hit, detail) — รูปแบบไม่ถูก = (None, detail) เพื่อให้ฝั่งเรียกเตือน/เล่นต่อ"""
        variables = variables if variables is not None else {}
        parts = parts or []
        if not parts:
            return None, "If Pixel Color: รูปแบบไม่ถูก (ต้องเป็น x,y #rrggbb)"
        for part in parts:
            sp = parse_pixel_spec(part)
            if not sp:
                return None, "If Pixel Color: รูปแบบไม่ถูก (%s)" % part
            x, y, rgb = sp
            hit = color_close(pixel_color_at(x, y), rgb)
            if not hit:
                return False, "If Pixel Color: สีจุด (%d,%d) ไม่ตรง" % (x, y)
        return True, "If Pixel Color: สีจุดตรงทุกจุด → จริง"

    def evaluate_block_condition(self, spec_text):
        """ตัดสินเงื่อนไขของ Block Start/End ให้ BlockRunner (v2.6 — ชุด N2)
        รองรับชุดเดียวกับเงื่อนไขทั้งหมด: สีจุด / ตัวแปร / ภาพ (&& ผสมได้ตาม N1)
        จำแนกจากชิ้นแรก: parse_pixel_spec → สายสี, parse_if_var → สายตัวแปร,
        อื่น ๆ = สายภาพ (ไม่เจอไฟล์/ไม่เจอบนจอ = False — เหมือน If Image)
        ชิ้นใด "รูปแบบไม่ถูก" (None) = แถวนี้ไม่จริง (False) — เหมือน If Variable ไม่มีตัวแปร
        คืน True/False"""
        s = str(spec_text or "").strip()
        if not s:
            return True
        parts = split_condition_and(s) or [s]
        head = parts[0]
        if parse_pixel_spec(head):                     # สายสีจุด (ผสมตัวแปรได้)
            for p in parts:
                if parse_pixel_spec(p):
                    _h, _d = self.evaluate_if_pixel([p], self.variables)
                else:
                    _h, _d = self.evaluate_if_var(p, self.variables)
                if _h is not True:
                    return _h if _h is None else False
            return True
        if parse_if_var(head):                         # สายตัวแปรล้วน
            for p in parts:
                _h, _d = self.evaluate_if_var(p, self.variables)
                if _h is not True:
                    return _h if _h is None else False
            return True
        head_m = self._match_cond(head)                # สายเงื่อนไข plugin (v2.13)
        if head_m is not None:                         # ชิ้นแรกตรงชื่อ CONDITION_NAME
            for p in parts:
                mm = self._match_cond(p)
                if mm is not None:
                    hit = self._run_cond_check(mm[0], mm[1], mm[2])
                elif parse_pixel_spec(p):
                    hit, _d = self.evaluate_if_pixel([p], self.variables)
                else:
                    hit, _d = self.evaluate_if_var(p, self.variables)
                if hit is not True:                    # ไม่จริง/รูปแบบพัง = ตามกติกาเดิม
                    return hit if hit is None else False
            return True
        # สายภาพ (default): ชิ้นแรกคือไฟล์ภาพ — เจอก่อนแล้วค่อยตรวจชิ้นถัดไป
        rr = {"button": IF_IMAGE, "additional": head}
        pos = self._find_image_pos(rr)
        if pos is None:
            return False
        self.variables["img_x"] = pos[0]
        self.variables["img_y"] = pos[1]
        for p in parts[1:]:
            if parse_pixel_spec(p):
                _h, _d = self.evaluate_if_pixel([p], self.variables)
            else:
                _h, _d = self.evaluate_if_var(p, self.variables)
            if _h is not True:
                return _h if _h is None else False
        return True

    @staticmethod
    def evaluate_condition(btn, additional, repeat, n_loop, now=None, variables=None):
        """ประเมินแถวเงื่อนไข If Loop / If Time / If Variable (v2.1, If Variable = v2.5)
        คืน (skip_n, message):
          ไม่ใช่เงื่อนไขที่รองรับ → (0, None)
          ยังไม่ถึงรอบ/เวลา → (0, ข้อความ "เล่นต่อ")
          ถึงรอบ/ผ่านเวลา → (จำนวนแถวที่ข้าม = Repeat, ข้อความ "ข้าม N แถว")
          Additional ไม่ถูก → (0, ข้อความเตือน)
        v2.10: โทเคน '>ชื่อ' ท้าย Additional = เก็บผลเงื่อนไข "1"/"0" ลงตัวแปรชื่อนั้น
        (ผ่าน dict variables ที่ส่งเข้ามา — เมธอดนี้เป็น staticmethod ไม่มี self)"""
        variables = variables if variables is not None else {}
        # v2.10: ดึงโทเคนเก็บผลออกก่อน parse (เช่น "3 >รอบเก็บ" → เงื่อนไข "3")
        additional, cond_store = parse_cond_store(additional)

        def _store(hit):
            if cond_store:
                variables[cond_store] = "1" if hit else "0"

        if btn == IF_LOOP:
            # v2.5.4 (ชุด N1): รองรับ && เช่น "3 && 10" — ถึงรอบตามทุกเลขจึงข้าม
            parts = split_condition_and(additional) or [additional]
            nums = []
            for p in parts:
                n = parse_if_loop(p)
                if n is None:
                    return 0, ("If Loop %s → Additional ไม่ถูก (ต้องเป็นเลข >= 1 คั่น && ได้) "
                               "เล่นต่อ" % (additional or ""))
                nums.append(n)
            not_yet = [n for n in nums if n_loop < n]
            if not_yet:
                _store(False)
                return 0, "If Loop %s → รอบที่ %d ยังไม่ถึง %d เล่นต่อ" % (
                    additional, n_loop, max(not_yet))
            skip = parse_int(repeat, 1)
            _store(True)
            return skip, "If Loop %s → รอบที่ %d >= %d ข้าม %d แถว" % (
                additional, n_loop, min(nums), skip)
        if btn == IF_TIME:
            # v2.5.4 (ชุด N1): รองรับ && เช่น "08:00 && 22:30" — ผ่านทุกเวลาจึงข้าม
            lt = now or time.localtime()
            parts = split_condition_and(additional) or [additional]
            specs = []
            for p in parts:
                spec = parse_if_time(p)
                if spec is None:
                    return 0, ("If Time %s → Additional ไม่ถูก (ต้องเป็น HH:MM คั่น && ได้) "
                               "เล่นต่อ" % (additional or ""))
                specs.append(spec)
            pending = [s for s in specs if (lt.tm_hour, lt.tm_min) < s]
            if pending:
                s = min(pending)
                _store(False)
                return 0, "If Time %02d:%02d → ยังไม่ถึง %02d:%02d เล่นต่อ" % (
                    lt.tm_hour, lt.tm_min, s[0], s[1])
            skip = parse_int(repeat, 1)
            s = max(specs)
            _store(True)
            return skip, "If Time %02d:%02d → ผ่านกำหนดแล้ว ข้าม %d แถว" % (
                s[0], s[1], skip)
        if btn == IF_VAR:
            # v2.5.4 (ชุด N1): รองรับ && เช่น "n > 5 && code = A-1" — ทุกเงื่อนไขต้องจริง
            parts = split_condition_and(additional) or [additional]
            details = []
            for p in parts:
                hit, detail = ActionRunner.evaluate_if_var(p, variables)
                if hit is None:                    # ชิ้นใดรูปแบบไม่ถูก → เตือนเล่นต่อ (เดิม)
                    return 0, detail + " เล่นต่อ"
                details.append(detail)
                if not hit:
                    skip = parse_int(repeat, 1)
                    _store(False)
                    return skip, " ".join(details) + " ข้าม %d แถว" % skip
            _store(True)
            return 0, " ".join(details) + " เล่นต่อ"
        return 0, None

    def execute(self, r):
        """ทำ action ตามแถว r — คืน False เฉพาะเมื่อ Type Text ถูกสั่งหยุดกลางคัน
        v2.10: dry_run=True → แถว input จริงถูกแทนด้วยข้อความรายงาน (ไม่แตะเมาส์/คีย์)"""
        btn = r.get("button", "")
        if self.dry_run and btn in _DRY_ACTIONS:
            add = str(r.get("additional") or "")
            self.on_message("DRY-RUN: จะ%s %s%s" % (
                _DRY_VERB.get(btn, "ทำ"), btn, (" " + add) if add else ""))
            if str(r.get("x", "")) != "" or str(r.get("y", "")) != "":
                self.on_message("DRY-RUN: ที่พิกัด %s,%s" % (r.get("x"), r.get("y")))
            return True
        if btn in BTN_TH:                                            # เมาส์ทั่วไป
            b, act = BTN_TH[btn]
            btn_obj = getattr(Button, b.lower())
            if str(r.get("x", "")) != "" and str(r.get("y", "")) != "":
                self.mouse_ctl.position = (int(r["x"]), int(r["y"]))
                time.sleep(0.03)
            if act == "Down":
                self.mouse_ctl.press(btn_obj)
                self.pressed_btns.add(btn_obj)      # จำไว้ปล่อยตอน STOP กลางคัน
            elif act == "Up":
                self.mouse_ctl.release(btn_obj)
                self.pressed_btns.discard(btn_obj)
            else:
                self.mouse_ctl.click(btn_obj, 1)
        elif btn in SCROLL_ACTIONS:                                  # เลื่อนล้อเมาส์
            try:
                notches = int(str(r.get("additional") or "1"))
            except ValueError:
                notches = 1
            self.mouse_ctl.scroll(0, notches if btn == "Scroll Up" else -notches)
        elif btn in DBL_ACTIONS:                                     # ดับเบิลคลิก
            if str(r.get("x", "")) != "" and str(r.get("y", "")) != "":
                self.mouse_ctl.position = (int(r["x"]), int(r["y"]))
                time.sleep(0.03)
            self.mouse_ctl.click(Button.right if "Right" in btn else Button.left, 2)
        elif btn in MOD_CLICKS:                                      # คลิก+modifier
            mods = [m for m in ("ctrl", "shift", "alt") if m.capitalize() in btn]
            self._do_mod_click(r, mods)
        elif btn == "Move Mouse":                                    # ย้ายเมาส์
            if str(r.get("x", "")) != "" and str(r.get("y", "")) != "":
                self.mouse_ctl.position = (int(r["x"]), int(r["y"]))
        elif btn == "Move Mouse by Offset":                          # ย้ายแบบสัมพัทธ์
            try:
                dx = int(str(r.get("x") or 0))
                dyo = int(str(r.get("y") or 0))
            except ValueError:
                dx = dyo = 0
            cx, cy = self.mouse_ctl.position
            self.mouse_ctl.position = (cx + dx, cy + dyo)
        elif btn == "Save Cursor":                                   # เซฟตำแหน่งเมาส์
            self.saved_pos = self.mouse_ctl.position
        elif btn == "Restore Cursor":                                # คืนตำแหน่งเมาส์
            if self.saved_pos:
                self.mouse_ctl.position = self.saved_pos
        elif btn == IMAGE_ACTION:                                    # คลิกตามภาพ
            pos = self._find_image_pos(r)
            if pos:
                self.variables["img_x"] = pos[0]     # v2.5: พิกัดที่เจอ → {img_x}/{img_y}
                self.variables["img_y"] = pos[1]
                self.mouse_ctl.position = pos
                time.sleep(0.03)
                self.mouse_ctl.click(Button.left, 1)
        elif btn == WAIT_PIXEL:                                      # รอจุดสี (v1.18)
            self._do_wait_for_pixel(r)
        elif btn == "Wait for Image":                                # รอภาพปรากฏ (v2.2: cb ผูกจาก GUI/CLI)
            self._do_wait_for_image(r)
        elif btn == IF_IMAGE:                                        # เงื่อนไขค้นภาพ (v2.2 — runner จัดการเอง)
            # v2.4: Additional ต่อท้ายด้วย "Ns" (เช่น "img.png 5s") = ตรวจซ้ำจนครบ 5 วิ
            # v2.5.4 (ชุด N1): รองรับเงื่อนไขรวม && เช่น "img.png && 300,300 #ffffff"
            # v2.10: โทเคน '>ชื่อ' ท้ายแถว = เก็บผลเงื่อนไข (ตัดออกก่อนแตก/ค้นภาพ)
            add0, _store_name = parse_cond_store(r.get("additional"))
            self.cond_store = _store_name
            raw, wait = parse_wait_timeout(add0, 0)
            parts = split_condition_and(raw)
            rr = dict(r, additional=(parts[0] if parts else raw))
            extra_parts = parts[1:] if parts else []
            deadline = time.time() + wait
            pos = self._find_image_pos(rr)
            while pos is None and time.time() < deadline and self.stop_check():
                time.sleep(0.25)
                pos = self._find_image_pos(rr)
            hit = pos is not None
            if hit and extra_parts:               # ส่วนย่อยอื่น ๆ ต้องจริงทุกชิ้น (AND)
                _pix = []                          # ชิ้นสีรวมกันตรวจครั้งเดียว
                for _p in extra_parts:
                    if parse_pixel_spec(_p):
                        _pix.append(_p)
                        continue
                    _h, _d2 = self.evaluate_if_var(_p, self.variables)
                    if _h is not True:            # ตัวแปรชิ้นไหนไม่จริง/พัง = ทั้งแถวไม่จริง
                        hit = False
                        break
                if hit and _pix:
                    _h, _d2 = self.evaluate_if_pixel(_pix, self.variables)
                    hit = (_h is True)
            self.last_if_found = hit
            self._save_cond_result(hit)           # v2.10: '>ชื่อ' เก็บผลลงตัวแปร
            if hit:
                self.on_message("If Image เจอ → เล่นต่อ")
                if pos is not None:               # ภาพที่เจอ (เฉพาะสายหลัก) ตั้ง {img_x}/{img_y}
                    self.variables["img_x"] = pos[0]
                    self.variables["img_y"] = pos[1]
            else:
                self.skip_n = parse_int(r.get("repeat"), 1)   # จำนวนแถวที่ข้าม = Repeat (กฎเดียว v1.21)
                self.on_message(("If Image ไม่เจอ" if not parts else
                                 "If Image ไม่เจอ/เงื่อนไขรวมไม่ครบ") + " → ข้าม %d แถว"
                                % self.skip_n, "#a60")
        elif btn == ELSE_IMAGE:                                      # ตัวแบ่งกลุ่ม A/B (v2.2)
            n = parse_int(r.get("repeat"), 1)
            if self.last_if_found:
                self.skip_n = n
                self.on_message("If เจอ → ข้ามกลุ่ม B %d แถว" % n, "#a60")
            else:
                self.on_message("If ไม่เจอ → เล่นกลุ่ม B ต่อ")
        elif btn == IF_PIXEL:                                        # เงื่อนไขสีจุด (v2.5)
            # v2.5.4 (ชุด N1): รองรับ && เช่น "300,300 #ffffff && 400,400 #000000"
            # v2.10: โทเคน '>ชื่อ' ท้ายแถว = เก็บผลเงื่อนไข (ตัดออกก่อนแตก)
            add0, _store_name = parse_cond_store(r.get("additional"))
            self.cond_store = _store_name
            raw, wait = parse_wait_timeout(add0, 0)
            parts = split_condition_and(raw) or [raw]
            if not parse_pixel_spec(parts[0]):
                self.on_message("If Pixel Color: รูปแบบไม่ถูก (ต้องเป็น x,y #rrggbb)", "#c00")
                return
            deadline = time.time() + wait
            hit, det = self.evaluate_if_pixel(parts, self.variables)
            while hit is False and time.time() < deadline and self.stop_check():
                time.sleep(0.25)
                hit, det = self.evaluate_if_pixel(parts, self.variables)
            if hit is None:                       # รูปแบบไม่ถูก → เตือนแล้วเล่นต่อ (เดิม)
                self.on_message(det, "#c00")
                return
            self._save_cond_result(bool(hit))     # v2.10: '>ชื่อ' เก็บผลลงตัวแปร
            if hit:
                self.on_message(det + " → เล่นต่อ")
            else:
                self.skip_n = parse_int(r.get("repeat"), 1)
                self.on_message("%s → ข้าม %d แถว" % (det, self.skip_n), "#a60")
        elif btn == READ_PIXEL:                                      # อ่านสีจุดเก็บตัวแปร (v2.5)
            parts = str(r.get("additional") or "").split()
            m = re.fullmatch(_VAR_NAME, parts[0]) if parts else None
            xy = None
            if m and len(parts) >= 2:
                try:
                    xy = tuple(int(p) for p in parts[1].split(","))
                except ValueError:
                    xy = None
            if not m or not xy or len(xy) != 2:
                self.on_message("Read Pixel Color: Additional ต้องเป็น 'ชื่อตัวแปร x,y' "
                                "เช่น mytext 100,200", "#c00")
                return
            rgb = pixel_color_at(*xy)
            self.variables[m.group(0)] = ("%02x%02x%02x" % tuple(rgb[:3])) if rgb else ""
            self.on_message("Read Pixel Color: %s = %s" % (
                m.group(0), self.variables[m.group(0)] or "(อ่านไม่ได้)"))
        elif btn == "Type Text":                                     # พิมพ์ข้อความ
            for ch in str(r.get("additional") or ""):
                if not self.stop_check():
                    return False
                if ch == "\n":
                    self.kb_ctl.tap(Key.enter)
                elif not send_unicode_char(ch):      # v1.20.2: ไม่ขึ้นกับ layout
                    self.kb_ctl.tap(KeyCode.from_char(ch))   # fallback (OS อื่น)
                time.sleep(0.015)                    # v1.20.3: กันแอป busy กลืน burst
        elif btn == "Launch App":                                    # เปิดแอป/เว็บ
            target = str(r.get("additional") or "").strip()
            if target:
                try:
                    os.startfile(target)      # Windows
                except (OSError, AttributeError):
                    import subprocess
                    opener = "open" if sys.platform == "darwin" else "xdg-open"
                    subprocess.Popen([opener, target])
        elif btn == "Beep":                                          # เสียงเตือน
            self.on_beep()
        elif btn in KEY_ACTIONS:                                     # คีย์บอร์ด
            combo = parse_key_combo(r.get("additional", ""))   # v1.20.4: Ctrl+W ฯลฯ
            mods, k = combo if combo else ((), parse_key(r.get("additional", "")))
            if k is None:
                return True
            if btn == "Press Key":
                for m in mods:
                    self.kb_ctl.press(m)
                    self.pressed_keys.add(m)
                self.kb_ctl.press(k)
                self.pressed_keys.add(k)           # จำไว้ปล่อยตอน STOP กลางคัน
            elif btn == "Release Key":
                self.kb_ctl.release(k)
                self.pressed_keys.discard(k)
                for m in reversed(mods):
                    self.kb_ctl.release(m)
                    self.pressed_keys.discard(m)
            else:
                for m in mods:
                    self.kb_ctl.press(m)
                    self.pressed_keys.add(m)
                self.kb_ctl.tap(k)
                for m in reversed(mods):
                    self.kb_ctl.release(m)
                    self.pressed_keys.discard(m)
        elif btn == "Set Variable":                                  # ตัวแปร (v1.19)
            if not apply_set_var(self.variables, r.get("additional", "")):
                self.on_message("Set Variable: รูปแบบไม่ถูก (%s) — ต้องเป็น "
                                "name = ค่า หรือ name += จำนวน" % (r.get("additional") or ""), "#c00")
        elif btn == "Set Clipboard":                                 # ตั้งคลิปบอร์ด (v1.20)
            text = str(r.get("additional") or "")
            if text:
                self.on_clipboard_set(text)
        elif btn == "Read Clipboard":                                # อ่านคลิปบอร์ดเป็นตัวแปร (v1.20)
            m = re.fullmatch(_VAR_NAME, str(r.get("additional") or "").strip())
            if not m:
                self.on_message("Read Clipboard: พิมพ์ชื่อตัวแปรใน Additional เช่น mytext", "#c00")
            elif getattr(self, "read_clipboard_mode", "direct") == "ui":
                # GUI: ผลักงานเข้า poller (main thread อ่านคลิปบอร์ด + ตั้งตัวแปรเอง)
                self.ui_read_clipboard(m.group(0))
            else:
                got = self.on_clipboard_read()
                if got is None:
                    self.on_message("⚠ Read Clipboard: อ่านคลิปบอร์ดไม่สำเร็จบนระบบนี้", "#a60")
                else:
                    self.variables[m.group(0)] = got
        elif self.dry_run:                     # plugin ในโหมด dry-run (v2.10) — ไม่รันจริง
            self.on_message("DRY-RUN: จะรัน plugin %s" % btn)
        else:                                                        # Custom Action (v1.16)
            mod = self.plugin_lookup(btn)
            if mod is not None:
                ctx = self._plugin_ctx()
                try:
                    mod.run(ctx, dict(r))
                except Exception as exc:
                    self.on_message("plugin error (%s): %s" % (btn, exc), "#c00")
            else:
                self.unsupported_cb(btn)
        return True


# ============================ ค้นภาพบนหน้าจอ (v2.2 — phase 3) ================
# ย้าย logic opencv จากฝั่ง GUI ลง engine — CLI ใช้ Image Click/If Image/Wait ได้จริง
# ไม่มี Tk — ผลลัพธ์สื่อสารผ่านค่าคืนเท่านั้น

def parse_search_area(raw):
    """อ่านกรอบค้นหา (search area) + threshold จากข้อความ Additional (v1.7)
        ไฟล์.png                     = ทั้งจอ, threshold 80%
        ไฟล์.png@x,y,กว้าง,สูง        = กรอบ, threshold 80%
        ไฟล์.png@x,y,กว้าง,สูง#90     = กรอบ, threshold 90%
        ไฟล์.png#65                  = ทั้งจอ, threshold 65%
    คืน (path, area, threshold) — area None = ทั้งจอ"""
    raw = (raw or "").strip()
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
    else:
        path, _, thr_s = raw.partition("#")
    if thr_s.strip():
        try:
            t = float(thr_s)
            if 1 < t <= 100:      # ใส่เป็นเปอร์เซ็นต์ เช่น #90 = 90%
                t /= 100.0
            thr = min(1.0, max(0.30, t))
        except ValueError:
            pass
    return path, area, thr


def grab_area_bgr(area=None):
    """จับภาพหน้าจอเฉพาะกรอบ (area=None = ทั้งจอ) — คืน (numpy BGR, (off_x, off_y))"""
    if area and len(area) == 4:
        shot = ImageGrab.grab(bbox=area, all_screens=True)
        off = (area[0], area[1])
    else:
        shot = ImageGrab.grab(all_screens=True)
        off = (0, 0)
    return cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR), off


def resolve_image_path(path):
    """พาธสัมพัทธ์ → เทียบกับโฟลเดอร์ของโปรแกรม (เหมือนเดิมทุกเวอร์ชัน)"""
    if not os.path.isabs(path):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
    return path


_template_cache = {}      # path -> ((mtime, size), ndarray) — แคช imread (v2.4)


def _load_template(path):
    """อ่าน template ภาพพร้อมแคช (v2.4) — สคริปต์วน 1000 รอบไม่ต้องอ่านไฟล์ซ้ำ
    อ่านใหม่อัตโนมัติเมื่อไฟล์เปลี่ยน (mtime/size ต่างจากเดิม) — คืน None ถ้าอ่านไม่ได้"""
    try:
        st = os.stat(path)
        key = (st.st_mtime, st.st_size)
    except OSError:
        return None
    hit = _template_cache.get(path)
    if hit is not None and hit[0] == key:
        return hit[1]
    tmpl = cv2.imread(path, cv2.IMREAD_COLOR)
    if tmpl is not None:
        _template_cache[path] = (key, tmpl)
    return tmpl


def find_image_pos(path, area=None, thr=None):
    """ค้นหาภาพย่อยบนหน้าจอ (cv2.matchTemplate) — คืน (x, y) จุดศูนย์กลาง หรือ None
    คืน None เมื่อ: ไม่มี opencv / ไฟล์หาย / อ่านไม่ได้ / ภาพใหญ่กว่ากรอบ / ไม่เจอ
    (ข้อความเหตุผลเขียนลง find_image_pos.last_error เพื่อให้ caller โชว์ได้)"""
    find_image_pos.last_error = None
    if not HAS_CV:
        find_image_pos.last_error = "ค้นภาพต้องติดตั้ง: pip install opencv-python Pillow"
        return None
    path = resolve_image_path(path)
    if not os.path.isfile(path):
        find_image_pos.last_error = "ไม่พบไฟล์ภาพ: %s" % path
        return None
    tmpl = _load_template(path)
    if tmpl is None:
        find_image_pos.last_error = "อ่านไฟล์ภาพไม่ได้: %s" % path
        return None
    try:
        screen, (off_x, off_y) = grab_area_bgr(area)
    except Exception as exc:
        find_image_pos.last_error = "จับภาพหน้าจอไม่ได้: %s" % exc
        return None
    if tmpl.shape[0] > screen.shape[0] or tmpl.shape[1] > screen.shape[1]:
        find_image_pos.last_error = "ภาพใหญ่กว่าพื้นที่ค้นหา: %s" % os.path.basename(path)
        return None
    res = cv2.matchTemplate(screen, tmpl, cv2.TM_CCOEFF_NORMED)
    _, maxv, _, maxloc = cv2.minMaxLoc(res)
    if maxv < thr:
        find_image_pos.last_error = ("หาภาพไม่เจอ (ความมั่นใจ %.0f%% < %.0f%%): %s"
                                     % (maxv * 100, thr * 100, os.path.basename(path)))
        return None
    return (off_x + maxloc[0] + tmpl.shape[1] // 2,
            off_y + maxloc[1] + tmpl.shape[0] // 2)


# ============================= Recorder (v2.2 — phase 3) =====================
# กลไก RECORD ล้วน ไม่มี Tk — listener threads ผลักเหตุการณ์เข้า pending_rows
# ฝั่ง UI ดึงผ่าน drain_pending() แล้ววาดตารางเอง (รูปแบบ thread-safe เดิมของโปรเจกต์)
class Recorder:
    """บันทึกเมาส์/คีย์เป็นแถวสคริปต์ (v2.2 — ย้ายจาก MacroApp._start_listeners)

    - ใช้ pynput Listener 2 ตัว (mouse + keyboard) ในเธรดแยก — ไม่แตะ Tk เด็ดขาด
    - recording = สถานะปัจจุบัน · start()/stop() สลับ
    - pending_rows คือรายการแถวรอ — ผู้ใช้ UI ดึงด้วย drain_pending() ทุก tick
    - on_event(row_dict) เรียกทุกครั้งที่อัดได้ (ถ้าให้มา — ใช้ทำ live callback)
    """

    def __init__(self, on_event=None):
        self.recording = False
        self._t0 = 0.0
        self.pending_rows = []
        self.on_event = on_event
        self._ms_listener = None
        self._kb_listener = None
        self._last_key = ""          # คีย์ล่าสุด (สำหรับหน้าจอสด)

    # ---- กลไก listener (เริ่มตอนสร้าง — สถานะอัดคุมด้วย self.recording) -----
    def _on_move(self, x, y):
        self.last_pos = (x, y)

    def _on_click(self, x, y, button, pressed):
        if self.recording and pressed:
            name = {"Button.left": "Left", "Button.right": "Right",
                    "Button.middle": "Middle"}.get(str(button))
            if name:
                self._push(dict(x=int(x), y=int(y), button=name + " Click",
                                additional="", mins=0,
                                secs=round(time.time() - self._t0, 2), repeat=1))

    def _on_scroll(self, x, y, dx, dy):
        if self.recording and dy:
            self._push(dict(x=int(x), y=int(y),
                            button="Scroll Up" if dy > 0 else "Scroll Down",
                            additional=str(abs(dy)), mins=0,
                            secs=round(time.time() - self._t0, 2), repeat=1))

    def _on_kb(self, key):
        try:
            txt = key.char or ""
        except AttributeError:
            txt = str(key).replace("Key.", "")
        if txt:
            self._last_key = txt
        if self.recording and txt and len(txt) <= 12 and not txt.startswith(" "):
            self._push(dict(x="", y="", button="Tap Key", additional=txt, mins=0,
                            secs=round(time.time() - self._t0, 2), repeat=1))

    def _push(self, row):
        self.pending_rows.append(row)
        if self.on_event:
            try:
                self.on_event(dict(row))
            except Exception:
                pass

    def start_listeners(self):
        """เปิด listener 2 ตัว (เรียกครั้งเดียวตอนสร้างโปรแกรม — ทน error ทุกจุด)"""
        self.pending_rows = []
        try:
            self._ms_listener = mouse.Listener(on_move=self._on_move,
                                               on_click=self._on_click,
                                               on_scroll=self._on_scroll)
            self._ms_listener.daemon = True
            self._ms_listener.start()
        except Exception:
            self._ms_listener = None
        try:
            self._kb_listener = keyboard.Listener(on_press=self._on_kb)
            self._kb_listener.daemon = True
            self._kb_listener.start()
        except Exception:
            self._kb_listener = None

    def stop_listeners(self):
        for attr in ("_ms_listener", "_kb_listener"):
            lis = getattr(self, attr, None)
            if lis is not None:
                try:
                    lis.stop()
                except Exception:
                    pass
                setattr(self, attr, None)

    # ---- ควบคุมสถานะอัด ---------------------------------------------------
    def start(self):
        """เริ่มอัด — คืน True ถ้า listener พร้อม"""
        self._t0 = time.time()
        self.pending_rows = []
        self.recording = True
        return (self._ms_listener is not None or self._kb_listener is not None)

    def stop(self):
        """หยุดอัด — คืนจำนวนเหตุการณ์ที่อัดได้ทั้งหมด (รวมที่ยังไม่ถูก drain)"""
        self.recording = False
        return len(self.pending_rows)

    def drain_pending(self):
        """ดึงแถวรอทั้งหมดออก (เรียกจาก UI poller — เธรดเดียวเท่านั้น)"""
        rows = self.pending_rows
        self.pending_rows = []
        return rows

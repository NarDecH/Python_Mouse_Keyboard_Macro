#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Mouse & Keyboard Macro  v1.13
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

APP_TITLE = "Auto Mouse & Keyboard Macro v1.13"
BACKUP_DIR = "backups"          # โฟลเดอร์เก็บ backup อัตโนมัติ
BACKUP_KEEP_DAYS = 7            # เก็บ snapshot ย้อนหลังกี่วัน
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
# ฟีเจอร์เพิ่มเติมแรงบันดาลใจจาก automouseclick.com (v1.5)
SCROLL_ACTIONS = ["Scroll Up", "Scroll Down"]
DBL_ACTIONS = ["Double Left Click", "Double Right Click"]
MOD_CLICKS = ["Ctrl+Click", "Shift+Click", "Alt+Click", "Ctrl+Right Click"]
MOVE_ACTIONS = ["Move Mouse", "Move Mouse by Offset", "Save Cursor", "Restore Cursor"]
EXTRA_ACTIONS = ["Type Text", "Launch App", "Wait for Image", "Beep"]
ACTIONS_ALL = (MOUSE_BTNS + KEY_ACTIONS + [IMAGE_ACTION] + SCROLL_ACTIONS
               + DBL_ACTIONS + MOD_CLICKS + MOVE_ACTIONS + EXTRA_ACTIONS)
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
    """แปลงข้อความในคอลัมน์ Additional เป็นออบเจ็กต์คีย์ของ pynput"""
    txt = (txt or "").strip()
    if not txt:
        return None
    if txt in MOD_KEYS[1:]:                       # Ctrl / Alt / Shift / Win
        return {"Win": Key.cmd}.get(txt, getattr(Key, txt.lower(), None))
    attr = txt.lower()
    if attr in SPECIAL_KEYS:
        return getattr(Key, SPECIAL_KEYS[attr], None)
    if len(txt) == 1:
        return KeyCode.from_char(txt)
    if txt.isdigit():                             # รหัส virtual key เช่น 27
        return KeyCode.from_vk(int(txt))
    return None


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
    stats = {"runs": 0, "steps": 0, "stops": 0, "restarts": 0, "slowest": None}
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if "[START]" in line:
                    stats["runs"] += 1
                elif "[STEP]" in line:
                    stats["steps"] += 1
                    m = re.search(r"\(([\d.]+) วิ\)", line)
                    if m and (stats["slowest"] is None
                              or float(m.group(1)) > stats["slowest"][1]):
                        stats["slowest"] = (line.strip(), float(m.group(1)))
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
             "stops": 0, "restarts": 0, "slowest": None}
    for f in files:
        s = parse_log_stats(f)
        for k in ("runs", "steps", "stops", "restarts"):
            total[k] += s[k]
        if s["slowest"] and (total["slowest"] is None
                             or s["slowest"][1] > total["slowest"][1]):
            total["slowest"] = s["slowest"]
    return total


# ------------------------------------------------ backup อัตโนมัติ (v1.13) --
def backup_snapshot(base_dir, data, now=None):
    """เขียน backup การตั้งค่า 1 snapshot ลง <base_dir>/backups/ แล้วตัดไฟล์เก่าเกิน 7 วัน
    คืนพาธไฟล์ที่เขียน (ทนต่อ error — backup ห้ามทำโปรแกรมพัง)"""
    try:
        bk = os.path.join(base_dir, BACKUP_DIR)
        os.makedirs(bk, exist_ok=True)
        t = now or datetime.datetime.now()
        path = os.path.join(bk, "backup_%s.json" % t.strftime("%Y-%m-%d_%H%M%S"))
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        prune_backups(bk)
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


# ---------------------------------------------------------------- HotkeyEdit --
class HotkeyEdit(tk.Toplevel):
    """หน้าต่างแก้ค่าในเซลล์ (เปิดโดยดับเบิลคลิก)"""

    def __init__(self, master, label, current, choices, on_done):
        super().__init__(master)
        self.title("แก้ค่า: " + label)
        self.resizable(False, False)
        self.configure(bg="#f0f0f0")
        tk.Label(self, text=label + ":", bg="#f0f0f0").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.var = tk.StringVar(value=str(current))
        if choices:
            w = ttk.Combobox(self, textvariable=self.var, values=choices,
                             width=22, state="readonly")
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
        self._live_pos = (0, 0)         # พิกัดเมาส์สด (จาก listener thread)
        self._live_key = ""             # คีย์ล่าสุด (จาก listener thread)
        self._ui_state = {"row": None, "msg": None, "reset": False, "prog": None}

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

        # การหยุดที่แม่นยำ (v1.7.1)
        self._play_gen = 0                 # รุ่นของการเล่น — เธรดเก่าหยุดเองเมื่อรุ่นเปลี่ยน
        self._pressed_keys = set()         # คีย์ที่กดค้าง (Press Key) เพื่อปล่อยตอน STOP
        self._pressed_btns = set()         # ปุ่มเมาส์ที่กดค้าง (* Down) เพื่อปล่อยตอน STOP

        self._build_style()
        self._build_menu()
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
        self._load_conf()  # โหลดงานล่าสุดของโปรไฟล์ที่ใช้อยู่ (ถ้ามี)
        self._self_check()  # ตรวจสุขภาพระบบ (v1.11) — ผลแสดงใน Settings
        if not (self._checks.get("mouse") and self._checks.get("hotkey")):
            self._ui_state["msg"] = ("⚠️ self-check: บางส่วนไม่พร้อม — ดูรายละเอียดใน Settings", "#a60")

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
                                    ("button", "Button / Action", 150, "w"),
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

        tools = tk.Frame(self.root)
        tools.pack(fill="x", padx=6)
        tk.Button(tools, text="＋ เพิ่มบรรทัด", command=self.add_row).pack(side="left", padx=2, pady=2)
        tk.Button(tools, text="－ ลบที่เลือก", command=self.del_selected).pack(side="left", padx=2)
        tk.Button(tools, text="▲ ขึ้น", width=6, command=lambda: self.move(-1)).pack(side="left", padx=2)
        tk.Button(tools, text="▼ ลง", width=6, command=lambda: self.move(1)).pack(side="left", padx=2)
        tk.Button(tools, text="ล้างทั้งหมด", command=self.clear_all).pack(side="left", padx=2)
        if HAS_CV:
            tk.Button(tools, text="📸 จับภาพ (ลากกรอบบนจอ)", command=self._capture_snip).pack(side="right", padx=2)

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
        if HAS_CV:
            tk.Button(tools, text="📸 จับภาพ (ลากกรอบบนจอ)", command=self._capture_snip).pack(side="right", padx=2)

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
        tk.Checkbutton(bot, text="วนซ้ำไม่จำกัด (F10)", variable=self.chk_forever).pack(side="left", padx=6)
        self.chk_restore = tk.BooleanVar(value=False)
        tk.Checkbutton(bot, text="คืนเมาส์จุดเดิม", variable=self.chk_restore).pack(side="left", padx=6)
        self.chk_shuffle = tk.BooleanVar(value=False)
        tk.Checkbutton(bot, text="สุ่มลำดับ", variable=self.chk_shuffle).pack(side="left", padx=6)
        tk.Label(bot, text="สัดส่วนแถว:").pack(side="left", padx=(10, 2))
        self.ent_pct = tk.Spinbox(bot, from_=5, to=100, increment=5, width=5)
        self.ent_pct.delete(0, "end")
        self.ent_pct.insert(0, "100")
        self.ent_pct.pack(side="left")
        tk.Label(bot, text="%", fg="#888").pack(side="left", padx=(2, 0))

        tk.Label(bot, text="ความเร็ว:").pack(side="left", padx=(10, 2))
        self.cmb_speed = ttk.Combobox(bot, width=5, state="readonly",
                                      values=["0.25", "0.5", "1", "2", "4"])
        self.cmb_speed.set("1")
        self.cmb_speed.pack(side="left")

        tk.Label(bot, text="รอบ:").pack(side="left", padx=(10, 2))
        self.ent_loops = tk.Spinbox(bot, from_=0, to=99999, width=6)
        self.ent_loops.delete(0, "end")
        self.ent_loops.insert(0, "1")
        self.ent_loops.pack(side="left")
        tk.Label(bot, text="(0=ไม่จำกัด)", fg="#888").pack(side="left", padx=(2, 0))

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
            if self.recording and pressed is not False and txt and len(txt) <= 12 and not txt.startswith(" "):
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

        # ข้อความสถานะ
        if st["msg"]:
            text, color = st.pop("msg")
            self.lbl_state.config(text=text, fg=color)

        # รีเซ็ตปุ่มเมื่อเล่นจบ
        if st.pop("reset", False):
            self._reset_ui()

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
                fmt_num(kw.get("secs", 1)), fmt_num(kw.get("repeat", 1))]
        n = len(self.tree.get_children())
        self.tree.insert("", "end", values=vals, tags=("even" if n % 2 else "odd",))
        self.tree.see(self.tree.get_children()[-1])

    def add_row(self):
        self._append_row(button="Left Click", secs=1)

    def refresh_nums(self):
        for i, iid in enumerate(self.tree.get_children(), 1):
            vals = list(self.tree.item(iid, "values"))
            vals[1] = i
            self.tree.item(iid, values=vals)

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
        for iid in self.tree.selection():
            self.tree.delete(iid)
        self.refresh_nums()

    # --------------------------------------------- context menu (คลิกขวา) ----
    def _on_right_click(self, event):
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        self.tree.selection_set(iid)
        self.tree.focus(iid)
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="📋 คัดลอกแถวนี้", command=lambda: self._row_duplicate(iid))
        menu.add_command(label="⬆️ แทรกแถวใหม่ด้านบน", command=lambda: self._row_insert_above(iid))
        menu.add_command(label="⬇️ แทรกแถวใหม่ด้านล่าง", command=lambda: self._row_insert_below(iid))
        menu.add_separator()
        menu.add_command(label="🗑️ ลบแถวนี้", command=self._on_del)
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

    def del_selected(self):
        self._on_del()

    def clear_all(self):
        if self.tree.get_children() and messagebox.askyesno(APP_TITLE, "ลบทุกบรรทัดใช่หรือไม่?"):
            self.tree.delete(*self.tree.get_children())
            self._hl_row = None

    def move(self, d):
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]
        idx = self.tree.index(iid)
        tgt = idx + d
        n = len(self.tree.get_children())
        if 0 <= tgt < n:
            self.tree.move(iid, "", tgt)
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
        choices = {"Action": ACTIONS_ALL,
                   "Additional": [""] + MOD_KEYS[1:] + sorted(SPECIAL_KEYS)}.get(label)
        if key == "additional":
            hint = {"Type Text": "พิมพ์ข้อความที่จะส่ง (เช่น สวัสดี)",
                    "Launch App": "พาธโปรแกรม หรือ URL เช่น https://example.com",
                    "Image Click": "ชื่อไฟล์ .png เช่น button.png",
                    "Wait for Image": "ชื่อไฟล์ .png เช่น button.png",
                    "Scroll Up": "จำนวนจังหวะ เช่น 3",
                    "Scroll Down": "จำนวนจังหวะ เช่น 3"}.get(str(vals[4]), "")
            if hint:
                self._ui_state["msg"] = ("ช่อง Additional: " + hint, "#06c")
        HotkeyEdit(self.root, label, vals[ci], choices,
                   lambda v, r=row_id, c=ci: self._apply_edit(r, c, v))

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
        rows = []
        for iid in self.tree.get_children():
            v = self.tree.item(iid, "values")
            if str(v[0]) == "☑":
                rows.append(dict(x=v[2], y=v[3], button=v[4], additional=v[5],
                                 mins=v[6], secs=v[7], repeat=v[8]))
        return rows

    def _validate_rows(self, rows):
        for r in rows:
            if r["button"] in KEY_ACTIONS and not parse_key(r["additional"]):
                return False
            if r["button"] == "Launch App" and not (r["additional"] or "").strip():
                return False
            if r["button"] in (IMAGE_ACTION, "Wait for Image"):
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

    def _start_player(self, loop):
        rows = self._rows_for_play()
        if not rows:
            messagebox.showinfo(APP_TITLE, "ยังไม่มีรายการที่เปิดใช้ (☑) ให้เล่น")
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
        self._restore_pos = self.chk_restore.get()
        self._shuffle = self.chk_shuffle.get()
        self._pct = self._play_options()
        self._log_src = self._loaded_file or "ตารางในโปรแกรม"
        if self._log_enabled:
            extra = " สุ่มลำดับ" if self._shuffle else ""
            if self._pct < 100:
                extra += " %d%%" % self._pct
            log_write("START", "เริ่มเล่น (%s) ความเร็ว %gx รอบ=%s แถวที่เล่น=%d%s" %
                      ("วนซ้ำ" if loop else "ครั้งเดียว", self._speed_mult,
                       self._script_loops if self._script_loops else "ไม่จำกัด",
                       len(rows), extra), self._log_src)
        self.btn_start.config(state="disabled", bg="#cfcfcf")
        self.btn_repeat.config(state="disabled", bg="#2e7d32")
        mode = "วนซ้ำ" if loop else "เล่นครั้งเดียว"
        self.root.title(APP_TITLE + "   [ RUNNING ]")
        self._ui_state["msg"] = ("กำลังเล่นสคริปต์ (%s) — F8 หยุด" % mode, "#080")
        threading.Thread(target=self._player, args=(rows, loop, gen), daemon=True).start()

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
            self._ui_state["msg"] = ("หยุดแล้ว — ปล่อยคีย์/ปุ่มที่ค้างแล้ว", "#a60")
            if self._log_enabled:
                log_write("STOP", "หยุดโดยผู้ใช้ (F8/ปุ่ม STOP) — ปล่อยคีย์/ปุ่มที่ค้างแล้ว",
                          self._log_src)

    def _player(self, rows, loop, gen=0):
        """เธรดผู้เล่น — เช็ค self._gen_ok(gen) ทุกจุด: STOP หรือ START ใหม่ = หยุดทันที"""
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
            elif btn == "Wait for Image":                        # รอภาพปรากฏ
                self._do_wait_for_image(r)
            elif btn == "Type Text":                             # พิมพ์ข้อความ
                for ch in str(r["additional"] or ""):
                    if not self._gen_ok(gen):
                        return
                    self.kb_ctl.tap(self.kb_ctrl_char(ch))
            elif btn == "Launch App":                            # เปิดแอป/เว็บ
                target = str(r["additional"] or "").strip()
                if target:
                    try:
                        os.startfile(target)      # Windows; Linux/macOS ใช้ subprocess
                    except (OSError, AttributeError):
                        import subprocess
                        subprocess.Popen(["xdg-open", target])
            elif btn == "Beep":                                  # เสียงเตือน
                try:
                    self.root.bell()
                except tk.TclError:
                    pass
            elif btn in KEY_ACTIONS:                             # คีย์บอร์ด
                k = parse_key(r["additional"])
                if k is None:
                    return
                if btn == "Press Key":
                    self.kb_ctl.press(k)
                    self._pressed_keys.add(k)      # จำไว้ปล่อยตอน STOP กลางคัน
                elif btn == "Release Key":
                    self.kb_ctl.release(k)
                    self._pressed_keys.discard(k)
                else:
                    self.kb_ctl.tap(k)

        # บั๊กฟิกซ์ v1.6: เดิมลูปนี้ถูกแทรกหลัง return ของ kb_ctrl_char ทำให้เป็น dead code
        # v1.7.1: ใช้ _gen_ok/_sleep_check — STOP แม่นทันทีแม้ดีเลย์ยาว + กันเล่นซ้อนเธรด
        try:
            start_pos = self.mouse_ctl.position if self._restore_pos else None
            total = len(rows)
            loop_no = 0
            outer = True
            play_started = time.time()
            self._shuffle = False
            self._pct = 100
            while outer:
                loop_no += 1
                # _script_loops: 0 = ไม่จำกัด, 1 = ครั้งเดียว, N = N รอบ
                play_rows = pick_play_order(rows, pct=self._pct, shuffle=self._shuffle)
                for i, r in enumerate(play_rows):
                    if not self._gen_ok(gen):
                        return
                    children = self.tree.get_children()
                    self._ui_state["row"] = children[i] if i < len(children) else None
                    self._ui_state["prog"] = (i + 1, total, loop_no)
                    for _ in range(parse_int(r["repeat"])):
                        if not self._gen_ok(gen):
                            return
                        lo, hi = delay_range(r["secs"])
                        base = delay_seconds(r["mins"], 0) + (lo if lo == hi else random.uniform(lo, hi))
                        if not self._sleep_check(base / self._speed_mult, gen):
                            return
                        step_t0 = time.time()
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
                    break                      # REPEAT/forever คุมรอบอยู่แล้ว
                if self._script_loops == 0:
                    outer = self._gen_ok(gen)  # ไม่จำกัดรอบ
                else:
                    self._script_loops -= 1
                    outer = self._script_loops > 0 and self._gen_ok(gen)
            if self._gen_ok(gen):
                self._ui_state["msg"] = ("เล่นจบแล้ว ✔", "#080")
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
        """แปลงอักขระเป็น KeyCode สำหรับ Type Text (รองรับไทย/อังกฤษ/ตัวเลข/สัญลักษณ์)"""
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
                mode = getattr(self, "_sched_mode", "")
                if not mode:
                    continue
                now = time.time()
                if mode == "interval":
                    if self._sched_next and now >= self._sched_next and not self.running:
                        self._sched_next = now + self._sched_every * 60
                        self._sched_q.put("play")
                elif mode == "daily":
                    stamp = time.strftime("%Y-%m-%d %H:%M")
                    if stamp == self._sched_at and self._sched_last != stamp and not self.running:
                        self._sched_last = stamp
                        self._sched_q.put("play")
            except Exception:
                pass

    def _sched_poll(self):
        """ฝั่ง UI: หยิบคำสั่งเล่นจาก scheduler มาทำ (thread-safe)"""
        try:
            while True:
                self._sched_q.get_nowait()
                if not self.running:
                    self._start_player(True)   # เล่นแบบวนซ้ำ 1 รอบจบ (F8 หยุดได้)
        except Exception:
            pass
        if not self._sched_stop.is_set():
            self.root.after(500, self._sched_poll)

    def _schedule_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("เล่นอัตโนมัติตามเวลา (Schedule)")
        win.resizable(False, False)
        tk.Label(win, text="เลือกโหมดเล่นอัตโนมัติของโปรไฟล์ '%s'" % self._active_profile,
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
            i = self.tree.index(iid)
            self.tree.item(iid, tags=("even" if i % 2 else "odd",))
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
        """รอจนกว่าจะเจอภาพบนหน้าจอ (timeout 30 วิ) — รองรับ search area + threshold"""
        path, area, thr = self._parse_search_area(r)
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
        deadline = time.time() + 30
        gen = self._play_gen
        while time.time() < deadline and self._gen_ok(gen):
            screen, _off = self._grab_area_bgr(area)
            if tmpl.shape[0] <= screen.shape[0] and tmpl.shape[1] <= screen.shape[1]:
                res = cv2.matchTemplate(screen, tmpl, cv2.TM_CCOEFF_NORMED)
                _, maxv, _, _ = cv2.minMaxLoc(res)
                if maxv >= thr:
                    return
            time.sleep(0.5)
        self._ui_state["msg"] = ("Wait for Image: ไม่เจอภาพภายใน 30 วิ — %s" % os.path.basename(path), "#a60")

    # ------------------------------------------------------ image click ------
    def _do_image_click(self, r):
        """หาภาพย่อยบนหน้าจอแล้วคลิกที่จุดศูนย์กลาง
        ช่อง Additional: ไฟล์.png / ไฟล์.png@x,y,กว้าง,สูง / ...#threshold"""
        path, area, thr = self._parse_search_area(r)
        if not HAS_CV:
            self._ui_state["msg"] = ("Image Click ต้องติดตั้ง: pip install opencv-python Pillow", "#c00")
            return
        if not os.path.isabs(path):
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
        if not os.path.isfile(path):
            self._ui_state["msg"] = ("ไม่พบไฟล์ภาพ: %s" % path, "#c00")
            return
        try:
            screen, (off_x, off_y) = self._grab_area_bgr(area)
            tmpl = cv2.imread(path, cv2.IMREAD_COLOR)
            if tmpl is None:
                self._ui_state["msg"] = ("อ่านไฟล์ภาพไม่ได้: %s" % path, "#c00")
                return
            if tmpl.shape[0] > screen.shape[0] or tmpl.shape[1] > screen.shape[1]:
                self._ui_state["msg"] = ("ภาพใหญ่กว่าพื้นที่ค้นหา: %s" % os.path.basename(path), "#c00")
                return
            res = cv2.matchTemplate(screen, tmpl, cv2.TM_CCOEFF_NORMED)
            _, maxv, _, maxloc = cv2.minMaxLoc(res)
            if maxv < thr:
                self._ui_state["msg"] = ("หาภาพไม่เจอ (ความมั่นใจ %.0f%% < %.0f%%): %s" % (maxv * 100, thr * 100, os.path.basename(path)), "#c00")
                return
            cx = off_x + maxloc[0] + tmpl.shape[1] // 2
            cy = off_y + maxloc[1] + tmpl.shape[0] // 2
            self.mouse_ctl.position = (cx, cy)
            time.sleep(0.03)
            self.mouse_ctl.click(Button.left, 1)
        except Exception as exc:
            self._ui_state["msg"] = ("Image Click ผิดพลาด: %s" % exc, "#c00")

    # ------------------------------------------------------ save / load ------
    def _serialize(self):
        out = []
        for iid in self.tree.get_children():
            v = self.tree.item(iid, "values")
            out.append(dict(enabled=str(v[0]) == "☑", x=v[2], y=v[3], button=v[4],
                            additional=v[5], mins=v[6], secs=v[7], repeat=v[8]))
        return out

    def _load_rows(self, rows):
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
            self.tree.item(iid, values=vals)
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
                           "hot_profile_dir": self._hp_dir},
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
        tk.Label(win, text="คีย์ลัดของโปรแกรม (ทำงานได้ทั้งแบบโฟกัสและไม่โฟกัส)",
                 font=("Segoe UI", 11, "bold")).pack(padx=20, pady=(14, 6))
        frm = tk.Frame(win)
        frm.pack(padx=20, pady=4)
        rows = [("เริ่มเล่นสคริปต์", "F6"), ("หยุดทั้งหมด", "F8"),
                ("เริ่ม/หยุดบันทึก", "F9"), ("สลับวนซ้ำไม่จำกัด", "F10"),
                ("Hot-profile: เล่นสคริปต์ลำดับ 1-4", "F1-F4"),
                ("ลบแถวที่เลือก", "Delete"), ("แก้ค่าในเซลล์", "ดับเบิลคลิก"),
                ("ตัวคูณความเร็ว / จำนวนรอบ", "แถบปุ่มด้านล่าง"),
                ("ดีเลย์สุ่มรายแถว", "Secs = 1-3")]
        for i, (name, key) in enumerate(rows):
            tk.Label(frm, text=name + ":").grid(row=i, column=0, sticky="e", padx=4, pady=3)
            tk.Label(frm, text=key, font=("Consolas", 10, "bold"), fg="#06c").grid(
                row=i, column=1, sticky="w", padx=4, pady=3)
        gk_state = "ทำงานอยู่ ✅ (กดได้ทุกที่)" if self._gk else "ไม่ทำงาน ⚠️ (ต้องโฟกัสหน้าต่าง)"
        tk.Label(win, text="Global Hotkey: " + gk_state,
                 fg="#080" if self._gk else "#a60").pack(pady=(10, 0))
        tk.Label(win, text="ตรวจสุขภาพระบบ (self-check ตอนเปิดโปรแกรม):",
                 font=("Segoe UI", 9, "bold")).pack(pady=(10, 2))
        for name, ok, note in self.self_check_text():
            tk.Label(win, text="%s %s — %s" % ("✅" if ok else "⚠️", name, note),
                     fg="#080" if ok else "#a60", justify="left").pack(anchor="w", padx=20)
        tk.Label(win, text="Image Click: " + ("พร้อมใช้ ✅" if HAS_CV else
                 "ยังไม่พร้อม — ติดตั้งด้วย: pip install opencv-python Pillow"),
                 fg="#080" if HAS_CV else "#a60").pack()
        self.var_log = tk.BooleanVar(value=self._log_enabled)
        tk.Checkbutton(win, text="บันทึก log การเล่นลงไฟล์ macro_log_วันที่.txt",
                       variable=self.var_log).pack(pady=(10, 0))
        tk.Button(win, text="เปิดโฟลเดอร์ log", width=14,
                  command=lambda: os.startfile(os.path.dirname(os.path.abspath(__file__)))
                  if hasattr(os, "startfile") else None).pack(pady=(4, 0))
        # 🧪 ทดสอบระบบจริง (v1.12): ขยับเมาส์ไปจุดสังเกต → คืนจุดเดิม → บี๊บ 2 ครั้ง
        def self_test():
            try:
                self._self_test_actions()
                res.config(text="🧪 ทดสอบแล้ว: เมาส์ขยับเป็นสามเหลี่ยมแล้วคืนจุดเดิม + บี๊บ 2 ครั้ง — "
                                "ถ้าเมาส์ไม่ขยับหรือไม่ได้ยินเสียง แสดงว่าระบบมีปัญหาจริง", fg="#080")
            except Exception as exc:
                res.config(text="🧪 ทดสอบล้มเหลว: %s" % exc, fg="#b00")

        tk.Button(win, text="🧪 ทดสอบระบบจริง (ขยับเมาส์+บี๊บ)", width=30,
                  command=self_test).pack(pady=(10, 0))
        res = tk.Label(win, text="", fg="#080", justify="left", wraplength=380)
        res.pack(padx=20)
        # Export/Import การตั้งค่า (v1.12)
        eib = tk.Frame(win)
        eib.pack(pady=(10, 0))
        tk.Button(eib, text="⬆️ Export การตั้งค่า", width=18,
                  command=self.export_settings).pack(side="left", padx=4)
        tk.Button(eib, text="⬇️ Import การตั้งค่า", width=18,
                  command=self.import_settings).pack(side="left", padx=4)
        tk.Label(win, text="Export = งานปัจจุบัน + โปรไฟล์ทุกชุด + ตั้งค่า log/hot-profile "
                 "เป็นไฟล์เดียว (ย้ายเครื่อง/สำรอง)", fg="#888",
                 justify="left", wraplength=400).pack(padx=20, pady=(4, 0))
        tk.Button(win, text="บันทึก", width=8,
                  command=lambda: (setattr(self, "_log_enabled", self.var_log.get()),
                                   win.destroy())).pack(pady=(8, 14))

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
        # backup อัตโนมัติทุกครั้งที่ปิดโปรแกรม (v1.13) — เก็บ 7 วันย้อนหลัง
        backup_snapshot(os.path.dirname(os.path.abspath(__file__)),
                        {"kind": "automousemacro-settings", "version": 1,
                         "rows": self._serialize(),
                         "profiles": self._profiles,
                         "active_profile": self._active_profile,
                         "log_enabled": self._log_enabled,
                         "hot_profile_dir": self._hp_dir})
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
            k = parse_key(r.get("additional", ""))
            if k is not None:
                if btn == "Press Key":
                    kb_ctl.press(k)
                    pending_keys.append(("k", k))
                elif btn == "Release Key":
                    kb_ctl.release(k)
                    if ("k", k) in pending_keys:
                        pending_keys.remove(("k", k))
                else:
                    kb_ctl.tap(k)
        elif btn == "Type Text":
            for ch in str(r.get("additional") or ""):
                if not running[0]:
                    return
                kb_ctl.tap(KeyCode.from_char(ch))
        elif btn == "Beep":
            print("\a", end="", flush=True)
        # (หมายเหตุ: Image Click/Wait for Image ยังไม่รองรับใน CLI — ใช้ GUI)

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

    def play_once():
        """เล่นสคริปต์ 1 ครั้ง — คืน True = จบครบเอง, False = ถูกหยุดกลางคัน"""
        try:
            loops = 0 if args.loop else max(0, args.loops)
            active = [r for r in rows if r.get("enabled", True) is not False]
            n_loop = 0
            while True:
                n_loop += 1
                play_rows = pick_play_order(active, pct=pct, shuffle=args.shuffle)
                print("— รอบที่ %d —" % n_loop)
                for i, r in enumerate(play_rows, 1):
                    if not running[0]:
                        return False
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

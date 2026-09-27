#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Mouse & Keyboard Macro  v1.5
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

APP_TITLE = "Auto Mouse & Keyboard Macro v1.5"
CONF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "macro_conf.json")
PROFILES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "macro_profiles.json")
DEFAULT_PROFILE = "ค่าเริ่มต้น"

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

        btn("💾", "Save", self.save_script)
        btn("📂", "Load", self.load_script)
        btn("⚙️", "Settings", self.settings_dialog)
        btn("ℹ️", "About", self.about)
        btn("❓", "Help", self.help_dialog)
        btn("⏻", "Exit", self._on_close, color="#b00")

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
        และออโต้ปิดตัวเองถ้าโปรแกรมอื่นใช้คีย์ชุดนี้อยู่แล้ว"""
        mapping = {
            "<f6>": lambda: self.root.after(0, self.start_play),
            "<f8>": lambda: self.root.after(0, self.stop_all),
            "<f9>": lambda: self.root.after(0, self.toggle_record),
            "<f10>": lambda: self.root.after(0, self._toggle_forever),
        }
        try:
            self._gk = GlobalHotKeys(mapping)
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
    def _rows_for_play(self):
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
                p = (r["additional"] or "").strip()
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
        self.stop_all(silent=True)
        self.running = True
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
        self.btn_start.config(state="disabled", bg="#cfcfcf")
        self.btn_repeat.config(state="disabled", bg="#2e7d32")
        mode = "วนซ้ำ" if loop else "เล่นครั้งเดียว"
        self.root.title(APP_TITLE + "   [ RUNNING ]")
        self._ui_state["msg"] = ("กำลังเล่นสคริปต์ (%s) — F8 หยุด" % mode, "#080")
        threading.Thread(target=self._player, args=(rows, loop), daemon=True).start()

    def _reset_ui(self):
        self.btn_start.config(state="normal", bg="#e8e8e8")
        self.btn_repeat.config(state="normal", bg="#3fa63f", fg="white")
        self.root.title(APP_TITLE)

    def stop_all(self, silent=False):
        was = self.running or self.recording
        self.running = False
        if self.recording:
            self._stop_record()
        self._ui_state["row"] = None
        self._ui_state["reset"] = True
        if was and not silent:
            self._ui_state["msg"] = ("หยุดแล้ว", "#a60")

    def _player(self, rows, loop):
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
                elif act == "Up":
                    self.mouse_ctl.release(btn_obj)
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
                    if not self.running:
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
                elif btn == "Release Key":
                    self.kb_ctl.release(k)
                else:
                    self.kb_ctl.tap(k)

        # บั๊กฟิกซ์ v1.6: เดิมลูปนี้ถูกแทรกหลัง return ของ kb_ctrl_char ทำให้เป็น dead code
        try:
            start_pos = self.mouse_ctl.position if self._restore_pos else None
            total = len(rows)
            loop_no = 0
            outer = True
            while outer:
                loop_no += 1
                # _script_loops: 0 = ไม่จำกัด, 1 = ครั้งเดียว, N = N รอบ
                for i, r in enumerate(rows):
                    if not self.running:
                        return
                    children = self.tree.get_children()
                    self._ui_state["row"] = children[i] if i < len(children) else None
                    self._ui_state["prog"] = (i + 1, total, loop_no)
                    for _ in range(parse_int(r["repeat"])):
                        if not self.running:
                            return
                        lo, hi = delay_range(r["secs"])
                        base = delay_seconds(r["mins"], 0) + (lo if lo == hi else random.uniform(lo, hi))
                        time.sleep(max(0.0, base / self._speed_mult))
                        if not self.running:
                            return
                        do_step(r)
                self._ui_state["row"] = None
                self._ui_state["prog"] = (total, total, loop_no)
                if self._restore_pos and start_pos and self.running:
                    self.mouse_ctl.position = start_pos
                if loop:
                    break                      # REPEAT/forever คุมรอบอยู่แล้ว
                if self._script_loops == 0:
                    outer = self.running       # ไม่จำกัดรอบ
                else:
                    self._script_loops -= 1
                    outer = self._script_loops > 0 and self.running
            if self.running:
                self._ui_state["msg"] = ("เล่นจบแล้ว ✔", "#080")
        finally:
            self.running = False
            self._ui_state["row"] = None
            self._ui_state["prog"] = None
            self._ui_state["reset"] = True

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
        """อ่านกรอบค้นหา (search area) จากช่อง Additional รูปแบบ
            ไฟล์.png@x,y,กว้าง,สูง     เช่น  button.png@100,200,300,400
        คืน (path, (left, top, right, bottom)) หรือ (path, None) = ค้นทั้งจอ"""
        raw = (r.get("additional") or "").strip()
        if "@" not in raw:
            return raw, None
        path, _, coords = raw.partition("@")
        try:
            x, y, w, h = [int(float(p.strip())) for p in coords.split(",")]
        except ValueError:
            return path, None          # พิมพ์พลาด → ค้นทั้งจอ
        if w <= 0 or h <= 0:
            return path, None
        return path, (x, y, x + w, y + h)

    def _grab_area_bgr(self, area):
        """จับภาพหน้าจอเฉพาะกรอบ (ถ้า area=None = ทั้งจอ) คืน numpy BGR"""
        if area and len(area) == 4:
            shot = ImageGrab.grab(bbox=area, all_screens=True)
        else:
            shot = ImageGrab.grab(all_screens=True)
        return cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR), (area[0], area[1]) if area else (0, 0)

    def _do_wait_for_image(self, r):
        """รอจนกว่าจะเจอภาพบนหน้าจอ (timeout 30 วิ) — รองรับ search area ใน Additional"""
        path, area = self._parse_search_area(r)
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
        while time.time() < deadline and self.running:
            screen, _off = self._grab_area_bgr(area)
            if tmpl.shape[0] <= screen.shape[0] and tmpl.shape[1] <= screen.shape[1]:
                res = cv2.matchTemplate(screen, tmpl, cv2.TM_CCOEFF_NORMED)
                _, maxv, _, _ = cv2.minMaxLoc(res)
                if maxv >= 0.80:
                    return
            time.sleep(0.5)
        self._ui_state["msg"] = ("Wait for Image: ไม่เจอภาพภายใน 30 วิ — %s" % os.path.basename(path), "#a60")

    # ------------------------------------------------------ image click ------
    def _do_image_click(self, r):
        """หาภาพย่อยบนหน้าจอแล้วคลิกที่จุดศูนย์กลาง
        ช่อง Additional: ไฟล์.png หรือ ไฟล์.png@x,y,กว้าง,สูง (กรอบค้นหา)"""
        path, area = self._parse_search_area(r)
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
            if maxv < 0.80:
                self._ui_state["msg"] = ("หาภาพไม่เจอ (ความมั่นใจ %.0f%%): %s" % (maxv * 100, os.path.basename(path)), "#c00")
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
                json.dump(self._serialize(), fh, ensure_ascii=False, indent=2)
        except OSError:
            pass

    # ------------------------------------------------------------- dialogs ---
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
        tk.Label(win, text="Image Click: " + ("พร้อมใช้ ✅" if HAS_CV else
                 "ยังไม่พร้อม — ติดตั้งด้วย: pip install opencv-python Pillow"),
                 fg="#080" if HAS_CV else "#a60").pack()
        tk.Button(win, text="ปิด", width=8, command=win.destroy).pack(pady=(8, 14))

    def about(self):
        messagebox.showinfo("About",
                            APP_TITLE + "\n\nโปรแกรมสั่งงานเมาส์/คีย์บอร์ดอัตโนมัติ\n"
                            "Python " + sys.version.split()[0] + "  •  Tkinter + pynput\n\n"
                            "F6 เล่น | F8 หยุด | F9 บันทึก | F10 วนซ้ำ\n"
                            "(คีย์ลัดกดได้แม้ไม่โฟกัสหน้าต่าง)")

    def help_dialog(self):
        messagebox.showinfo("Help",
            "วิธีใช้งาน\n"
            "1) กด RECORD (F9) แล้วคลิก/พิมพ์ตามจริง โปรแกรมจะจดทุกเหตุการณ์ลงตาราง\n"
            "2) ดับเบิลคลิกช่อง X หรือ Y เพื่อจับพิกัดเมาส์ใหม่ (นับถอยหลัง 3 วิ)\n"
            "3) ดับเบิลคลิกช่องอื่นเพื่อแก้ Action / คีย์ / เวลาหน่วง / Repeat\n"
            "4) คลิกช่องแรก (☑/☐) เพื่อเปิด-ปิดการใช้งานแต่ละแถว\n"
            "5) START (F6) เล่นรอบเดียว, REPEAT เล่นซ้ำ, F10 วนไม่จำกัด, STOP (F8) หยุด\n"
            "6) Save / Load เก็บสคริปต์เป็นไฟล์ .json และเปิดกลับมาแก้ไขได้\n"
            "7) แถบ 'โปรไฟล์' — เก็บหลายสคริปต์สลับใช้ได้ (เช่น งานบ้าน / เกม A / เกม B)\n"
            "8) ปุ่ม ⏰ เล่นอัตโนมัติ — ตั้งเล่นทุก N นาที หรือทุกวันตามเวลา HH:MM\n"
            "9) Action 'Image Click' — คลิกตามภาพ: ใส่ชื่อไฟล์ .png ในช่อง Additional\n"
            "   (ต้องติดตั้ง: pip install opencv-python Pillow)\n"
            "10) Action ใหม่ v1.5: Scroll Up/Down, Double Click, Ctrl/Shift/Alt+Click,\n"
            "   Move Mouse (+Offset), Save/Restore Cursor, Type Text, Launch App,\n"
            "   Wait for Image, Beep\n"
            "11) ช่อง Secs ใส่แบบสุ่มได้ เช่น 1-3 = สุ่มดีเลย์ 1–3 วิ\n"
            "12) ปุ่มล่าง: ความเร็ว (0.25×–4×), จำนวนรอบ (0=ไม่จำกัด), คืนเมาส์จุดเดิม\n\n"
            "หมายเหตุ: Secs คือเวลารอก่อนทำคำสั่งในแถวนั้น, Repeat คือจำนวนครั้งที่ทำซ้ำ")

    def _on_close(self):
        self.running = False
        self.recording = False
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
    args = ap.parse_args(argv)

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
            elif act == "Up":
                mouse_ctl.release(btn_obj)
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
                elif btn == "Release Key":
                    kb_ctl.release(k)
                else:
                    kb_ctl.tap(k)
        elif btn == "Type Text":
            for ch in str(r.get("additional") or ""):
                kb_ctl.tap(KeyCode.from_char(ch))
        elif btn == "Beep":
            print("\a", end="", flush=True)
        # (หมายเหตุ: Image Click/Wait for Image ยังไม่รองรับใน CLI — ใช้ GUI)

    stops = {"<f8>", "<esc>"}
    try:
        stopper = keyboard.GlobalHotKeys({k: (lambda: running.__setitem__(0, False))
                                         for k in stops})
        stopper.daemon = True
        stopper.start()
        gk_ok = True
    except Exception:
        gk_ok = False

    print("เล่นสคริปต์: %s (%d แถว)%s%s" % (
        os.path.basename(args.script), len(rows),
        "  •  วนไม่จำกัด" if (args.loop or args.loops == 0) else "",
        "  •  ความเร็ว %gx" % speed))
    if gk_ok:
        print("หยุด: กด F8 หรือ Esc (หรือ Ctrl+C)")
    else:
        print("หยุด: Ctrl+C")
    try:
        loops = 0 if args.loop else max(0, args.loops)
        active = [r for r in rows if r.get("enabled", True) is not False]
        n_loop = 0
        while True:
            n_loop += 1
            print("— รอบที่ %d —" % n_loop)
            for i, r in enumerate(active, 1):
                if not running[0]:
                    break
                lo, hi = delay_range(r.get("secs", 1))
                base = delay_seconds(r.get("mins", 0), 0) + (lo if lo == hi else random.uniform(lo, hi))
                time.sleep(max(0.0, base / speed))
                if not running[0]:
                    break
                do_step(r)
                print("  [%d/%d] %s %s" % (i, len(active), r.get("button", ""),
                                          r.get("additional", "")))
            if not running[0]:
                break
            if loops == 0:
                continue
            loops -= 1
            if loops <= 0:
                break
        print("จบแล้ว ✔")
        return 0
    except KeyboardInterrupt:
        print("\nหยุดโดยผู้ใช้")
        return 130
    finally:
        running[0] = False
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

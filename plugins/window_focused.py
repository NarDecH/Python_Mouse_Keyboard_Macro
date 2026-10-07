# -*- coding: utf-8 -*-
"""Plugin API v3 (v2.13) — เงื่อนไข: Window Focused (v2.16 — Issue #5)

เช็คว่า**หน้าต่างที่โฟกัสอยู่ตอนนี้** (foreground) มีข้อความนี้ในชื่อหรือไม่
(ต่างจาก Window Exists ที่สแกนทุกหน้าต่าง — ตัวนี้ดูเฉพาะตัวที่ active จึงเหมาะกับ
งานแบบ "ทำต่อเมื่อหน้าต่างงานยังอยู่หน้าเดียว")
- Windows: ctypes ล้วน (GetForegroundWindow + GetWindowTextW) — ไม่เพิ่ม dependency
- Linux: xdotool getactivewindow getwindowname — ไม่มีเครื่องมือ = False (ไม่พัง)
- macOS: osascript ผ่าน System Events — บล็อกเพราะสิทธิ์ accessibility = False

Additional = ข้อความในชื่อหน้าต่าง เช่น "Notepad" (เทียบไม่สนตัวพิมพ์ · ใช้ {ตัวแปร} ได้)

ใช้ได้ 2 ทาง:
  1. คอลัมน์ Action = "Window Focused" → โฟกัสตรง = เล่นต่อ, ไม่ตรง = ข้าม N แถว (N = Repeat)
  2. Block Start → Additional: `if Window Focused งานเอกสาร` (ผสม && กับเงื่อนไขอื่นได้)
"""
import sys

CONDITION_NAME = "Window Focused"


def _foreground_title():
    """ชื่อหน้าต่าง foreground ของ OS นี้ — ดึงไม่ได้ = \"\" (เงื่อนไขเป็นเท็จ ไม่พัง)"""
    if sys.platform == "win32":
        import ctypes
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if not hwnd:
            return ""
        n = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        if n <= 0:
            return ""
        buf = ctypes.create_unicode_buffer(n + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, n + 1)
        return buf.value
    if sys.platform.startswith("linux"):
        import subprocess
        out = subprocess.run(["xdotool", "getactivewindow", "getwindowname"],
                             capture_output=True, timeout=3,
                             text=True, errors="replace")
        return (out.stdout or "").strip()
    if sys.platform == "darwin":
        import subprocess
        out = subprocess.run(
            ["osascript", "-e",
             'tell application "System Events" to get name of '
             "first application process whose frontmost is true"],
            capture_output=True, timeout=5, text=True, errors="replace")
        return (out.stdout or "").strip()
    return ""


def check(ctx, row):
    """คืน True เมื่อหน้าต่าง foreground มีข้อความนี้ (ไม่สนตัวพิมพ์) — ห้าม raise"""
    try:
        needle = str(row.get("additional") or "").strip().lower()
        if not needle:
            return False
        title = _foreground_title()
        return bool(title) and needle in title.lower()
    except Exception:
        return False

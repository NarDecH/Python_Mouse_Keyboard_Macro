# -*- coding: utf-8 -*-
"""Plugin API v3 (v2.13) — เงื่อนไข: Window Exists (v2.14)

เช็คว่ามีหน้าต่างที่ชื่อ (title) มีข้อความนี้อยู่หรือไม่ (เทียบแบบไม่สนตัวพิมพ์)
- Windows: ctypes ล้วน (EnumWindows + GetWindowTextW) — ไม่เพิ่ม dependency
- macOS/Linux: fallback ผ่าน xdotool (Linux) — ไม่มีเครื่องมือ = False (ไม่พัง)

ใช้ได้ 2 ทาง:
  1. คอลัมน์ Action = "Window Exists" → เจอหน้าต่าง = เล่นต่อ, ไม่เจอ = ข้าม N แถว (N = Repeat)
  2. Block Start → Additional: `if Window Exists Notepad` (ผสม && กับเงื่อนไขอื่นได้)

Additional = ข้อความในชื่อหน้าต่าง เช่น "Notepad" หรือ "chrome" (ใช้ {ตัวแปร} ได้)
"""
import sys

CONDITION_NAME = "Window Exists"


def _titles_windows():
    """Windows: ดึงชื่อหน้าต่างทั้งหมดด้วย ctypes (ล้วน stdlib)"""
    import ctypes
    import ctypes.wintypes
    titles = []

    cb = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)

    def on_window(hwnd, _lparam):
        if ctypes.windll.user32.IsWindowVisible(hwnd):
            n = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            if n > 0:
                buf = ctypes.create_unicode_buffer(n + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, buf, n + 1)
                titles.append(buf.value)
        return True

    ctypes.windll.user32.EnumWindows(cb(on_window), 0)
    return titles


def _titles_linux():
    """Linux: xdotool ถ้ามี — ไม่มี = [] (เงื่อนไขเป็นเท็จ โปรแกรมไม่พัง)"""
    try:
        import subprocess
        out = subprocess.run(["xdotool", "search", "", "getwindowname", "%@"],
                             capture_output=True, timeout=3,
                             text=True, errors="replace")
        return [t for t in (out.stdout or "").splitlines() if t.strip()]
    except Exception:
        return []


def check(ctx, row):
    """คืน True เมื่อมีหน้าต่างที่ชื่อมีข้อความ (ไม่สนตัวพิมพ์) — ห้าม raise"""
    try:
        needle = str(row.get("additional") or "").strip().lower()
        if not needle:
            return False
        if sys.platform == "win32":
            titles = _titles_windows()
        else:
            titles = _titles_linux()
        return any(needle in t.lower() for t in titles)
    except Exception:
        return False

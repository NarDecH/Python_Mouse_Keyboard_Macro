# -*- coding: utf-8 -*-
"""Plugin API v3 (v2.13) — เงื่อนไข: Window Closed (v2.17 — Issue #6)

เช็คว่าไม่มีหน้าต่างที่ชื่อมีข้อความนี้เปิดอยู่ = จริง — **ตรงข้ามกับ Window Exists**
ใช้จบงานเมื่อปิดหน้าต่างเป้าหมาย เช่น "เกมปิดแล้ว → ล้างไฟล์ temp แล้วบี๊บแจ้ง"

Windows: ctypes ล้วน (EnumWindows + GetWindowTextW) — ไม่เพิ่ม dependency
Linux: xdotool — ไม่มีเครื่องมือ = ถือว่าปิดแล้ว (จริง) โปรแกรมไม่พัง

Additional = ข้อความในชื่อหน้าต่าง เช่น "Notepad" (เทียบไม่สนตัวพิมพ์ · ใช้ {ตัวแปร} ได้)

ใช้ได้ 2 ทาง:
  1. คอลัมน์ Action = "Window Closed" → ปิดแล้ว = เล่นต่อ, ยังเปิด = ข้าม N แถว (N = Repeat)
  2. Block Start → Additional: `if Window Closed Setup.exe` (ผสม && กับเงื่อนไขอื่นได้)
"""
import sys

CONDITION_NAME = "Window Closed"


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
    """Linux: xdotool ถ้ามี — ไม่มี = [] (ถือว่าไม่มีหน้าต่าง → ปิดแล้ว = จริง)"""
    try:
        import subprocess
        out = subprocess.run(["xdotool", "search", "", "getwindowname", "%@"],
                             capture_output=True, timeout=3,
                             text=True, errors="replace")
        return [t for t in (out.stdout or "").splitlines() if t.strip()]
    except Exception:
        return []


def check(ctx, row):
    """คืน True เมื่อไม่มีหน้าต่างที่ชื่อมีข้อความนี้ (ไม่สนตัวพิมพ์) — ห้าม raise

    ⚠️ แถว Additional ว่าง = ไม่รู้จะดูหน้าต่างอะไร = เท็จ (กันสคริปต์พิมพ์ผิดแล้วคิดว่าปิดแล้ว)"""
    try:
        needle = str(row.get("additional") or "").strip().lower()
        if not needle:
            return False
        if sys.platform == "win32":
            titles = _titles_windows()
        else:
            titles = _titles_linux()
        return not any(needle in t.lower() for t in titles)
    except Exception:
        return False

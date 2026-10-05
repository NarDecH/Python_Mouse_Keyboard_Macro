# -*- coding: utf-8 -*-
"""Plugin API v3 (v2.13) — เงื่อนไข: Process Running (v2.14)

เช็คว่ามีโปรเซสที่ชื่อตรงกับ Additional กำลังรันอยู่หรือไม่
- Windows: ใช้ tasklist (มีในตัว Windows เสมอ) — ไม่เพิ่ม dependency
- Linux: pgrep · macOS: pgrep (มีในตัว) — ไม่มีคำสั่ง = False (ไม่พัง)

Additional = ชื่อโปรเซส เช่น "chrome" หรือ "explorer.exe" (เทียบแบบไม่สนตัวพิมพ์
และไม่สนนามสกุล .exe — ใช้ {ตัวแปร} ได้)

ใช้ได้ 2 ทาง:
  1. คอลัมน์ Action = "Process Running" → รันอยู่ = เล่นต่อ, ไม่รัน = ข้าม N แถว (N = Repeat)
  2. Block Start → Additional: `if Process Running chrome` (ผสม && กับเงื่อนไขอื่นได้)
"""
import shutil
import subprocess
import sys

CONDITION_NAME = "Process Running"


def _running_windows(needle):
    """Windows: tasklist /FO CSV — แถวแรกคือหัวตาราง ข้าม"""
    out = subprocess.run(["tasklist", "/FO", "CSV"], capture_output=True,
                         timeout=10, text=True, errors="replace")
    lines = (out.stdout or "").splitlines()[1:]
    for ln in lines:
        # CSV รูปแบบ: "ชื่อ","pid",... — ชื่ออยู่คอลัมน์แรกเสมอ (แม้มี comma ในชื่อก็ไม่มีจริง)
        name = ln.split('","', 1)[0].strip().strip('"').lower()
        if name and needle in name:
            return True
    return False


def _running_pgrep(needle):
    """Linux/macOS: pgrep -f (จับจากบรรทัดคำสั่งเต็ม) — ไม่เจอคืน rc=1, ไม่มี pgrep = False"""
    exe = shutil.which("pgrep")
    if not exe:
        return False
    out = subprocess.run([exe, "-f", needle], capture_output=True, timeout=5,
                         text=True, errors="replace")
    return bool((out.stdout or "").strip())


def check(ctx, row):
    """คืน True เมื่อโปรเซสรันอยู่ — ห้าม raise (engine จับให้อยู่แล้ว แต่กติกา plugin = ทนเอง)"""
    try:
        needle = str(row.get("additional") or "").strip().lower()
        if not needle:
            return False
        if needle.endswith(".exe"):
            needle = needle[:-4]
        if sys.platform == "win32":
            return _running_windows(needle)
        if sys.platform == "darwin" and not shutil.which("pgrep"):
            # macOS เก่าไม่มี pgrep ใน PATH — เช็ค /proc ยาก ปล่อย False
            return False
        return _running_pgrep(needle)
    except Exception:
        return False

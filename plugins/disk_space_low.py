# -*- coding: utf-8 -*-
"""Plugin API v3 (v2.13) — เงื่อนไข: Disk Space Low (v2.17 — Issue #6)

เช็คว่าพื้นที่ดิสก์เหลือน้อยกว่าที่กำหนดหรือยัง — กันงานเขียนไฟล์/บันทึกผลพังกลางทาง
stdlib ล้วน (shutil.disk_usage) — ไม่เพิ่ม dependency

Additional = `[ไดรฟ์/พาธ] N[GB|MB]` เช่น
  5GB          → โฟลเดอร์ทำงานปัจจุบันเหลือ < 5 GB = จริง
  500MB        → เหลือ < 500 MB
  D: 2GB       → ไดรฟ์ D: เหลือ < 2 GB
  C:\\ 1.5GB   → พาธใดก็ได้ (ใช้ระบบไฟล์ของพาธนั้น)

ไม่ใส่หน่วย = ถือเป็น MB · ใช้ {ตัวแปร} ได้

ใช้ได้ 2 ทาง:
  1. คอลัมน์ Action = "Disk Space Low" → พื้นที่เหลือน้อย = จริง (ทำกลุ่มล้างไฟล์/แจ้งเตือน),
     ปกติ = ข้าม N แถว (N = Repeat)
  2. Block Start → Additional: `if Disk Space Low D: 2GB` (ผสม && กับเงื่อนไขอื่นได้)
"""
import os
import shutil

CONDITION_NAME = "Disk Space Low"


def _parse_bytes(tok):
    """ตัวเลข + หน่วย → จำนวนไบต์ (ไม่มีหน่วย = MB) · แปลไม่ได้ = None"""
    t = str(tok).strip().upper()
    if not t:
        return None
    mult = 1024 * 1024                     # ไม่ใส่หน่วย = MB
    for suffix, m in (("GB", 1024 ** 3), ("MB", 1024 * 1024),
                      ("KB", 1024), ("B", 1)):
        if t.endswith(suffix):
            t = t[:-len(suffix)].strip()
            mult = m
            break
    try:
        return int(float(t) * mult)
    except (ValueError, TypeError):
        return None


def check(ctx, row):
    """คืน True เมื่อพื้นที่ว่างเหลือ < ที่กำหนด — ห้าม raise (อ่านดิสก์ไม่ได้ = เท็จ)"""
    try:
        parts = str(row.get("additional") or "").split()
        if not parts:
            return False
        # โทเคนท้ายสุดคือขนาด — ที่เหลือคือไดรฟ์/พาธ (รองรับพาธมีช่องว่างด้วยการ rsplit)
        size = _parse_bytes(parts[-1])
        if size is None:
            return False
        path = " ".join(parts[:-1]).strip() or os.getcwd()
        total, used, free = shutil.disk_usage(path)
        return free < size
    except Exception:
        return False

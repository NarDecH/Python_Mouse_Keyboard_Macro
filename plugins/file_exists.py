# -*- coding: utf-8 -*-
"""Plugin API v3 (v2.13) — เงื่อนไขตัวอย่าง: File Exists

เงื่อนไข plugin ประกาศ CONDITION_NAME + check(ctx, row) -> bool (แทน ACTION_NAME+run)
ใช้ได้ 2 ทาง:
  1. คอลัมน์ Action = "File Exists" → ไฟล์มีจริง = เล่นต่อ, ไม่มี = ข้าม N แถว (N = Repeat)
  2. Block Start → Additional: `if File Exists C:\\tmp\\done.flag` (ผสม && กับเงื่อนไขอื่นได้)

Additional = พาธไฟล์ (ใช้ {ตัวแปร} ได้ — ถูกแทนค่าก่อนส่งเข้ามาแล้ว) · แนะนำพาธเต็ม
Dry-run: เงื่อนไขเดินจริงเหมือนเงื่อนไขในตัว — check ถูกเรียกจริง (อย่าให้ check แตะเมาส์/คีย์)
"""
import os

CONDITION_NAME = "File Exists"


def check(ctx, row):
    """คืน True/False — ห้าม raise (engine จับให้อยู่แล้ว แต่กติกา plugin = ทนเอง)"""
    try:
        path = str(row.get("additional") or "").strip()
        if not path:
            return False
        return os.path.isfile(path)
    except Exception:
        return False

# -*- coding: utf-8 -*-
"""Plugin API v3 (v2.13) — เงื่อนไข: File Newer Than (v2.16 — Issue #5)

เช็คว่าไฟล์ถูกเขียน/แก้ล่าสุดเมื่อไหร่ — ใช้ได้ 2 รูปแบบในช่อง Additional:

  1. `ไฟล์A > ไฟล์B`  — ไฟล์A ใหม่กว่าไฟล์B = จริง (watch งาน: report.csv ใหม่กว่า
     done.flag → ยังไม่เคยประมวลผล → เล่นกลุ่มแปลงไฟล์ต่อ)
  2. `ไฟล์ Ns`        — ไฟล์ถูกแก้ภายใน N วินาทีล่าสุด = จริง (รอ download เสร็จ:
     setup.zip 5s → เพิ่งโหลดมาแป๊บเดียว)

หมายเหตุ: พาธมีช่องว่างใช้ได้เพราะแยกโทเคนด้วย ` > ` และช่องว่างก่อน `Ns` เท่านั้น
(โทเคน Ns สไตล์เดียวกับ Internet Up / Wait for Image) · ใช้ {ตัวแปร} ได้

ใช้ได้ 2 ทาง:
  1. คอลัมน์ Action = "File Newer Than" → จริง = เล่นต่อ, เท็จ = ข้าม N แถว (N = Repeat)
  2. Block Start → Additional: `if File Newer Than C:\\log\\a.txt > C:\\log\\b.txt`
"""
import os

CONDITION_NAME = "File Newer Than"


def _mtime(path):
    """mtime ของไฟล์ — ไม่มีไฟล์/อ่านไม่ได้ = None"""
    try:
        return os.path.getmtime(str(path))
    except OSError:
        return None


def check(ctx, row):
    """คืน True ตามเงื่อนไขเวลาแก้ไฟล์ — ห้าม raise (input พังทุกแบบ = เท็จ)"""
    try:
        spec = str(row.get("additional") or "").strip()
        if not spec:
            return False
        if " > " in spec:                        # รูปแบบที่ 1: ไฟล์A > ไฟล์B
            a, _, b = spec.partition(" > ")
            ma, mb = _mtime(a.strip()), _mtime(b.strip())
            if ma is None or mb is None:
                return False
            return ma > mb
        parts = spec.rsplit(None, 1)             # รูปแบบที่ 2: ไฟล์ Ns
        if len(parts) == 2:
            path, tok = parts[0], parts[1].strip()
            if tok.endswith("s") and tok[:-1].replace(".", "", 1).isdigit():
                m = _mtime(path)
                if m is None:
                    return False
                import time
                age = time.time() - m
                return age <= max(0.0, float(tok[:-1]))
        m = _mtime(spec)                         # ไฟล์ล้วน = "มีไฟล์และแก้ได้" = จริง
        return m is not None
    except Exception:
        return False

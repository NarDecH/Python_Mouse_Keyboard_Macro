# -*- coding: utf-8 -*-
"""Counter — นับ/ตั้งตัวแปรสำหรับแถวถัดไป (v2.8 plugin ชุมชนตัวอย่างที่ 2)

Additional: "ชื่อ"          → ชื่อ += 1 (สร้างใหม่เริ่ม 0)
            "ชื่อ += 5"      → เพิ่ม 5
            "ชื่อ -= 2"      → ลด 2
            "ชื่อ = ค่าใด ๆ" → ตั้งค่าตรง
            "ชื่อ = rand 1-10" → สุ่มเลข
ใช้ตัวแปรได้ในแถวถัดไปด้วย {ชื่อ} — คู่กับ If Variable เป็นลูปนับรอบได้
ผ่านตัวแปรที่มีอยู่ให้ substitute แทนค่าก่อน (เหมือน Set Variable)
"""

ACTION_NAME = "Counter"


def run(ctx, row):
    if not isinstance(ctx, dict):
        return None
    vars_ = ctx.get("vars")
    if not isinstance(vars_, dict):
        return None
    try:
        from macro_engine import apply_set_var
    except Exception:
        return None
    raw = str(row.get("additional") or "").strip()
    if not raw:
        return None
    if " " not in raw and "=" not in raw:
        raw = raw + " += 1"                      # ชื่อเดี่ยว = นับ +1
    apply_set_var(vars_, raw)
    log = ctx.get("log")
    if callable(log):
        log("counter: " + raw)
    return None

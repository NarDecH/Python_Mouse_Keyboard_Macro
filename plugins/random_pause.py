# -*- coding: utf-8 -*-
"""Random Pause — สุ่มพักช่วงเวลา (v2.8 plugin ชุมชนตัวอย่างที่ 1)

Additional: "ต่ำสุด-สูงสุด" วินาที เช่น "1.5-4" (หรือเลขเดียว = คงที่)
ทำไม่ได้/รูปแบบพัง = พัก 1 วินาที — โปรแกรมต้องไม่พังเด็ดขาด
ตัวอย่างใช้จริง: แทรกก่อนคลิกซ้ำ ๆ ให้จังหวะเป็นธรรมชาติกว่า
ใช้เฉพาะกับงานของคุณเอง — อ่านเงื่อนไขการใช้ใน docs/PLUGINS.md
"""

import random
import time

ACTION_NAME = "Random Pause"


def run(ctx, row):
    raw = str(row.get("additional") or "").strip()
    lo, hi = 1.0, 1.0
    try:
        if "-" in raw:
            a, b = raw.split("-", 1)
            lo, hi = float(a or 1.0), float(b or lo)
        elif raw:
            lo = hi = float(raw)
    except ValueError:
        lo = hi = 1.0
    if lo > hi:
        lo, hi = hi, lo
    secs = max(0.0, random.uniform(lo, hi))
    # พักเป็นชิ้นสั้น ๆ (≤0.2 วิ) เพื่อเช็ค STOP ระหว่างทาง (ctx["stop_check"] ขาดก็ทน)
    stop_check = ctx.get("stop_check") if isinstance(ctx, dict) else None
    left = secs
    while left > 0:
        if callable(stop_check) and stop_check():
            return None
        chunk = min(0.2, left)
        time.sleep(chunk)
        left -= chunk
    log = ctx.get("log") if isinstance(ctx, dict) else None
    if callable(log):
        log("random pause %.2fs" % secs)
    return None

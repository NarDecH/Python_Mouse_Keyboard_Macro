# -*- coding: utf-8 -*-
# แม่แบบ plugin (ไฟล์ขึ้นต้น _ → โปรแกรมไม่โหลด) — ก๊อปเป็นชื่ออื่นแล้วแก้ได้เลย
# ดูตัวอย่างจริงที่ sleep_seconds.py และ message_box.py

import time

ACTION_NAME = "My Action"          # ชื่อที่โชว์ในคอลัมน์ Action (ห้ามซ้ำ)


def run(ctx, row):
    """ctx: mouse, kb, log(ข้อความ), cfg={"lang": "th"/"en"},
          stop_check() (v1.20 — False เมื่อผู้ใช้กด STOP), ui={"msg", "beep"} (v1.20)
    row: dict ของแถว (x, y, additional, mins, secs, repeat, ...)"""
    msg = str(row.get("additional") or "")
    if callable(ctx.get("log")):
        ctx["log"]("my action: %r" % msg)
    # ... ทำงานของคุณที่นี่ เช่น ctx["mouse"].position, ctx["kb"].tap(...)
    time.sleep(0.1)

# -*- coding: utf-8 -*-
"""Custom Action plugin ตัวอย่าง: "Sleep (plugin)" — หน่วงตามวินาทีที่ระบุ
ใช้เป็นแม่แบบเขียน plugin ของคุณเอง (ดูรายละเอียดเพิ่มใน plugins/README.md):

    ACTION_NAME = "ชื่อที่โชว์ในคอลัมน์ Action"   # ห้ามซ้ำกับ Action เดิม
    def run(ctx, row): ...

ctx มี: ctx["mouse"] (pynput mouse controller), ctx["kb"] (pynput keyboard),
        ctx["log"](ข้อความ) — เขียนลง log การเล่น, ctx["cfg"] = {"lang": "th"/"en"}
row คือ dict ของแถวนั้น (x, y, additional, mins, secs, repeat, ...)

ตั้งค่าในตาราง: Additional = จำนวนวินาที (เช่น 2 หรือ 1.5)
"""

import time

ACTION_NAME = "Sleep (plugin)"


def run(ctx, row):
    try:
        secs = float(str(row.get("additional") or "1").strip() or "1")
    except ValueError:
        secs = 1.0
    if secs < 0:
        secs = 0.0
    if callable(ctx.get("log")):
        ctx["log"]("sleep %.1f วินาที (plugin)" % secs)
    time.sleep(secs)

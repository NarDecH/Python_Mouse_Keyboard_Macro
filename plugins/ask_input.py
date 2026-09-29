# -*- coding: utf-8 -*-
"""Custom Action plugin: "Ask Input" — ถามค่าจากผู้ใช้ตอนเล่น เก็บเป็นตัวแปร (v2.5)
ตั้งค่าในตาราง: Additional = ชื่อตัวแปร | หัวข้อ | ค่าเริ่มต้น   (ค่าเริ่มต้น/หัวข้อ ใส่ได้)
ตัวอย่าง:  code | ใส่รหัสลูกค้า | C-000
หลังแถวนี้ เรียกใช้ค่าที่กรอกด้วย {code} ในช่องอื่นได้ทันที (เช่น Type Text)
- ใช้ tkinter simpledialog แบบ lazy import — ไม่มี display → ใช้ค่าเริ่มต้น + log
"""
ACTION_NAME = "Ask Input"


def run(ctx, row):
    parts = (str(row.get("additional") or "").split("|") + ["", "", ""])[:3]
    name = parts[0].strip()
    title = parts[1].strip() or "กรอกค่าสำหรับ " + (name or "สคริปต์")
    default = parts[2].strip()
    ui = ctx.get("ui") or {}
    show = ui.get("msg") if isinstance(ui, dict) else None

    def report(text, color="#080"):
        if callable(show):
            show(text, color)
        if callable(ctx.get("log")):
            ctx["log"](text)

    if not name:
        report("Ask Input: ต้องระบุชื่อตัวแปรก่อน | เช่น code|ใส่รหัส", "#c00")
        return
    vars_ = ctx.get("vars") if isinstance(ctx.get("vars"), dict) else None
    if vars_ is None:
        report("Ask Input: ตัวแปรใช้ไม่ได้ในโหมดนี้ (ไม่มี vars) — ข้าม", "#a60")
        return
    try:
        import tkinter as tk
        from tkinter import simpledialog
        r = tk.Tk()
        r.withdraw()
        try:
            val = simpledialog.askstring("Auto Mouse Macro — Ask Input", title,
                                         initialvalue=default)
        finally:
            r.destroy()
    except Exception as exc:                       # ไม่มี display → ใช้ค่าเริ่มต้น + log
        report("Ask Input: ถามผู้ใช้ไม่ได้ (%s) — ใช้ค่าเริ่มต้น %r" % (
            type(exc).__name__, default))
        vars_[name] = default
        return
    vars_[name] = str(val if val is not None else default)
    report("Ask Input: %s = %r" % (name, vars_[name]))

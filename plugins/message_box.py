# -*- coding: utf-8 -*-
"""Custom Action plugin ตัวอย่าง: "Message Box" — แสดงกล่องข้อความกลางการเล่น
ข้อความเอาจากคอลัมน์ Additional ของแถวนั้น (ว่าง = "Hello from plugin!")

หมายเหตุ: import tkinter แบบ lazy ใน run() เพื่อไม่ให้การโหลด plugin
(ที่เกิดตอนเปิดโปรแกรม/รัน CLI) พึ่ง GUI
"""

ACTION_NAME = "Message Box"


def run(ctx, row):
    msg = str(row.get("additional") or "").strip() or "Hello from plugin!"
    try:
        import tkinter as tk
        from tkinter import messagebox
        r = tk.Tk()
        r.withdraw()
        try:
            messagebox.showinfo("Auto Mouse Macro — plugin", msg)
        finally:
            r.destroy()
    except Exception as exc:                       # ไม่มี display / Tk พัง → log แทน
        if callable(ctx.get("log")):
            ctx["log"]("message box แสดงไม่ได้ (%s): %s" % (type(exc).__name__, msg))

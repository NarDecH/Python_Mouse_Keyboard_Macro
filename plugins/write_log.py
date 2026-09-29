# -*- coding: utf-8 -*-
"""Custom Action plugin: "Write Log" — เขียนข้อความของคุณเองลง log การเล่น (v2.5)
ตั้งค่าในตาราง: Additional = ข้อความ (ใช้ {ตัวแปร} ได้)
เหมาะกับ: ประกอบรายงานระหว่างเล่น เช่น "ลูกค้ารหัส {code} เสร็จแล้ว" — ดูย้อนหลังใน 📊/📝
"""
ACTION_NAME = "Write Log"


def run(ctx, row):
    msg = str(row.get("additional") or "").strip() or "(ว่าง)"
    if callable(ctx.get("log")):
        ctx["log"](msg)
    ui = ctx.get("ui") or {}
    show = ui.get("msg") if isinstance(ui, dict) else None
    if callable(show):
        show("📝 " + msg)

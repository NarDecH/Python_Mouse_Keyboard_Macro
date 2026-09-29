# -*- coding: utf-8 -*-
"""Custom Action plugin: "Webhook" — ยิง POST ไป URL ที่ระบุ (v2.2)

ตั้งค่าในตาราง: Additional = URL (บังคับ) — ส่ง JSON {"event": "...", "row": {...}}
ตัวอย่าง: https://hooks.mycompany.com/notify/abc123

- ใช้ urllib.request จาก stdlib — ไม่ต้องติดตั้งอะไรเพิ่ม
- timeout 5 วินาที — ล้มเหลวรายงานผ่าน ctx["ui"]["msg"] แล้วเล่นแถวถัดไปต่อ
- ⚠️ URL มีข้อมูลส่วนตัวอยู่ในสคริปต์ — แชร์สคริปต์แล้วตรวจก่อนเสมอ
"""

import json

ACTION_NAME = "Webhook"


def run(ctx, row):
    import urllib.request
    import urllib.error

    url = str(row.get("additional") or "").strip()
    if not url.lower().startswith(("http://", "https://")):
        ui = ctx.get("ui") or {}
        msg = ui.get("msg") if isinstance(ui, dict) else None
        if callable(msg):
            msg("Webhook: Additional ต้องเป็น URL http(s)://…", "#c00")
        return
    payload = json.dumps({
        "event": "auto_mouse_macro",
        "action": str(row.get("button") or ""),
        "x": row.get("x", ""), "y": row.get("y", ""),
        "additional": row.get("additional", ""),
    }).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload, method="POST",
        headers={"Content-Type": "application/json",
                 "User-Agent": "AutoMouseMacro-Plugin/2.2"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            status = getattr(resp, "status", 0)
    except Exception as exc:
        ui = ctx.get("ui") or {}
        msg = ui.get("msg") if isinstance(ui, dict) else None
        if callable(msg):
            msg("Webhook: ส่งไม่สำเร็จ — %s" % exc, "#a60")
        return
    if callable(ctx.get("log")):
        ctx["log"]("webhook: POST %s → HTTP %s" % (url, status))

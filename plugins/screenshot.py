# -*- coding: utf-8 -*-
"""Custom Action plugin: "Screenshot" — ถ่ายภาพหน้าจอเก็บเป็นไฟล์ (v2.5)
ตั้งค่าในตาราง: Additional = ชื่อไฟล์ (ว่าง = screenshot_วันที่_เวลา.png ในโฟลเดอร์ปัจจุบัน)
- ใช้ PIL.ImageGrab จาก stdlib Pillow (มาพร้อม opencv-python ที่แนะนำอยู่แล้ว)
- เหมาะกับงานเฝ้าระบบ: ถ่ายหลักฐานตอนเงื่อนไขผิดปกติ คู่กับ If Image/Watchdog
"""
import time
ACTION_NAME = "Screenshot"


def run(ctx, row):
    raw = str(row.get("additional") or "").strip()
    try:
        from PIL import ImageGrab
    except Exception as exc:
        if callable(ctx.get("log")):
            ctx["log"]("screenshot: ต้องติดตั้ง Pillow (%s)" % exc)
        return
    if not raw:
        raw = time.strftime("screenshot_%Y%m%d_%H%M%S.png", time.localtime())
    if not raw.lower().endswith((".png", ".jpg", ".jpeg")):
        raw += ".png"
    try:
        img = ImageGrab.grab(all_screens=True)
        img.save(raw)
        if callable(ctx.get("log")):
            ctx["log"]("screenshot: บันทึก %s (%dx%d)" % (raw, img.size[0], img.size[1]))
        ui = ctx.get("ui") or {}
        msg = ui.get("msg") if isinstance(ui, dict) else None
        if callable(msg):
            msg("Screenshot: %s" % raw)
    except Exception as exc:
        if callable(ctx.get("log")):
            ctx["log"]("screenshot: ถ่ายไม่สำเร็จ (%s)" % exc)


# -*- coding: utf-8 -*-
"""Custom Action plugin: "Multi Image Click" — คลิกภาพหลายไฟล์ตามลำดับ (v2.2)

ตั้งค่าในตาราง: Additional = รายชื่อไฟล์ภาพคั่นด้วย |  (รองรับ @กรอบ#threshold เหมือน Image Click)
ตัวอย่าง: btn_ok.png|btn_next.png@10,20,300,150#90

- ไล่ค้นและคลิกทีละไฟล์ — ไฟล์ไหนไม่เจอข้ามไปไฟล์ถัดไป (รายงานเหตุผล)
- ใช้กลไกค้นภาพจาก macro_engine (cv2) — ถ้าไม่มี opencv รายงานแล้วจบ
"""

import os
import time

ACTION_NAME = "Multi Image Click"


def run(ctx, row):
    try:
        import macro_engine as me
    except ImportError:
        return
    raw = str(row.get("additional") or "").strip()
    if not raw:
        return
    ui = ctx.get("ui") or {}
    msg = ui.get("msg") if isinstance(ui, dict) else None

    def say(text, color="#080"):
        if callable(msg):
            msg(text, color)

    if not getattr(me, "HAS_CV", False):
        say("Multi Image Click ต้องติดตั้ง: pip install opencv-python Pillow", "#c00")
        return
    clicked = 0
    for part in raw.split("|"):
        part = part.strip()
        if not part:
            continue
        path, area, thr = me.parse_search_area(part)
        pos = me.find_image_pos(path, area, thr)
        if not pos:
            say("Multi Image: ข้าม %s — %s" % (os.path.basename(part),
                                               me.find_image_pos.last_error or "ไม่เจอ"), "#a60")
            continue
        stop = ctx.get("stop_check")
        if callable(stop) and not stop():
            return
        ctx["mouse"].position = pos
        time.sleep(0.03)
        ctx["mouse"].click()
        clicked += 1
    if callable(ctx.get("log")):
        ctx["log"]("multi_image_click: คลิกสำเร็จ %d/%d ภาพ" %
                   (clicked, len([p for p in raw.split("|") if p.strip()])))

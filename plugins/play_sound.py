# -*- coding: utf-8 -*-
"""Custom Action plugin: "Play Sound" — บี๊บ/เสียงเตือนตามจำนวนครั้ง (v2.2)

ตั้งค่าในตาราง: Additional = จำนวนครั้ง (ค่าเริ่มต้น 1)

- Windows: ใช้ winsound.Beep ความถี่ 1000 Hz ดัง 200 ms ต่อครั้ง (เสียงจริง ไม่ใช่ bell)
- OS อื่น: fallback เป็น ctx["ui"]["beep"] (bell ของระบบ)
"""

ACTION_NAME = "Play Sound"


def run(ctx, row):
    try:
        times = int(float(str(row.get("additional") or "1").strip() or "1"))
    except ValueError:
        times = 1
    times = max(1, min(10, times))
    try:
        import winsound
        for _ in range(times):
            winsound.Beep(1000, 200)
    except Exception:
        ui = ctx.get("ui") or {}
        beep = ui.get("beep") if isinstance(ui, dict) else None
        for _ in range(times):
            if callable(beep):
                beep()
    if callable(ctx.get("log")):
        ctx["log"]("play_sound: บี๊บ %d ครั้ง" % times)

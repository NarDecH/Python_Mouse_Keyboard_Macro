# -*- coding: utf-8 -*-
# แม่แบบ plugin (ไฟล์ขึ้นต้น _ → โปรแกรมไม่โหลด) — ก๊อปเป็นชื่ออื่นแล้วแก้ได้เลย
# ดูตัวอย่างจริงที่ sleep_seconds.py, message_box.py และ file_exists.py (เงื่อนไข)

import time

ACTION_NAME = "My Action"          # ชื่อที่โชว์ในคอลัมน์ Action (ห้ามซ้ำ)


def run(ctx, row):
    """ctx: mouse, kb, log(ข้อความ), cfg={"lang": "th"/"en"},
          stop_check() (v1.20 — False เมื่อผู้ใช้กด STOP), ui={"msg", "beep"} (v1.20),
          vars (v2.5 — dict ตัวแปรของสคริปต์ แถวถัดไปใช้ {ชื่อ} ต่อได้)
    row: dict ของแถว (x, y, additional, mins, secs, repeat, ...)
    กฎสำคัญ: input พัง/ขาดต้องทนได้เอง — ห้ามให้โปรแกรม crash ตอนเล่น"""
    msg = str(row.get("additional") or "")
    if callable(ctx.get("log")):
        ctx["log"]("my action: %r" % msg)
    # ... ทำงานของคุณที่นี่ เช่น ctx["mouse"].position, ctx["kb"].tap(...)
    time.sleep(0.1)


# ---------------------------------------------------------------------------
# Plugin API v3 (v2.13): เงื่อนไข plugin — ประกาศ CONDITION_NAME + check(ctx, row) -> bool
# (ใช้แทนหรือคู่กับ ACTION_NAME ในไฟล์เดียวกันได้ — ชื่อต้องต่างกัน)
# ใช้เป็นเงื่อนไขในคอลัมน์ Action และใน Block Start/End (if <ชื่อ> [อาร์กิวเมนต์]) ได้
# กติกาเดียวกับเงื่อนไขทุกชนิด: จริง = เล่นต่อ · ไม่จริง = ข้าม N แถว (N = Repeat)
#
# CONDITION_NAME = "My Condition"       # ห้ามซ้ำกับ Action เดิม/plugin อื่น
#
# def check(ctx, row):
#     """คืน True/False — ห้าม raise · อย่าแตะเมาส์/คีย์ (dry-run เรียก check จริง)"""
#     try:
#         arg = str(row.get("additional") or "").strip()
#         return bool(arg) and arg.lower() == "on"     # ตรวจจริงของคุณที่นี่
#     except Exception:
#         return False
#
# ตัวอย่างจริง: plugins/file_exists.py (File Exists — เช็คว่าไฟล์มีอยู่จริง)
#               plugins/window_exists.py · process_running.py · internet_up.py (v2.14)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# แม่แบบเทสต์มาตรฐาน (v2.7) — ก๊อปไป test_auto_macro.py แล้วแก้ชื่อ plugin ได้เลย
# เกณฑ์ครบ 4 อย่าง: เรียก run จริงด้วย ctx จำลอง / ทน Additional พัง / ทน ctx ขาด / เขียน vars ได้
# (ตัวอย่างเต็ม: TestPluginsComplete ใน test_auto_macro.py)
#
# class TestMyPlugin(unittest.TestCase):
#     """v2.7+PR: เทสต์ plugin My Action — มาตรฐานตาม docs/PLUGINS.md"""
#
#     def _ctx(self):
#         import queue
#         return {"mouse": mock.MagicMock(), "kb": mock.MagicMock(),
#                 "log": lambda text: None, "cfg": {"lang": "th"},
#                 "stop_check": lambda: True,
#                 "ui": {"msg": lambda text, color="#080": None,
#                        "beep": lambda: None},
#                 "vars": {}}
#
#     def test_runs_with_defaults(self):
#         import my_action
#         self.assertIsNone(my_action.run(self._ctx(), {}))   # เรียกจริง = ไม่ raise
#
#     def test_tolerates_bad_input(self):
#         import my_action
#         for bad in (None, "ไม่ใช่ตัวเลข", -1):
#             self.assertIsNone(my_action.run(self._ctx(), {"additional": bad}))
#
#     def test_tolerates_missing_ctx_keys(self):
#         import my_action
#         ctx = self._ctx()
#         ctx.pop("ui"); ctx.pop("vars")
#         self.assertIsNone(my_action.run(ctx, {"additional": "x"}))
#
#     def test_can_write_vars(self):
#         import my_action
#         ctx = self._ctx()
#         my_action.run(ctx, {"additional": "ค่า 42"})
#         self.assertEqual(ctx["vars"].get("ค่า"), "42")       # แถวถัดไปใช้ {ค่า} ได้
#
# เงื่อนไข plugin (v2.13) — เทสต์พื้นฐานเดียวกันแต่เรียก check:
#     def test_check_true_false(self):
#         import my_condition
#         self.assertTrue(my_condition.check(self._ctx(), {"additional": "on"}))
#         self.assertFalse(my_condition.check(self._ctx(), {"additional": "off"}))

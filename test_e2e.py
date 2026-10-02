# -*- coding: utf-8 -*-
"""
E2E tests: รัน auto_macro.py จริงเป็นโปรเซสย่อย (CLI) แล้วทดสอบการหยุด
- สคริปต์ที่ใช้มีแต่ Beep เท่านั้น — ปลอดภัย ไม่ขยับเมาส์/ไม่กดคีย์จริงบนเครื่อง
- ทดสอบ 2 สถานการณ์: หยุดผ่าน --stop-file กลางดีเลย์ยาว และ เล่นจบเองปกติ

รันด้วย:  py -m unittest test_e2e -v
"""

import json
import os
import queue
import subprocess
import sys
import tempfile
import threading
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import auto_macro as am  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(HERE, "auto_macro.py")


class _Child:
    """รัน CLI เป็นโปรเซสย่อย อ่าน stdout แบบมี deadline (ไม่ให้เทสต์ค้าง)"""

    def __init__(self, args):
        self.p = subprocess.Popen(
            [sys.executable, "-u", APP] + args,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace", bufsize=1)
        self.q = queue.Queue()
        self.lines = []
        threading.Thread(target=self._reader, daemon=True).start()

    def _reader(self):
        try:
            for line in self.p.stdout:
                self.q.put(line.rstrip("\n"))
        finally:
            self.q.put(None)

    def collect(self, deadline_s, on_line=None):
        """อ่านบรรทัดจนโปรเซสจบ หรือหมดเวลา (คืนเวลาที่ใช้)"""
        t0 = time.time()
        while time.time() - t0 < deadline_s:
            try:
                line = self.q.get(timeout=0.5)
            except queue.Empty:
                if self.p.poll() is not None:
                    break
                continue
            if line is None:
                break
            self.lines.append(line)
            if on_line is not None and on_line(line):
                break
            if self.p.poll() is not None and self.q.empty():
                break
        else:
            self.p.kill()
        return time.time() - t0

    def wait(self, timeout=20):
        return self.p.wait(timeout=timeout)

    def close(self):
        try:
            self.p.kill()
        except OSError:
            pass


class TestE2EStop(unittest.TestCase):
    """สถานการณ์จริง: เล่นสคริปต์ที่มีดีเลย์ยาว แล้วสั่งหยุดกลางทาง"""

    def _script(self, rows):
        d = tempfile.mkdtemp(prefix="macro_e2e_")
        p = os.path.join(d, "s.json")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, ensure_ascii=False)
        return p

    @unittest.skipUnless(os.name == "nt",
                         "ตรวจคีย์ค้างด้วย GetAsyncKeyState = Windows เท่านั้น")
    def test_watchdog_press_key_stop_file_no_stuck(self):
        """v2.2.1: watchdog + Press Key ค้าง + ดีเลย์ยาว → หยุดด้วย stop-file กลางทาง →
        ต้องจบ exit 130 และ**ไม่มีคีย์ค้าง** (ตรวจ GetAsyncKeyState ของ Ctrl ทั้งซ้ายขวา
        ในโปรเซสนี้หลัง child จบ) — คีย์/ปุ่มค้าง = บั๊กร้ายแรงของโปรแกรมควบคุมคีย์บอร์ด"""
        import ctypes
        script = self._script([
            {"enabled": True, "button": "Press Key", "additional": "ctrl", "mins": 0,
             "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Beep", "mins": 1, "secs": 0, "repeat": 1},  # ค้างระหว่างนี้
            {"enabled": True, "button": "Release Key", "additional": "ctrl", "mins": 0,
             "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Beep", "mins": 0, "secs": 0, "repeat": 1},
        ])
        stopf = os.path.join(tempfile.mkdtemp(prefix="macro_e2e_stk_"), "stop.flg")
        ch = _Child([script, "--watchdog", "1", "--stop-file", stopf, "--no-log"])
        try:
            triggered = []

            def on_line(line):
                if "รอบที่ 1" in line and not triggered:
                    with open(stopf, "w", encoding="utf-8") as fh:
                        fh.write("stop")
                    triggered.append(True)
                return False

            el = ch.collect(deadline_s=30, on_line=on_line)
            rc = ch.wait(timeout=15)
            out = "\n".join(ch.lines)
            self.assertTrue(triggered, "ต้อง trigger stop-file กลางดีเลย์ (ตอน ctrl ยังกดค้าง)")
            self.assertEqual(rc, 130)
            self.assertLess(el, 15, "ต้องหยุดทันทีกลางดีเลย์ — ใช้จริง %.1f วิ" % el)
            self.assertIn("ถูกหยุดโดยผู้ใช้", out)
            self.assertNotIn("จบแล้ว ✔", out)          # (หัวโปรแกรมพิมพ์ "จบแล้วเริ่มใหม่..." — ไม่นับ)
            time.sleep(0.2)                            # ให้ OS หายจาก event ค้าง
            VK_LCONTROL, VK_RCONTROL = 0xA2, 0xA3
            GetAsyncKeyState = ctypes.windll.user32.GetAsyncKeyState
            for vk, name in ((VK_LCONTROL, "Ctrl ซ้าย"), (VK_RCONTROL, "Ctrl ขวา")):
                state = GetAsyncKeyState(vk)
                self.assertFalse(state & 0x8000,
                                 "หยุดแล้ว %s ยังติดค้าง! (release_all ไม่ครบ)" % name)
        finally:
            ch.close()
            # เผื่อเคสเทสต์ล้มเหลว — ปล่อย ctrl ทิ้งกันค้างรบกวนเทสต์ต่อไป
            try:
                from pynput.keyboard import Controller as _C, Key as _K
                _c = _C()
                _c.release(_K.ctrl)
            except Exception:
                pass

    def test_stop_file_mid_long_delay(self):
        # Beep → ดีเลย์ 60 วิ → Beep: สร้าง stop-file หลังเห็น "รอบที่ 1" = กลางดีเลย์พอดี
        script = self._script([
            {"enabled": True, "button": "Beep", "mins": 0, "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Beep", "mins": 1, "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Beep", "mins": 0, "secs": 0, "repeat": 1},
        ])
        stopf = os.path.join(tempfile.mkdtemp(prefix="macro_e2e_stop_"), "stop.flg")
        ch = _Child([script, "--stop-file", stopf])
        try:
            triggered = []

            def on_line(line):
                if "รอบที่ 1" in line and not triggered:
                    with open(stopf, "w", encoding="utf-8") as fh:
                        fh.write("stop")
                    triggered.append(True)
                return False

            el = ch.collect(deadline_s=30, on_line=on_line)
            rc = ch.wait(timeout=15)
            out = "\n".join(ch.lines)
            self.assertTrue(triggered, "ต้อง trigger stop-file กลางดีเลย์")
            self.assertEqual(rc, 130, "exit code เมื่อถูกหยุดต้องเป็น 130")
            self.assertLess(el, 15, "ต้องหยุดภายในไม่กี่วินาที (ไม่รอดีเลย์ 60 วิ) — ใช้จริง %.1f วิ" % el)
            self.assertIn("ถูกหยุดโดยผู้ใช้", out)
            self.assertNotIn("จบแล้ว", out)
        finally:
            ch.close()

    def test_finishes_normally(self):
        # สคริปต์สั้น ๆ ต้องจบเอง แจ้ง "จบแล้ว" และ exit 0
        script = self._script([
            {"enabled": True, "button": "Beep", "mins": 0, "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Beep", "mins": 0, "secs": 0, "repeat": 1},
        ])
        ch = _Child([script, "--no-log"])
        try:
            el = ch.collect(deadline_s=30)
            rc = ch.wait(timeout=15)
            out = "\n".join(ch.lines)
            self.assertEqual(rc, 0)
            self.assertLess(el, 15)
            self.assertIn("จบแล้ว", out)
        finally:
            ch.close()

    def test_plugin_action_runs(self):
        """Custom Action plugin (v1.16): เล่นแถว plugin จริงผ่าน CLI
        (Sleep (plugin) 0.2s — ปลอดภัย ไม่แตะเมาส์/คีย์)"""
        script = self._script([
            {"enabled": True, "button": "Sleep (plugin)", "additional": "0.2",
             "mins": 0, "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Beep", "mins": 0, "secs": 0, "repeat": 1},
        ])
        ch = _Child([script, "--no-log"])
        try:
            el = ch.collect(deadline_s=30)
            rc = ch.wait(timeout=15)
            out = "\n".join(ch.lines)
            self.assertEqual(rc, 0)
            self.assertIn("plugins:", out)
            self.assertIn("Sleep (plugin)", out)      # ในรายชื่อ + บรรทัดเล่นจริง
            self.assertIn("จบแล้ว", out)
            self.assertLess(el, 15)
        finally:
            ch.close()

    def test_watchdog_restarts_then_stop_file(self):
        # --watchdog 1: จบแล้วเริ่มใหม่อัตโนมัติ — พอเห็นข้อความ watchdog ให้สร้าง
        # stop-file ระหว่างช่วงพัก = ต้องหยุดถาวร (exit 130) ไม่เริ่มรอบใหม่
        script = self._script([
            {"enabled": True, "button": "Beep", "mins": 0, "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Beep", "mins": 0, "secs": 0, "repeat": 1},
        ])
        stopf = os.path.join(tempfile.mkdtemp(prefix="macro_e2e_wd_"), "stop.flg")
        ch = _Child([script, "--watchdog", "1", "--stop-file", stopf, "--no-log"])
        try:
            saw = []

            def on_line(line):
                if "watchdog" in line and not saw:
                    with open(stopf, "w", encoding="utf-8") as fh:
                        fh.write("stop")
                    saw.append(True)
                return False

            el = ch.collect(deadline_s=30, on_line=on_line)
            rc = ch.wait(timeout=15)
            self.assertTrue(saw, "ต้องเห็นข้อความ watchdog (จบแล้วเริ่มใหม่)")
            self.assertEqual(rc, 130, "stop-file ระหว่างพักต้องหยุดถาวร")
            self.assertLess(el, 20)
        finally:
            ch.close()

    def test_shuffle_rows_pct_finishes(self):
        # --shuffle --rows-pct 50 กับ 4 แถว = เล่นรอบละ 2 แถว (สุ่มชุดใหม่ทุกรอบ) แล้วจบเอง
        script = self._script([
            {"enabled": True, "button": "Beep", "mins": 0, "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Beep", "mins": 0, "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Beep", "mins": 0, "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Beep", "mins": 0, "secs": 0, "repeat": 1},
        ])
        ch = _Child([script, "--shuffle", "--rows-pct", "50", "--no-log"])
        try:
            el = ch.collect(deadline_s=30)
            rc = ch.wait(timeout=15)
            out = "\n".join(ch.lines)
            self.assertEqual(rc, 0)
            self.assertIn("[2/2]", out)              # เล่น 2 จาก 4 แถวตามสัดส่วน 50%
            self.assertIn("จบแล้ว", out)
        finally:
            ch.close()

    def test_stop_before_any_row(self):
        # สร้าง stop-file ก่อนเริ่มเลย = หยุดทันทีโดยไม่เล่นแถวใด
        script = self._script([
            {"enabled": True, "button": "Beep", "mins": 0, "secs": 0, "repeat": 1},
        ])
        stopf = os.path.join(tempfile.mkdtemp(prefix="macro_e2e_pre_"), "stop.flg")
        with open(stopf, "w", encoding="utf-8") as fh:
            fh.write("stop")
        ch = _Child([script, "--stop-file", stopf])
        try:
            el = ch.collect(deadline_s=20)
            rc = ch.wait(timeout=15)
            self.assertEqual(rc, 130)
            self.assertLess(el, 10)
            # ห้ามเล่นแถวใดเลย (หัวข้อ "รอบที่" พิมพ์ก่อนเช็ค stop-file ได้ แต่ห้ามลงมือทำแถว)
            self.assertNotIn("[1/1]", "\n".join(ch.lines))
            self.assertIn("ถูกหยุดโดยผู้ใช้", "\n".join(ch.lines))
        finally:
            ch.close()


class TestE2EUtility(unittest.TestCase):
    """ทดสอบสาธารณูปโภคผ่านโมดูลจริง (ไม่เปิด GUI): export/import ครบวงจร + self-test เมาส์"""

    def test_export_import_roundtrip_real(self):
        """export → แก้ข้อมูล → import: ข้อมูลต้องกลับมาตรงเดิม (ใช้โค้ดจริงทั้งสาย)"""
        import io
        import tempfile
        from unittest import mock
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "settings.json")
            app = mock.MagicMock()
            app._serialize.return_value = [
                {"enabled": True, "button": "Beep", "mins": 0, "secs": 1, "repeat": 2}]
            app._profiles = {"งานเดิม": [{"button": "Beep"}], "งานใหม่": []}
            app._active_profile = "งานเดิม"
            app._log_enabled = True
            app._hp_dir = None
            app._ui_state = {"msg": None}
            # 1) export
            with mock.patch.object(am.filedialog, "asksaveasfilename", return_value=f):
                am.MacroApp.export_settings(app)
            self.assertTrue(os.path.isfile(f))
            # 2) เหมือนย้ายเครื่อง: เปลี่ยนข้อมูลปัจจุบันให้ต่างจากเดิมทั้งหมด
            app2 = mock.MagicMock()
            app2._serialize.return_value = []
            app2._profiles = {"ค่าเริ่มต้น": []}
            app2._active_profile = "ค่าเริ่มต้น"
            app2._log_enabled = False
            app2._hp_dir = None
            app2._ui_state = {"msg": None}
            app2._load_rows = mock.MagicMock()
            app2._refresh_profile_ui = mock.MagicMock()
            app2._save_profiles = mock.MagicMock()
            app2._save_conf = mock.MagicMock()
            # 3) import (ยอมรับ)
            with mock.patch.object(am.filedialog, "askopenfilename", return_value=f), \
                 mock.patch.object(am.messagebox, "askyesno", return_value=True):
                am.MacroApp.import_settings(app2)
            self.assertEqual(app2._active_profile, "งานเดิม")
            self.assertTrue(app2._log_enabled)
            app2._load_rows.assert_called_once_with(
                [{"enabled": True, "button": "Beep", "mins": 0, "secs": 1, "repeat": 2}])
            app2._save_profiles.assert_called_once()
            app2._save_conf.assert_called_once()

    @unittest.skipUnless(os.name == "nt",
                         "ต้องควบคุมเมาส์จริง (อ่าน/ย้ายตำแหน่ง) — macOS runner "
                         "ไม่มีสิทธิ์ accessibility จึงตั้งตำแหน่งเมาส์ไม่ได้")
    def test_self_test_real_mouse(self):
        """ปุ่ม 🧪 ทดสอบระบบจริง: เรียก _self_test_actions() โค้ดจริง —
        เมาส์ขยับแล้วคืนจุดเดิมพอดี + บี๊บ 2 ครั้ง (ไม่คลิก ไม่กดคีย์)"""
        from unittest import mock
        app = mock.MagicMock()
        app.mouse_ctl = am.MouseController()             # ควบคุมเมาส์จริง
        bells = []
        app.root.bell = lambda: bells.append(1)
        app.root.after = lambda delay, fn: fn()          # รันทันที (ไม่มี mainloop)
        cur = am.MacroApp._self_test_actions(app)        # โค้ดจริงจากโปรแกรม
        self.assertEqual(app.mouse_ctl.position, cur)    # คืนจุดเดิมพอดี
        self.assertEqual(len(bells), 2)                  # บี๊บ 2 ครั้ง


class TestE2ECliWarnings(unittest.TestCase):
    """v1.19: CLI ต้องเตือนชัด ๆ เมื่อเจอ action ที่ยังไม่รองรับ (ไม่ข้ามเงียบ ๆ)"""

    def _script(self, rows):
        d = tempfile.mkdtemp(prefix="macro_e2e_warn_")
        p = os.path.join(d, "s.json")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, ensure_ascii=False)
        return p

    def test_image_click_reports_missing_file(self):
        # v2.2: CLI ค้นภาพได้จริงแล้ว (find_image_cb ผูกเข้า runner เดียวกับ GUI) —
        # ไฟล์ภาพหายต้องรายงานเหตุผลชัด ๆ แล้วเล่นแถวถัดไปจนจบ ไม่พัง
        script = self._script([
            {"enabled": True, "button": "Image Click", "additional": "no_such_target.png",
             "mins": 0, "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Beep", "mins": 0, "secs": 0, "repeat": 1},
        ])
        ch = _Child([script, "--no-log"])
        try:
            ch.collect(deadline_s=30)
            rc = ch.wait(timeout=15)
            out = "\n".join(ch.lines)
            self.assertEqual(rc, 0)
            self.assertIn("Image Click", out)
            # เครื่องมี opencv = "ไม่พบไฟล์ภาพ" · ไม่มี = "ค้นภาพต้องติดตั้ง" (CI)
            self.assertTrue(("ไม่พบไฟล์ภาพ" in out) or ("ต้องติดตั้ง" in out))
            self.assertIn("จบแล้ว", out)
        finally:
            ch.close()

    def test_set_variable_runs_in_cli(self):
        # ตัวแปรในสคริปต์ทำงานใน CLI ด้วย — ตั้ง/บวก/อ้างอิง {n} ใน secs
        script = self._script([
            {"enabled": True, "button": "Set Variable", "additional": "n = 1",
             "mins": 0, "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Set Variable", "additional": "n += 4",
             "mins": 0, "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Beep", "mins": 0, "secs": "{n}", "repeat": 1},
        ])
        ch = _Child([script, "--no-log"])
        try:
            ch.collect(deadline_s=30)
            rc = ch.wait(timeout=15)
            out = "\n".join(ch.lines)
            self.assertEqual(rc, 0)
            self.assertIn("จบแล้ว", out)      # secs {n} = 5 วิ แต่ Beep ทำงานและจบครบ
            self.assertIn("Beep", out)
        finally:
            ch.close()


    def test_clipboard_actions_in_cli(self):
        # v1.20: Set/Read Clipboard ทำงานใน CLI ด้วย (Windows: Win32 API) —
        # ลูกตั้งคลิปบอร์ด แล้วพ่อแม่ (process นี้) อ่านยืนยันข้อความจริง
        # ⚠️ แตะคลิปบอร์ดจริงของคนรันเทสต์ — snapshot แล้วคืนค่าเมื่อจบเสมอ
        saved = am.clip_get()
        script = self._script([
            {"enabled": True, "button": "Set Clipboard", "additional": "จาก CLI ไทย 123",
             "mins": 0, "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Read Clipboard", "additional": "t",
             "mins": 0, "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Beep", "mins": 0, "secs": 0, "repeat": 1},
        ])
        ch = _Child([script, "--no-log"])
        try:
            ch.collect(deadline_s=30)
            rc = ch.wait(timeout=15)
            self.assertEqual(rc, 0)
            if os.name == "nt":
                self.assertEqual(am.clip_get(), "จาก CLI ไทย 123")
        finally:
            ch.close()
            if saved is not None:
                am.clip_set(saved)


class TestE2EBlocks(unittest.TestCase):
    """v2.6 (ชุด N2): Block Start/End + ลูปย่อยเล่นจริงผ่าน CLI
    (สคริปต์ Beep/Set Variable ล้วน — ปลอดภัยไม่แตะเมาส์/คีย์)"""

    def _script(self, rows):
        d = tempfile.mkdtemp(prefix="macro_e2e_block_")
        p = os.path.join(d, "s.json")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, ensure_ascii=False)
        return p

    def test_block_if_false_skips_block(self):
        # เงื่อนไขไม่จริง → เนื้อในถูกข้ามทั้งบล็อก เห็นเฉพาะ Beep นอกบล็อก
        script = self._script([
            {"enabled": True, "button": "Set Variable", "additional": "m = off",
             "mins": 0, "secs": 0, "repeat": 1},
            {"enabled": True, "button": "🔷 Block Start", "additional": "if m = on",
             "mins": 0, "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Beep", "additional": "ในบล็อก",
             "mins": 0, "secs": 0, "repeat": 1},
            {"enabled": True, "button": "🔷 Block End", "additional": "",
             "mins": 0, "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Beep", "additional": "นอกบล็อก",
             "mins": 0, "secs": 0, "repeat": 1},
        ])
        ch = _Child([script, "--no-log"])
        try:
            ch.collect(deadline_s=30)
            rc = ch.wait(timeout=15)
            out = "\n".join(ch.lines)
            self.assertEqual(rc, 0)
            self.assertNotIn("ในบล็อก", out)
            self.assertIn("นอกบล็อก", out)
        finally:
            ch.close()

    def test_block_until_loop_counts(self):
        # ลูปย่อย: วน 5 รอบจน n > 5 แล้วเล่นต่อ — ต้องเห็น Beep ครบ 5 ครั้ง
        script = self._script([
            {"enabled": True, "button": "Set Variable", "additional": "n = 1",
             "mins": 0, "secs": 0, "repeat": 1},
            {"enabled": True, "button": "🔷 Block Start", "additional": "until n > 5 max 20",
             "mins": 0, "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Beep", "additional": "รอบ {n}",
             "mins": 0, "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Set Variable", "additional": "n += 1",
             "mins": 0, "secs": 0, "repeat": 1},
            {"enabled": True, "button": "🔷 Block End", "additional": "",
             "mins": 0, "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Beep", "additional": "จบลูปแล้ว",
             "mins": 0, "secs": 0, "repeat": 1},
        ])
        ch = _Child([script, "--no-log"])
        try:
            ch.collect(deadline_s=30)
            rc = ch.wait(timeout=15)
            out = "\n".join(ch.lines)
            self.assertEqual(rc, 0)
            for k in range(1, 6):
                self.assertIn("รอบ %d" % k, out)
            self.assertNotIn("รอบ 6", out)
            self.assertIn("จบลูปแล้ว", out)
        finally:
            ch.close()

    def test_nested_blocks_validate_error(self):
        # บล็อกไม่ปิด → --validate ต้อง exit 1 พร้อมข้อความตำแหน่งแถวชัดเจน
        script = self._script([
            {"enabled": True, "button": "🔷 Block Start", "additional": "",
             "mins": 0, "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Beep", "mins": 0, "secs": 0, "repeat": 1},
        ])
        ch = _Child([script, "--validate", "--no-log"])
        try:
            ch.collect(deadline_s=30)
            rc = ch.wait(timeout=15)
            out = "\n".join(ch.lines)
            self.assertEqual(rc, 1)
            self.assertIn("ไม่มี Block End", out)
        finally:
            ch.close()


class TestE2EStartValidateSkip(unittest.TestCase):
    """v2.9.1: CLI ตรวจสคริปต์ตั้งแต่หัวโปรแกรม — แถวพังถูกข้ามพร้อมรายงาน + log [SKIP]
    (สคริปต์ Beep/Tap Key ล้วน — ปลอดภัยไม่แตะเมาส์/คีย์)"""

    def _script(self, rows):
        d = tempfile.mkdtemp(prefix="macro_e2e_skip_")
        p = os.path.join(d, "s.json")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, ensure_ascii=False)
        return p

    def test_invalid_rows_skipped_with_report(self):
        # แถวคีย์ว่าง 2 แถวถูกข้าม — เล่นเฉพาะ Beep 2 แถว + รายงานหัวโปรแกรม
        script = self._script([
            {"enabled": True, "button": "Tap Key", "additional": "",
             "mins": 0, "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Beep", "additional": "ok1",
             "mins": 0, "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Tap Key", "additional": "",
             "mins": 0, "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Beep", "additional": "ok2",
             "mins": 0, "secs": 0, "repeat": 1},
        ])
        ch = _Child([script, "--no-log"])
        try:
            ch.collect(deadline_s=30)
            rc = ch.wait(timeout=15)
            out = "\n".join(ch.lines)
            self.assertEqual(rc, 0)
            self.assertIn("แถวต่อไปนี้จะถูกข้าม", out)
            self.assertEqual(out.count("[1/2] Beep ok1"), 1)
            self.assertEqual(out.count("[2/2] Beep ok2"), 1)
            self.assertNotIn("[3/", out)          # แถวพังไม่ถูกเล่นและไม่นับเลข
        finally:
            ch.close()

    def test_skip_logged_to_log_file(self):
        # log เปิด (ไม่ใส่ --no-log) → ต้องมี [SKIP] แถว 1 พร้อมเหตุผล + START ระบุ ข้าม=1
        # (log_path เขียนข้างไฟล์แอป — รัน in-process แล้ว patch log_path ลง tempdir กันเขียน log จริง)
        script = self._script([
            {"enabled": True, "button": "Tap Key", "additional": "",
             "mins": 0, "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Beep", "additional": "ok",
             "mins": 0, "secs": 0, "repeat": 1},
        ])
        d = os.path.dirname(script)
        boot = (
            "import sys; sys.path.insert(0, r'%s'); import auto_macro; "
            "auto_macro.log_path = lambda: sys.argv[1] + r'\\macro_log_test.txt'; "
            "sys.exit(auto_macro.cli_main(sys.argv[2:]))" % HERE.replace("\\", "\\\\")
        )
        p = subprocess.Popen(
            [sys.executable, "-X", "utf8", "-c", boot, d, script],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace")
        try:
            out, _ = p.communicate(timeout=60)
            rc = p.returncode
            self.assertEqual(rc, 0, out)
            with open(os.path.join(d, "macro_log_test.txt"), encoding="utf-8") as fh:
                content = fh.read()
            self.assertIn("[SKIP]", content)
            self.assertIn("แถว 1 ถูกข้าม", content)
            self.assertIn("ข้าม=1", content)
        finally:
            if p.poll() is None:
                p.kill()

    def test_all_invalid_exits_1_without_playing(self):
        # ทุกแถวพัง → รายงาน + จบด้วย exit code 1 ไม่เล่นสักแถว
        script = self._script([
            {"enabled": True, "button": "Tap Key", "additional": "",
             "mins": 0, "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Image Click", "additional": "no_such_file.png",
             "mins": 0, "secs": 0, "repeat": 1},
        ])
        ch = _Child([script, "--no-log"])
        try:
            ch.collect(deadline_s=30)
            rc = ch.wait(timeout=15)
            out = "\n".join(ch.lines)
            self.assertEqual(rc, 1)
            self.assertIn("ทุกแถวตรวจไม่ผ่าน", out)
            self.assertNotIn("— รอบที่", out)     # ไม่มีการเล่นเกิดขึ้นเลย
        finally:
            ch.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)

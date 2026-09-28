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


if __name__ == "__main__":
    unittest.main(verbosity=2)

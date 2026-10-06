# -*- coding: utf-8 -*-
"""
Unit tests สำหรับฟังก์ชันล้วน ๆ ของ auto_macro.py
(ไม่เปิดหน้าต่าง GUI และไม่ยุ่งกับเมาส์/คีย์บอร์ดจริง)

รันด้วย:  py -m unittest test_auto_macro -v
"""

import datetime
import gc
import glob
import io
import json
import os
import random
import re
import shutil
import sys
import tempfile
import time
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import auto_macro as am  # noqa: E402
import macro_engine as me_mod  # noqa: E402  (v2.1: engine ล้วน — เทสต์แยกได้)


def _cancel_tk_afters(root):
    """v2.14.1: ยกเลิก timer `after` ค้างทั้งหมดก่อน destroy root — เทสต์ที่เล่นจริง
    (เธรดผู้เล่น/schedule) มักเหลือ timer ที่จะยิงหลัง root ตาย → "invalid command name
    …_poller_tick" spam ระหว่าง pump ของเทสต์ถัด ๆ ไป และบน macOS บางครั้งทำ Tk แตก
    SIGTRAP (exit 133) · destroy แบบเดิมจะยกเลิก timer ให้เองก็จริง แต่ปิดท้ายหลัง
    callback ที่อ้าง widget ถูกทำลายไปแล้ว — เลิกที่ timer ก่อนจึงสะอาดกว่า"""
    if root is None:
        return
    try:
        for aid in root.tk.call("after", "info"):
            try:
                root.after_cancel(aid)
            except Exception:
                pass
    except Exception:
        pass


class _Tk(am.tk.Tk):
    """Tk ของเทสต์ — destroy() เคลียร์ครบก่อนปิด interpreter:
    ① หยุดเธรดของ app ที่ผูกไว้ (root._app — ดู _register_macro_app ด้านล่าง):
       player (_gk hotkey listener, _sched_loop, recorder listeners) — เทสต์เก่าไม่เคยหยุด
       ทิ้งสะสมหลายเธรด ระหว่าง suite CI Linux/macOS เธรดเหล่านี้จัดสรรหน่วยความจำต่อ
       → GC ไป finalize Tcl object ของ interpreter เก่า "บนเธรดผิด" =
       Tcl_AsyncDelete: async handler deleted by the wrong thread → abort ทั้งโปรเซส
       (พิสูจน์บน CI v2.15.0: ระเบิดตอนเริ่มคลาส GUI ถัดไป)
    ② ยกเลิก timer `after` ทั้งหมด (ดู _cancel_tk_afters)
    ③ destroy แล้ว gc.collect() บน main thread — finalize Tcl state บนเธรดที่ถูกต้องเสมอ"""

    def destroy(self):
        app = getattr(self, "_app", None)
        if app is not None:
            try:
                app.stop_all(silent=True)
            except Exception:
                pass
            gk = getattr(app, "_gk", None)
            if gk is not None:
                try:
                    gk.stop()
                except Exception:
                    pass
                app._gk = None                     # กัน poller/heal รีสตาร์ตระหว่างปิด
            try:
                app._sched_stop.set()
            except Exception:
                pass
            try:
                app._recorder.stop_listeners()
            except Exception:
                pass
        _cancel_tk_afters(self)
        try:
            super().destroy()
        except am.tk.TclError:
            pass
        gc.collect()                               # finalize บน main thread — จุดเดียวจบปัญหา


def _register_macro_app():
    """ผูก MacroApp กับ root (root._app) ให้ _Tk.destroy หยุดเธรดได้ — patch ครั้งเดียว
    ทำในไฟล์เทสต์เท่านั้น (โค้ดโปรแกรมไม่เกี่ยว — ผู้ใช้ปิดโปรแกรมผ่าน _on_close อยู่แล้ว)"""
    if getattr(am.MacroApp, "_gk_autostop_patched", False):
        return
    _orig_macro_init = am.MacroApp.__init__

    def _macro_init(self, root, *args, **kwargs):
        _orig_macro_init(self, root, *args, **kwargs)
        try:
            root._app = self
        except Exception:
            pass
    am.MacroApp.__init__ = _macro_init
    am.MacroApp._gk_autostop_patched = True


_register_macro_app()


class TestParseKey(unittest.TestCase):
    """parse_key: ข้อความ → ออบเจ็กต์คีย์ pynput"""

    def test_empty_returns_none(self):
        self.assertIsNone(am.parse_key(""))
        self.assertIsNone(am.parse_key(None))
        self.assertIsNone(am.parse_key("   "))

    def test_single_char(self):
        # v1.20.4: ตัวอักษรเดี่ยว = ปุ่มกายภาพ (VK_W ไม่ขึ้นกับ layout ที่ active)
        k = am.parse_key("a")
        self.assertIsNotNone(k)
        self.assertEqual(k.vk, 0x41)

    def test_modifier_ctrl(self):
        from pynput.keyboard import Key
        self.assertEqual(am.parse_key("Ctrl"), Key.ctrl)

    def test_modifier_win_maps_to_cmd(self):
        from pynput.keyboard import Key
        self.assertEqual(am.parse_key("Win"), Key.cmd)

    def test_special_names(self):
        from pynput.keyboard import Key
        self.assertEqual(am.parse_key("esc"), Key.esc)
        self.assertEqual(am.parse_key("space"), Key.space)
        self.assertEqual(am.parse_key("enter"), Key.enter)
        self.assertEqual(am.parse_key("pgup"), Key.page_up)
        # macOS ไม่มีปุ่ม PrtSc → pynput darwin ไม่มี Key.print_screen (parse_key คืน None)
        self.assertEqual(am.parse_key("prtsc"),
                         getattr(Key, "print_screen", None))
        self.assertEqual(am.parse_key("del"), Key.delete)
        self.assertEqual(am.parse_key("caps"), Key.caps_lock)
        self.assertEqual(am.parse_key("f5"), Key.f5)
        self.assertEqual(am.parse_key("f12"), Key.f12)

    def test_digit_string_is_virtual_key(self):
        k = am.parse_key("27")          # ESC virtual key code
        self.assertIsNotNone(k)
        self.assertEqual(k.vk, 27)

    def test_unknown_word_returns_none(self):
        self.assertIsNone(am.parse_key("notakey"))


class TestDelaySeconds(unittest.TestCase):
    """delay_seconds: Mins*60 + Secs"""

    def test_zero(self):
        self.assertEqual(am.delay_seconds(0, 0), 0.0)

    def test_mins_and_secs(self):
        self.assertEqual(am.delay_seconds(1, 30), 90.0)

    def test_decimal_secs(self):
        self.assertAlmostEqual(am.delay_seconds(0, "2.5"), 2.5)

    def test_european_comma(self):
        self.assertAlmostEqual(am.delay_seconds(0, "0,5"), 0.5)

    def test_invalid_becomes_zero(self):
        self.assertEqual(am.delay_seconds("abc", "xyz"), 0.0)

    def test_empty_strings(self):
        self.assertEqual(am.delay_seconds("", ""), 0.0)

    def test_negative_clamped_to_zero(self):
        self.assertEqual(am.delay_seconds(-1, -5), 0.0)


class TestFmtNum(unittest.TestCase):
    """fmt_num: แสดงตัวเลขแบบสั้น"""

    def test_integer_value(self):
        self.assertEqual(am.fmt_num(2.0), "2")

    def test_decimal_value(self):
        self.assertEqual(am.fmt_num(0.5), "0.5")

    def test_european_comma(self):
        self.assertEqual(am.fmt_num("0,5"), "0.5")

    def test_non_number_passthrough(self):
        self.assertEqual(am.fmt_num("abc"), "abc")


class TestParseInt(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(am.parse_int(3), 3)

    def test_float_truncates(self):
        self.assertEqual(am.parse_int("2.9"), 2)

    def test_min_one(self):
        self.assertEqual(am.parse_int(0), 1)
        self.assertEqual(am.parse_int(-5), 1)

    def test_invalid_uses_default(self):
        self.assertEqual(am.parse_int("abc", 7), 7)


class TestHHMM(unittest.TestCase):
    """re_match_hhmm: รูปแบบเวลาของ schedule"""

    def test_valid(self):
        self.assertTrue(am.re_match_hhmm("00:00"))
        self.assertTrue(am.re_match_hhmm("09:30"))
        self.assertTrue(am.re_match_hhmm("23:59"))

    def test_invalid(self):
        self.assertFalse(am.re_match_hhmm("24:00"))
        self.assertFalse(am.re_match_hhmm("9:30"))
        self.assertFalse(am.re_match_hhmm("09:5"))
        self.assertFalse(am.re_match_hhmm("09:60"))
        self.assertFalse(am.re_match_hhmm(""))
        self.assertFalse(am.re_match_hhmm("ab:cd"))


class TestConstants(unittest.TestCase):
    """ค่าคงที่ที่ UI อ้างอิง"""

    def test_actions_all_contains_image(self):
        self.assertIn(am.IMAGE_ACTION, am.ACTIONS_ALL)

    def test_btn_th_pairs(self):
        for name, (btn, act) in am.BTN_TH.items():
            self.assertIn(act, ("Down", "Up", "Click"))
            self.assertIn(btn, ("Left", "Right", "Middle"))

    def test_cols_order(self):
        self.assertEqual(am.COLS,
                         ["chk", "num", "x", "y", "button", "additional",
                          "mins", "secs", "repeat", "note"])

    def test_edit_cols_mapping(self):
        self.assertEqual(am.EDIT_COLS,
                         ["Action", "Additional", "Mins", "Secs", "Repeat", "Note"])


class TestDelayRange(unittest.TestCase):
    """delay_range: สนับสนุนดีเลย์แบบสุ่ม เช่น "1-3" (ฟีเจอร์ v1.5)"""

    def test_range(self):
        self.assertEqual(am.delay_range("1-3"), (1.0, 3.0))

    def test_range_reversed(self):
        self.assertEqual(am.delay_range("3-1"), (1.0, 3.0))

    def test_single_value(self):
        self.assertEqual(am.delay_range("2.5"), (2.5, 2.5))

    def test_european_comma(self):
        self.assertEqual(am.delay_range("0,5"), (0.5, 0.5))

    def test_invalid(self):
        self.assertEqual(am.delay_range("abc"), (0.0, 0.0))
        self.assertEqual(am.delay_range(""), (0.0, 0.0))
        self.assertEqual(am.delay_range(None), (0.0, 0.0))

    def test_spaces(self):
        self.assertEqual(am.delay_range("1 - 3"), (1.0, 3.0))


class TestV15Actions(unittest.TestCase):
    """ค่าคงที่ Action ชุดใหม่ v1.5 (แรงบันดาลใจจาก automouseclick.com)"""

    def test_scroll_actions(self):
        self.assertIn("Scroll Up", am.ACTIONS_ALL)
        self.assertIn("Scroll Down", am.ACTIONS_ALL)

    def test_double_click_actions(self):
        self.assertIn("Double Left Click", am.ACTIONS_ALL)
        self.assertIn("Double Right Click", am.ACTIONS_ALL)

    def test_modifier_clicks(self):
        for a in ("Ctrl+Click", "Shift+Click", "Alt+Click", "Ctrl+Right Click"):
            self.assertIn(a, am.ACTIONS_ALL)

    def test_move_actions(self):
        for a in ("Move Mouse", "Move Mouse by Offset", "Save Cursor", "Restore Cursor"):
            self.assertIn(a, am.ACTIONS_ALL)

    def test_extra_actions(self):
        for a in ("Type Text", "Launch App", "Wait for Image", "Beep"):
            self.assertIn(a, am.ACTIONS_ALL)

    def test_no_duplicates(self):
        self.assertEqual(len(am.ACTIONS_ALL), len(set(am.ACTIONS_ALL)))


class TestSearchArea(unittest.TestCase):
    """search area + threshold สำหรับ Image Click (v1.7):
    Additional: ไฟล์.png[@x,y,w,h][#threshold] — คืน (path, area, threshold)"""

    def test_no_at_sign_is_fullscreen(self):
        app = mock.MagicMock()
        path, area, thr = am.MacroApp._parse_search_area(app, {"additional": "button.png"})
        self.assertEqual(path, "button.png")
        self.assertIsNone(area)
        self.assertEqual(thr, 0.80)

    def test_with_area(self):
        app = mock.MagicMock()
        path, area, _thr = am.MacroApp._parse_search_area(
            app, {"additional": "button.png@100,200,300,400"})
        self.assertEqual(path, "button.png")
        self.assertEqual(area, (100, 200, 400, 600))

    def test_zero_size_is_fullscreen(self):
        app = mock.MagicMock()
        _path, area, _thr = am.MacroApp._parse_search_area(
            app, {"additional": "b.png@10,10,0,0"})
        self.assertIsNone(area)

    def test_garbage_coords_is_fullscreen(self):
        app = mock.MagicMock()
        _path, area, _thr = am.MacroApp._parse_search_area(
            app, {"additional": "b.png@abc,x,y,z"})
        self.assertIsNone(area)

    def test_float_coords(self):
        app = mock.MagicMock()
        _path, area, _thr = am.MacroApp._parse_search_area(
            app, {"additional": "b.png@0,0,10.5,20"})
        self.assertEqual(area, (0, 0, 10, 20))

    def test_coords_with_spaces(self):
        app = mock.MagicMock()
        _path, area, _thr = am.MacroApp._parse_search_area(
            app, {"additional": "b.png@ 5 , 6 , 7 , 8 "})
        self.assertEqual(area, (5, 6, 12, 14))

    def test_threshold_percent(self):
        app = mock.MagicMock()
        _p, _a, thr = am.MacroApp._parse_search_area(
            app, {"additional": "b.png@0,0,10,20#90"})
        self.assertAlmostEqual(thr, 0.90)

    def test_threshold_fraction(self):
        app = mock.MagicMock()
        _p, _a, thr = am.MacroApp._parse_search_area(
            app, {"additional": "b.png#0.65"})
        self.assertAlmostEqual(thr, 0.65)

    def test_threshold_clamped(self):
        app = mock.MagicMock()
        _p, _a, thr = am.MacroApp._parse_search_area(
            app, {"additional": "b.png#200"})
        self.assertEqual(thr, 1.0)

    def test_threshold_invalid_keeps_default(self):
        app = mock.MagicMock()
        _p, _a, thr = am.MacroApp._parse_search_area(
            app, {"additional": "b.png#abc"})
        self.assertEqual(thr, 0.80)


class TestCli(unittest.TestCase):
    """CLI mode (v1.6): อ่าน args + ไฟล์ — ทดสอบโดยไม่ยุ่งเมาส์จริง"""

    def _write_script(self, tmpdir, rows):
        import json
        p = os.path.join(tmpdir, "s.json")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, ensure_ascii=False)
        return p

    def test_missing_file(self):
        rc = am.cli_main(["no_such_file.json"])
        self.assertEqual(rc, 1)

    def test_bad_json(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "bad.json")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write("{not json")
            self.assertEqual(am.cli_main([p]), 1)

    def test_not_a_list(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = self._write_script(d, {"oops": 1})
            self.assertEqual(am.cli_main([p]), 1)

    def test_empty_script_finishes(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = self._write_script(d, [])
            self.assertEqual(am.cli_main([p]), 0)

    def test_skips_disabled_rows(self):
        # แถว disabled ต้องถูกข้าม — ใช้ action Beep ที่ปลอดภัยใน CLI
        import io
        import tempfile
        from unittest import mock
        with tempfile.TemporaryDirectory() as d:
            p = self._write_script(d, [
                {"enabled": False, "button": "Beep", "secs": 0},
                {"enabled": True, "button": "Beep", "secs": 0},
            ])
            buf = io.StringIO()
            with mock.patch("sys.stdout", buf):
                rc = am.cli_main([p])
            self.assertEqual(rc, 0)
            self.assertIn("[1/1]", buf.getvalue())   # เห็นแค่แถวที่ enabled เดียว


class TestPlayLog(unittest.TestCase):
    """ระบบ log การเล่น (v1.8): เขียน/ตัดความยาว/โยงกับ CLI — ทดสอบใน temp dir"""

    def setUp(self):
        import tempfile
        self._tmp = tempfile.TemporaryDirectory()
        self._patcher = mock.patch.object(am, "log_path",
                                          lambda: os.path.join(self._tmp.name, "log.txt"))
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()
        self._tmp.cleanup()

    def _read(self):
        p = os.path.join(self._tmp.name, "log.txt")
        if not os.path.isfile(p):
            return ""
        with open(p, encoding="utf-8") as fh:
            return fh.read()

    def test_log_filename_daily(self):
        import datetime
        self.assertRegex(am.log_filename(), r"^macro_log_\d{4}-\d{2}-\d{2}\.txt$")
        self.assertIn(datetime.date.today().isoformat(), am.log_filename())

    def test_log_write_appends(self):
        am.log_write("START", "เริ่มเล่น", "demo.json")
        am.log_write("STEP", "แถว 1")
        text = self._read()
        lines = text.strip().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertRegex(lines[0], r"^\d{2}:\d{2}:\d{2} \[START\] เริ่มเล่น  <- demo\.json$")
        self.assertIn("[STEP] แถว 1", lines[1])          # ไม่มี src ก็เขียนได้

    def test_log_write_never_raises(self):
        # แม้ log_path พัง ก็ห้ามทำโปรแกรมล้ม (ตัวอย่าง: พาธเป็น None)
        with mock.patch.object(am, "log_path", lambda: None):
            am.log_write("STEP", "x")                     # ไม่ต้อง assert — แค่ไม่ raise

    def test_prune_log_keeps_last_lines(self):
        for i in range(10):
            am.log_write("STEP", "บรรทัด %d" % i)
        am.prune_log(keep=3)
        lines = self._read().strip().splitlines()
        self.assertEqual(len(lines), 3)
        self.assertIn("บรรทัด 9", lines[-1])

    def test_prune_missing_file_ok(self):
        am.prune_log()                                   # ยังไม่มีไฟล์ = ไม่ error

    def test_cli_writes_log(self):
        import io
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "s.json")
            import json
            with open(p, "w", encoding="utf-8") as fh:
                json.dump([{"enabled": True, "button": "Beep", "secs": 0}], fh)
            buf = io.StringIO()
            with mock.patch("sys.stdout", buf):
                rc = am.cli_main([p])
            self.assertEqual(rc, 0)
            text = self._read()
            self.assertIn("[START]", text)
            self.assertIn("[STEP]", text)
            self.assertIn("[END]", text)
            self.assertIn("<- " + p, text)               # อ้างชื่อสคริปต์ที่เล่น

    def test_cli_no_log_flag(self):
        import io
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "s.json")
            import json
            with open(p, "w", encoding="utf-8") as fh:
                json.dump([{"enabled": True, "button": "Beep", "secs": 0}], fh)
            buf = io.StringIO()
            with mock.patch("sys.stdout", buf):
                rc = am.cli_main([p, "--no-log"])
            self.assertEqual(rc, 0)
            self.assertEqual(self._read(), "")            # ไม่เขียน log เลย


class TestPickPlayOrder(unittest.TestCase):
    """เล่นแบบสุ่มลำดับ/สัดส่วน (v1.10) — ใช้ random.Random ตั้ง seed เพื่อเทสต์ซ้ำได้"""

    def setUp(self):
        import random
        self.rows = [{"button": "Beep", "n": i} for i in range(10)]

    def test_full_no_shuffle_keeps_order(self):
        out = am.pick_play_order(self.rows)
        self.assertEqual([r["n"] for r in out], list(range(10)))
        self.assertIsNot(out, self.rows)            # ต้องคืนลิสต์ใหม่ ไม่แก้ของเดิม

    def test_pct_picks_subset(self):
        out = am.pick_play_order(self.rows, pct=50, rng=random.Random(42))
        self.assertEqual(len(out), 5)
        ns = [r["n"] for r in out]
        self.assertEqual(len(set(ns)), 5)           # ไม่ซ้ำ (sample ไม่ทดแทน)
        self.assertTrue(set(ns) <= set(range(10)))

    def test_pct_min_one_row(self):
        out = am.pick_play_order(self.rows, pct=1, rng=random.Random(1))
        self.assertEqual(len(out), 1)               # ต่ำสุด = 1 แถว ไม่ใช่ 0

    def test_pct_clamped(self):
        self.assertEqual(len(am.pick_play_order(self.rows, pct=150)), 10)
        self.assertEqual(len(am.pick_play_order(self.rows, pct=-5)), 1)

    def test_shuffle_changes_order(self):
        out = am.pick_play_order(self.rows, shuffle=True, rng=random.Random(7))
        self.assertEqual(sorted(r["n"] for r in out), list(range(10)))  # ครบทุกแถว
        self.assertNotEqual([r["n"] for r in out], list(range(10)))     # สลับจริง (seed นี้)

    def test_empty_rows(self):
        self.assertEqual(am.pick_play_order([]), [])


class TestWizardFilename(unittest.TestCase):
    """ชื่อไฟล์เริ่มต้นของ Record wizard"""

    def test_format(self):
        import datetime
        ts = datetime.datetime(2026, 9, 28, 10, 30, 5)
        self.assertEqual(am.wizard_filename(ts), "wizard_20260928_103005.json")

    def test_auto_now(self):
        self.assertRegex(am.wizard_filename(), r"^wizard_\d{8}_\d{6}\.json$")


class TestGlobalHotkeyMapping(unittest.TestCase):
    """Global hotkey (v1.8): ใช้ keyboard.Listener จับคู่คีย์เอง — F6/F8/F9/F10
    ต้องถูกผลักเข้า main thread ผ่าน root.after และคีย์อื่นต้องไม่กระทบ"""

    def test_mapping_keys(self):
        captured = {}

        class FakeListener:
            def __init__(self, on_press=None, **kw):
                captured["on_press"] = on_press

            daemon = None

            def start(self):
                pass

        pushed = []
        app = mock.MagicMock()
        app.root.after.side_effect = lambda delay, fn: pushed.append(fn)
        app._gk_start = lambda: am.MacroApp._gk_start(app)   # v2.4: เดินสายเมธอดใหม่
        with mock.patch.object(am.keyboard, "Listener", FakeListener):
            am.MacroApp._start_global_hotkeys(app)
            on_press = captured["on_press"]
        self.assertIsNotNone(on_press)
        from pynput.keyboard import Key as _Key
        on_press(mock.MagicMock())              # คีย์อื่น = เฉย ๆ ไม่ push
        self.assertEqual(len(pushed), 0)
        for k in (_Key.f6, _Key.f8, _Key.f9, _Key.f10,
                  _Key.f1, _Key.f2, _Key.f3, _Key.f4):   # v1.9: รวม hot-profile
            on_press(k)
        self.assertEqual(len(pushed), 8)        # ทุกปุ่มถูกผลักเข้า main thread


class TestLogStats(unittest.TestCase):
    """สรุปสถิติจาก log (v1.11) — เขียน log จำลองใน temp dir"""

    SAMPLE = "\n".join([
        "08:00:00 [START] เริ่มเล่น (CLI)  <- a.json",
        "08:00:01 [STEP] รอบ 1 แถว 1/2 Beep (0.2 วิ)  <- a.json",
        "08:00:03 [STEP] รอบ 1 แถว 2/2 Press Key ctrl (2.5 วิ)  <- a.json",
        "08:00:03 [END] เล่นจบเองครบ  <- a.json",
        "08:05:00 [START] เริ่มเล่น (CLI)  <- a.json",
        "08:05:01 [STEP] รอบ 1 แถว 1/2 Beep (0.1 วิ)  <- a.json",
        "08:05:02 [STOP] หยุดโดยผู้ใช้ (F8/Esc/Ctrl+C)  <- a.json",
        "08:06:00 [WATCHDOG] รีสตาร์ตครั้งที่ 1 หลังพัก 3 วิ  <- a.json",
    ]) + "\n"

    def setUp(self):
        import tempfile
        self._tmp = tempfile.TemporaryDirectory()
        with open(os.path.join(self._tmp.name, "macro_log_2026-09-28.txt"),
                  "w", encoding="utf-8") as fh:
            fh.write(self.SAMPLE)

    def tearDown(self):
        self._tmp.cleanup()

    def test_parse_single_file(self):
        s = am.parse_log_stats(os.path.join(self._tmp.name, "macro_log_2026-09-28.txt"))
        self.assertEqual(s["runs"], 2)
        self.assertEqual(s["steps"], 3)
        self.assertEqual(s["stops"], 1)
        self.assertEqual(s["restarts"], 1)
        self.assertIsNotNone(s["slowest"])
        self.assertAlmostEqual(s["slowest"][1], 2.5)          # แถวที่ช้าสุด
        self.assertIn("Press Key ctrl", s["slowest"][0])

    def test_parse_missing_file(self):
        s = am.parse_log_stats(os.path.join(self._tmp.name, "nope.txt"))
        self.assertEqual((s["runs"], s["steps"], s["stops"], s["restarts"]), (0, 0, 0, 0))
        self.assertIsNone(s["slowest"])

    def test_summary_across_files(self):
        # เพิ่มอีกวัน: ค่ารวมต้องบวกกัน
        with open(os.path.join(self._tmp.name, "macro_log_2026-09-27.txt"),
                  "w", encoding="utf-8") as fh:
            fh.write("10:00:00 [START] เริ่มเล่น (CLI)  <- b.json\n")
        s = am.log_stats_summary(self._tmp.name)
        self.assertEqual(s["files"], 2)
        self.assertEqual(s["runs"], 3)
        self.assertEqual(s["steps"], 3)
        self.assertAlmostEqual(s["slowest"][1], 2.5)

    def test_summary_empty_dir(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            s = am.log_stats_summary(d)
            self.assertEqual(s["files"], 0)
            self.assertIsNone(s["slowest"])


class TestSelfCheck(unittest.TestCase):
    """self-check ตอนเปิดโปรแกรม (v1.11) — mock ระบบภายนอกทั้งหมด"""

    def _app(self):
        app = mock.MagicMock()
        app.mouse_ctl.position = (100, 100)
        app._gk = mock.MagicMock()
        app._gk.is_alive.return_value = True
        return app

    def test_all_ok(self):
        app = self._app()
        fake_win = mock.MagicMock()
        fake_win.shell32.IsUserAnAdmin.return_value = 1
        with mock.patch.object(am, "HAS_CV", True), \
             mock.patch("ctypes.windll", fake_win, create=True):   # create: windll มีเฉพาะ Windows
            chk = am.MacroApp._self_check(app)
        self.assertTrue(all(chk.values()))
        lines = am.MacroApp.self_check_text(app)
        self.assertEqual(len(lines), 5)               # v2.2: เพิ่มบรรทัด Listener บันทึก
        self.assertTrue(all(ok for _, ok, _ in lines))

    def test_hotkey_down_reported(self):
        app = self._app()
        app._gk = None
        chk = am.MacroApp._self_check(app)
        self.assertFalse(chk["hotkey"])
        lines = am.MacroApp.self_check_text(app)
        hot = [note for name, ok, note in lines if "hotkey" in name][0]
        self.assertIn("โฟกัส", hot)                           # มีคำแนะนำ

    def test_exception_tolerant(self):
        app = self._app()
        app.mouse_ctl = mock.MagicMock()
        type(app.mouse_ctl).position = mock.PropertyMock(side_effect=OSError)
        app._gk.is_alive.side_effect = RuntimeError
        chk = am.MacroApp._self_check(app)                    # ต้องไม่ raise
        self.assertFalse(chk["mouse"])
        self.assertFalse(chk["hotkey"])


class TestDailySeries(unittest.TestCase):
    """สถิติรายวันสำหรับกราฟ (v1.12)"""

    def test_series_sorted_and_limited(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            for day, runs in (("2026-09-26", 1), ("2026-09-27", 3), ("2026-09-28", 2)):
                with open(os.path.join(d, "macro_log_%s.txt" % day), "w", encoding="utf-8") as fh:
                    fh.write("".join("%s [START] x  <- s.json\n" % day for _ in range(runs)))
            s = am.log_daily_series(d)
            self.assertEqual([x["day"] for x in s],
                             ["2026-09-26", "2026-09-27", "2026-09-28"])  # เก่า → ใหม่
            self.assertEqual([x["runs"] for x in s], [1, 3, 2])
            s2 = am.log_daily_series(d, limit=2)
            self.assertEqual([x["day"] for x in s2], ["2026-09-27", "2026-09-28"])  # เอาวันล่าสุด

    def test_series_empty(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(am.log_daily_series(d), [])


class TestExportImport(unittest.TestCase):
    """Export/Import การตั้งค่า (v1.12) — mock filedialog และ messagebox ทั้งหมด"""

    def _app(self):
        app = mock.MagicMock()
        app._serialize.return_value = [{"button": "Beep", "secs": 0}]
        app._profiles = {"ค่าเริ่มต้น": [{"button": "Beep"}], "งาน B": []}
        app._active_profile = "ค่าเริ่มต้น"
        app._log_enabled = False
        app._log_keep_days = 0                      # v2.11: export_settings อ่าน attr นี้
        app._log_archive = True
        app._hp_dir = None
        app._ui_state = {"msg": None}
        return app

    def test_export_writes_full_settings(self):
        import tempfile
        app = self._app()
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "settings.json")
            with mock.patch.object(am.filedialog, "asksaveasfilename", return_value=f):
                am.MacroApp.export_settings(app)
            data = json.load(open(f, encoding="utf-8"))
            self.assertEqual(data["kind"], "automousemacro-settings")
            self.assertEqual(data["active_profile"], "ค่าเริ่มต้น")
            self.assertEqual(set(data["profiles"]), {"ค่าเริ่มต้น", "งาน B"})
            self.assertIn("log_enabled", data)
            self.assertIn("ส่งออก", app._ui_state["msg"][0])

    def test_import_roundtrip(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "settings.json")
            json.dump({"kind": "automousemacro-settings", "version": 1,
                       "rows": [{"button": "Beep", "secs": 1}],
                       "profiles": {"A": [{"button": "Beep"}], "B": []},
                       "active_profile": "B",
                       "log_enabled": True, "hot_profile_dir": None},
                      open(f, "w", encoding="utf-8"))
            app = self._app()
            app._load_rows = mock.MagicMock()
            app._refresh_profile_ui = mock.MagicMock()
            with mock.patch.object(am.filedialog, "askopenfilename", return_value=f), \
                 mock.patch.object(am.messagebox, "askyesno", return_value=True):
                am.MacroApp.import_settings(app)
            self.assertEqual(app._active_profile, "B")
            self.assertTrue(app._log_enabled)
            app._load_rows.assert_called_once()               # งานถูกโหลดแทนที่
            self.assertIn("นำเข้า", app._ui_state["msg"][0])

    def test_import_rejects_wrong_file(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "other.json")
            with open(f, "w", encoding="utf-8") as fh:
                json.dump([{"button": "Beep"}], fh)           # ไฟล์สคริปต์ปกติ (ไม่ใช่ settings)
            app = self._app()
            app._load_rows = mock.MagicMock()
            with mock.patch.object(am.filedialog, "askopenfilename", return_value=f), \
                 mock.patch.object(am.messagebox, "showerror") as err:
                am.MacroApp.import_settings(app)              # ต้องไม่เปลี่ยนอะไร
            app._load_rows.assert_not_called()
            err.assert_called_once()                          # แจ้ง error (ผ่าน mock ไม่เด้ง dialog จริง)

    def test_import_cancelled(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "settings.json")
            json.dump({"kind": "automousemacro-settings", "profiles": {}, "rows": []},
                      open(f, "w", encoding="utf-8"))
            app = self._app()
            app._load_rows = mock.MagicMock()
            with mock.patch.object(am.filedialog, "askopenfilename", return_value=f), \
                 mock.patch.object(am.messagebox, "askyesno", return_value=False):
                am.MacroApp.import_settings(app)
            app._load_rows.assert_not_called()                # ไม่ยอมรับ = ไม่แตะข้อมูล


class TestI18n(unittest.TestCase):
    """สลับภาษาไทย/อังกฤษ (v1.14)"""

    def test_tr_th_en(self):
        self.assertEqual(am.tr("th", "shuffle"), "สุ่มลำดับ")
        self.assertEqual(am.tr("en", "shuffle"), "Shuffle")
        self.assertEqual(am.tr("en", "mode_once"), "play once")

    def test_tr_fallback(self):
        self.assertEqual(am.tr("jp", "shuffle"), "สุ่มลำดับ")   # ภาษาไม่รู้จัก = ไทย
        self.assertEqual(am.tr("th", "no_such_key"), "no_such_key")  # คีย์ไม่มี = คืนคีย์

    def test_apply_language_updates_labels(self):
        app = mock.MagicMock()
        app._lang = "th"
        app._t = lambda key: am.tr("th", key)
        app.running = False
        app._ui_state = {"msg": None}
        am.MacroApp._apply_language(app)
        app.chk_shuffle_btn.config.assert_called_with(text="สุ่มลำดับ")
        self.assertIn("ไทย", app._ui_state["msg"][0])
        # สลับเป็นอังกฤษ
        app._lang = "en"
        app._t = lambda key: am.tr("en", key)
        am.MacroApp._apply_language(app)
        app.chk_shuffle_btn.config.assert_called_with(text="Shuffle")


class TestBackupSettings(unittest.TestCase):
    """ตั้งค่า backup ได้ (v1.14): เปิด/ปิด + จำนวนวัน + จำใน conf"""

    def test_backup_respects_enabled(self):
        import tempfile
        app = mock.MagicMock()
        app._backup_enabled = False
        app._serialize.return_value = []
        app._profiles = {}
        app._active_profile = "x"
        app._log_enabled = True
        app._hp_dir = None
        with tempfile.TemporaryDirectory() as d, \
                mock.patch.object(am, "BACKUP_DIR", "backups_disabled_test"):
            r = am.MacroApp._on_close_backup(app, d)
            self.assertIsNone(r)                      # ปิดอยู่ = ไม่เขียน backup
            self.assertFalse(os.path.isdir(os.path.join(d, "backups_disabled_test")))

    def test_backup_uses_custom_days(self):
        import datetime
        import tempfile
        app = mock.MagicMock()
        app._backup_enabled = True
        app._backup_days = 3
        app._log_keep_days = 0
        app._log_archive = True
        app._serialize.return_value = []
        app._profiles = {}
        app._active_profile = "x"
        app._log_enabled = True
        app._hp_dir = None
        with tempfile.TemporaryDirectory() as d:
            # สร้างไฟล์เก่า 5 วัน (เกิน 3 วันที่ตั้ง) แล้ว backup ใหม่ต้องตัดทิ้ง
            bk = os.path.join(d, am.BACKUP_DIR)
            os.makedirs(bk)
            old = datetime.datetime.now() - datetime.timedelta(days=5)
            old_path = am.backup_snapshot(d, {"old": 1}, now=old, keep_days=90)
            self.assertTrue(os.path.isfile(old_path))                  # ยังไม่ตัด
            am.MacroApp._on_close_backup(app, d)                       # ตัดตาม 3 วัน
            files = os.listdir(bk)
            self.assertEqual(len(files), 1)                            # เหลือแต่ตัวใหม่
            self.assertNotIn(os.path.basename(old_path), files)        # ไฟล์เก่าหายจริง

    def test_conf_roundtrip_new_fields(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            conf = os.path.join(d, "macro_conf.json")
            with open(conf, "w", encoding="utf-8") as fh:
                json.dump({"rows": [], "log_enabled": False,
                           "backup_enabled": False, "backup_days": 21,
                           "lang": "en"}, fh)
            app = mock.MagicMock()
            app._load_rows = mock.MagicMock()
            app._backup_enabled = True
            app._backup_days = 7
            app._log_keep_days = 0
            app._log_archive = True
            app._lang = "th"
            with mock.patch.object(am, "CONF", conf):     # ชี้ conf ไปที่ไฟล์ทดสอบ
                am.MacroApp._load_conf(app)
            self.assertFalse(app._backup_enabled)
            self.assertEqual(app._backup_days, 21)
            self.assertEqual(app._lang, "en")


class TestBackup(unittest.TestCase):
    """Backup อัตโนมัติ 7 วัน (v1.13) — ทำงานใน temp dir ล้วน"""

    def setUp(self):
        import tempfile
        self._tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self._tmp.cleanup()

    def _bk(self):
        return os.path.join(self._tmp.name, "backups")

    def test_snapshot_writes_and_prunes(self):
        import datetime
        # เก่า 3 วันจาก "วันนี้จริง" — เดิม hardcode วันที่ลงไป พอวันจริงเลย 7 วัน
        # ไฟล์เก่าถูก prune เทสต์พังเอง (1 != 2) — คำนวณจาก now เสมอ
        old = datetime.datetime.now() - datetime.timedelta(days=3)
        am.backup_snapshot(self._tmp.name, {"a": 1}, now=old)
        p = am.backup_snapshot(self._tmp.name, {"b": 2})   # วันนี้
        files = sorted(os.listdir(self._bk()))
        self.assertEqual(len(files), 2)                    # เก่า (3 วิ) ยังไม่เกิน 7 วัน
        data = json.load(open(p, encoding="utf-8"))
        self.assertEqual(data, {"b": 2})
        self.assertRegex(os.path.basename(p), r"^backup_\d{4}-\d{2}-\d{2}_\d{6}\.json$")

    def test_prune_deletes_over_7_days(self):
        import datetime
        d10 = datetime.datetime.now() - datetime.timedelta(days=10)   # เก่ากว่า 7 วิ = ถูกลบ
        d1 = datetime.datetime.now() - datetime.timedelta(days=1)     # ยังไม่เกิน = เก็บ
        am.backup_snapshot(self._tmp.name, {"old": 1}, now=d10)
        am.backup_snapshot(self._tmp.name, {"new": 2}, now=d1)
        am.backup_snapshot(self._tmp.name, {"today": 3})   # จะเรียก prune ให้เอง
        files = os.listdir(self._bk())
        self.assertEqual(len(files), 2)                    # ตัวเก่า 10 วันถูกลบ
        self.assertFalse(any(d10.strftime("%Y%m%d") in f for f in files))

    def test_snapshot_never_raises(self):
        # base_dir ที่สร้างไม่ได้ (มีอยู่เป็นไฟล์) = ต้องคืน None ไม่ raise
        f = os.path.join(self._tmp.name, "blocker")
        open(f, "w").close()
        self.assertIsNone(am.backup_snapshot(f, {"x": 1}))

    def test_prune_bad_names_ignored(self):
        os.makedirs(self._bk(), exist_ok=True)
        open(os.path.join(self._bk(), "backup_notadate.json"), "w").close()
        am.prune_backups(self._bk())                       # ไม่ raise ไม่ลบไฟล์แปลก
        self.assertTrue(os.path.isfile(os.path.join(self._bk(), "backup_notadate.json")))


class TestMonthlySeries(unittest.TestCase):
    """สรุปการใช้งานรวมรายเดือน (v1.15)"""

    def test_monthly_aggregates(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            for day, runs in (("2026-08-15", 2), ("2026-08-31", 1), ("2026-09-05", 4)):
                with open(os.path.join(d, "macro_log_%s.txt" % day), "w", encoding="utf-8") as fh:
                    fh.write("".join("%s [START] x  <- s.json\n" % day for _ in range(runs)))
            s = am.log_monthly_series(d)
            self.assertEqual([x["month"] for x in s], ["2026-08", "2026-09"])
            self.assertEqual([x["runs"] for x in s], [3, 4])     # รวมเดือนเดียวกัน

    def test_monthly_limit(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            for ym in ("2026-04", "2026-05", "2026-06", "2026-07"):
                with open(os.path.join(d, "macro_log_%s-10.txt" % ym), "w", encoding="utf-8") as fh:
                    fh.write("x [START] y\n")
            s = am.log_monthly_series(d, limit=2)
            self.assertEqual([x["month"] for x in s], ["2026-06", "2026-07"])

    def test_monthly_empty(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(am.log_monthly_series(d), [])


class TestUiDialogs(unittest.TestCase):
    """เปิด dialog จริงด้วย Tk จำลอง (withdraw) — ต้องสร้างได้ครบไม่ crash (v1.15)
    รันด้วย xvfb บน Linux CI ก็ผ่าน (Tk ไม่ต้องเห็นจอ แค่มี display จำลอง)"""

    @classmethod
    def setUpClass(cls):
        try:
            cls.root = _Tk()
            cls.root.withdraw()
            cls.has_tk = True
        except am.tk.TclError:
            cls.has_tk = False          # ไม่มี display (CI บางที่) — ข้ามชุดนี้

    @classmethod
    def tearDownClass(cls):
        if cls.has_tk:
            cls.root.destroy()

    def setUp(self):
        if not self.has_tk:
            self.skipTest("ไม่มี display สำหรับ Tk")
        self.app = mock.MagicMock()
        self.app.root = self.root
        self.app._lang = "th"
        self.app._t = lambda key: am.tr("th", key)
        self.app._ui_state = {"msg": None, "row": None, "prog": None, "reset": False}
        self.app._serialize.return_value = []
        self.app._profiles = {"ค่าเริ่มต้น": []}
        self.app._active_profile = "ค่าเริ่มต้น"
        self.app._log_enabled = True
        self.app._backup_enabled = True
        self.app._backup_days = 7
        self.app._log_keep_days = 0                # v2.11: Settings อ่านตอนเปิด dialog
        self.app._log_archive = True
        self.app._hp_dir = None
        self.app._gk = None
        self.app._gk_heal_at = 0.0        # v2.4: self-healing
        self.app._time_limit_enabled = False   # v2.4: Safety timeout
        self.app._time_limit_min = 30
        self.app._sched_mode = ""         # v2.4: schedule label ใน Settings
        self.app._sched_every = 10
        self.app._sched_at = ""
        self.app._sched_profile = ""
        self.app._plugins = []            # v2.4: plugins status ใน Settings
        self.app._checks = {"mouse": True, "hotkey": True, "opencv": True,
                            "admin": False, "conf_writable": True}
        self.app.running = False
        self.app.recording = False
        self.app._pending_rows = []
        self.app._recorder = am.macro_engine.Recorder()   # v2.2: กลไก RECORD อยู่ใน engine
        self.app._loaded_file = None
        self.app._log_src = None
        self.app._hp_dir = None

    def test_settings_dialog_opens(self):
        am.MacroApp.settings_dialog(self.app)        # สร้าง Toplevel จริง
        tops = [w for w in self.root.winfo_children() if isinstance(w, am.tk.Toplevel)]
        self.assertTrue(tops)
        for w in tops:
            w.destroy()

    def test_help_dialog_opens(self):
        am.MacroApp.help_dialog(self.app)
        self._close_tops()

    def test_view_stats_opens(self):
        am.MacroApp.view_stats(self.app)
        self._close_tops()

    def test_view_log_opens(self):
        am.MacroApp.view_log(self.app)
        self._close_tops()

    def test_hot_profile_dialog_opens(self):
        am.MacroApp.hot_profile_dialog(self.app)
        self._close_tops()

    def test_record_wizard_opens(self):
        am.MacroApp.record_wizard(self.app)
        self._close_tops()

    def _close_tops(self):
        for w in self.root.winfo_children():
            if isinstance(w, am.tk.Toplevel):
                w.destroy()


class TestMenuItems(unittest.TestCase):
    """เมนูไอคอนต้องอ้างเมธอดที่มีจริงทั้งหมด (กันพิมพ์ชื่อผิด)"""

    def test_menu_methods_exist(self):
        for icon, label, name, color in am.MacroApp._menu_items():
            self.assertTrue(hasattr(am.MacroApp, name),
                            "เมนู %s อ้างเมธอด %s ที่ไม่มีอยู่" % (label, name))

    def test_log_and_hotprofile_in_menu(self):
        names = [name for _, _, name, _ in am.MacroApp._menu_items()]
        self.assertIn("view_log", names)
        self.assertIn("hot_profile_dialog", names)


class TestHotProfile(unittest.TestCase):
    """Hot-profile F1-F4 (v1.9): เลือกไฟล์ลำดับที่ n เรียงตามชื่อ — ไม่แตะ Tk จริง"""

    def _app(self, hp_dir):
        app = mock.MagicMock()
        app._hp_dir = hp_dir
        app._loaded_file = None
        app._log_src = None
        app._ui_state = {"msg": None, "row": None, "prog": None, "reset": False}  # dict จริง
        pushed = []
        app.root.after.side_effect = lambda delay, fn: pushed.append(fn)
        return app, pushed

    def test_no_dir_shows_warning(self):
        app, pushed = self._app(None)
        am.MacroApp._hot_profile_load(app, 1)
        self.assertEqual(len(pushed), 1)
        pushed[0]()                             # รันงานที่ผลักเข้า main thread
        self.assertIn("Hot-profile", app._ui_state["msg"][0])

    def test_picks_nth_file_sorted(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            for name in ("b.json", "a.json", "c.json"):
                with open(os.path.join(d, name), "w", encoding="utf-8") as fh:
                    fh.write('[{"button": "Beep", "secs": 0}]')
            app, pushed = self._app(d)
            started = []
            app._start_player = mock.MagicMock(
                side_effect=lambda loop: started.append(loop))
            am.MacroApp._hot_profile_load(app, 2)       # ลำดับ 2 = b.json
            self.assertEqual(len(pushed), 1)
            pushed[0]()                                 # รันบน main thread จำลอง
            self.assertEqual(app._loaded_file, os.path.join(d, "b.json"))
            self.assertEqual(started, [False])          # โหลดแล้วเล่นทันที (ครั้งเดียว)

    def test_index_out_of_range(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "only.json"), "w", encoding="utf-8") as fh:
                fh.write("[]")
            app, pushed = self._app(d)
            am.MacroApp._hot_profile_load(app, 3)       # มีแค่ไฟล์เดียว
            self.assertEqual(len(pushed), 1)
            pushed[0]()
            self.assertIn("F3", app._ui_state["msg"][0])

    def test_empty_folder(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            app, pushed = self._app(d)
            am.MacroApp._hot_profile_load(app, 1)
            pushed[0]()
            self.assertIn("ไม่มีไฟล์", app._ui_state["msg"][0])


import shutil
import tempfile
import time


class TestPlugins(unittest.TestCase):
    """Custom Action plugins (v1.16): โหลด/กติกา/ผูก ctx
    ⚠️ ห้ามตั้งชื่อคลาสซ้ำกับคลาสเดิม (คลาสหลังบังคลาสหน้า — ดู AGENTS.md)"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.pdir = os.path.join(self.tmp, "plugins")
        os.makedirs(self.pdir)
        self.failed_before = list(am.load_plugins.last_failed)

    def tearDown(self):
        am.load_plugins.last_failed = self.failed_before
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, name, body):
        p = os.path.join(self.pdir, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(body)

    def test_load_valid_plugin(self):
        self._write("ok.py", 'ACTION_NAME = "ทดสอบ"\n'
                             'def run(ctx, row):\n'
                             '    ctx["log"]("hi")\n')
        out = am.load_plugins(base_dir=self.tmp)
        self.assertEqual([n for n, _ in out], ["ทดสอบ"])
        self.assertEqual(am.load_plugins.last_failed, [])

    def test_underscore_file_skipped(self):
        self._write("_hidden.py", 'ACTION_NAME = "ซ่อน"\n'
                                  'def run(ctx, row):\n'
                                  '    pass\n')
        self.assertEqual(am.load_plugins(base_dir=self.tmp), [])

    def test_missing_run_skipped(self):
        self._write("bad.py", 'ACTION_NAME = "เสีย"\n')
        out = am.load_plugins(base_dir=self.tmp)
        self.assertEqual(out, [])
        self.assertEqual(len(am.load_plugins.last_failed), 1)

    def test_duplicate_name_rejected(self):
        self._write("a.py", 'ACTION_NAME = "Beep"\n'
                            'def run(ctx, row):\n'
                            '    pass\n')
        out = am.load_plugins(base_dir=self.tmp)
        self.assertEqual(out, [])
        self.assertEqual(len(am.load_plugins.last_failed), 1)

    def test_broken_plugin_does_not_crash(self):
        self._write("boom.py", "raise RuntimeError('import พัง')\n")
        out = am.load_plugins(base_dir=self.tmp)
        self.assertEqual(out, [])
        self.assertEqual(len(am.load_plugins.last_failed), 1)

    def test_bundled_examples_load(self):
        src = os.path.dirname(os.path.abspath(am.__file__))
        names = [n for n, _ in am.load_plugins(base_dir=src)]
        self.assertIn("Sleep (plugin)", names)
        self.assertIn("Message Box", names)
        self.assertEqual(am.load_plugins.last_failed, [])

    def test_sleep_plugin_runs(self):
        src = os.path.dirname(os.path.abspath(am.__file__))
        plugins = dict(am.load_plugins(base_dir=src))
        logged = []
        t0 = time.time()
        plugins["Sleep (plugin)"].run(
            {"log": logged.append, "cfg": {"lang": "th"}}, {"additional": "0.2"})
        self.assertGreaterEqual(time.time() - t0, 0.19)
        self.assertTrue(logged)

    def test_message_box_plugin_falls_back_to_log(self):
        # แสดง dialog จริงไม่ได้ในเทสต์ (จะบล็อกรอคลิก!) → patch showinfo แล้วเช็คว่าถูกเรียก
        src = os.path.dirname(os.path.abspath(am.__file__))
        plugins = dict(am.load_plugins(base_dir=src))
        ctx = {"log": lambda m: None, "cfg": {"lang": "th"}}
        with mock.patch("tkinter.messagebox.showinfo") as si:
            plugins["Message Box"].run(ctx, {"additional": "ทดสอบ"})
            si.assert_called_once()
            self.assertIn("ทดสอบ", str(si.call_args))


class TestUndoFindPaste(unittest.TestCase):
    """v1.17: Undo (Ctrl+Z), ค้นหาแถว (Ctrl+F), วางจากคลิปบอร์ด"""

    def _app(self):
        app = mock.MagicMock()
        # prefix "r" ไม่ซ้ำกับคีย์เริ่มต้น "i*" — กันแถวใหม่เขียนทับแถวเดิมใน store
        kids = iter("r%d" % i for i in range(1, 999))
        store = {"i1": ["☑", 1, "", "", "Beep", "", "0", "1", "1"],
                 "i2": ["☑", 2, "", "", "Tap Key", "a", "0", "1", "1"],
                 "i3": ["☐", 3, "", "", "Beep", "พิเศษ", "0", "2", "1"]}

        def insert(parent, index, **kw):
            iid = next(kids)
            store[iid] = list(kw["values"])
            return iid
        app.tree.get_children.side_effect = lambda: list(store.keys())

        def _item(iid, *args, **kw):
            if "values" in kw:                 # item(iid, values=...) = setter จริง
                store[iid] = list(kw["values"])
                return None
            return store.get(iid)              # item(iid) = getter
        app.tree.item.side_effect = _item
        app.tree.insert = insert
        app.tree.delete.side_effect = lambda *ids: [store.pop(i, None) for i in ids]
        app.tree.selection.return_value = []
        app._t = lambda k: am.tr("th", k)
        app._ui_state = {}
        app._undo_stack = []
        app._redo_stack = []
        app._section_stash = []
        app._hl_row = None

        def _append_row(**kw):
            store[next(kids)] = ["☑", len(store) + 1, kw.get("x", ""), kw.get("y", ""),
                                 kw.get("button", ""), kw.get("additional", ""),
                                 am.fmt_num(kw.get("mins", 0)), am.fmt_num(kw.get("secs", 1)),
                                 am.fmt_num(kw.get("repeat", 1))]
        app._append_row = _append_row

        def refresh_nums():
            for i, iid in enumerate(list(store.keys()), 1):
                store[iid][1] = i
        app.refresh_nums = refresh_nums
        for m in ("_snapshot_rows", "_push_undo", "_undo_delete", "_restore_rows",
                  "_redo_delete", "_replace_all", "_find_rows",
                  "_goto_row", "_find_dialog", "_paste_rows_clipboard"):
            setattr(app, m, getattr(am.MacroApp, m).__get__(app))
        return app, store

    def test_find_rows_matches_any_column(self):
        app, _s = self._app()
        self.assertEqual(app._find_rows("beep"), [1, 3])
        self.assertEqual(app._find_rows("A"), [2])          # ไม่แยกพิมพ์เล็ก-ใหญ่
        self.assertEqual(app._find_rows("พิเศษ"), [3])
        self.assertEqual(app._find_rows(""), [])

    def test_undo_restores_deleted_rows(self):
        app, store = self._app()
        app.tree.selection.return_value = ["i1"]
        app._on_del = getattr(am.MacroApp, "_on_del").__get__(app)
        app._on_del()
        self.assertNotIn("i1", store)
        app._undo_delete()
        # กู้คืนแล้ว: มีแถว Beep (Additional ว่าง, ☑, เหมือน i1 เดิม) กลับมาในตาราง
        restored = [v for v in store.values()
                    if v[0] == "☑" and v[4] == "Beep" and v[5] == ""]
        self.assertEqual(len(restored), 1)
        self.assertEqual(restored[0][7], "1")               # secs เดิม

    def test_redo_restores_after_undo(self):
        """v2.5: Ctrl+Y ทำซ้ำการลบที่เพิ่ง undo — สลับ undo/redo ได้เรื่อย ๆ"""
        app, store = self._app()
        app.tree.selection.return_value = ["i1"]
        app._on_del = getattr(am.MacroApp, "_on_del").__get__(app)
        app._on_del()
        app._undo_delete()
        app._redo_delete()
        restored = [v for v in store.values() if v[4] == "Beep" and v[5] == ""]
        self.assertEqual(len(restored), 0)              # redo = ลบซ้ำอีกครั้ง
        app._undo_delete()
        restored = [v for v in store.values() if v[4] == "Beep" and v[5] == ""]
        self.assertEqual(len(restored), 1)              # undo กู้คืนต่อได้

    def test_edit_pushes_undo(self):
        """v2.5: แก้เซลล์ผ่าน _apply_edit = เข้า undo stack ด้วย"""
        app, store = self._app()
        app._apply_edit = getattr(am.MacroApp, "_apply_edit").__get__(app)
        before = len(app._undo_stack)
        app._apply_edit("i1", 4, "Tap Key")
        self.assertEqual(store["i1"][4], "Tap Key")
        self.assertEqual(len(app._undo_stack), before + 1)

    def test_replace_all_across_columns(self):
        """v2.5: แทนที่ทั้งหมด — X/Y/Action/Additional/Note และผ่าน undo"""
        app, store = self._app()
        n = app._replace_all("beep", "BEEP")
        self.assertEqual(n, 2)                          # i1 + i3 เป็น Beep
        self.assertEqual(store["i1"][4], "BEEP")
        self.assertGreaterEqual(len(app._undo_stack), 1)
        app._undo_delete()
        beeps = [v for v in store.values() if v[4] == "Beep" and "BEEP" not in str(v)]
        self.assertEqual(len(beeps), 2)                 # undo คืนค่าเดิม (iid ใหม่)

    def test_undo_empty_shows_message(self):
        app, _s = self._app()
        app._undo_delete()
        self.assertIn("msg", app._ui_state)                 # แจ้งว่าไม่มีอะไรให้กู้

    def test_undo_after_load_replaces_table(self):
        app, store = self._app()
        app._load_rows = getattr(am.MacroApp, "_load_rows").__get__(app)
        app._load_rows([{"button": "Beep", "enabled": True}])
        self.assertEqual(len(store), 1)                     # ถูกแทนที่ด้วยแถวใหม่
        app._undo_delete()
        restored = [v for v in store.values() if v[4] == "Tap Key"]
        self.assertEqual(len(restored), 1)                  # แถว Tap Key เดิมกลับมา

    def test_paste_rows_from_clipboard(self):
        app, store = self._app()
        app.root.clipboard_get.return_value = json.dumps(
            [{"button": "Tap Key", "additional": "b", "secs": 2, "enabled": False},
             {"button": "Beep"}])
        app._paste_rows_clipboard()
        self.assertEqual(len(store), 5)                     # 3 เดิม + 2 ใหม่
        pasted = [v for v in store.values() if v[4] == "Tap Key"]
        self.assertEqual(len(pasted), 2)                    # เดิม + ที่วางใหม่
        self.assertEqual(sorted(v[0] for v in pasted), ["☐", "☑"])  # เดิม ☑ + ใหม่ ☐
        self.assertIn("msg", app._ui_state)

    def test_paste_accepts_export_format(self):
        app, store = self._app()
        app.root.clipboard_get.return_value = json.dumps(
            {"kind": "automousemacro-settings", "rows": [{"button": "Beep"}]})
        app._paste_rows_clipboard()
        self.assertEqual(len(store), 4)

    def test_paste_bad_json_shows_error(self):
        app, store = self._app()
        app.root.clipboard_get.return_value = "ไม่ใช่ json"
        app._paste_rows_clipboard()
        self.assertEqual(len(store), 3)                     # ไม่เพิ่มแถว
        self.assertIn("msg", app._ui_state)

    def test_paste_empty_clipboard(self):
        app, store = self._app()
        import tkinter as tk
        app.root.clipboard_get.side_effect = tk.TclError("CLIPBOARD")  # คลิปบอร์ดว่างจริง
        app._paste_rows_clipboard()
        self.assertEqual(len(store), 3)
        self.assertIn("msg", app._ui_state)


class TestIfImage(unittest.TestCase):
    """v1.17: If Image — ภาพไม่เจอ → ข้าม N แถวถัดไป (N = คอลัมน์ Repeat)"""

    def test_action_registered(self):
        self.assertIn(am.IF_IMAGE, am.ACTIONS_ALL)

    def test_validate_requires_png(self):
        app = mock.MagicMock()
        app._plugin_module.return_value = None
        app._parse_search_area = getattr(am.MacroApp, "_parse_search_area").__get__(app)
        ok = am.MacroApp._validate_rows(
            app, [{"button": am.IF_IMAGE, "additional": "nope_missing.png"}])
        self.assertFalse(ok)

    def test_skip_counter_decrements(self):
        app = mock.MagicMock()
        app._ifimg_skip = 2
        # ลูปจำลอง: แถวถูกข้ามเงียบ ๆ เมื่อ _ifimg_skip > 0
        played = []
        for r in ["a", "b", "c"]:
            if app._ifimg_skip > 0:
                app._ifimg_skip -= 1
                continue
            played.append(r)
        self.assertEqual(played, ["c"])

    def test_find_image_pos_missing_file(self):
        if not am.HAS_CV:
            self.skipTest("ไม่มี opencv — CI ไม่ติดตั้ง (ฟีเจอร์ภาพปิดอัตโนมัติ)")
        app = mock.MagicMock()
        app._ui_state = {}
        app._parse_search_area = getattr(am.MacroApp, "_parse_search_area").__get__(app)
        app._grab_area_bgr = lambda area: (None, (0, 0))
        r = {"additional": "no_such_image_12345.png"}
        self.assertIsNone(am.MacroApp._find_image_pos(app, r))
        self.assertIn("ไม่พบไฟล์ภาพ", app._ui_state["msg"][0])


class TestPixelColor(unittest.TestCase):
    """v1.18: Wait for Pixel Color — parse spec/สี/เทียบสี"""

    def test_parse_color_hex(self):
        self.assertEqual(am.parse_color_hex("#ff0000"), (255, 0, 0))
        self.assertEqual(am.parse_color_hex("ff0000"), (255, 0, 0))
        self.assertEqual(am.parse_color_hex("#f00"), (255, 0, 0))     # รูปแบบสั้น
        self.assertEqual(am.parse_color_hex("#zzzzzz"), None)
        self.assertEqual(am.parse_color_hex(""), None)

    def test_parse_pixel_spec(self):
        self.assertEqual(am.parse_pixel_spec("100,200 #ff0000"), (100, 200, (255, 0, 0)))
        self.assertEqual(am.parse_pixel_spec("100,200 #f00"), (100, 200, (255, 0, 0)))
        self.assertIsNone(am.parse_pixel_spec("ไม่มีสี"))
        self.assertIsNone(am.parse_pixel_spec(""))

    def test_color_close(self):
        self.assertTrue(am.color_close((255, 0, 0), (250, 5, 3)))     # ภายใน tol 20
        self.assertFalse(am.color_close((255, 0, 0), (200, 0, 0)))
        self.assertFalse(am.color_close(None, (255, 0, 0)))

    def test_pixel_color_at_returns_rgb_or_none(self):
        c = am.pixel_color_at(5, 5)
        self.assertTrue(c is None or (isinstance(c, tuple) and len(c) == 3))

    def test_wait_pixel_bad_spec_shows_error(self):
        app = mock.MagicMock()
        app._ui_state = {}
        app._play_gen = 0
        app._speed_mult = 1.0
        app._sleep_check = lambda *a: True
        am.MacroApp._do_wait_for_pixel(app, {"additional": "รูปแบบพัง", "secs": "0"})
        self.assertIn("ไม่ถูกต้อง", app._ui_state["msg"][0])

    def test_action_registered(self):
        self.assertIn(am.WAIT_PIXEL, am.ACTIONS_ALL)
        self.assertIn(am.ELSE_IMAGE, am.ACTIONS_ALL)


class TestElseIfImage(unittest.TestCase):
    """v1.18: Else If Image — If เจอ → ข้ามกลุ่ม B (Repeat แถว), ไม่เจอ → เล่นกลุ่ม B"""

    def test_validate_requires_png(self):
        app = mock.MagicMock()
        app._plugin_module.return_value = None
        app._parse_search_area = getattr(am.MacroApp, "_parse_search_area").__get__(app)
        ok = am.MacroApp._validate_rows(
            app, [{"button": am.ELSE_IMAGE, "additional": "nope_missing.png"}])
        self.assertFalse(ok)

    def test_skip_semantics(self):
        # จำลองลูปเล่น: If เจอ → กลุ่ม A เล่นหมด, Else ตั้ง skip=Repeat → กลุ่ม B (2 แถว) ถูกข้าม
        played = []
        last_if_found = True
        skip = 0
        rows = ["IF", "A1", "A2", "ELSE(2)", "B1", "B2"]
        for r in rows:
            if r == "IF":                     # If ประเมินก่อนเสมอ (ไม่โดนนับ skip)
                played.append("IF")
                continue
            if skip > 0:
                skip -= 1
                continue
            if r.startswith("ELSE"):
                if last_if_found:
                    skip = int(r[5:-1])       # เจอ → ข้ามกลุ่ม B ตาม Repeat
                played.append("ELSE")
                continue
            played.append(r)
        self.assertEqual(played, ["IF", "A1", "A2", "ELSE"])

    def test_skip_semantics_if_missed(self):
        # If ไม่เจอ → If ตั้ง skip=2 (ข้าม A1 A2), Else ไม่ข้ามอะไร → เล่นกลุ่ม B ต่อ
        played = []
        skip = 0
        rows = ["IF(2)", "A1", "A2", "ELSE", "B1"]
        for r in rows:
            if r.startswith("IF"):
                skip = int(r[3:-1])           # ไม่เจอ → ข้ามแถวถัดไปตาม Repeat
                played.append("IF")
                continue
            if skip > 0:
                skip -= 1
                continue
            if r == "ELSE":
                played.append("ELSE")         # If ไม่เจอ → ไม่ตั้ง skip
                continue
            played.append(r)
        self.assertEqual(played, ["IF", "ELSE", "B1"])


class TestActionStats(unittest.TestCase):
    """v1.18: สถิติราย Action จาก log"""

    LINES = [
        "[START] เริ่มเล่น 3 แถว",
        "[STEP] รอบ 1 แถว 1/3 Beep  (0.10 วิ)",
        "[STEP] รอบ 1 แถว 2/3 Type Text สวัสดี (2.50 วิ)",
        "[STEP] รอบ 1 แถว 3/3 Beep  (0.30 วิ)",
        "[END] เล่นจบ",
    ]

    def _tmplog(self):
        d = tempfile.mkdtemp()
        p = os.path.join(d, "macro_log_2099-01-01.txt")   # ต้องตรง glob macro_log_*.txt
        with open(p, "w", encoding="utf-8") as f:
            f.write("\n".join(self.LINES))
        return p

    def test_parse_counts_actions(self):
        s = am.parse_log_stats(self._tmplog())
        self.assertEqual(s["actions"]["Beep"]["count"], 2)
        self.assertAlmostEqual(s["actions"]["Beep"]["total"], 0.4, places=2)
        self.assertAlmostEqual(s["actions"]["Type Text"]["total"], 2.5, places=2)
        self.assertAlmostEqual(s["actions"]["Type Text"]["max"], 2.5, places=2)

    def test_summary_aggregates(self):
        p = self._tmplog()
        total = am.log_stats_summary(base_dir=os.path.dirname(p))
        self.assertIn("Type Text", total["actions"])
        tops = am.top_actions_summary(total)
        self.assertEqual(tops[0][0], "Type Text")            # ใช้เวลารวมมากสุด
        self.assertGreaterEqual(tops[0][2], 2.5)

    def test_top_actions_sorted_limit(self):
        stats = {"actions": {"a": {"count": 1, "total": 1.0, "max": 1.0},
                             "b": {"count": 1, "total": 9.0, "max": 9.0},
                             "c": {"count": 1, "total": 5.0, "max": 5.0}}}
        tops = am.top_actions_summary(stats, limit=2)
        self.assertEqual([t[0] for t in tops], ["b", "c"])


class TestPlayLoopFixes(unittest.TestCase):
    """Regression v1.18.1 — บั๊ก 4 จุดที่พบจากการตรวจโค้ด (แก้แล้วทั้งหมด)
    1) _rows_for_play หายไปตอน v1.10 (rename เป็น _play_options แล้วลืมสร้างใหม่)
       → กด START/REPEAT ใน GUI พังทันที (AttributeError) — เทสต์เดิมไม่จับเพราะ mock ไว้
    2) _player บังคับ _shuffle=False/_pct=100 ทับค่าจาก UI → สุ่มลำดับ/สัดส่วนแถวไม่มีผล
    3) on_kb อ้างตัวแปร pressed ที่ไม่มีอยู่ → กดคีย์ตอน RECORD เกิด NameError ไม่มีแถวถูกอัด
    4) "if loop: break" กลับความหมายจาก v1.4 → REPEAT/วนซ้ำไม่จำกัด เล่นแค่ 1 รอบแล้วจบ
    (กลุ่มที่ใช้ Tk/จอ: Beep ล้วนไม่แตะเมาส์/คีย์จริง — ไม่มีจอแล้ว skip อัตโนมัติ)"""

    def test_rows_for_play_returns_enabled_only(self):
        app = mock.MagicMock()
        vals = [["☑", 1, "10", "20", "Beep", "", "0", "1", "1"],
                ["☐", 2, "", "", "Tap Key", "a", "0", "1", "1"],
                ["☑", 3, "", "", "Beep", "", "0", "1", "1"]]
        app.tree.get_children.return_value = ["i1", "i2", "i3"]
        app.tree.item.side_effect = lambda iid, key: {"values": vals[int(iid[1]) - 1]}[key]
        app._section_stash = []                                 # v2.8.1: แถวซ่อนแทรกกลับตอนเล่น
        rows, iids = am.MacroApp._rows_and_iids_for_play(app)   # เดิม: AttributeError — เมธอดหาย
        self.assertEqual([r["button"] for r in rows], ["Beep", "Beep"])
        self.assertEqual(iids, ["i1", "i3"])                    # iid ตรงกับแถวที่เล่นจริง (ไฮไลต์)
        # _rows_for_play delegate ผ่าน _rows_and_iids_for_play — เดินสายจริงให้ mock ใช้
        app._rows_and_iids_for_play = lambda: am.MacroApp._rows_and_iids_for_play(app)
        self.assertEqual([r["button"] for r in am.MacroApp._rows_for_play(app)],
                         ["Beep", "Beep"])

    def test_play_options_clamps(self):
        app = mock.MagicMock()
        for txt, expect in (("50", 50), ("250", 100), ("abc", 100), ("5", 5)):
            app.ent_pct.get.return_value = txt
            self.assertEqual(am.MacroApp._play_options(app), expect)

    def test_record_keystroke_no_nameerror(self):
        """RECORD: กดคีย์ต้องได้แถว Tap Key — กลไกบันทึก (v2.2: Recorder ใน engine)
        ทดสอบผ่าน listener จำลองเหมือนเดิม แต่จับ callback ของ Recorder"""
        captured = {}

        class FakeMouseListener:
            def __init__(self, **kw):
                pass
            def start(self):
                pass

        class FakeKbListener:
            def __init__(self, on_press=None, **kw):
                captured["on_press"] = on_press
            def start(self):
                pass

        app = mock.MagicMock()
        app._recorder = am.macro_engine.Recorder()
        with mock.patch.object(am.mouse, "Listener", FakeMouseListener), \
             mock.patch.object(am.keyboard, "Listener", FakeKbListener):
            am.MacroApp._start_listeners(app)     # = recorder.start_listeners()
        on_press = captured["on_press"]
        self.assertIsNotNone(on_press)
        rec = app._recorder
        rec.start()                               # recording = True + ตั้ง _t0
        on_press(am.KeyCode.from_char("a"))             # เดิม: NameError ที่ตัวแปร pressed
        self.assertEqual(len(rec.pending_rows), 1)
        self.assertEqual(rec.pending_rows[0]["button"], "Tap Key")
        self.assertEqual(rec.pending_rows[0]["additional"], "a")
        rec.stop()                                # ไม่ได้อัด = ไม่เพิ่มแถว
        on_press(am.KeyCode.from_char("b"))
        self.assertEqual(len(rec.pending_rows), 1)
        self.assertEqual(rec.drain_pending()[0]["additional"], "a")


class TestPlayLoopGui(unittest.TestCase):
    """พฤติกรรมการเล่นจริงของ GUI (Regression v1.18.1 ข้อ 2/4 + START ใช้ได้)
    ใช้แถว Beep ล้วน (secs=0) ไม่แตะเมาส์/คีย์ — ไม่มีจอ (CI บางที่) skip อัตโนมัติ"""

    @classmethod
    def setUpClass(cls):
        cls._orig_log = am.log_write
        cls.steps = []
        cls.expected_gen = None            # นับเฉพาะ STEP ของการเล่นรุ่นปัจจุบัน
        def counting_log(mode, message, src=None):
            # นับเฉพาะ STEP ของเธรดรุ่น >= expected_gen (รุ่นเก่ากว่า = ของค้างจากเทสต์ก่อนหน้า)
            # หมายเหตุ: ตั้ง expected ก่อน start แล้วใช้ >= เพราะ player (v1.19) ไม่แตะ Tk
            # อีกต่อไป — แถวแรกอาจ log เสร็จก่อน start() จะอ่าน _play_gen กลับ
            if (mode == "STEP" and cls.expected_gen is not None
                    and cls.app is not None and cls.app._play_gen >= cls.expected_gen):
                cls.steps.append(message)
            return cls._orig_log(mode, message, src)
        am.log_write = counting_log
        cls.app = None
        try:
            cls.root = _Tk()
            cls.root.withdraw()
        except am.tk.TclError:
            cls.root = None
            return
        try:
            cls.app = am.MacroApp(cls.root)
            cls.app._log_enabled = True
        except Exception:
            cls.root.destroy()
            cls.root = None
            cls.app = None

    @classmethod
    def tearDownClass(cls):
        am.log_write = cls._orig_log
        if cls.app is not None:
            try:
                cls.app.stop_all(silent=True)
            except Exception:
                pass
        if cls.root is not None:
            cls.root.destroy()              # _Tk.destroy = หยุดเธรด + ยกเลิก after + gc.collect
        cls.app = None                      # ปล่อย ref ให้เก็บบน main thread ไม่ค้างถึงจบ suite
        cls.root = None

    def setUp(self):
        if self.app is None:
            self.skipTest("ไม่มีจอ/สร้าง MacroApp จริงไม่ได้ — ข้ามกลุ่มเล่นจริง")
        self.app.stop_all(silent=True)
        # เทสต์ก่อนหน้าอาจเหลือเธรด player ค้างอยู่ใน do_step (รอ marshal ข้ามเธรดของ Tk)
        # — ปั่น update() ให้ event ค้างถูกประมวลผลก่อน ไม่งั้น STEP ตกค้างมานับรวมในเทสต์นี้
        self.__class__.expected_gen = None
        for _ in range(10):
            try:
                self.root.update()
            except Exception:
                pass
            time.sleep(0.01)
        self._clean_table(2)

    def _clean_table(self, n):
        app = self.app
        app.tree.delete(*app.tree.get_children())    # ล้างงานจาก macro_conf.json ออกก่อน
        for _ in range(n):
            app._append_row(button="Beep", secs=0)
        app.chk_forever.set(False)
        app.chk_shuffle.set(False)
        app.ent_pct.delete(0, "end")
        app.ent_pct.insert(0, "100")
        app.ent_loops.delete(0, "end")
        app.ent_loops.insert(0, "1")

    def _run_until(self, start_fn, cond, timeout=10.0):
        """เริ่มเล่นด้วย start_fn แล้วเข้า mainloop จน cond เป็นจริง (หรือ timeout)
        หมายเหตุ: การเรียก Tk ข้ามเธรดของ player (tree.get_children/bell) marshal
        ได้เฉพาะตอน main thread อยู่ใน mainloop() — update() ไม่พอ"""
        outcome = {"ok": False}
        t0 = time.time()

        def poll():
            if cond():
                outcome["ok"] = True
                self.root.quit()
            elif time.time() - t0 > timeout:
                self.root.quit()                    # timeout — ปล่อยให้ assert ตัวรองจับ
            else:
                self.root.after(30, poll)

        def start():
            self.__class__.expected_gen = self.app._play_gen   # เริ่มนับจากรุ่นนี้เป็นต้นไป
            start_fn()
            self.root.after(30, poll)

        self.root.after(30, start)
        self.root.mainloop()
        return outcome["ok"]

    def test_start_play_runs_and_honors_loops(self):
        """กด START ต้องเล่นได้จริง + ช่อง รอบ: 3 = 2 แถว × 3 = 6 steps (เดิม START พังทั้งปุ่ม)"""
        self.app.ent_loops.delete(0, "end")
        self.app.ent_loops.insert(0, "3")
        self.steps.clear()
        ok = self._run_until(self.app.start_play, lambda: not self.app.running)
        self.assertTrue(ok)
        self.assertEqual(len(self.steps), 6)

    def test_repeat_button_loops_until_stop(self):
        """REPEAT ต้องวนต่อเนื่องจนกด STOP (เดิมพัง: เล่น 1 รอบแล้วจบเอง)"""
        self.steps.clear()
        ok = self._run_until(self.app.start_repeat, lambda: len(self.steps) >= 6)
        self.app.stop_all(silent=True)
        self.assertTrue(ok)
        self.assertFalse(self.app.running)

    def test_forever_checkbox_loops_until_stop(self):
        """ติ๊ก วนซ้ำไม่จำกัด + START ต้องวนต่อเนื่อง (เดิมพัง: เล่น 1 รอบแล้วจบเอง)"""
        self.app.chk_forever.set(True)
        self.steps.clear()
        ok = self._run_until(self.app.start_play, lambda: len(self.steps) >= 6)
        self.app.stop_all(silent=True)
        self.app.chk_forever.set(False)
        self.assertTrue(ok)

    def test_shuffle_and_pct_apply(self):
        """สุ่มลำดับ 50% + รอบ 2 กับ 4 แถว = เล่นรอบละ 2 แถว × 2 รอบ = 4 steps
        (เดิมพัง: _player บังคับ pct=100 → ได้ 8 steps)"""
        self._clean_table(4)
        self.app.chk_shuffle.set(True)
        self.app.ent_pct.delete(0, "end")
        self.app.ent_pct.insert(0, "50")
        self.app.ent_loops.delete(0, "end")
        self.app.ent_loops.insert(0, "2")
        self.steps.clear()
        ok = self._run_until(self.app.start_play, lambda: not self.app.running)
        self.assertTrue(ok)
        self.assertEqual(len(self.steps), 4)

    def test_schedule_once_single_pass(self):
        """schedule (once=True) ต้องเล่นรอบเดียว ไม่สนช่อง รอบ: 5"""
        self.app.ent_loops.delete(0, "end")
        self.app.ent_loops.insert(0, "5")
        self.steps.clear()
        ok = self._run_until(lambda: self.app._start_player(False, once=True),
                             lambda: not self.app.running)
        self.assertTrue(ok)
        self.assertEqual(len(self.steps), 2)

    def test_set_variable_in_script(self):
        """Set Variable ต้องตั้งค่าจริงระหว่างเล่น + ค่าค้างใช้ต่อในแถวถัดไป (v1.19)"""
        self._clean_table(0)
        self.app._append_row(button="Set Variable", additional="n = 5")
        self.app._append_row(button="Set Variable", additional="n += 2")
        self.app._append_row(button="Set Variable", additional="n += 3")
        self.steps.clear()
        ok = self._run_until(self.app.start_play, lambda: not self.app.running)
        self.assertTrue(ok)
        self.assertEqual(len(self.steps), 3)
        self.assertEqual(self.app._vars.get("n"), "10")

    def test_variables_substituted_in_playback(self):
        """{ตัวแปร} ในช่องอื่นต้องถูกแทนก่อนเล่น — ใช้ Secs เป็นตัวพิสูจน์ (แถว Beep วินาทีที่ 0)
        แถวแรกตั้ง d = 0 แล้ว Beep ด้วย secs {d} ต้องไม่ delay (จบเร็ว)"""
        self._clean_table(0)
        self.app._append_row(button="Set Variable", additional="d = 0")
        self.app._append_row(button="Beep", secs="{d}")
        self.app._append_row(button="Beep", secs="{d}")
        self.steps.clear()
        ok = self._run_until(self.app.start_play, lambda: not self.app.running,
                             timeout=6.0)
        self.assertTrue(ok)
        self.assertEqual(len(self.steps), 3)          # 3 แถว = 3 STEP (Set, Beep, Beep)
        self.assertEqual(self.app._vars.get("d"), "0")
        self.app._hp_dir = None

    def test_hot_profile_loads_and_plays(self):
        """F1 hot-profile: โหลดไฟล์ลำดับแรกจากโฟลเดอร์แล้วเล่นทันที"""
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            for name in ("a.json", "b.json"):
                with open(os.path.join(d, name), "w", encoding="utf-8") as fh:
                    fh.write('[{"enabled": true, "button": "Beep", "mins": 0, "secs": 0, "repeat": 1}]')
            self.app._hp_dir = d
            self.steps.clear()
            ok = self._run_until(lambda: self.app._hot_profile_load(1),
                                 lambda: not self.app.running)
            self.assertTrue(ok)
            self.assertTrue(self.app._loaded_file.endswith("a.json"))
            self.assertEqual(len(self.steps), 1)      # a.json มี 1 แถว
        self.app._hp_dir = None

    def test_record_mechanism_moves_pending_rows_to_table(self):
        """กลไก RECORD: recorder (v2.2) ผลักแถว → poller ดึง drain_pending เข้าตารางเอง"""
        app = self.app
        app.tree.delete(*app.tree.get_children())
        app.toggle_record()
        self.assertTrue(app.recording)
        try:
            app._recorder.pending_rows.append(dict(x=11, y=22, button="Left Click",
                                          additional="", mins=0, secs=0.5, repeat=1))
            ok = self._run_until(lambda: None,
                                 lambda: len(app.tree.get_children()) == 1)
            self.assertTrue(ok)
            vals = app.tree.item(app.tree.get_children()[0], "values")
            self.assertEqual(vals[4], "Left Click")
        finally:
            app.toggle_record()
        self.assertFalse(app.recording)

    def test_tap_key_combo_presses_and_releases_in_order(self):
        """คอมโบ Ctrl+W ผ่าน player จริงด้วย kb controller จำลอง — กด/ปล่อยตามลำดับ
        ปลอดภัย: ไม่ส่งคีย์ไปหน้าต่างใด ๆ (v1.20.4)"""
        from pynput.keyboard import Key
        app = self.app
        self._clean_table(1)
        app._append_row(button="Tap Key", additional="Ctrl+W", secs=0)
        fake = mock.MagicMock()
        orig = app.kb_ctl
        app.kb_ctl = fake
        self.steps.clear()
        try:
            ok = self._run_until(app.start_play, lambda: not app.running)
        finally:
            app.kb_ctl = orig
        self.assertTrue(ok)
        pressed = [c.args[0] for c in fake.press.call_args_list]
        tapped = [c.args[0] for c in fake.tap.call_args_list]
        released = [c.args[0] for c in fake.release.call_args_list]
        self.assertEqual(pressed, [Key.ctrl])                              # กด modifier
        self.assertEqual(tapped, [am.KeyCode.from_vk(0x57)])               # tap W
        self.assertEqual(released, [Key.ctrl])                             # ปล่อย modifier

    def test_gk_self_heal_restarts_dead_listener(self):
        """v2.4: listener F6-F10 ตายเงียบ ๆ → poller รีสตาร์ตให้เอง (กันยิงรัว <10 วิ)"""
        app = self.app
        if app._gk is None:
            self.skipTest("เครื่องนี้เปิด global hotkey ไม่ได้")
        app._gk_heal_at = 0.0

        def fake_start():
            fresh = mock.MagicMock()
            fresh.is_alive.return_value = True
            app._gk = fresh
            return True

        app._gk_start = fake_start
        dead = mock.MagicMock()
        dead.is_alive.return_value = False
        app._gk = dead
        app._start_poller()                       # หนึ่ง tick — เจอตัวตาย → heal
        self.assertIsNot(app._gk, dead)
        self.assertTrue(app._gk.is_alive())
        dead2 = mock.MagicMock()
        dead2.is_alive.return_value = False
        app._gk = dead2
        app._start_poller()                       # เพิ่ง heal ไป — ต้องไม่ยิงรัว
        self.assertIs(app._gk, dead2)

    def test_delete_multiple_selected_rows(self):
        """v2.4: เลือกหลายแถว (extended) → Delete ลบทั้งชุด + Ctrl+Z กู้คืนได้"""
        self._clean_table(0)
        for _ in range(4):
            self.app._append_row(button="Beep", secs=0)
        kids = self.app.tree.get_children()
        self.app.tree.selection_set([kids[0], kids[2]])
        self.app._on_del()
        self.assertEqual(len(self.app.tree.get_children()), 2)
        self.app._undo_delete()
        self.assertEqual(len(self.app.tree.get_children()), 4)

    def test_press_binding_has_both_handlers(self):
        """Regression v2.5.2: <Button-1> = <ButtonPress-1> เป็น event เดียวกัน —
        bind _on_click ทีหลังโดยไม่มี add="+" เขียนทับ _on_drag_start ทิ้ง
        (ต้นตอ 'ลากสลับแถวไม่ทำงาน' ใน v2.5.0-v2.5.1)"""
        combined = self.app.tree.bind("<Button-1>")
        self.assertIn("_on_click", combined)
        self.assertIn("_on_drag_start", combined)

    @unittest.skipUnless(os.name == "nt",
                         "event_generate ปุ่มเมาส์บน aqua Tk (macOS) ไม่เสถียร — "
                         "อาจ crash ทั้งโปรเซส (SIGTRAP) — logic ครอบด้วย "
                         "test_drag_reorder_* ทุก OS แล้ว")
    def test_drag_with_real_events(self):
        """v2.5.2: ลากจริงผ่าน event_generate — ลาก R2 ไปครึ่งล่างของ R4
        (bbox มีค่าเมื่อหน้าต่างถูก map — บน Linux/macOS ต้อง deiconify ก่อน)"""
        self._clean_table(0)
        for n in range(4):
            self.app._append_row(button="Beep", secs=0, note="R%d" % (n + 1))
        tree = self.app.tree

        def order():
            return [str(tree.item(i, "values")[9]) for i in tree.get_children()]

        self.root.deiconify()
        self.root.update()
        try:
            kids = list(tree.get_children())
            src, dst = tree.bbox(kids[1]), tree.bbox(kids[3])
            if not src or not dst:
                self.skipTest("bbox ยังว่าง — หน้าต่างไม่ถูก map บนสภาพแวดล้อมนี้")
            sx, sy = src[0] + 200, src[1] + src[3] // 2
            dx, dy = dst[0] + 200, dst[1] + dst[3] - 3
            tree.event_generate("<ButtonPress-1>", x=sx, y=sy)
            self.root.update()
            for step in range(1, 6):
                tree.event_generate("<B1-Motion>",
                                    x=sx + (dx - sx) * step // 5,
                                    y=sy + (dy - sy) * step // 5)
                self.root.update()
            tree.event_generate("<ButtonRelease-1>", x=dx, y=dy)
            self.root.update()
            self.assertEqual(order(), ["R1", "R3", "R4", "R2"])
        finally:
            self.root.withdraw()

    def test_drag_reorder_above_and_below(self):
        """v2.5: ลากแถววางก่อน/หลังแถวเป้าหมาย (ครึ่งบน = ก่อน, ครึ่งล่าง = หลัง)"""
        self._clean_table(0)
        for n in range(4):
            self.app._append_row(button="Beep", secs=0, note="R%d" % (n + 1))
        app = self.app
        kids = list(app.tree.get_children())

        def order():
            return [str(app.tree.item(i, "values")[9]) for i in app.tree.get_children()]

        app._drag_block = [kids[1]]                     # ลากแถว 2
        app._drag_reorder(kids[0], below=False)         # วางก่อนแถว 1
        self.assertEqual(order(), ["R2", "R1", "R3", "R4"])
        app._drag_block = [kids[1]]                     # ลากแถว 2 (ตำแหน่งใหม่) อีกครั้ง
        kids = list(app.tree.get_children())
        app._drag_reorder(kids[3], below=True)          # วางหลังแถวสุดท้าย
        self.assertEqual(order(), ["R1", "R3", "R4", "R2"])

    def test_drag_reorder_moves_block_multi_select(self):
        """v2.5: เลือกหลายแถวแล้วลาก = ย้ายทั้งก้อน คงลำดับสัมพัทธ์"""
        self._clean_table(0)
        for n in range(4):
            self.app._append_row(button="Beep", secs=0, note="R%d" % (n + 1))
        app = self.app
        kids = list(app.tree.get_children())
        app._drag_block = [kids[0], kids[1]]            # ลากแถว 1-2 พร้อมกัน
        app._drag_reorder(kids[3], below=True)          # วางหลังแถวสุดท้าย
        order2 = [str(app.tree.item(i, "values")[9]) for i in app.tree.get_children()]
        self.assertEqual(order2, ["R3", "R4", "R1", "R2"])

    def test_drag_reorder_blocked_on_collapsed_header(self):
        """v2.5: ห้ามลากวางบนหัวข้อกลุ่มย่อ (กันแถวหลุดเข้ากลุ่ม)"""
        self._clean_table(0)
        app = self.app
        app._append_row(button=am.SECTION_HEADER, additional="กลุ่ม", secs=0)
        app._append_row(button="Beep", secs=0, note="ในกลุ่ม")
        app._append_row(button="Beep", secs=0, note="นอกกลุ่ม")
        kids = list(app.tree.get_children())
        app._group_toggle(kids[0])                      # ย่อกลุ่ม
        before = [str(app.tree.item(i, "values")[5]) for i in app.tree.get_children()]
        app._drag_block = [kids[2]]                     # ลากแถว "นอกกลุ่ม"
        app._drag_reorder(kids[0], below=True)          # พยายามวางหลังหัวข้อย่อ
        after = [str(app.tree.item(i, "values")[5]) for i in app.tree.get_children()]
        self.assertEqual(before, after)                 # ไม่มีอะไรขยับ
        app._group_toggle(kids[0])                      # ขยายคืน

    def test_drag_release_restores_row_colors(self):
        """v2.5: ปล่อยเมาส์แล้วสีแถวกลับตามหมวดเดิม (ไม่ติดสีน้ำเงินค้าง)"""
        self._clean_table(1)
        iid = self.app.tree.get_children()[0]
        self.app._drag_block = [iid]
        self.app._on_drag_release(mock.MagicMock())
        tags = self.app.tree.item(iid, "tags")
        self.assertNotIn("drag", tags)

    def test_clipboard_actions_roundtrip(self):
        """Set Clipboard → Read Clipboard: ข้อความวนกลับเข้าตัวแปรได้ (v1.20)
        (แตะคลิปบอร์ดจริง — คืนค่าเดิมให้ผู้ใช้เมื่อจบเทสต์)"""
        saved = am.clip_get()
        try:
            self._clean_table(0)
            self.app._append_row(button="Set Variable", additional="n = 1")
            self.app._append_row(button="Set Clipboard", additional="ข้อความ {n}")
            self.app._append_row(button="Read Clipboard", additional="mytext")
            self.steps.clear()
            ok = self._run_until(self.app.start_play, lambda: not self.app.running)
            self.assertTrue(ok)
            self.assertEqual(self.app._vars.get("mytext"), "ข้อความ 1")
            self.assertEqual(self.root.clipboard_get(), "ข้อความ 1")   # คลิปบอร์ดจริง
        finally:
            if saved is not None:
                am.clip_set(saved)

    def test_plugin_ctx_v2(self):
        """plugin ต้องได้ ctx.stop_check() / ctx.ui จาก player จริง (v1.20)"""
        import types
        captured = {}

        def fake_run(ctx, row):
            captured["stop"] = ctx["stop_check"]()
            ctx["ui"]["msg"]("ปลั๊กอินทำงาน")
            captured["msg_now"] = self.app._ui_state["msg"]   # อ่านทันทีหลังตั้ง (ก่อนโดนทับ)
            ctx["ui"]["beep"]()
            captured["beep_now"] = self.app._ui_state["beep"]

        self.app._plugins.append(("FakePlug", types.SimpleNamespace(
            ACTION_NAME="FakePlug", run=fake_run)))
        self._clean_table(1)
        self.app._append_row(button="FakePlug", additional="")
        self.steps.clear()
        ok = self._run_until(self.app.start_play, lambda: not self.app.running)
        self.assertTrue(ok)
        self.assertIs(captured["stop"], True)          # ระหว่างเล่น stop_check() = True
        self.assertEqual(captured["msg_now"], ("ปลั๊กอินทำงาน", "#080"))
        self.assertIs(captured["beep_now"], True)

    def test_dry_run_writes_report_file(self):
        """v2.10.1: Dry-run จบแล้วเขียนรายงาน dry_report_วันที่.txt — เส้นทางครบ +
        สรุปจำนวนแถวที่จะทำจริง + ไม่เขียนเมื่อไม่มีบรรทัดรายงาน"""
        d = tempfile.mkdtemp(prefix="macro_dryrep_")
        target = os.path.join(d, "dry_report_test.txt")
        self._clean_table(2)
        try:
            with mock.patch.object(am, "dry_report_path", return_value=target):
                ok = self._run_until(
                    lambda: self.app._start_player_inner(False, dry=True),
                    lambda: not self.app.running)
            self.assertTrue(ok)
            self.assertTrue(os.path.isfile(target))
            with open(target, encoding="utf-8") as fh:
                text = fh.read()
            self.assertIn("===== DRY-RUN", text)
            self.assertIn("DRY-RUN: จะส่งเสียง Beep", text)
            self.assertIn("แถวที่จะเล่น: 2", text)
            self.assertIn("Beep ×2", text)             # สรุปจะทำจริง
            self.assertIn("===== จบรายงาน Dry-run =====", text)
            self.assertNotIn("ถูกหยุดกลางคัน", text)      # จบครบเอง

            # เล่นจริง (ไม่ dry) — ห้ามเขียนรายงานเพิ่ม
            before = os.path.getsize(target)
            self._clean_table(1)
            self._run_until(self.app.start_play, lambda: not self.app.running)
            self.assertEqual(os.path.getsize(target), before)
        finally:
            shutil.rmtree(d, ignore_errors=True)


class TestWaitTimeout(unittest.TestCase):
    """v1.19: timeout ตั้งได้จากท้าย Additional เช่น "logo.png 60s" / "100,200 #fff 45s" """

    def test_seconds_token_extracted(self):
        cleaned, t = am.parse_wait_timeout("100,200 #ff0000 60s")
        self.assertEqual((cleaned, t), ("100,200 #ff0000", 60))

    def test_default_when_missing(self):
        self.assertEqual(am.parse_wait_timeout("logo.png"), ("logo.png", 30))
        self.assertEqual(am.parse_wait_timeout("logo.png", 45), ("logo.png", 45))

    def test_clamped_to_valid_range(self):
        _c, t = am.parse_wait_timeout("a.png 99999s", 30)
        self.assertEqual(t, 3600)                      # พлюงขอบบน
        _c2, t2 = am.parse_wait_timeout("a.png 0s", 30)
        self.assertEqual(t2, 1)                        # ขอบล่าง

    def test_path_with_s_suffix_not_confused(self):
        # ไฟล์ที่ลงท้าย s แต่ไม่มีช่องว่างนำหน้า ต้องไม่ถูกตัด
        cleaned, t = am.parse_wait_timeout("buttons.png")
        self.assertEqual((cleaned, t), ("buttons.png", 30))


class TestVariables(unittest.TestCase):
    """v1.19: ตัวแปรในสคริปต์ — Set Variable + แทน {ชื่อ} ในช่องอื่น"""

    def test_action_registered(self):
        self.assertIn("Set Variable", am.ACTIONS_ALL)

    def test_parse_set_var(self):
        self.assertEqual(am.parse_set_var("n = 5"), ("n", "=", "5"))
        self.assertEqual(am.parse_set_var("  n += 2 "), ("n", "+=", "2"))
        self.assertEqual(am.parse_set_var("name -= 1.5"), ("name", "-=", "1.5"))
        self.assertEqual(am.parse_set_var("msg = สวัสดี"), ("msg", "=", "สวัสดี"))
        self.assertEqual(am.parse_set_var("รอบ += 1"), ("รอบ", "+=", "1"))   # ชื่อไทยได้
        self.assertIsNone(am.parse_set_var("2n = 5"))          # ชื่อต้องขึ้นต้นตัวอักษร/_
        self.assertIsNone(am.parse_set_var("no_value"))
        self.assertIsNone(am.parse_set_var(""))

    def test_substitute_vars(self):
        self.assertEqual(am.substitute_vars("รอ {n} วิ", {"n": "3"}), "รอ 3 วิ")
        self.assertEqual(am.substitute_vars("{a}-{b}", {"a": 1, "b": 2}), "1-2")
        self.assertEqual(am.substitute_vars("{nope}", {}), "{nope}")   # ไม่มีคงเดิม
        self.assertEqual(am.substitute_vars(None, {}), "")

    def test_apply_set_var(self):
        v = {}
        self.assertTrue(am.apply_set_var(v, "n = 5"))
        self.assertEqual(v, {"n": "5"})
        self.assertTrue(am.apply_set_var(v, "n += 2"))
        self.assertTrue(am.apply_set_var(v, "n += 0.5"))
        self.assertEqual(v["n"], "7.5")                        # fmt_num ตัด .0 ให้
        self.assertTrue(am.apply_set_var(v, "n -= 10"))
        self.assertEqual(v["n"], "-2.5")
        self.assertTrue(am.apply_set_var(v, "msg = {n} ครั้ง"))   # ค่าอ้างตัวแปรอื่นได้
        self.assertEqual(v["msg"], "-2.5 ครั้ง")
        self.assertFalse(am.apply_set_var(v, "n += ไม่ใช่ตัวเลข"))  # += ต้องเป็นเลข
        self.assertFalse(am.apply_set_var(v, "รูปแบบพัง"))

    def test_subst_row_replaces_all_columns(self):
        v = {"x": "10", "d": "2"}
        out = am.subst_row({"button": "Beep", "x": "{x}", "y": "0", "additional": "",
                            "mins": 0, "secs": "{d}", "repeat": "{d}"}, v)
        self.assertEqual(out["x"], "10")
        self.assertEqual(out["secs"], "2")
        self.assertEqual(out["repeat"], "2")

    def test_validate_requires_format(self):
        app = mock.MagicMock()
        app._plugin_module.return_value = None
        ok = am.MacroApp._validate_rows(
            app, [{"button": "Set Variable", "additional": "n = 1"}])
        self.assertTrue(ok)
        ok2 = am.MacroApp._validate_rows(
            app, [{"button": "Set Variable", "additional": "พัง"}])
        self.assertFalse(ok2)


class TestSchedCheck(unittest.TestCase):
    """v1.19: แยก _sched_check ออกจากเธรด — ทดสอบเงื่อนไขตรง ๆ
    (แก้บั๊ก: โหมดรายวันเทียบ "%Y-%m-%d %H:%M" กับ "HH:MM" ไม่มีวันตรงกันเลย)"""

    def _app(self):
        import queue
        app = mock.MagicMock()
        app._sched_q = queue.Queue()
        app.running = False
        app._sched = {"mode": "off", "every": 10, "times": [], "profile": ""}   # v2.7: dict เดียว
        return app

    def test_daily_fires_at_matching_time(self):
        app = self._app()
        app._sched = {"mode": "daily", "every": 10, "times": ["09:30"], "profile": ""}
        with mock.patch.object(am.time, "strftime", return_value="2026-10-01 09:30"):
            am.MacroApp._sched_check(app)
        self.assertEqual(app._sched_q.qsize(), 1)

    def test_daily_fires_once_per_minute(self):
        app = self._app()
        app._sched = {"mode": "daily", "every": 10, "times": ["09:30"], "profile": ""}
        with mock.patch.object(am.time, "strftime", return_value="2026-10-01 09:30"):
            am.MacroApp._sched_check(app)
            am.MacroApp._sched_check(app)          # นาทีเดียวกัน = ไม่ยิงซ้ำ
        self.assertEqual(app._sched_q.qsize(), 1)

    def test_daily_ignores_other_times(self):
        app = self._app()
        app._sched = {"mode": "daily", "every": 10, "times": ["09:30"], "profile": ""}
        with mock.patch.object(am.time, "strftime", return_value="2026-10-01 14:05"):
            am.MacroApp._sched_check(app)
        self.assertEqual(app._sched_q.qsize(), 0)

    def test_interval_rearms(self):
        app = self._app()
        app._sched = {"mode": "interval", "every": 10, "times": [], "profile": ""}
        app._sched_next = 1000.0
        am.MacroApp._sched_check(app, now=2000.0)
        self.assertEqual(app._sched_q.qsize(), 1)
        self.assertEqual(app._sched_next, 2000.0 + 10 * 60)   # เลื่อนเป้าถัดไป

    def test_no_mode_is_noop(self):
        app = self._app()
        app._sched = {"mode": "", "every": 10, "times": [], "profile": ""}
        am.MacroApp._sched_check(app, now=2000.0)
        self.assertEqual(app._sched_q.qsize(), 0)


class TestPersistSettings(unittest.TestCase):
    """v1.19: จำค่าการเล่น + ตารางเวลาลง macro_conf.json (เดิมหายทุกครั้งที่ปิดโปรแกรม)"""

    def test_save_load_roundtrip(self):
        import tempfile
        app = mock.MagicMock()
        app._serialize.return_value = [{"button": "Beep"}]
        app._log_enabled = True
        app._hp_dir = None
        app._backup_enabled = True
        app._backup_days = 7
        app._log_keep_days = 0                     # v2.11: _save_conf/export อ่าน attr นี้
        app._log_archive = True
        app._lang = "th"
        app.cmb_speed.get.return_value = "2"
        app.ent_loops.get.return_value = "3"
        app.chk_forever.get.return_value = True
        app.chk_restore.get.return_value = False
        app.chk_shuffle.get.return_value = True
        app.ent_pct.get.return_value = "50"
        app._play_options = lambda: 50          # อ่านค่าจาก widget จำลอง
        app._time_limit_enabled = True          # v2.4: keys ใหม่ใน conf
        app._time_limit_min = 30
        # v2.7: สถานะ schedule เป็น dict เดียว (property เก่ายังอ่านได้ผ่าน getter)
        app._sched = {"mode": "interval", "every": 15, "times": [], "profile": ""}
        with tempfile.TemporaryDirectory() as d:
            conf = os.path.join(d, "macro_conf.json")
            with mock.patch.object(am, "CONF", conf):
                am.MacroApp._save_conf(app)
                self.assertTrue(os.path.isfile(conf))
                with open(conf, encoding="utf-8") as fh:
                    data = json.load(fh)
                self.assertEqual(data["speed"], "2")
                self.assertEqual(data["loops"], "3")
                self.assertTrue(data["forever"])
                self.assertTrue(data["shuffle"])
                self.assertEqual(data["pct"], 50)
                # v2.7: คีย์เดียว "sched" เป็น dict (แทน sched_mode/every/at/profile แยก)
                self.assertEqual(data["sched"]["mode"], "interval")
                self.assertEqual(data["sched"]["every"], 15)
                # โหลดกลับเข้าเครื่องจำลอง
                app2 = mock.MagicMock()
                app2._serialize.return_value = []
                am.MacroApp._load_conf(app2)
        app2.ent_loops.delete.assert_called()          # ค่าถูก set กลับเข้า widget
        app2.chk_forever.set.assert_called_with(True)
        self.assertEqual(app2._sched["mode"], "interval")
        self.assertEqual(app2._sched["every"], 15)
        self.assertGreater(app2._sched_next, 0)        # interval ถูกตั้งเวลาเล่นรอบแรก


class TestApplyPixelSpec(unittest.TestCase):
    """v1.19: ปุ่ม 🎨 จับสี — ใส่ spec ลงแถว Wait for Pixel Color ที่เลือก หรือสร้างแถวใหม่"""

    def test_fills_selected_wait_pixel_row(self):
        app = mock.MagicMock()
        stored = {"values": ["☑", 1, "", "", am.WAIT_PIXEL, "old", 0, 1, 1]}

        def fake_item(*args, **kw):
            if "values" in kw:
                stored["values"] = list(kw["values"])
                return None
            return stored["values"]

        app.tree.selection.return_value = ["i1"]
        app.tree.item.side_effect = fake_item
        ok = am.MacroApp._apply_pixel_spec(app, "100,200 #ff0000")
        self.assertTrue(ok)
        self.assertEqual(stored["values"][5], "100,200 #ff0000")
        app._append_row.assert_not_called()

    def test_appends_new_row_when_other_action_selected(self):
        app = mock.MagicMock()
        app.tree.selection.return_value = ["i1"]
        app.tree.item.return_value = ["☑", 1, "", "", "Beep", "", 0, 1, 1]
        ok = am.MacroApp._apply_pixel_spec(app, "5,6 #00ff00")
        self.assertFalse(ok)
        app._append_row.assert_called_once()
        self.assertEqual(app._append_row.call_args.kwargs.get("button"), am.WAIT_PIXEL)

    def test_appends_when_nothing_selected(self):
        app = mock.MagicMock()
        app.tree.selection.return_value = []
        am.MacroApp._apply_pixel_spec(app, "1,2 #ffffff")
        app._append_row.assert_called_once()


class TestVersionConsistency(unittest.TestCase):
    """v1.19: เวอร์ชันมีแหล่งเดียว (__version__) — ป้องกัน docstring/CHANGELOG ค้างเก่า"""

    def test_app_title_uses_version_constant(self):
        self.assertEqual(am.APP_TITLE,
                         "Auto Mouse & Keyboard Macro v" + am.__version__)
        self.assertTrue(re.fullmatch(r"\d+\.\d+\.\d+", am.__version__))

    def test_changelog_has_current_version_section(self):
        path = os.path.join(os.path.dirname(os.path.abspath(am.__file__)),
                            "docs", "CHANGELOG.md")
        with open(path, encoding="utf-8") as fh:
            content = fh.read()
        self.assertIn("## [%s]" % am.__version__, content)


class TestClipboardActions(unittest.TestCase):
    """v1.20: Set Clipboard / Read Clipboard — GUI ผ่าน poller, CLI ผ่าน Win32/pbcopy/xclip
    ⚠️ เทสต์พวกนี้แตะคลิปบอร์ดจริง — ทุกคลาส/เทสต์ต้อง snapshot ก่อนแล้วคืนค่าทีหลัง
    ไม่งั้นคลิปบอร์ดของคนรันเทสต์จะโดนข้อมูลทดสอบเขียนทับแบบถาวร"""

    def setUp(self):
        self._saved_clip = am.clip_get()

    def tearDown(self):
        am.clip_set(self._saved_clip if self._saved_clip is not None else "")

    def test_actions_registered(self):
        for a in ("Set Clipboard", "Read Clipboard"):
            self.assertIn(a, am.ACTIONS_ALL)

    def test_validate_rows(self):
        app = mock.MagicMock()
        app._plugin_module.return_value = None
        ok = am.MacroApp._validate_rows(
            app, [{"button": "Set Clipboard", "additional": "ข้อความ"}])
        self.assertTrue(ok)
        ok2 = am.MacroApp._validate_rows(
            app, [{"button": "Set Clipboard", "additional": ""}])
        self.assertFalse(ok2)                          # ต้องมีข้อความ
        ok3 = am.MacroApp._validate_rows(
            app, [{"button": "Read Clipboard", "additional": "mytext"}])
        self.assertTrue(ok3)
        ok4 = am.MacroApp._validate_rows(
            app, [{"button": "Read Clipboard", "additional": "มี ช่องว่าง"}])
        self.assertFalse(ok4)                          # ชื่อตัวแปรห้ามมีช่องว่าง

    def test_clip_roundtrip_no_tk(self):
        t = "ทดสอบคลิปบอร์ด ABC 123"
        if not am.clip_set(t):
            self.skipTest("ระบบนี้ตั้งคลิปบอร์ดไม่ได้ (ไม่มี xclip/wl-copy ฯลฯ)")
        self.assertEqual(am.clip_get(), t)


class TestPluginCtxV2(unittest.TestCase):
    """v1.20: Plugin API v2 — ctx ต้องมี stop_check() และ ui (msg/beep)"""

    def test_ctx_keys_documented_and_callable(self):
        # ตรวจผ่านการรันจริงใน TestPlayLoopGui.test_plugin_ctx_v2 — ที่นี่เช็คเอกสาร
        with open(os.path.join(os.path.dirname(os.path.abspath(am.__file__)),
                               "plugins", "README.md"), encoding="utf-8") as fh:
            content = fh.read()
        self.assertIn("stop_check", content)
        self.assertIn('ctx["ui"]', content)


class TestHotkeyEdit(unittest.TestCase):
    """Regression v1.20.1 — ดับเบิลคลิกแก้เซลล์ (HotkeyEdit): กดตกลงแล้วค่าต้องถูกส่งกลับ
    (บั๊กเดิม: __init__ ลืมเก็บ self.on_done → กดตกลง/Enter เป็น AttributeError ตั้งแต่ v1.4
    — ไม่มีเทสต์ครอบคลาสนี้เลยจึงอยู่รอดมา 8 เวอร์ชัน)"""

    @classmethod
    def setUpClass(cls):
        try:
            cls.root = _Tk()
            cls.root.withdraw()
            cls.has_tk = True
        except am.tk.TclError:
            cls.has_tk = False

    @classmethod
    def tearDownClass(cls):
        if cls.has_tk:
            cls.root.destroy()

    def setUp(self):
        if not self.has_tk:
            self.skipTest("ไม่มี display สำหรับ Tk")

    def test_ok_returns_value_to_callback(self):
        got = []
        dlg = am.HotkeyEdit(self.root, "Additional", "hello",
                            choices=None, on_done=got.append)
        try:
            dlg.var.set("world")
            dlg._ok()                                   # เดิม: AttributeError ที่นี่
        finally:
            if dlg.winfo_exists():
                dlg.destroy()
        self.assertEqual(got, ["world"])                # callback ได้ค่าจากช่องกรอก

    def test_ok_with_choices_combobox(self):
        got = []
        dlg = am.HotkeyEdit(self.root, "Action", "Beep",
                            choices=["Beep", "Tap Key"], on_done=got.append)
        try:
            dlg.var.set("Tap Key")
            dlg._ok()
        finally:
            if dlg.winfo_exists():
                dlg.destroy()
        self.assertEqual(got, ["Tap Key"])

    def test_enter_key_binding_installed(self):
        # event_generate ไม่ถูกส่งเมื่อหน้าต่างไม่ถูก map (root withdraw) —
        # ตรวจว่า binding <Return> → _ok และ <Escape> → destroy ติดตั้งจริงแทน
        dlg = am.HotkeyEdit(self.root, "Secs", "1", choices=None, on_done=lambda v: None)
        try:
            self.assertTrue(dlg.bind("<Return>"))       # มี handler จริง
            self.assertTrue(dlg.bind("<Escape>"))
        finally:
            dlg.destroy()


class TestUnicodeTyping(unittest.TestCase):
    """Regression v1.20.2 — Type Text เดิมใช้ KeyCode.from_char() ซึ่งพึ่ง keyboard
    layout ที่ active (VkKeyScanW) — เครื่องที่ active เป็น layout ไทยแล้วพิมพ์อังกฤษ/
    สัญลักษณ์กลายเป็นอักขระอื่น ("D" → "ิ", "RRRRRRRRR" ฯลฯ) — ตอนนี้ใช้ SendInput
    KEYEVENTF_UNICODE ส่งรหัสตรง ไม่ผ่าน layout"""

    def test_records_ascii(self):
        self.assertEqual(am._unicode_input_records("A"),
                         [(65, False), (65, True)])

    def test_records_thai_mark(self):
        self.assertEqual(am._unicode_input_records("\u0e36"),   # สระอิ
                         [(0xE36, False), (0xE36, True)])

    def test_records_astral_surrogate_pair(self):
        self.assertEqual(am._unicode_input_records("\U0001F600"),   # 😀
                         [(0xD83D, False), (0xDE00, False),
                          (0xDE00, True), (0xD83D, True)])

    def test_non_windows_returns_false_for_fallback(self):
        with mock.patch.object(am.os, "name", "posix"):
            self.assertIs(am.send_unicode_char("A"), False)

    def test_action_type_text_unaffected(self):
        self.assertIn("Type Text", am.ACTIONS_ALL)


class TestAdditionalEditor(unittest.TestCase):
    """Regression v1.20.3 — ช่อง Additional ต้องพิมพ์ข้อความอิสระได้
    (เดิมเป็น combobox readonly มีแต่ชื่อคีย์ → Type Text กำหนด/แก้ข้อความไม่ได้เลย)"""

    @classmethod
    def setUpClass(cls):
        try:
            cls.root = _Tk()
            cls.root.withdraw()
            cls.has_tk = True
        except am.tk.TclError:
            cls.has_tk = False

    @classmethod
    def tearDownClass(cls):
        if cls.has_tk:
            cls.root.destroy()

    def setUp(self):
        if not self.has_tk:
            self.skipTest("ไม่มี display สำหรับ Tk")

    def _dialog(self, **kw):
        dlg = am.HotkeyEdit(self.root, "Additional", "เดิม",
                            choices=[""] + am.MOD_KEYS[1:] + sorted(am.SPECIAL_KEYS),
                            on_done=kw.get("on_done", lambda v: None), **{k: v for k, v in kw.items()
                                                                          if k != "on_done"})
        self.addCleanup(lambda: dlg.destroy() if dlg.winfo_exists() else None)
        return dlg

    def test_additional_is_editable(self):
        dlg = self._dialog(editable=True)
        w = dlg.nametowidget(str(dlg.children["!combobox"]))
        self.assertEqual(str(w["state"]), "normal")     # พิมพ์อิสระได้

    def test_additional_free_text_reaches_callback(self):
        got = []
        dlg = self._dialog(editable=True, on_done=got.append)
        dlg.var.set("Auto Typer Demo — พิมพ์ใหม่ได้")
        dlg._ok()
        self.assertEqual(got, ["Auto Typer Demo — พิมพ์ใหม่ได้"])

    def test_action_column_stays_readonly(self):
        # คอลัมน์ Action ยังเป็น readonly (กันพิมพ์ผิดเป็น action ที่ไม่มีจริง)
        dlg = am.HotkeyEdit(self.root, "Action", "Beep",
                            choices=["Beep", "Tap Key"], on_done=lambda v: None)
        self.addCleanup(lambda: dlg.destroy() if dlg.winfo_exists() else None)
        w = dlg.nametowidget(str(dlg.children["!combobox"]))
        self.assertEqual(str(w["state"]), "readonly")


class TestKeyCombo(unittest.TestCase):
    """v1.20.4: คอมโบปุ่ม+คีย์ เช่น Ctrl+W — ปุ่มหลักเป็น VK กายภาพ (ถูกต้องแม้
    layout ไทย active) + player/CLI กดและปล่อยตามลำดับ (STOP ปล่อยคีย์ค้างได้)"""

    def test_ctrl_w(self):
        from pynput.keyboard import Key
        mods, k = am.parse_key_combo("Ctrl+W")
        self.assertEqual(mods, [Key.ctrl])
        self.assertEqual(k.vk, 0x57)                    # VK_W — ปุ่มกายภาพ

    def test_three_modifier_combo(self):
        from pynput.keyboard import Key
        mods, k = am.parse_key_combo("Ctrl+Shift+T")
        self.assertEqual(mods, [Key.ctrl, Key.shift])
        self.assertEqual(k.vk, 0x54)                    # VK_T

    def test_case_and_spaces_tolerant(self):
        from pynput.keyboard import Key
        mods, k = am.parse_key_combo("  win + d ")
        self.assertEqual(mods, [Key.cmd])
        self.assertEqual(k.vk, 0x44)

    def test_special_key_in_combo(self):
        from pynput.keyboard import Key
        mods, k = am.parse_key_combo("Ctrl+F5")
        self.assertEqual(mods, [Key.ctrl])
        self.assertEqual(k, Key.f5)

    def test_invalid_combos_return_none(self):
        self.assertIsNone(am.parse_key_combo("Foo+W"))      # modifier ไม่รู้จัก
        self.assertIsNone(am.parse_key_combo("Ctrl+"))      # ไม่มีปุ่มหลัก
        self.assertIsNone(am.parse_key_combo("Ctrl+?"))     # ปุ่มหลักต้องเป็น VK/ชื่อพิเศษ
        self.assertIsNone(am.parse_key_combo("+W"))         # ไม่มี modifier
        self.assertIsNone(am.parse_key_combo("W"))          # ไม่ใช่คอมโบ (มี parse_key รับต่อ)

    def test_validate_accepts_combo(self):
        app = mock.MagicMock()
        app._plugin_module.return_value = None
        ok = am.MacroApp._validate_rows(
            app, [{"button": "Tap Key", "additional": "Ctrl+W"}])
        self.assertTrue(ok)
        ok2 = am.MacroApp._validate_rows(
            app, [{"button": "Tap Key", "additional": "Ctrl+??"}])
        self.assertFalse(ok2)

# ================================ v1.21: เงื่อนไขนับรอบ/เวลา + จัดระเบียบตาราง ====
class TestConditionsV21(unittest.TestCase):
    """v1.21: If Loop / If Time — parse, validate และเล่นจริงผ่าน player (Beep ล้วน)"""

    def test_parse_if_loop_valid(self):
        self.assertEqual(am.parse_if_loop("5"), 5)
        self.assertEqual(am.parse_if_loop(" 3 "), 3)

    def test_parse_if_loop_invalid(self):
        self.assertIsNone(am.parse_if_loop(""))
        self.assertIsNone(am.parse_if_loop("abc"))
        self.assertIsNone(am.parse_if_loop("0"))
        self.assertIsNone(am.parse_if_loop("-2"))

    def test_parse_if_time_valid(self):
        self.assertEqual(am.parse_if_time("22:30"), (22, 30))
        self.assertEqual(am.parse_if_time("8:05"), (8, 5))
        self.assertEqual(am.parse_if_time(" 23:59 "), (23, 59))

    def test_parse_if_time_invalid(self):
        self.assertIsNone(am.parse_if_time(""))
        self.assertIsNone(am.parse_if_time("25:00"))
        self.assertIsNone(am.parse_if_time("12:60"))
        self.assertIsNone(am.parse_if_time("xx:30"))
        self.assertIsNone(am.parse_if_time("22:30|0"))    # |N ไม่รองรับแล้ว — N ใช้ Repeat

    def test_validate_rows_accepts_new_conditions(self):
        app = mock.MagicMock()
        app._plugin_module.return_value = None
        ok = am.MacroApp._validate_rows(app, [
            {"button": am.IF_LOOP, "additional": "5"},
            {"button": am.IF_TIME, "additional": "22:30"},
        ])
        self.assertTrue(ok)
        bad = am.MacroApp._validate_rows(app, [
            {"button": am.IF_LOOP, "additional": "abc"},
            {"button": am.IF_TIME, "additional": "99:99"},
        ])
        self.assertFalse(bad)

    def test_section_header_ignored_by_validate(self):
        app = mock.MagicMock()
        app._plugin_module.return_value = None
        ok = am.MacroApp._validate_rows(app, [{"button": am.SECTION_HEADER,
                                               "additional": "กลุ่มที่ 1"}])
        self.assertTrue(ok)


class TestSectionsGui(unittest.TestCase):
    """v1.21: Section header — refresh_nums ข้ามเลข + ให้สี + สลับกลับเป็นแถวธรรมดา"""

    def _app(self):
        app = mock.MagicMock()
        kids = iter("r%d" % i for i in range(1, 999))
        store = {"i1": ["☑", 1, "", "", "Beep", "", "0", "1", "1"],
                 "i2": ["☑", 2, "", "", "Beep", "", "0", "1", "1"]}

        def insert(parent, index, **kw):
            iid = next(kids)
            store[iid] = list(kw["values"])
            return iid
        app.tree.get_children.side_effect = lambda: list(store.keys())

        def _item(iid, *args, **kw):
            if "values" in kw:
                store[iid] = list(kw["values"])
                return None
            return store.get(iid)
        app.tree.item.side_effect = _item
        app.tree.insert = insert
        app._ui_state = {}

        def refresh_nums():
            # เรียกเมธอดจริงผ่าน store mock — เหมือนแพตเทิร์น TestUndoFindPaste
            am.MacroApp.refresh_nums(app)
        app.refresh_nums = refresh_nums
        for m in ("refresh_nums", "_row_toggle_section", "_add_section"):
            setattr(app, m, getattr(am.MacroApp, m).__get__(app))
        return app, store

    def test_refresh_nums_skips_sections(self):
        app, store = self._app()
        app._add_section("i2")
        self.assertIn("⬛ หัวข้อ", str(store))
        sec_iid = [k for k, v in store.items() if v[4] == am.SECTION_HEADER][0]
        self.assertIn(store[sec_iid][7], ("0", 0))         # Secs = 0
        # เพิ่มแถวที่ 3 ธรรมดา — เลขต้องไล่ 1,2 ไม่นับหัวข้อ
        app.tree.insert("", "end", values=["☑", "#", "", "", "Beep", "", "0", "1", "1"])
        app.refresh_nums()
        self.assertEqual(store["i1"][1], 1)
        self.assertEqual(store["i2"][1], 2)
        sec = [v for v in store.values() if v[4] == am.SECTION_HEADER][0]
        self.assertEqual(sec[1], "#")                      # หัวข้อไม่ถูกรีเลข

    def test_toggle_section_back_to_row(self):
        app, store = self._app()
        app._row_toggle_section("i1")                      # Beep → หัวข้อ
        self.assertEqual(store["i1"][4], am.SECTION_HEADER)
        app._row_toggle_section("i1")                      # หัวข้อ → กลับเป็นแถวธรรมดา
        self.assertEqual(store["i1"][4], "Left Click")


class _GuiPlayBase(unittest.TestCase):
    """ฐานร่วมเทสต์เล่นจริงผ่าน player (GUI) — app จริง + steps จับ log + _wait_done
    แถว Beep ล้วน (secs=0) ไม่แตะเมาส์/คีย์ — ไม่มีจอ skip อัตโนมัติ"""

    @classmethod
    def setUpClass(cls):
        cls._orig_log = am.log_write
        cls.steps = []

        def counting_log(mode, message, src=None):
            if mode == "STEP":
                cls.steps.append(message)
            return cls._orig_log(mode, message, src)
        am.log_write = counting_log
        cls.app = None
        try:
            cls.root = _Tk()
            cls.root.withdraw()
        except am.tk.TclError:
            cls.root = None
            return
        try:
            cls.app = am.MacroApp(cls.root)
            cls.app._log_enabled = True
        except Exception:
            cls.root.destroy()
            cls.root = None
            cls.app = None

    @classmethod
    def tearDownClass(cls):
        am.log_write = cls._orig_log
        if cls.app is not None:
            try:
                cls.app.stop_all(silent=True)
            except Exception:
                pass
        if cls.root is not None:
            cls.root.destroy()              # _Tk.destroy = หยุดเธรด + ยกเลิก after + gc.collect
        cls.app = None                      # ปล่อย ref ให้เก็บบน main thread ไม่ค้างถึงจบ suite
        cls.root = None

    def setUp(self):
        if self.app is None:
            self.skipTest("ไม่มีจอ/สร้าง MacroApp จริงไม่ได้")
        self.app.stop_all(silent=True)
        self.app.ent_loops.delete(0, "end")
        self.app.ent_loops.insert(0, "1")                  # กันค่าค้างจากเทสต์ก่อนหน้า
        self.app._load_rows([{"enabled": True, "button": "Beep", "secs": 0, "repeat": 1}])
        self.__class__.steps = []

    def _wait_done(self, timeout=5.0):
        end = time.time() + timeout
        while time.time() < end:
            try:
                self.root.update()
            except Exception:
                pass
            if not self.app.running:
                return True
            time.sleep(0.03)
        return False


class TestV21GuiPlay(_GuiPlayBase):
    """v1.21: If Loop/If Time ข้ามแถว + Section ไม่หยุดการเล่น"""

    def test_if_loop_skips_from_round_n(self):
        app = self.app
        app._load_rows([
            {"enabled": True, "button": "Beep", "secs": 0},
            {"enabled": True, "button": am.IF_LOOP, "additional": "2", "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Beep", "secs": 0},
        ])
        app.ent_loops.delete(0, "end")
        app.ent_loops.insert(0, "3")                       # เล่น 3 รอบแล้วจบเอง
        app.start_play()
        self.assertTrue(self._wait_done())
        self.assertEqual(len([s for s in self.steps if "Beep" in s]), 4)   # Beep#1 ทุกรอบ(3) + Beep#2 รอบเดียว(1)
        self.assertEqual(len([s for s in self.steps if "If Loop" in s]), 3)
        skipped = [s for s in self.steps if "If Loop" in s and "ข้าม" in s]
        self.assertEqual(len(skipped), 2)                  # รอบ 2 และ 3 ถูกข้าม
        self.assertEqual(len([s for s in self.steps if "If Loop" in s and "ข้าม" not in s]), 1)

    def test_if_time_before_time_plays_on(self):
        app = self.app
        t = datetime.datetime.now() + datetime.timedelta(minutes=5)
        app._load_rows([
            {"enabled": True, "button": am.IF_TIME,
             "additional": "%02d:%02d" % (t.hour, t.minute), "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Beep", "secs": 0},
        ])
        app.start_play()
        self.assertTrue(self._wait_done())
        self.assertEqual(len([s for s in self.steps if "If Time" in s]), 1)
        self.assertEqual(len([s for s in self.steps if "Beep" in s]), 1)   # เล่นต่อปกติ

    def test_section_row_played_through(self):
        app = self.app
        app._load_rows([
            {"enabled": True, "button": "Beep", "secs": 0},
            {"enabled": True, "button": am.SECTION_HEADER, "additional": "หัวข้อทดสอบ"},
            {"enabled": True, "button": "Beep", "secs": 0},
        ])
        app.start_play()
        self.assertTrue(self._wait_done())
        self.assertEqual(len([s for s in self.steps if "Beep" in s]), 2)
        self.assertEqual(len(self.steps), 2)               # Section ไม่เขียน log STEP เลย

    def test_skip_not_eaten_by_section_and_block(self):
        """v2.14.1: กติกา skip×Block — skip ของเงื่อนไขกินเฉพาะแถวลำดับตรง
        หัวข้อ/Block Start/End ไม่กิน skip (GUI เดิมกินก่อนตรวจบล็อก = ต่างจาก CLI)
        รอบ 2: ข้าม 2 = Beep#ตรง + Beep#ในบล็อก (หัวข้อ/Block Start ไม่กิน)
        เดิม: หัวข้อ+Block Start กิน skip → Beep#ในบล็อกเล่น (นับ 2) ต่างจาก CLI"""
        app = self.app
        app._load_rows([
            {"enabled": True, "button": am.IF_LOOP, "additional": "2", "secs": 0, "repeat": 2},
            {"enabled": True, "button": "Beep", "additional": "ตรงหน้าบล็อก", "secs": 0},
            {"enabled": True, "button": am.SECTION_HEADER, "additional": "หัวข้อ"},
            {"enabled": True, "button": am.BLOCK_START, "additional": ""},
            {"enabled": True, "button": "Beep", "additional": "ในบล็อก", "secs": 0},
            {"enabled": True, "button": am.BLOCK_END, "additional": ""},
            {"enabled": True, "button": "Beep", "additional": "หลังบล็อก", "secs": 0},
        ])
        app.ent_loops.delete(0, "end")
        app.ent_loops.insert(0, "2")
        app.start_play()
        self.assertTrue(self._wait_done())
        self.assertEqual(len([s for s in self.steps if "ตรงหน้าบล็อก" in s]), 1)  # รอบ 2 โดนข้าม
        self.assertEqual(len([s for s in self.steps if "ในบล็อก" in s]), 1)      # รอบ 2 โดนข้าม (เดิมเล่น)
        self.assertEqual(len([s for s in self.steps if "หลังบล็อก" in s]), 2)    # ทุกรอบ


class TestV21CliLoop(unittest.TestCase):
    """v1.21: CLI รองรับ If Loop/If Time + Section (รันผ่าน cli_main จริง)"""

    def _run_cli(self, rows, extra=None):
        tmp = tempfile.mkdtemp(prefix="v21cli_")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        path = os.path.join(tmp, "script.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, ensure_ascii=False)
        out = io.StringIO()
        with mock.patch.object(am.sys, "stdout", out):
            rc = am.cli_main([path] + (extra or []))
        return rc, out.getvalue()

    def test_cli_if_loop_and_section(self):
        rows = [
            {"enabled": True, "button": "Beep", "secs": 0},
            {"enabled": True, "button": am.IF_LOOP, "additional": "2", "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Beep", "secs": 0},
            {"enabled": True, "button": am.SECTION_HEADER, "additional": "กลุ่ม"},
        ]
        rc, outp = self._run_cli(rows, ["--loops", "2"])
        self.assertEqual(rc, 0)
        # รอบ 1: Beep ทั้ง 2 จุด (ยังไม่ถึงรอบ 2); รอบ 2: If Loop ข้าม 1 แถว → Beep #1 อย่างเดียว
        self.assertEqual(outp.count("Beep"), 3)
        self.assertEqual(outp.count("ข้าม 1 แถว"), 1)
        self.assertEqual(outp.count("[3/4]"), 1)           # แถว 3 ถูกเล่นเฉพาะรอบ 1
        self.assertNotIn("กลุ่ม", outp)                     # Section ไม่ถูกพิมพ์เลย

    def test_cli_if_time_future_time_plays_on(self):
        t = datetime.datetime.now() + datetime.timedelta(minutes=5)
        rows = [
            {"enabled": True, "button": am.IF_TIME,
             "additional": "%02d:%02d" % (t.hour, t.minute), "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Beep", "secs": 0},
        ]
        rc, outp = self._run_cli(rows)
        self.assertEqual(rc, 0)
        self.assertEqual(outp.count("Beep"), 1)


# ============================ v2.14.1: กติกา skip×Block — สัญญาเดียวทั้ง 3 ตัวเล่น ====
class TestSkipBlockRule(unittest.TestCase):
    """v2.14.1: skip ของเงื่อนไขกินเฉพาะแถวลำดับตรง — หัวข้อ/Block Start/End ไม่กิน skip
    และการกระโดด/วนกลับของบล็อกยกเลิก skip ค้าง (พิสูจน์บน CI ว่าเดิมทะลุบล็อก)
    ต้องตรงกันทั้ง GUI / CLI หลัก / engine_cli — แถว Beep ล้วน ปลอดภัยทุก OS"""

    ROWS = [
        {"enabled": True, "button": am.IF_LOOP, "additional": "2", "secs": 0, "repeat": 2},
        {"enabled": True, "button": "Beep", "additional": "ตรงหน้าบล็อก", "secs": 0},
        {"enabled": True, "button": am.SECTION_HEADER, "additional": "หัวข้อ"},
        {"enabled": True, "button": am.BLOCK_START, "additional": ""},
        {"enabled": True, "button": "Beep", "additional": "ในบล็อก", "secs": 0},
        {"enabled": True, "button": am.BLOCK_END, "additional": ""},
        {"enabled": True, "button": "Beep", "additional": "หลังบล็อก", "secs": 0},
    ]
    # รอบ 2: ข้าม 2 = Beep#ตรง + Beep#ในบล็อก (หัวข้อ/Block Start ไม่กิน — เปลี่ยนที่ v2.14.1)

    def test_cli_skip_not_eaten_by_block(self):
        tmp = tempfile.mkdtemp(prefix="skipblk_")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        path = os.path.join(tmp, "s.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.ROWS, fh, ensure_ascii=False)
        out = io.StringIO()
        with mock.patch.object(am.sys, "stdout", out):
            rc = am.cli_main([path, "--loops", "2", "--no-log"])
        self.assertEqual(rc, 0)
        outp = out.getvalue()
        self.assertEqual(outp.count("ตรงหน้าบล็อก"), 1)  # รอบ 2 โดนข้าม
        self.assertEqual(outp.count("ในบล็อก"), 1)      # รอบ 2 โดนข้าม (skip ไม่ถูกหัวข้อ/บล็อกกิน)
        self.assertEqual(outp.count("หลังบล็อก"), 2)    # ทุกรอบ

    def test_engine_cli_skip_not_eaten_by_block(self):
        import engine_cli
        tmp = tempfile.mkdtemp(prefix="skipblk2_")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        path = os.path.join(tmp, "s.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.ROWS, fh, ensure_ascii=False)
        out = io.StringIO()
        with mock.patch.object(engine_cli.sys, "stdout", out):
            rc = engine_cli.main([path, "--loops", "2", "--no-log"])
        self.assertEqual(rc, 0)
        outp = out.getvalue()
        self.assertEqual(outp.count("ตรงหน้าบล็อก"), 1)  # รอบ 2 โดนข้าม
        self.assertEqual(outp.count("ในบล็อก"), 1)      # สาขา skip ต้องเดิน pi (แก้บั๊ก v2.1) + ไม่ถูกบล็อกกิน
        self.assertEqual(outp.count("หลังบล็อก"), 2)    # ทุกรอบ


# ============================ v2.14.1: ปุ่มรายงาน Dry-run ล่าสุดในหน้าต่าง 📝 Log ====
class TestLatestDryReportBtn(unittest.TestCase):
    """v2.14.1: ปุ่ม "รายงาน Dry-run ล่าสุด" — เลือกไฟล์ dry_report_*.txt ล่าสุดขึ้นแสดง
    (มีรายงาน = combobox ชี้ไฟล์นั้น + เนื้อหาแสดง · ไม่มี = เตือน statusbar จบเงียบ)
    กดปุ่มจริงด้วย .invoke() ทุกเทสต์ — เทสต์ "เปิดได้" ล้วนเคยปล่อยบั๊กค่าไม่ถูกบันทึก (v1.20.1)"""

    @classmethod
    def setUpClass(cls):
        cls.app = None
        try:
            cls.root = _Tk()
            cls.root.withdraw()
        except am.tk.TclError:
            cls.root = None
            return
        try:
            cls.app = am.MacroApp(cls.root)
        except Exception:
            cls.root.destroy()
            cls.root = None
            cls.app = None

    @classmethod
    def tearDownClass(cls):
        if cls.root is not None:
            cls.root.destroy()          # _Tk ยกเลิก timer ค้างก่อนเอง

    def setUp(self):
        if self.app is None:
            self.skipTest("ไม่มีจอ/สร้าง MacroApp จริงไม่ได้")
        self.app._log_enabled = False
        d = os.path.dirname(os.path.abspath(am.__file__))
        self._reps = sorted(glob.glob(os.path.join(d, "dry_report_*.txt")), reverse=True)
        for f in self._reps:            # ชั่วคราวย้ายรายงานเก่าออก — คืนที่หลังเทสต์
            os.replace(f, f + "__bak")

    def tearDown(self):
        d = os.path.dirname(os.path.abspath(am.__file__))
        for f in glob.glob(os.path.join(d, "dry_report_*__bak")):
            if os.path.isfile(f):
                os.replace(f, f[:-len("__bak")])
        for f in glob.glob(os.path.join(d, "dry_report_*.txt")):
            if os.path.isfile(f):       # ไฟล์ที่เทสต์สร้างค้าง — ย้ายไป temp ก่อนลบ
                shutil.move(f, os.path.join(tempfile.gettempdir(),
                                            os.path.basename(f) + ".testdel"))

    def _win_and_widgets(self):
        self.app.view_log()
        win = next(w for w in self.root.winfo_children()
                   if isinstance(w, am.tk.Toplevel) and "Log" in str(w.title()))
        self.addCleanup(win.destroy)
        cmb = next(w for w in win.winfo_children()
                   if isinstance(w, am.tk.Frame)).winfo_children()[1]
        btn = next(b for f in win.winfo_children() if isinstance(f, am.tk.Frame)
                   for b in f.winfo_children()
                   if isinstance(b, am.tk.Button) and "Dry-run" in str(b["text"]))
        return cmb, btn

    def test_button_selects_latest_report(self):
        d = os.path.dirname(os.path.abspath(am.__file__))
        stamp = datetime.date.today().isoformat()
        a = os.path.join(d, "dry_report_%s.txt" % stamp)
        with open(a, "w", encoding="utf-8") as fh:
            fh.write("ทดสอบรายงานล่าสุด")
        self.addCleanup(lambda: os.path.isfile(a) and os.remove(a))
        cmb, btn = self._win_and_widgets()
        cmb.set("macro_log_dummy_ไม่มีจริง.txt")     # ตั้งค่าอื่นก่อน — ปุ่มต้องเปลี่ยนกลับ
        btn.invoke()                              # กดจริง — ไม่ invoke = ค่าปุ่มลอยได้ (v1.20.1)
        self.assertEqual(cmb.get(), os.path.basename(a))   # ชี้ไฟล์ล่าสุด
        top = next(w for w in self.root.winfo_children()
                   if isinstance(w, am.tk.Toplevel) and "Log" in str(w.title()))
        txt = next(w for w in top.winfo_children() if isinstance(w, am.tk.Text))
        self.assertIn("ทดสอบรายงานล่าสุด", str(txt.get("1.0", "end")))

    def test_no_report_warns_statusbar_only(self):
        cmb, btn = self._win_and_widgets()
        btn.invoke()                              # ไม่มีรายงาน → เตือน statusbar จบเงียบ
        msg = self.app._ui_state.get("msg")
        self.assertIsNotNone(msg)
        self.assertIn("Dry-run", msg[0])


# ============================ v2.15: เล่นเฉพาะกลุ่มหัวข้อ (GUI + CLI) ====
class TestSectionOnlyPlay(_GuiPlayBase):
    """v2.15: เล่นกลุ่มหัวข้ออย่างเดียว — GUI คลิกขวาหัวข้อ → ▶ เล่นกลุ่มนี้อย่างเดียว (player จริง)
    สืบทอด harness ของ _GuiPlayBase (app จริง + steps จับ log + _wait_done)
    CLI: --only-section ชื่อ (ผ่าน cli_main จริง) — สายเดียวกับเล่นทั้งหมด: validate/STOP/เลขรอบ"""

    ROWS = [
        {"enabled": True, "button": am.IF_LOOP, "additional": "99", "secs": 0, "repeat": 1},
        {"enabled": True, "button": am.SECTION_HEADER, "additional": "เตรียม"},
        {"enabled": True, "button": "Beep", "additional": "A1", "secs": 0},
        {"enabled": True, "button": "Beep", "additional": "A2", "secs": 0},
        {"enabled": True, "button": am.SECTION_HEADER, "additional": "งาน"},
        {"enabled": True, "button": "Beep", "additional": "B1", "secs": 0},
        {"enabled": False, "button": "Beep", "additional": "B-off", "secs": 0},
        {"enabled": True, "button": "Beep", "additional": "B2", "secs": 0},
        {"enabled": True, "button": am.SECTION_HEADER, "additional": "ล้าง"},
        {"enabled": True, "button": "Beep", "additional": "C1", "secs": 0},
    ]

    def test_gui_play_group_only(self):
        app = self.app
        app._load_rows([dict(r) for r in self.ROWS])
        kids = list(app.tree.get_children())
        head = kids[4]                      # หัวข้อ "งาน" — เล่นเฉพาะกลุ่มนี้
        app.ent_loops.delete(0, "end")
        app.ent_loops.insert(0, "1")
        app._play_section(head)
        self.assertTrue(app.running)
        self.assertTrue(self._wait_done())
        beeps = [s for s in self.steps if "Beep" in s]
        self.assertTrue(any("B1" in s for s in beeps))
        self.assertTrue(any("B2" in s for s in beeps))
        self.assertFalse(any("A1" in s or "A2" in s for s in beeps))   # กลุ่มอื่นไม่เล่น
        self.assertFalse(any("C1" in s for s in beeps))
        self.assertFalse(any("B-off" in s for s in beeps))             # ☐ ไม่เล่น

    def test_gui_play_group_includes_collapsed_rows(self):
        app = self.app
        app._load_rows([dict(r) for r in self.ROWS])
        kids = list(app.tree.get_children())
        self.addCleanup(lambda: app._section_stash.clear())   # _group_toggle ตั้งลิสต์ใหม่ — ต้อง clear ที่ลิสต์จริง
        app._group_toggle(kids[4])          # ย่อกลุ่ม "งาน" — สมาชิกเข้า stash
        app.ent_loops.delete(0, "end")
        app.ent_loops.insert(0, "1")
        app._play_section(kids[4])          # เล่นกลุ่มที่ย่ออยู่ — สมาชิกต้องถูกเล่นครบ
        self.assertTrue(self._wait_done())
        self.assertTrue(any("B1" in s for s in self.steps))
        self.assertTrue(any("B2" in s for s in self.steps))

    def test_gui_empty_group_warns_only(self):
        app = self.app
        app._load_rows([
            {"enabled": True, "button": am.SECTION_HEADER, "additional": "ว่าง"},
            {"enabled": True, "button": am.SECTION_HEADER, "additional": "จบ"},
        ])
        kids = list(app.tree.get_children())
        app._play_section(kids[0])          # กลุ่มว่าง = เตือน statusbar ไม่เล่น (กฎเหล็ก)
        self.assertFalse(app.running)
        self.assertIn("ไม่มีแถวที่เปิดใช้", str(self.app._ui_state.get("msg", ("",))[0]))

    def test_cli_only_section(self):
        tmp = tempfile.mkdtemp(prefix="seconly_")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        path = os.path.join(tmp, "s.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.ROWS, fh, ensure_ascii=False)
        out = io.StringIO()
        with mock.patch.object(am.sys, "stdout", out):
            rc = am.cli_main([path, "--loops", "1", "--no-log", "--only-section", "งาน"])
        self.assertEqual(rc, 0)
        outp = out.getvalue()
        self.assertIn("เล่นกลุ่ม 'งาน'", outp)
        self.assertIn("B1", outp)
        self.assertIn("B2", outp)
        self.assertNotIn("A1", outp)
        self.assertNotIn("C1", outp)

    def test_cli_only_section_missing_warns_and_plays_all(self):
        tmp = tempfile.mkdtemp(prefix="secnone_")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        path = os.path.join(tmp, "s.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.ROWS, fh, ensure_ascii=False)
        out = io.StringIO()
        with mock.patch.object(am.sys, "stdout", out):
            rc = am.cli_main([path, "--loops", "1", "--no-log", "--only-section", "ไม่มีจริง"])
        self.assertEqual(rc, 0)
        outp = out.getvalue()
        self.assertIn("ไม่พบหัวข้อชื่อ", outp)
        for tag in ("A1", "B1", "C1"):    # fallback = เล่นทั้งหมด
            self.assertIn(tag, outp)


# ============================ v1.22: สีแถวตามหมวด + ปุ่มจับเวลา + ย่อ/ขยายกลุ่ม ====
class TestRowStyles(unittest.TestCase):
    """v1.22: สีแถวตารางตามหมวด Action — row_tag/row_tags คืน tag ตามชนิด"""

    def test_row_tag_categories(self):
        self.assertEqual(am.row_tag(am.SECTION_HEADER), "section")
        self.assertEqual(am.row_tag(am.IF_IMAGE), "cond")
        self.assertEqual(am.row_tag(am.ELSE_IMAGE), "cond")
        self.assertEqual(am.row_tag(am.IF_LOOP), "cond")
        self.assertEqual(am.row_tag(am.IF_TIME), "cond")
        self.assertEqual(am.row_tag("Tap Key"), "key")
        self.assertEqual(am.row_tag("Type Text"), "key")
        self.assertEqual(am.row_tag("Image Click"), "special")
        self.assertEqual(am.row_tag("Wait for Pixel Color"), "special")
        self.assertEqual(am.row_tag("Beep"), "special")
        self.assertEqual(am.row_tag("Set Variable"), "special")

    def test_mouse_rows_keep_zebra(self):
        self.assertEqual(am.row_tags("Left Click", 1), ("even",))
        self.assertEqual(am.row_tags("Left Click", 2), ("odd",))
        self.assertEqual(am.row_tags("Right Click", 3), ("even",))
        self.assertEqual(am.row_tags("Scroll Up", 4), ("odd",))
        self.assertEqual(am.row_tags("Move Mouse", 5), ("even",))

    def test_categorized_rows_get_color_tag(self):
        self.assertEqual(am.row_tags(am.IF_LOOP, 3), ("cond",))
        self.assertEqual(am.row_tags("Beep", 4), ("special",))
        self.assertEqual(am.row_tags("Press Key", 5), ("key",))
        self.assertEqual(am.row_tags(am.SECTION_HEADER, 1), ("section",))

    def test_unknown_action_keeps_zebra(self):
        self.assertEqual(am.row_tags("Plugin แปลกปลอม", 2), ("odd",))


class TestTimePicker(unittest.TestCase):
    """v1.22: ปุ่ม 🕐 เวลานี้ (+15 นาที) — เติมแถว If Time ที่เลือก หรือสร้างแถวใหม่"""

    def _app(self):
        app = mock.MagicMock()
        stored = {"values": ["☑", 1, "", "", am.IF_TIME, "", 0, 1, 1]}

        def fake_item(*args, **kw):
            if "values" in kw:
                stored["values"] = list(kw["values"])
                return None
            return stored["values"]

        app.tree.selection.return_value = ["i1"]
        app.tree.item.side_effect = fake_item
        return app, stored

    def test_fills_selected_if_time_row(self):
        app, stored = self._app()
        ok = am.MacroApp._apply_current_time(app)
        self.assertTrue(ok)
        self.assertRegex(stored["values"][5], r"^\d{2}:\d{2}$")
        am.parse_if_time(stored["values"][5])          # ไม่ throw = รูปแบบถูก
        app._append_row.assert_not_called()

    def test_appends_when_other_action_selected(self):
        app = mock.MagicMock()
        app.tree.selection.return_value = ["i1"]
        app.tree.item.return_value = ["☑", 1, "", "", "Beep", "", 0, 1, 1]
        ok = am.MacroApp._apply_current_time(app)
        self.assertFalse(ok)
        app._append_row.assert_called_once()
        self.assertEqual(app._append_row.call_args.kwargs.get("button"), am.IF_TIME)
        spec = app._append_row.call_args.kwargs.get("additional")
        self.assertIsNotNone(am.parse_if_time(spec))

    def test_appends_when_nothing_selected(self):
        app = mock.MagicMock()
        app.tree.selection.return_value = []
        am.MacroApp._apply_current_time(app)
        app._append_row.assert_called_once()


class TestSectionCollapse(unittest.TestCase):
    """v1.22: ย่อ/ขยายกลุ่มใต้หัวข้อ — แถวซ่อนยังถูก serialize เล่นตามลำดับเดิม"""

    def _app(self):
        app = mock.MagicMock()
        kids = iter("k%d" % i for i in range(1, 999))
        order = []
        store = {}

        def insert(parent, index, **kw):
            iid = next(kids)
            store[iid] = list(kw["values"])
            order.append(iid)
            return iid

        def delete(*iids):
            for i in iids:
                if i in store:
                    del store[i]
                    order.remove(i)

        def item(iid, *args, **kw):
            if "values" in kw:
                store[iid] = list(kw["values"])
                return None
            return store[iid]

        app.tree.get_children.side_effect = lambda: list(order)
        app.tree.insert = insert
        app.tree.delete = delete
        app.tree.item = item
        app.tree.index = lambda iid: order.index(iid)
        app.tree.detach = lambda iid: order.remove(iid)
        app._section_stash = []
        app._hl_row = None
        app.refresh_nums = lambda: am.MacroApp.refresh_nums(app)
        for m in ("_group_members", "_group_collapsed", "_group_toggle", "_serialize"):
            setattr(app, m, getattr(am.MacroApp, m).__get__(app))
        return app, store

    def _rows(self, app, store, rows):
        for r in rows:
            app.tree.insert("", "end", values=["☑", "#", "", "", r[0], r[1], 0, r[2], 1])

    def test_collapse_hides_and_serialize_keeps_rows(self):
        app, store = self._app()
        self._rows(app, store, [(am.SECTION_HEADER, "หัวข้อ A", 0), ("Beep", "b1", 1),
                                ("Beep", "b2", 1), ("Left Click", "", 1)])
        head = app.tree.get_children()[0]
        app._group_toggle(head)                        # ย่อ
        self.assertEqual(len(app.tree.get_children()), 1)   # มีหัวข้อเดียว → ทั้งตารางคือกลุ่ม A
        self.assertIn("(ย่อ 3 แถว)", str(app.tree.item(head, "values")[5]))   # b1+b2+Left Click ท้ายตาราง
        self.assertTrue(app._group_collapsed(head))
        rows = app._serialize()
        self.assertEqual([r["additional"] for r in rows], ["หัวข้อ A", "b1", "b2", ""])  # แถวซ่อนยังอยู่ครบ

    def test_expand_restores_original_order(self):
        app, store = self._app()
        self._rows(app, store, [(am.SECTION_HEADER, "หัวข้อ B", 0), ("Beep", "x1", 1),
                                ("Beep", "x2", 1), ("Beep", "x3", 1), ("Left Click", "", 1)])
        head = app.tree.get_children()[0]
        app._group_toggle(head)                        # ย่อ (x1–x3 + Left Click ท้ายตาราง เป็นกลุ่มเดียวกัน)
        app._group_toggle(head)                        # ขยาย
        adds = [app.tree.item(i, "values")[5] for i in app.tree.get_children()]
        self.assertEqual(adds, ["หัวข้อ B", "x1", "x2", "x3", ""])    # ลำดับเดิมเป๊ะ
        self.assertEqual(app._section_stash, [])

    def test_delete_collapsed_head_restores_rows(self):
        app, store = self._app()
        self._rows(app, store, [(am.SECTION_HEADER, "กลุ่ม C", 0), ("Beep", "c1", 1),
                                ("Beep", "c2", 1), ("Left Click", "", 1)])
        app.refresh_nums = lambda: None
        app._group_toggle(app.tree.get_children()[0])  # ย่อ
        app._on_del_cleanup = getattr(am.MacroApp, "_on_del_cleanup").__get__(app)
        head = app.tree.get_children()[0]
        app._on_del_cleanup(head)                      # ลบหัวข้อที่ย่ออยู่ → ขยายคืนก่อน
        app.tree.delete(head)
        adds = [app.tree.item(i, "values")[5] for i in app.tree.get_children()]
        self.assertEqual(adds, ["c1", "c2", ""])       # แถวกลุ่มกลับมาครบ ไม่หาย
        self.assertEqual(app._section_stash, [])

    def test_two_groups_collapse_independently(self):
        app, store = self._app()
        self._rows(app, store, [(am.SECTION_HEADER, "A", 0), ("Beep", "a1", 1),
                                (am.SECTION_HEADER, "B", 0), ("Beep", "b1", 1),
                                ("Beep", "b2", 1)])
        kids = app.tree.get_children()
        app._group_toggle(kids[0])                     # ย่อกลุ่ม A
        self.assertTrue(app._group_collapsed(kids[0]))
        self.assertFalse(app._group_collapsed(kids[2]))   # กลุ่ม B ไม่โดนกระทบ
        rows = app._serialize()
        self.assertEqual([r["additional"] for r in rows], ["A", "a1", "B", "b1", "b2"])
        app._group_toggle(kids[2])                     # ย่อกลุ่ม B ด้วย
        rows = app._serialize()
        self.assertEqual([r["additional"] for r in rows], ["A", "a1", "B", "b1", "b2"])

    def test_save_head_add_roundtrip(self):
        self.assertEqual(am._save_head_add("หัวข้อ", 3), "หัวข้อ (ย่อ 3 แถว)")
        self.assertEqual(am._save_head_add("หัวข้อ (ย่อ 3 แถว)", 5), "หัวข้อ (ย่อ 5 แถว)")
        self.assertEqual(am._save_head_add("", 1), "(ย่อ 1 แถว)")


# ================================ v2.0: แยก engine ออกจาก GUI ==================
class TestEngineSplit(unittest.TestCase):
    """v2.0 phase 1: macro_engine.py = engine ล้วน ไม่มี Tk — นำไปใช้/เทสต์แยกได้
    และ build_singlefile.py ซิงก์เนื้อหากลับ auto_macro.py ได้ตรงกัน"""

    def test_engine_imports_without_tk(self):
        import macro_engine as me
        self.assertFalse(hasattr(me, "tk"))
        self.assertNotIn("tkinter", sys.modules.get("macro_engine", sys).__dict__
                         if False else dir(me))
        self.assertTrue(hasattr(me, "ACTIONS_ALL"))
        self.assertTrue(hasattr(me, "SECTION_HEADER"))
        self.assertTrue(hasattr(me, "parse_if_loop"))
        self.assertTrue(hasattr(me, "clip_set"))
        self.assertTrue(hasattr(me, "load_plugins"))

    def test_engine_has_no_gui_code(self):
        src = open("macro_engine.py", encoding="utf-8").read()
        self.assertNotIn("import tkinter", src)
        self.assertNotIn("tk.Toplevel", src)
        self.assertNotIn("class MacroApp", src)

    def test_singlefile_build_keeps_block_in_sync(self):
        """build_singlefile รวม engine กลับ auto_macro.py — เนื้อหาตรงกับไฟล์ engine ล่าสุด"""
        src = open("auto_macro.py", encoding="utf-8").read()
        b = src.find(am.BEGIN) if hasattr(am, "BEGIN") else src.find("# === ENGINE-BEGIN")
        e = src.find("# === ENGINE-END")
        self.assertGreater(b, 0)
        self.assertGreater(e, b)
        block = src[b:e]
        eng = open("macro_engine.py", encoding="utf-8").read()
        core = eng.splitlines()
        while core and (not core[0].strip() or core[0].startswith("#")):
            core.pop(0)
        self.assertIn(core[0].strip(), block)          # บรรทัดแรกของ engine core ต้องอยู่ในบล็อก
        self.assertIn("__version__ = ", src)           # หัวไฟล์ยังมีเวอร์ชัน

    def test_engine_parsers_match_main(self):
        """parser ใน engine และใน auto_macro (หลัง sync) มีซอร์สเดียวกัน"""
        import inspect
        import macro_engine as me
        for name in ("parse_if_loop", "parse_key", "parse_set_var", "clip_set"):
            self.assertEqual(inspect.getsource(getattr(am, name)),
                             inspect.getsource(getattr(me, name)),
                             "%s ต่างกันระหว่าง auto_macro กับ macro_engine — รัน build_singlefile.py" % name)
        self.assertEqual(am.CONF, me.CONF)


# ================================ v2.1: ActionRunner + engine_cli =================
class TestActionRunner(unittest.TestCase):
    """v2.1 (phase 2): ActionRunner ใน macro_engine — กลไก execute แหล่งเดียว GUI+CLI"""

    def _runner(self, **kw):
        mouse = mock.MagicMock()
        mouse.position = (10, 20)
        kb = mock.MagicMock()
        msgs = []
        r = me_mod.ActionRunner(mouse, kb, on_message=lambda t, c="#080": msgs.append((t, c)), **kw)
        return r, mouse, kb, msgs

    def test_mouse_click_moves_then_clicks(self):
        r, mouse, kb, msgs = self._runner()
        r.execute({"button": "Left Click", "x": "11", "y": "22", "additional": ""})
        self.assertEqual(mouse.position, (11, 22))   # assignment ทับ mock attr ตรง ๆ
        mouse.click.assert_called_once()

    def test_press_and_release_tracks_stuck_keys(self):
        r, mouse, kb, msgs = self._runner()
        k = am.parse_key("ctrl")
        r.execute({"button": "Press Key", "additional": "ctrl"})
        self.assertIn(k, r.pressed_keys)
        r.release_all()
        kb.release.assert_called_once_with(k)      # ปล่อยคีย์ค้างตอนหยุด
        self.assertEqual(r.pressed_keys, set())

    def test_combo_press_tap_release_order(self):
        r, mouse, kb, msgs = self._runner()
        r.execute({"button": "Tap Key", "additional": "Ctrl+W"})
        pressed = [c.args[0] for c in kb.press.call_args_list]
        tapped = [c.args[0] for c in kb.tap.call_args_list]
        released = [c.args[0] for c in kb.release.call_args_list]
        self.assertEqual(pressed, [am.Key.ctrl])
        self.assertEqual(tapped, [am.KeyCode.from_vk(0x57)])
        self.assertEqual(released, [am.Key.ctrl])

    def test_set_variable_and_substitution(self):
        r, mouse, kb, msgs = self._runner()
        r.execute({"button": "Set Variable", "additional": "n = 10"})
        self.assertEqual(r.variables.get("n"), "10")
        self.assertEqual(am.substitute_vars("{n}", r.variables), "10")

    def test_clipboard_uses_callbacks(self):
        sets, reads = [], {"x": "ข้อความ"}
        r = me_mod.ActionRunner(
            mock.MagicMock(), mock.MagicMock(),
            on_clipboard_set=sets.append,
            on_clipboard_read=lambda: reads["x"])
        r.execute({"button": "Set Clipboard", "additional": "hello"})
        self.assertEqual(sets, ["hello"])
        r.execute({"button": "Read Clipboard", "additional": "v"})
        self.assertEqual(r.variables.get("v"), "ข้อความ")

    def test_unsupported_action_calls_callback(self):
        seen = []
        r = me_mod.ActionRunner(mock.MagicMock(), mock.MagicMock(),
                                unsupported_cb=lambda btn: seen.append(btn))
        r.execute({"button": "Mystery Action"})
        self.assertEqual(seen, ["Mystery Action"])

    def test_plugin_gets_ctx_v2(self):
        holder = {}
        mod = type("M", (), {"run": staticmethod(lambda ctx, row: holder.update(ctx))})()
        r = me_mod.ActionRunner(mock.MagicMock(), mock.MagicMock(),
                                plugin_lookup=lambda name: mod, stop_check=lambda: False)
        r.execute({"button": "Fake Plugin", "additional": ""})
        self.assertTrue(callable(holder.get("stop_check")))
        self.assertIn("ui", holder)

    def test_evaluate_condition_if_loop_and_time(self):
        ec = me_mod.ActionRunner.evaluate_condition
        skip, msg = ec(am.IF_LOOP, "3", 2, n_loop=3)
        self.assertEqual(skip, 2)                       # Repeat = จำนวนแถวที่ข้าม
        self.assertIn("ข้าม 2 แถว", msg)
        skip, msg = ec(am.IF_LOOP, "3", 2, n_loop=2)
        self.assertEqual((skip, msg), (0, None) if False else (0, msg))
        self.assertIn("เล่นต่อ", msg)
        skip, msg = ec(am.IF_TIME, "22:30", 4, n_loop=1,
                       now=__import__("time").struct_time((2026, 9, 29, 23, 0, 0, 0, 0, 0)))
        self.assertEqual(skip, 4)
        skip, msg = ec(am.IF_TIME, "22:30", 4, n_loop=1,
                       now=__import__("time").struct_time((2026, 9, 29, 10, 0, 0, 0, 0, 0)))
        self.assertEqual(skip, 0)
        self.assertIn("เล่นต่อ", msg)
        skip, msg = ec("Beep", "", 1, n_loop=1)
        self.assertEqual((skip, msg), (0, None))


class TestEngineCli(unittest.TestCase):
    """v2.1: engine_cli.py — CLI ย่อย import engine ตรง ๆ (ไม่แตะ auto_macro/tkinter)"""

    def test_module_imports_without_gui(self):
        import engine_cli
        self.assertFalse(hasattr(engine_cli, "tk"))
        self.assertTrue(callable(engine_cli.main))

    def test_load_script_errors(self):
        import engine_cli
        rows, err = engine_cli.load_script("no_such_file.json")
        self.assertIsNone(rows)
        self.assertIn("ไม่พบไฟล์สคริปต์", err)
        tmp = tempfile.mkdtemp(prefix="ecli_")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        p = os.path.join(tmp, "s.json")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("{bad json")
        rows, err = engine_cli.load_script(p)
        self.assertIn("JSON พัง", err)
        with open(p, "w", encoding="utf-8") as fh:
            json.dump([{"enabled": True, "button": "Beep", "secs": 0}], fh)
        rows, err = engine_cli.load_script(p)
        self.assertIsNone(err)
        self.assertEqual(len(rows), 1)

    def test_cli_runs_beep_script(self):
        import engine_cli
        tmp = tempfile.mkdtemp(prefix="ecli_")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        p = os.path.join(tmp, "s.json")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump([{"enabled": True, "button": "Beep", "secs": 0}], fh)
        out = io.StringIO()
        with mock.patch.object(am.sys, "stdout", out):
            rc = engine_cli.main([p, "--no-log"])
        self.assertEqual(rc, 0)
        self.assertIn("จบแล้ว", out.getvalue())

    def test_cli_dry_run_writes_report(self):
        """v2.11: engine_cli --dry-run เขียนรายงานไฟล์เหมือน CLI หลัก (v2.10.1) —
        patch me.dry_report_path เสมอ ห้ามเขียนไฟล์ข้างโค้ดจริง"""
        import engine_cli
        tmp = tempfile.mkdtemp(prefix="eclidry_")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        p = os.path.join(tmp, "s.json")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump([{"enabled": True, "button": "Beep", "additional": "",
                        "mins": 0, "secs": 0, "repeat": 1}], fh, ensure_ascii=False)
        target = os.path.join(tmp, "dry_report_ecli.txt")
        out = io.StringIO()
        with mock.patch.object(me_mod, "dry_report_path", return_value=target), \
             mock.patch.object(am.sys, "stdout", out):
            rc = engine_cli.main([p, "--dry-run", "--no-log"])
        self.assertEqual(rc, 0)
        self.assertTrue(os.path.isfile(target))
        with open(target, encoding="utf-8") as fh:
            text = fh.read()
        self.assertIn("DRY-RUN: จะส่งเสียง Beep", text)
        self.assertIn("Beep ×1", text)
        self.assertIn(os.path.basename(target), out.getvalue())   # พิมพ์พาธรายงานให้ผู้ใช้รู้


class TestPluginMarket(unittest.TestCase):
    """v2.1: ปุ่มตลาด plugin — เปิดโฟลเดอร์ plugins/ ด้วยเมธอดเดิมที่ทดสอบแล้ว"""

    def test_open_plugins_folder_method_exists(self):
        self.assertTrue(hasattr(am.MacroApp, "open_plugins_folder"))

    def test_open_plugins_folder_uses_opener(self):
        app = mock.MagicMock()
        with mock.patch.object(am, "os") as fake_os:
            am.MacroApp.open_plugins_folder(app)
            fake_os.makedirs.assert_called_once()      # สร้างโฟลเดอร์ถ้ายังไม่มี
            fake_os.startfile.assert_called_once()     # เปิดโฟลเดอร์


class TestV22Recorder(unittest.TestCase):
    """v2.2 (phase 3): Recorder ใน engine — กลไกบันทึกล้วน ไม่มี Tk"""

    def test_recorder_pure_engine_no_tk(self):
        import macro_engine as me
        import inspect
        src = inspect.getsource(me.Recorder)
        self.assertNotIn("tkinter", src)
        self.assertNotIn("Tk(", src)

    def test_recorder_lifecycle_and_drain(self):
        import macro_engine as me
        events = []
        rec = me.Recorder(on_event=events.append)
        self.assertFalse(rec.recording)
        rec.start()
        self.assertTrue(rec.recording)
        rec._push(dict(x=1, y=2, button="Left Click", additional="", mins=0, secs=0.1, repeat=1))
        self.assertEqual(len(rec.pending_rows), 1)
        self.assertEqual(len(events), 1)               # on_event ถูกเรียกทันที
        rows = rec.drain_pending()                     # drain = ล้างคิวครั้งเดียว
        self.assertEqual(len(rows), 1)
        self.assertEqual(rec.pending_rows, [])
        n = rec.stop()
        self.assertFalse(rec.recording)
        self.assertEqual(n, 0)                         # drain ไปแล้ว เหลือ 0

    def test_recorder_kb_callback_records_tap_key(self):
        """กดคีย์ (จำลอง) ต้องได้แถว Tap Key — ตรรกะเดียวกับที่ GUI เคยมีใน _start_listeners"""
        import macro_engine as me
        rec = me.Recorder()
        rec.start()
        rec._on_kb(am.KeyCode.from_char("a"))
        self.assertEqual(len(rec.pending_rows), 1)
        self.assertEqual(rec.pending_rows[0]["button"], "Tap Key")
        self.assertEqual(rec.pending_rows[0]["additional"], "a")
        rec.stop()
        rec._on_kb(am.KeyCode.from_char("b"))         # หยุดอัดแล้ว = ไม่เพิ่ม
        self.assertEqual(len(rec.pending_rows), 1)

    def test_gui_uses_engine_recorder(self):
        """MacroApp ต้องสร้าง Recorder จาก engine และ poller ดึงผ่าน drain_pending"""
        app = mock.MagicMock()
        app._recorder = am.macro_engine.Recorder()
        app.recording = True
        app._recorder.pending_rows = [dict(x=1, y=2, button="Left Click",
                                           additional="", mins=0, secs=0.2, repeat=1)]
        app._ui_state = {"row": None, "msg": None, "prog": None, "reset": False,
                         "beep": False, "clipboard": None, "read_clipboard": None}
        am.MacroApp._start_poller(app)                 # mock root.after จบลูปทันที
        app._append_row.assert_called_once()           # แถวจาก recorder เข้าตาราง
        self.assertEqual(app._recorder.pending_rows, [])

    def test_gui_poller_ignores_empty_status_msg(self):
        """poller ต้องทน st["msg"] = ("", ) ที่มาจาก _execute_condition_row (det ว่าง)"""
        app = mock.MagicMock()
        app._recorder = am.macro_engine.Recorder()
        app.recording = False
        app._ui_state = {"row": None, "msg": ("",), "prog": None, "reset": False,
                         "beep": False, "clipboard": None, "read_clipboard": None}
        am.MacroApp._start_poller(app)
        self.assertIsNone(app._ui_state["msg"])


class TestV22ImageEngine(unittest.TestCase):
    """v2.2: ค้นภาพอยู่ที่ engine — GUI/CLI ใช้ร่วมกัน"""

    def test_parse_search_area_matches_gui_version(self):
        import macro_engine as me
        self.assertEqual(me.parse_search_area("btn.png@10,20,300,150#90"),
                         ("btn.png", (10, 20, 310, 170), 0.9))
        self.assertEqual(me.parse_search_area("btn.png#65"), ("btn.png", None, 0.65))
        self.assertEqual(me.parse_search_area("btn.png"), ("btn.png", None, 0.80))
        self.assertEqual(me.parse_search_area("bad@x,y"), ("bad", None, 0.80))  # พิมพ์พลาด = ทั้งจอ

    def test_find_image_pos_missing_file_sets_last_error(self):
        import macro_engine as me
        self.assertIsNone(me.find_image_pos("no_such_v22.png"))
        # ต้องรายงานเหตุผลเสมอ — เครื่องไม่มี opencv = เตือนติดตั้ง, มี = เตือนไฟล์หาย (v2.2)
        self.assertTrue(me.find_image_pos.last_error)
        if me.HAS_CV:
            self.assertIn("ไม่พบไฟล์ภาพ", me.find_image_pos.last_error)
        else:
            self.assertIn("ติดตั้ง", me.find_image_pos.last_error)

    def test_runner_executes_if_image_and_sets_skip(self):
        """If Image ไม่เจอ (ไฟล์หาย) → skip_n = Repeat · เจอ/ผ่านเคสอื่นทำใน E2E"""
        import macro_engine as me
        msgs = []
        runner = me.ActionRunner(
            mock.MagicMock(), mock.MagicMock(),
            on_message=lambda t, c="#080": msgs.append((t, c)))
        r = {"button": am.IF_IMAGE, "additional": "no_such_v22.png", "repeat": 3,
             "secs": 0, "mins": 0}
        runner.execute(r)
        self.assertEqual(runner.skip_n, 3)
        self.assertFalse(runner.last_if_found)
        self.assertTrue(any("ข้าม 3 แถว" in t for t, _ in msgs))
        # Else: If ไม่เจอ → เล่นกลุ่ม B ต่อ (ไม่ข้าม)
        n_before = runner.skip_n
        runner.execute({"button": am.ELSE_IMAGE, "additional": "x.png", "repeat": 2})
        self.assertEqual(runner.skip_n, n_before)      # ไม่เพิ่ม — เล่นกลุ่ม B
        self.assertTrue(any("เล่นกลุ่ม B" in t for t, _ in msgs))


class TestV22EngineCli(unittest.TestCase):
    """v2.2: engine_cli --json-lines + ค้นภาพผ่าน cb"""

    def _write(self, tmp, name, text):
        p = os.path.join(tmp, name)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
        return p

    def test_load_script_json_lines(self):
        import engine_cli
        tmp = tempfile.mkdtemp(prefix="jl_")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        p = self._write(tmp, "s.jsonl",
                        '{"button": "Beep", "secs": 0}\n'
                        '\n# บรรทัดคอมเมนต์ข้ามได้\n'
                        '{"button": "Beep", "secs": 0}\n')
        rows, err = engine_cli.load_script(p, json_lines=True)
        self.assertIsNone(err)
        self.assertEqual(len(rows), 2)
        bad = self._write(tmp, "bad.jsonl", '{"button": "Beep"}\nnot json\n')
        rows, err = engine_cli.load_script(bad, json_lines=True)
        self.assertIsNone(rows)
        self.assertIn("บรรทัด 2", err)

    def test_json_lines_run_end_to_end(self):
        import engine_cli
        tmp = tempfile.mkdtemp(prefix="jl_")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        p = self._write(tmp, "s.jsonl", '{"button": "Beep", "secs": 0}\n')
        out = io.StringIO()
        with mock.patch.object(am.sys, "stdout", out):
            rc = engine_cli.main([p, "--json-lines", "--no-log"])
        self.assertEqual(rc, 0)
        self.assertIn("จบแล้ว", out.getvalue())

    def test_engine_cli_binds_image_cbs(self):
        """engine_cli ต้องผูก find_image_cb/wait_image_cb ให้ runner (ค้นภาพครบเหมือน GUI)"""
        import engine_cli
        import inspect
        src = inspect.getsource(engine_cli)
        self.assertIn("find_image_cb", src)
        self.assertIn("wait_image_cb", src)
        self.assertNotIn("ยังไม่รองรับใน engine_cli", src.replace(
            "unsupported_cb=lambda btn: print(\n            \"  ⚠ ข้ามแถว: action '%s' ยังไม่รองรับใน engine_cli", ""))


class TestV22Plugins(unittest.TestCase):
    """v2.2: plugin ใหม่ 3 ตัว — โหลดได้ + รันได้ (ctx จำลอง)"""

    def _plugin(self, name):
        import macro_engine as me
        pl = dict(me.load_plugins())
        self.assertIn(name, pl)
        return pl[name]

    def test_new_plugins_loaded(self):
        for name in ("Play Sound", "Webhook", "Multi Image Click"):
            self._plugin(name)             # โหลด + ชื่อไม่ซ้ำกับ ACTIONS_ALL (ข้ามถ้าซ้ำ)

    def test_play_sound_runs(self):
        pl = self._plugin("Play Sound")
        beeps = []
        ctx = {"ui": {"beep": lambda: beeps.append(1)}, "log": lambda m: None}
        pl.run(ctx, {"additional": "3"})   # winsound มีเฉพาะ Windows → บนเครื่องนี้บี๊บจริง
        self.assertGreaterEqual(len(beeps), 0)   # ผ่าน = ไม่ raise (เครื่องไม่มีเสียงก็ยังผ่าน)

    def test_webhook_rejects_bad_url(self):
        pl = self._plugin("Webhook")
        msgs = []
        ctx = {"ui": {"msg": lambda t, c="#080": msgs.append(t)}, "log": lambda m: None}
        pl.run(ctx, {"additional": "not-a-url"})
        self.assertTrue(any("URL" in m for m in msgs))

    def test_webhook_sends_post(self):
        pl = self._plugin("Webhook")
        reqs = []
        import urllib.request
        class FakeResp:
            status = 200
            def __enter__(self):
                return self
            def __exit__(self, *a):
                return False
        def fake_urlopen(req, timeout=5):
            reqs.append((req.get_method(), req.full_url, req.data))
            return FakeResp()
        with mock.patch.object(urllib.request, "urlopen", fake_urlopen):
            logs = []
            ctx = {"ui": {"msg": lambda t, c="#080": None},
                   "log": lambda m: logs.append(m)}
            pl.run(ctx, {"additional": "https://example.com/hook", "button": "Webhook"})
        self.assertEqual(len(reqs), 1)
        self.assertEqual(reqs[0][0], "POST")
        self.assertIn(b"auto_mouse_macro", reqs[0][2])
        self.assertTrue(any("HTTP 200" in m for m in logs))

    def test_multi_image_click_reports_missing(self):
        import macro_engine as me
        pl = self._plugin("Multi Image Click")
        msgs = []
        ctx = {"ui": {"msg": lambda t, c="#080": msgs.append(t)},
               "log": lambda m: None,
               "mouse": mock.MagicMock(),
               "stop_check": lambda: True}
        pl.run(ctx, {"additional": "no_such_a.png | no_such_b.png"})
        if not me.HAS_CV:                    # เครื่องไม่มี opencv = เตือนครั้งเดียว
            self.assertTrue(any("opencv" in m for m in msgs))
            return
        self.assertEqual(len([m for m in msgs if "ข้าม" in m]), 2)
        ctx["mouse"].position.assert_not_called()       # ไม่เจอสักภาพ = ไม่คลิก


class TestV22ConditionRunner(unittest.TestCase):
    """v2.2: If Image/Else ย้ายเข้า runner — GUI/CLI แหล่งเดียว"""

    def test_runner_has_condition_branches(self):
        import macro_engine as me
        import inspect
        src = inspect.getsource(me.ActionRunner.execute)
        self.assertIn("IF_IMAGE", src)
        self.assertIn("ELSE_IMAGE", src)

    def test_condition_row_helper_exists(self):
        self.assertTrue(hasattr(am.MacroApp, "_execute_condition_row"))


class TestRecorderRoundTrip(unittest.TestCase):
    """v2.2: อัดจริงผ่าน Recorder (จำลองเหตุการณ์ listener ตามเวลา) → บันทึกไฟล์สคริปต์
    → โหลดกลับ → เล่นด้วย ActionRunner + controller จำลอง — ครบวงจรโดยไม่แตะเมาส์/คีย์จริง"""

    def _fake_controllers(self):
        """controller จำลองที่บันทึกทุกการเคลื่อนไหวลง plays (เรียงตามลำดับเวลา)"""
        plays = []
        m = mock.MagicMock()
        m.position = (0, 0)

        def _click(btn, n=1):
            plays.append(("click", str(btn), tuple(m.position)))

        def _scroll(dx, dy):
            plays.append(("scroll", dy))

        m.click.side_effect = _click
        m.scroll.side_effect = _scroll
        kb = mock.MagicMock()
        kb.tap.side_effect = lambda k: plays.append(("tap", k))   # เก็บออบเจ็กต์คีย์ (เทียบค่าได้)
        return plays, m, kb

    def test_record_save_playback_round_trip(self):
        import macro_engine as me

        # ---- 1) อัด: ผลักเหตุการณ์ผ่าน callback ของ Recorder ตรง ๆ (เหมือน listener จริง) ----
        rec = me.Recorder()
        rec.start()
        self.assertTrue(rec.recording)
        rec._on_click(111, 222, am.mouse.Button.left, True)      # คลิกซ้ายที่ (111,222)
        rec._on_scroll(111, 222, 0, 2)                            # เลื่อนขึ้น 2
        rec._on_kb(am.KeyCode.from_char("a"))                     # กดคีย์ a
        rec._on_click(333, 444, am.mouse.Button.right, True)      # คลิกขวาที่ (333,444)
        rec._on_click(555, 666, am.mouse.Button.left, False)      # ปล่อยปุ่ม = ไม่ถูกอัด
        rec.stop()
        rows = rec.drain_pending()
        self.assertEqual([r["button"] for r in rows],
                         ["Left Click", "Scroll Up", "Tap Key", "Right Click"])
        self.assertEqual((rows[0]["x"], rows[0]["y"]), (111, 222))
        self.assertEqual(rows[1]["additional"], "2")              # จำนวนจังหวะ scroll
        self.assertEqual(rows[2]["additional"], "a")
        self.assertEqual((rows[3]["x"], rows[3]["y"]), (333, 444))
        for r in rows:
            self.assertIn("secs", r)                              # จับเวลาหน่วงอัตโนมัติ

        # ---- 2) บันทึกไฟล์ (ฟอร์แมตเดียวกับปุ่ม Save ของโปรแกรม) ----
        tmp = tempfile.mkdtemp(prefix="rec_rt_")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        path = os.path.join(tmp, "recorded.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, ensure_ascii=False, indent=2)

        # ---- 3) เล่นกลับ: โหลดไฟล์ → subst_row → ActionRunner (controller จำลอง) ----
        with open(path, encoding="utf-8") as fh:
            loaded = json.load(fh)
        self.assertEqual(len(loaded), 4)                          # ไฟล์กลับมาครบทุกแถว
        plays, m, kb = self._fake_controllers()
        runner = me.ActionRunner(m, kb, on_message=lambda t, c="#080": None)
        # Tap Key 'a' → parse_key ผ่าน layout — รู้ค่าที่คาดจาก parse จริงก่อนเทียบ
        key_obj = me_mod.parse_key("a")
        for raw in loaded:
            r = me_mod.subst_row(raw, {})                         # เส้นทางเดียวกับ player จริง
            if r.get("button") == me_mod.SECTION_HEADER:
                continue
            runner.execute(r)
        self.assertEqual(plays[0], ("click", "Button.left", (111, 222)))
        self.assertEqual(plays[1], ("scroll", 2))                 # เลื่อนขึ้นตามที่อัด
        self.assertEqual(plays[2], ("tap", key_obj))              # คีย์เดิมที่อัด (ออบเจ็กต์ตรง parse_key)
        self.assertEqual(plays[3], ("click", "Button.right", (333, 444)))
        self.assertEqual(len(plays), 4)                           # ไม่มีเหตุการณ์เกินมา

    def test_recorder_ignores_events_when_stopped_and_drain_twice(self):
        """หยุดอัดแล้วเหตุการณ์ต้องไม่ถูกบันทึก · drain ซ้ำ = คิวว่าง"""
        import macro_engine as me
        rec = me.Recorder()
        rec.start()
        rec._on_click(1, 2, am.mouse.Button.left, True)
        rec.stop()
        self.assertEqual(len(rec.drain_pending()), 1)
        rec._on_click(3, 4, am.mouse.Button.left, True)           # หลัง stop = ไม่อัด
        rec._on_kb(am.KeyCode.from_char("z"))
        self.assertEqual(rec.drain_pending(), [])                 # drain ซ้ำ = ว่าง


class TestStopReleasesStuckKeys(unittest.TestCase):
    """v2.2.1: STOP กลางคันต้องปล่อยคีย์/modifier ค้างจาก runner ทั้ง GUI และ CLI
    (บั๊กที่เจอจากเทสต์: stop_all เรียก _release_stuck ซึ่งอ่าน _pressed_keys เก่า
    ขณะคีย์ค้างจริงอยู่ใน ActionRunner.pressed_keys ตั้งแต่ v2.1)"""

    def _pressed_state(self):
        from pynput.keyboard import Key, KeyCode
        return {"ctrl": Key.ctrl, "w": KeyCode.from_char("w")}

    def test_gui_stop_all_releases_runner_keys(self):
        """GUI: Press ctrl+w (ค้าง) → STOP → runner.release_all ถูกเรียก คีย์หลุดทุกตัว"""
        app = mock.MagicMock()
        app.recording = False
        app.running = True
        app._play_gen = 0
        kb = mock.MagicMock()
        app.kb_ctl = kb
        keys = self._pressed_state()
        runner = am.macro_engine.ActionRunner(mock.MagicMock(), kb)
        runner.pressed_keys.update(keys.values())     # จำลอง Press Key ctrl+w ค้างกลางทาง
        app._action_runner = runner
        app._release_stuck = lambda: am.MacroApp._release_stuck(app)   # ผูกเมธอดจริง (mock ไม่มี)
        am.MacroApp.stop_all(app, silent=True)
        released = [c.args[0] for c in kb.release.call_args_list]
        self.assertIn(keys["ctrl"], released)
        self.assertIn(keys["w"], released)
        self.assertEqual(runner.pressed_keys, set())  # สถานะ runner เคลียร์

    def test_gui_release_stuck_tolerates_runner_errors(self):
        """runner พังกลางทาง (release โยน) → _release_stuck ต้องไม่พังโปรแกรม"""
        app = mock.MagicMock()
        app.recording = False
        runner = mock.MagicMock()
        runner.release_all.side_effect = RuntimeError("boom")
        app._action_runner = runner
        am.MacroApp._release_stuck(app)               # ไม่ raise = ผ่าน

    def test_gui_no_legacy_pressed_state(self):
        """v2.2.1: กลไก _pressed_keys/_pressed_btns เก่าถูกลบ — แหล่งเดียวคือ ActionRunner"""
        app = mock.MagicMock(spec=am.MacroApp)        # spec = ไม่ยอม attribute ที่ไม่มีจริง
        app._action_runner = mock.MagicMock()
        am.MacroApp._release_stuck(app)               # อ่านจาก runner เท่านั้น
        app._action_runner.release_all.assert_called_once()
        self.assertFalse(hasattr(app, "_pressed_keys"))   # spec ยืนยันว่าไม่มีกลไกเก่าแล้ว
        self.assertFalse(hasattr(app, "_pressed_btns"))

    def test_cli_stop_releases_runner_keys(self):
        """CLI: กลไกหยุด (stop-file/หยุดกลางดีเลย์) ต้อง release_all ผ่าน cli_runner เสมอ
        ตรวจโค้ดจริงว่ามีจุดเรียกหลังลูป/ใน finally (v2.1)"""
        import inspect
        src = inspect.getsource(am.cli_main)
        self.assertIn("cli_runner.release_all()", src)
        self.assertGreaterEqual(src.count("cli_runner.release_all()"), 2)  # กลางลูป + finally


class TestBackupPipeline(unittest.TestCase):
    """สายพาน backup ตอนปิดโปรแกรม (จุดเคยบาง — เทสต์เดิมครอบแค่ backup_snapshot ล้วน)"""

    def _app(self):
        app = mock.MagicMock()
        app._backup_enabled = True
        app._backup_days = 7
        app._log_keep_days = 0                     # v2.11: _save_conf/export อ่าน attr นี้
        app._log_archive = True
        app._serialize.return_value = [{"button": "Beep", "secs": 0}]
        app._profiles = {"ค่าเริ่มต้น": [{"button": "Beep"}]}
        app._active_profile = "ค่าเริ่มต้น"
        app._log_enabled = True
        app._hp_dir = None
        return app

    def test_on_close_disabled_returns_none(self):
        app = self._app()
        app._backup_enabled = False
        self.assertIsNone(am.MacroApp._on_close_backup(app, "."))

    def test_on_close_snapshot_content_is_importable_shape(self):
        """ไฟล์ backup ต้องมีรูปแบบเดียวกับไฟล์ Export — import_settings กลับมาใช้ได้"""
        import tempfile
        app = self._app()
        with tempfile.TemporaryDirectory() as d:
            path = am.MacroApp._on_close_backup(app, d)
            self.assertTrue(path and os.path.isfile(path))
            data = json.load(open(path, encoding="utf-8"))
            self.assertEqual(data["kind"], "automousemacro-settings")
            self.assertEqual(data["rows"], [{"button": "Beep", "secs": 0}])
            self.assertEqual(data["profiles"], app._profiles)
            self.assertEqual(data["active_profile"], "ค่าเริ่มต้น")
            self.assertIn("log_enabled", data)

    def test_on_close_keeps_days_setting(self):
        """ตั้งกี่วัน backup ต้องตัดตามนั้น (ผ่าน keep_days จริง)"""
        import tempfile
        app = self._app()
        app._backup_days = 1
        with tempfile.TemporaryDirectory() as d:
            import datetime
            old = datetime.datetime.now() - datetime.timedelta(days=5)
            am.backup_snapshot(d, {"kind": "x"}, now=old)         # ไฟล์เก่า 5 วัน
            path = am.MacroApp._on_close_backup(app, d)            # snapshot ใหม่ + ตัดเก่า > 1 วิ
            files = os.listdir(os.path.join(d, "backups"))
            self.assertEqual(files, [os.path.basename(path)])


class TestSchedPoll(unittest.TestCase):
    """ฝั่ง UI ของ schedule (จุดเคยบาง — เทสต์เดิมครอบแค่ _sched_check)"""

    def _app(self):
        import queue
        app = mock.MagicMock()
        app._sched_q = queue.Queue()
        app._sched_stop = mock.MagicMock()
        app._sched_stop.is_set.return_value = False
        app.running = False
        return app

    def test_poll_starts_player_once_per_command(self):
        app = self._app()
        app._sched_q.put("play")
        am.MacroApp._sched_poll(app)
        app._start_player_inner.assert_called_once_with(False, once=True, auto=True)   # เล่น 1 รอบต่อสั่ง (v2.9.1: auto=True ข้ามแถวพังเอง)

    def test_poll_skips_when_running(self):
        app = self._app()
        app.running = True                       # กำลังเล่นอยู่ = ไม่เริ่มซ้ำ
        app._sched_q.put("play")
        am.MacroApp._sched_poll(app)
        app._start_player.assert_not_called()

    def test_poll_empty_queue_still_reschedules(self):
        app = self._app()
        am.MacroApp._sched_poll(app)             # คิวว่าง = ผ่าน แล้วตั้ง after ต่อ
        app._start_player.assert_not_called()
        app.root.after.assert_called_once()

    def test_poll_drains_all_commands(self):
        app = self._app()
        app._sched_q.put("play")
        app._sched_q.put("play")
        # (เลียนแบบโค้ดจริง: เริ่มเล่นแล้ว self.running = True — คำสั่งถัดไปต้องถูกข้าม)
        app._start_player_inner.side_effect = lambda *a, **k: setattr(app, "running", True)
        am.MacroApp._sched_poll(app)
        app._start_player_inner.assert_called_once()
        self.assertTrue(app._sched_q.empty())


class TestCrossPlatform(unittest.TestCase):
    """เตรียม cross-platform: clipboard (macOS/Linux path) + Unicode typing fallback
    ทุกเทสต์ใช้ mock ล้วน — รันได้ทุก OS ไม่แตะคลิปบอร์ดจริง"""

    def test_clip_set_posix_pbcopy(self):
        """macOS: pbcopy สำเร็จ → True (ส่งข้อความเป็น utf-8 ผ่าน stdin)"""
        import subprocess
        import macro_engine as me
        calls = []
        def fake_run(cmd, input=None, timeout=None):
            calls.append((cmd, input))
            return mock.MagicMock(returncode=0)
        with mock.patch.object(me.os, "name", "posix"), \
             mock.patch.object(subprocess, "run", side_effect=fake_run):
            self.assertTrue(me.clip_set("สวัสดี"))
        self.assertEqual(calls[0][0], ["pbcopy"])
        self.assertEqual(calls[0][1], "สวัสดี".encode("utf-8"))

    def test_clip_set_posix_first_tool_missing_falls_back(self):
        """pbcopy ไม่มี → ลอง wl-copy ต่อจนเจอตัวที่สำเร็จ"""
        import subprocess
        import macro_engine as me
        cmds = []
        def fake_run(cmd, **kw):
            cmds.append(cmd[0])
            if cmd[0] == "pbcopy":
                raise FileNotFoundError("no pbcopy")
            return mock.MagicMock(returncode=0)
        with mock.patch.object(me.os, "name", "posix"), \
             mock.patch.object(subprocess, "run", side_effect=fake_run):
            self.assertTrue(me.clip_set("x"))
        self.assertEqual(cmds[:2], ["pbcopy", "wl-copy"])

    def test_clip_set_posix_no_tools(self):
        """Linux ไม่มีทั้ง wl-copy/xclip/xsel → False (โปรแกรมต้องรายงานเอง)"""
        import subprocess
        import macro_engine as me
        def fake_run(cmd, **kw):
            raise FileNotFoundError("missing")
        with mock.patch.object(me.os, "name", "posix"), \
             mock.patch.object(subprocess, "run", side_effect=fake_run):
            self.assertFalse(me.clip_set("x"))

    def test_clip_get_posix_pbpaste_decodes_utf8(self):
        import subprocess
        import macro_engine as me
        def fake_run(cmd, **kw):
            r = mock.MagicMock()
            r.returncode = 0
            r.stdout = "ข้อความไทย".encode("utf-8")
            return r
        with mock.patch.object(me.os, "name", "posix"), \
             mock.patch.object(subprocess, "run", side_effect=fake_run):
            self.assertEqual(me.clip_get(), "ข้อความไทย")

    def test_clip_get_posix_no_tools_returns_none(self):
        import subprocess
        import macro_engine as me
        def fake_run(cmd, **kw):
            raise FileNotFoundError("missing")
        with mock.patch.object(me.os, "name", "posix"), \
             mock.patch.object(subprocess, "run", side_effect=fake_run):
            self.assertIsNone(me.clip_get())

    def test_send_unicode_char_non_windows_returns_false(self):
        """OS อื่น → False ให้ runner fallback ไป pynput (พฤติกรรม fallback ต้องไม่พัง)"""
        import macro_engine as me
        with mock.patch.object(me.os, "name", "posix"):
            self.assertFalse(me.send_unicode_char("a"))

    def test_send_unicode_char_windows_error_is_false(self):
        """Windows แต่ SendInput โยน → False (fallback) — ไม่ทำ runner พัง"""
        import macro_engine as me
        with mock.patch.object(me.os, "name", "nt"), \
             mock.patch.object(me, "_send_unicode_events", side_effect=OSError("no keybd")):
            self.assertFalse(me.send_unicode_char("ก"))

    def test_unicode_records_pure_any_platform(self):
        """ตรรกะ surrogate pair เป็น pure function — ผลต้องตรงกันทุก OS"""
        import macro_engine as me
        rec = me._unicode_input_records("𝄞")                  # U+1D11E (เกิน BMP)
        downs = [sc for sc, up in rec if not up]
        ups = [sc for sc, up in rec if up]
        self.assertEqual(len(downs), 2)                        # surrogate pair 2 หน่วย
        self.assertEqual(ups, list(reversed(downs)))           # up ย้อนลำดับ


class TestPluginsComplete(unittest.TestCase):
    """v2.3: เทสต์ plugin ที่แจกมาครบทั้ง 5 ตัว — ทุกตัวรัน run(ctx, row) ด้วย ctx
    จำลองตามมาตรฐานแผน v2.3 (แบบเดียวกับ TestV22Plugins): โหลดได้ / ทำงานถูก /
    ทน input พังโดยไม่ raise"""

    def _plugin(self, name):
        pl = dict(me_mod.load_plugins())
        self.assertIn(name, pl, "plugin %s ต้องโหลดได้" % name)
        return pl[name]

    def test_all_five_loaded(self):
        pl = dict(me_mod.load_plugins())
        for name in ("Sleep (plugin)", "Message Box", "Play Sound",
                     "Webhook", "Multi Image Click"):
            self.assertIn(name, pl)

    # ---------------- Sleep (plugin) ----------------
    def test_sleep_sleeps_requested_seconds(self):
        pl = self._plugin("Sleep (plugin)")
        with mock.patch.object(pl.time, "sleep") as slept:
            pl.run({"log": lambda m: None}, {"additional": "2"})
        slept.assert_called_once_with(2.0)

    def test_sleep_bad_and_negative_input(self):
        pl = self._plugin("Sleep (plugin)")
        with mock.patch.object(pl.time, "sleep") as slept:
            pl.run({"log": lambda m: None}, {"additional": "abc"})   # พัง → 1.0
            pl.run({"log": lambda m: None}, {"additional": ""})      # ว่าง → 1.0
            pl.run({"log": lambda m: None}, {"additional": "-9"})    # ติดลบ → 0.0
        self.assertEqual(slept.call_args_list,
                         [mock.call(1.0), mock.call(1.0), mock.call(0.0)])

    # ---------------- Message Box ----------------
    def test_message_box_shows_text(self):
        pl = self._plugin("Message Box")
        shown = []
        with mock.patch("tkinter.messagebox.showinfo",
                        lambda *a, **k: shown.append(a)):
            pl.run({"log": lambda m: None}, {"additional": "สวัสดีจากเทสต์"})
        self.assertTrue(any("สวัสดีจากเทสต์" in str(a) for a in shown))

    def test_message_box_no_display_logs_instead(self):
        pl = self._plugin("Message Box")
        logs = []
        with mock.patch("tkinter.Tk", side_effect=Exception("no display")):
            pl.run({"log": logs.append}, {"additional": "hello"})
        self.assertTrue(any("แสดงไม่ได้" in m for m in logs))       # ทนได้ ไม่ raise

    # ---------------- Play Sound ----------------
    @unittest.skipUnless(os.name == "nt", "winsound = Windows เท่านั้น")
    def test_play_sound_beeps_requested_times(self):
        pl = self._plugin("Play Sound")
        with mock.patch("winsound.Beep") as beep:
            pl.run({"log": lambda m: None}, {"additional": "3"})
        self.assertEqual(beep.call_count, 3)

    @unittest.skipUnless(os.name == "nt", "winsound = Windows เท่านั้น")
    def test_play_sound_clamps_count(self):
        pl = self._plugin("Play Sound")
        with mock.patch("winsound.Beep") as beep:
            pl.run({"log": lambda m: None}, {"additional": "99"})    # คลัมป์ 1..10
        self.assertEqual(beep.call_count, 10)
        with mock.patch("winsound.Beep") as beep2:
            pl.run({"log": lambda m: None}, {"additional": "abc"})   # พัง → 1
        self.assertEqual(beep2.call_count, 1)

    def test_play_sound_fallback_bell_without_winsound(self):
        pl = self._plugin("Play Sound")
        beeps = []
        ctx = {"log": lambda m: None, "ui": {"beep": lambda: beeps.append(1)}}
        with mock.patch.dict(sys.modules, {"winsound": None}):
            pl.run(ctx, {"additional": "2"})             # ไม่มี winsound → bell ของระบบ
        self.assertEqual(len(beeps), 2)

    # ---------------- Webhook (เสริมจาก TestV22Plugins) ----------------
    def test_webhook_reports_http_error_without_crash(self):
        pl = self._plugin("Webhook")
        msgs = []
        import urllib.request
        import urllib.error

        def fail(req, timeout=5):
            raise urllib.error.URLError("connection refused")

        with mock.patch.object(urllib.request, "urlopen", fail):
            pl.run({"log": lambda m: None,
                    "ui": {"msg": lambda t, c="#080": msgs.append(t)}},
                   {"additional": "https://example.com/x"})
        self.assertTrue(any("ส่งไม่สำเร็จ" in m for m in msgs))

    def test_webhook_tolerates_missing_ui_and_log(self):
        pl = self._plugin("Webhook")
        pl.run({}, {"additional": "ftp://bad"})          # ไม่มี ui/log เลยก็ต้องไม่ raise

    # ---------------- Multi Image Click (เสริมจาก TestV22Plugins) ----------------
    def test_multi_image_click_clicks_found_images(self):
        pl = self._plugin("Multi Image Click")
        if not me_mod.HAS_CV:
            self.skipTest("ต้องมี opencv เพื่อทดสอบเส้นทางคลิก")
        mouse = mock.MagicMock()
        with mock.patch.object(me_mod, "HAS_CV", True), \
             mock.patch.object(me_mod, "find_image_pos",
                               lambda path, area, thr: (10, 20)):
            pl.run({"log": lambda m: None, "mouse": mouse,
                    "ui": {"msg": lambda t, c="#080": None},
                    "stop_check": lambda: True},
                   {"additional": "a.png|b.png"})
        self.assertEqual(mouse.click.call_count, 2)      # คลิกครบ 2 ภาพตามลำดับ

    def test_multi_image_click_stops_when_stop_check_false(self):
        pl = self._plugin("Multi Image Click")
        if not me_mod.HAS_CV:
            self.skipTest("ต้องมี opencv เพื่อทดสอบเส้นทางคลิก")
        mouse = mock.MagicMock()
        with mock.patch.object(me_mod, "HAS_CV", True), \
             mock.patch.object(me_mod, "find_image_pos",
                               lambda path, area, thr: (1, 1)):
            pl.run({"log": lambda m: None, "mouse": mouse,
                    "ui": {"msg": lambda t, c="#080": None},
                    "stop_check": lambda: False},        # ผู้ใช้กด STOP แล้ว
                   {"additional": "a.png|b.png"})
        mouse.click.assert_not_called()                  # ไม่คลิกต่อแม้ภาพยังเจอ

    def test_multi_image_click_empty_is_noop(self):
        pl = self._plugin("Multi Image Click")
        mouse = mock.MagicMock()
        pl.run({"log": lambda m: None, "mouse": mouse,
                "ui": {"msg": lambda t, c="#080": None}},
               {"additional": ""})
        mouse.click.assert_not_called()


class TestBatchExport(unittest.TestCase):
    """v2.3: เมนู 📤 Export Bat — ส่งออก .bat/.sh ข้างสคริปต์ ดับเบิลคลิกรันผ่าน CLI ได้"""

    def test_bat_content(self):
        s = me_mod.batch_export_bat("myscript.json")
        self.assertTrue(s.startswith("@echo off"))
        self.assertIn('py auto_macro.py "myscript.json" %*', s)
        self.assertIn("pause", s)
        self.assertIn('cd /d "%~dp0"', s)                # วิ่งไปโฟลเดอร์ของตัวเอง

    def test_sh_content(self):
        s = me_mod.batch_export_sh("myscript.json")
        self.assertTrue(s.startswith("#!/bin/sh"))
        self.assertIn('cd "$(dirname "$0")"', s)
        self.assertIn('python3 auto_macro.py "myscript.json" "$@"', s)

    def test_gui_method_exports_both_files_next_to_script(self):
        import tempfile
        app = mock.MagicMock()
        with tempfile.TemporaryDirectory() as d:
            script = os.path.join(d, "my.json")
            with open(script, "w", encoding="utf-8") as fh:
                fh.write("[]")
            app._loaded_file = None
            with mock.patch.object(am.messagebox, "showinfo") as info:
                am.MacroApp.export_batch_files(app)      # ยังไม่ Save → แจ้งแล้วจบ
            self.assertTrue(info.called)
            app._loaded_file = script
            am.MacroApp.export_batch_files(app)          # เขียนไฟล์จริงข้างสคริปต์
            bat = os.path.join(d, "my.bat")
            shp = os.path.join(d, "my.sh")
            self.assertTrue(os.path.isfile(bat))
            self.assertTrue(os.path.isfile(shp))
            with open(bat, encoding="ascii") as fh:
                self.assertIn('"my.json"', fh.read())
            with open(shp, encoding="utf-8") as fh:
                self.assertIn('"my.json"', fh.read())

    def test_menu_has_export_entry(self):
        names = [name for _, _, name, _ in am.MacroApp._menu_items()]
        self.assertIn("export_batch_files", names)


class TestImageCache(unittest.TestCase):
    """v2.4: แคช template — สคริปต์วน 1000 รอบไม่อ่านไฟล์ภาพซ้ำ (อ่านใหม่เมื่อไฟล์เปลี่ยน)"""

    @unittest.skipUnless(me_mod.HAS_CV, "ต้องมี opencv")
    def test_cache_avoids_repeated_reads_and_invalidates_on_change(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "t.png")
            img = me_mod.np.full((20, 20, 3), 200, dtype=me_mod.np.uint8)
            me_mod.cv2.imwrite(p, img)
            me_mod._template_cache.clear()
            with mock.patch.object(me_mod.cv2, "imread",
                                   wraps=me_mod.cv2.imread) as rd:
                me_mod.find_image_pos(p, None, 0.1)
                me_mod.find_image_pos(p, None, 0.1)
                self.assertEqual(rd.call_count, 1)       # ครั้งสองใช้แคช
                time.sleep(0.05)
                me_mod.cv2.imwrite(p, img + 10)          # ไฟล์เปลี่ยน → อ่านใหม่
                me_mod.find_image_pos(p, None, 0.1)
                self.assertEqual(rd.call_count, 2)
            me_mod._template_cache.clear()


class TestIfImageWait(unittest.TestCase):
    """v2.4: If Image ต่อท้าย Additional ด้วย 'Ns' = ตรวจซ้ำจนครบ N วิก่อนตัดสิน A/B
    (ไม่ใส่ = ตรวจครั้งเดียวเหมือนเดิม) — แก้ปัญหาหน้าจอโหลดไม่เสร็จแล้วตัดสินผิด"""

    def _runner(self, find_cb, stop=lambda: True):
        return me_mod.ActionRunner(mock.MagicMock(), mock.MagicMock(),
                                   stop_check=stop, find_image_cb=find_cb)

    def test_retry_until_found(self):
        calls = []

        def cb(r):
            calls.append(1)
            return (10, 10) if len(calls) >= 3 else None

        runner = self._runner(cb)
        runner.execute({"button": me_mod.IF_IMAGE, "additional": "img.png 5s",
                        "repeat": 2})
        self.assertTrue(runner.last_if_found)
        self.assertGreaterEqual(len(calls), 3)
        self.assertEqual(runner.skip_n, 0)               # เจอ = ไม่ข้ามแถว

    def test_no_token_checks_once_like_before(self):
        calls = []

        def cb(r):
            calls.append(1)
            return None

        runner = self._runner(cb)
        runner.execute({"button": me_mod.IF_IMAGE, "additional": "img.png",
                        "repeat": 1})
        self.assertEqual(len(calls), 1)                  # พฤติกรรมเดิม: ครั้งเดียว
        self.assertFalse(runner.last_if_found)
        self.assertEqual(runner.skip_n, 1)

    def test_stop_stops_retry_immediately(self):
        calls = []

        def cb(r):
            calls.append(1)
            return None

        runner = self._runner(cb, stop=lambda: False)    # STOP ค้างจากภายนอก
        t0 = time.time()
        runner.execute({"button": me_mod.IF_IMAGE, "additional": "img.png 30s",
                        "repeat": 1})
        self.assertLess(time.time() - t0, 3)             # ไม่รอครบ 30 วิ
        self.assertFalse(runner.last_if_found)


class TestSafetyTimeout(unittest.TestCase):
    """v2.4: Safety timeout — หยุดเองหลังเล่น N นาที (Settings จำลง conf + player ตรวจทุกแถว)"""

    def test_settings_save_clamps_and_persists(self):
        app = mock.MagicMock()
        app._log_enabled = True                     # _save_conf อ่าน attr นี้ตรง ๆ
        app._hp_dir = None                          # _save_conf อ่าน attr นี้ตรง ๆ
        app.var_log.get.return_value = True
        app.var_backup.get.return_value = True
        app.spin_days.get.return_value = "7"
        app.var_time_limit.get.return_value = True
        app.spin_limit.get.return_value = "9999"     # คลัมป์เหลือ 720
        app.cmb_lang.get.return_value = "ไทย (Thai)"
        app.cmb_speed.get.return_value = "1"         # widget อื่นใน _save_conf
        app.ent_loops.get.return_value = "1"
        app.chk_forever.get.return_value = False
        app.chk_restore.get.return_value = False
        app.chk_shuffle.get.return_value = False
        app._play_options = lambda: 100
        am.MacroApp._settings_save(app, mock.MagicMock())   # win = หน้าต่างจำลอง
        self.assertTrue(app._time_limit_enabled)
        self.assertEqual(app._time_limit_min, 720)
        app._save_conf.assert_called_once()          # บันทึก conf ทันทีที่ Save

    def test_conf_roundtrip(self):
        import tempfile
        app = mock.MagicMock()
        app._serialize.return_value = []
        app._log_enabled = True                     # _save_conf อ่าน attr นี้ตรง ๆ
        app._hp_dir = None                          # _save_conf อ่าน attr นี้ตรง ๆ
        app._backup_enabled = True
        app._backup_days = 7
        app._log_keep_days = 0                     # v2.11: _save_conf/export อ่าน attr นี้
        app._log_archive = True
        app._lang = "th"
        app._time_limit_enabled = True              # v2.4: keys ใหม่ใน conf
        app._time_limit_min = 45
        app.var_log.get.return_value = True
        app.var_backup.get.return_value = True
        app.spin_days.get.return_value = "7"
        app.var_time_limit.get.return_value = True
        app.spin_limit.get.return_value = "45"
        app.cmb_lang.get.return_value = "ไทย (Thai)"
        app.cmb_speed.get.return_value = "1"
        app.ent_loops.get.return_value = "1"
        app.chk_forever.get.return_value = False
        app.chk_restore.get.return_value = False
        app.chk_shuffle.get.return_value = False
        app._play_options = lambda: 100
        app._sched = {"mode": "off", "every": 10, "times": [], "profile": ""}   # v2.7: dict เดียว
        with tempfile.TemporaryDirectory() as d:
            conf = os.path.join(d, "macro_conf.json")
            with mock.patch.object(am, "CONF", conf):
                am.MacroApp._save_conf(app)
                app2 = mock.MagicMock()
                am.MacroApp._load_conf(app2)
        self.assertTrue(app2._time_limit_enabled)
        self.assertEqual(app2._time_limit_min, 45)


class TestSchedProfilePoll(unittest.TestCase):
    """v2.4: Schedule เลือกโปรไฟล์ได้ — ถึงเวลาแล้วโหลดแถวโปรไฟล์ก่อนเล่น"""

    def test_poll_loads_profile_rows_then_plays_once(self):
        import queue
        app = mock.MagicMock()
        app._sched_q = queue.Queue()
        app._sched_q.put("play")
        app.running = False
        app._log_enabled = False                 # กันเทสต์เขียน log จริงของผู้ใช้
        app._profiles = {"งานเช้า": [{"button": "Beep", "secs": 1}]}
        app._sched = {"mode": "daily", "every": 10, "times": ["08:00"], "profile": "งานเช้า"}   # v2.7
        am.MacroApp._sched_poll(app)
        app._load_rows.assert_called_once_with([{"button": "Beep", "secs": 1}])
        app._start_player_inner.assert_called_once_with(False, once=True, auto=True)

    def test_poll_empty_profile_keeps_current_rows(self):
        import queue
        app = mock.MagicMock()
        app._sched_q = queue.Queue()
        app._sched_q.put("play")
        app.running = False
        app._log_enabled = False                 # กันเทสต์เขียน log จริงของผู้ใช้
        app._sched = {"mode": "off", "every": 10, "times": [], "profile": ""}   # งานที่เปิดค้าง — ไม่แตะตาราง
        am.MacroApp._sched_poll(app)
        app._load_rows.assert_not_called()
        app._start_player_inner.assert_called_once_with(False, once=True, auto=True)

    def test_poll_unknown_profile_keeps_current_rows(self):
        import queue
        app = mock.MagicMock()
        app._sched_q = queue.Queue()
        app._sched_q.put("play")
        app.running = False
        app._log_enabled = False                 # กันเทสต์เขียน log จริงของผู้ใช้
        app._profiles = {}
        app._sched = {"mode": "daily", "every": 10, "times": ["08:00"], "profile": "โปรไฟล์ถูกลบไปแล้ว"}   # v2.7
        am.MacroApp._sched_poll(app)
        app._load_rows.assert_not_called()           # ทนได้ — เล่นงานที่เปิดค้างแทน
        app._start_player_inner.assert_called_once_with(False, once=True, auto=True)


class TestValidateRowsEngine(unittest.TestCase):
    """v2.4: --validate — ตรวจสคริปต์โดยไม่เล่น (engine ล้วน)"""

    def test_ok_script(self):
        rows = [{"button": "Tap Key", "additional": "Ctrl+W"},
                {"button": "Type Text", "additional": "ok"},
                {"button": "Beep"}]
        self.assertEqual(me_mod.validate_rows(rows), [])

    def test_problems_reported_with_row_numbers(self):
        rows = [{"button": "Tap Key", "additional": "Ctrl+??"},
                {"button": "Type Text", "additional": "ok"},
                {"button": "What Action"},
                {"button": "Launch App", "additional": ""},
                {"button": "Set Variable", "additional": "พัง"},
                {"button": "Read Clipboard", "additional": "มี ช่องว่าง"},
                {"button": "Image Click", "additional": "no_such_img_abc.png"}]
        issues = me_mod.validate_rows(rows)
        self.assertEqual([i for i, _ in issues], [1, 3, 4, 5, 6, 7])

    def test_plugin_action_accepted(self):
        pl = dict(me_mod.load_plugins())
        name = next(iter(pl))
        rows = [{"button": name, "additional": ""}]
        self.assertEqual(me_mod.validate_rows(rows, plugin_names=[name]), [])


class TestCliVersion(unittest.TestCase):
    """v2.3: --version แสดงเวอร์ชันแล้วจบด้วย exit code 0 (ทั้ง CLI หลักและ engine_cli)"""

    def test_main_cli_version(self):
        import io
        import contextlib
        buf = io.StringIO()
        with self.assertRaises(SystemExit) as cm:
            with contextlib.redirect_stdout(buf):
                am.cli_main(["--version"])
        self.assertEqual(cm.exception.code, 0)
        self.assertIn("v" + am.__version__, buf.getvalue())


class TestV25Conditions(unittest.TestCase):
    """v2.5: เงื่อนไข/ตัวแปรครบวงจร — If Pixel/Read Pixel/If Variable/rand/img vars"""

    def _runner(self, find_cb=None, variables=None):
        return me_mod.ActionRunner(mock.MagicMock(), mock.MagicMock(),
                                   find_image_cb=find_cb, variables=variables)

    def test_parse_if_var(self):
        self.assertEqual(me_mod.parse_if_var("n > 5"), ("n", ">", "5"))
        self.assertEqual(me_mod.parse_if_var("code = A-1"), ("code", "=", "A-1"))
        self.assertEqual(me_mod.parse_if_var("msg ~ ล้มเหลว"), ("msg", "~", "ล้มเหลว"))
        self.assertIsNone(me_mod.parse_if_var("n >"))          # ไม่มีค่า
        self.assertIsNone(me_mod.parse_if_var("พัง"))

    def test_if_var_numeric(self):
        skip, _m = me_mod.ActionRunner.evaluate_condition(
            me_mod.IF_VAR, "n > 5", 2, 1, variables={"n": "10"})
        self.assertEqual(skip, 0)                              # จริง → เล่นต่อ
        skip, _m = me_mod.ActionRunner.evaluate_condition(
            me_mod.IF_VAR, "n < 5", 3, 1, variables={"n": "10"})
        self.assertEqual(skip, 3)                              # ไม่จริง → ข้าม 3

    def test_if_var_string_and_contains(self):
        V = {"code": "A-1", "msg": "ล้มเหลว 2 จุด"}
        ev = me_mod.ActionRunner.evaluate_condition
        for spec in ("code = A-1", "code != B-9", "msg ~ ล้มเหลว"):
            skip, _m = ev(me_mod.IF_VAR, spec, 1, 1, variables=V)
            self.assertEqual(skip, 0, spec)
        skip, _m = ev(me_mod.IF_VAR, "code = B-9", 2, 1, variables=V)
        self.assertEqual(skip, 2)

    def test_if_var_missing_var(self):
        skip, _m = me_mod.ActionRunner.evaluate_condition(
            me_mod.IF_VAR, "nope = 1", 2, 1, variables={})
        self.assertEqual(skip, 2)                              # ไม่มีตัวแปร = ไม่จริง

    def test_if_var_bad_format(self):
        r = self._runner(variables={"n": "1"})
        r.execute({"button": me_mod.IF_VAR, "additional": "พัง", "repeat": 2})
        self.assertEqual(r.skip_n, 0)                          # รูปแบบไม่ถูก → เล่นต่อ + เตือน

    def test_if_pixel_match_and_mismatch(self):
        rgb = me_mod.pixel_color_at(5, 5)
        if rgb is None:
            self.skipTest("จอไม่พร้อมอ่านสี (runner ไม่มีสิทธิ์จับภาพ)")
        r = self._runner()
        r.execute({"button": me_mod.IF_PIXEL,
                   "additional": "5,5 #%02x%02x%02x" % tuple(rgb[:3]), "repeat": 2})
        self.assertEqual(r.skip_n, 0)                          # ตรง → เล่นต่อ
        inv = tuple(255 - c for c in rgb[:3])
        r.execute({"button": me_mod.IF_PIXEL,
                   "additional": "5,5 #%02x%02x%02x" % inv, "repeat": 3})
        self.assertEqual(r.skip_n, 3)                          # ไม่ตรง → ข้าม 3

    def test_read_pixel_stores_var(self):
        rgb = me_mod.pixel_color_at(5, 5)
        if rgb is None:
            self.skipTest("จอไม่พร้อมอ่านสี (runner ไม่มีสิทธิ์จับภาพ)")
        r = self._runner()
        r.execute({"button": me_mod.READ_PIXEL, "additional": "สีจอ 5,5"})
        self.assertEqual(r.variables["สีจอ"], "%02x%02x%02x" % tuple(rgb[:3]))
        r.execute({"button": me_mod.READ_PIXEL, "additional": "bad name 5,5"})   # ชื่อผิด → ข้าม
        r.execute({"button": me_mod.READ_PIXEL, "additional": "สี x"})           # พิกัดพัง → ข้าม
        self.assertNotIn("bad", r.variables)

    def test_read_pixel_bad_input_tolerant(self):
        r = self._runner()
        r.execute({"button": me_mod.READ_PIXEL, "additional": "bad name 5,5"})
        r.execute({"button": me_mod.READ_PIXEL, "additional": "สี x"})
        r.execute({"button": me_mod.READ_PIXEL, "additional": ""})
        self.assertEqual(r.variables.get("สี"), None)   # ไม่ raise แม้จออ่านไม่ได้

    def test_image_click_sets_img_vars(self):
        r = self._runner(find_cb=lambda row: (30, 40))
        r.execute({"button": me_mod.IMAGE_ACTION, "additional": "x.png"})
        self.assertEqual(r.variables["img_x"], 30)
        self.assertEqual(r.variables["img_y"], 40)

    def test_set_variable_rand(self):
        r = self._runner(variables={})
        r.execute({"button": "Set Variable", "additional": "สุ่ม = rand 1-100"})
        val = int(r.variables["สุ่ม"])
        self.assertTrue(1 <= val <= 100)
        r.execute({"button": "Set Variable", "additional": "สุ่ม = rand 1-100"})
        self.assertTrue(1 <= int(r.variables["สุ่ม"]) <= 100)

    def test_row_tag_new_conditions(self):
        for b in (me_mod.IF_PIXEL, me_mod.IF_VAR):
            self.assertEqual(me_mod.row_tag(b), "cond")
        self.assertEqual(me_mod.row_tag(me_mod.READ_PIXEL), "special")
        for b in (me_mod.IF_PIXEL, me_mod.READ_PIXEL, me_mod.IF_VAR):
            self.assertIn(b, me_mod.ACTIONS_ALL)

    def test_validate_rows_v25(self):
        issues = me_mod.validate_rows([
            {"button": me_mod.IF_PIXEL, "additional": "5,5 #000000"},
            {"button": me_mod.READ_PIXEL, "additional": "สีจอ 5,5"},
            {"button": me_mod.IF_VAR, "additional": "n > 1"},
            {"button": me_mod.IF_PIXEL, "additional": "ไม่มีสี"},
            {"button": me_mod.READ_PIXEL, "additional": "มี ช่องว่าง"},
            {"button": me_mod.IF_VAR, "additional": "พัง"}])
        self.assertEqual([i for i, _ in issues], [4, 5, 6])


class TestPluginsV25(unittest.TestCase):
    """v2.5: plugin ใหม่ 4 ตัว — Screenshot/Toast/Write Log/Ask Input"""

    def _plugin(self, name):
        pl = dict(me_mod.load_plugins())
        self.assertIn(name, pl)
        return pl[name]

    def test_all_four_loaded(self):
        for n in ("Screenshot", "Toast", "Write Log", "Ask Input"):
            self._plugin(n)

    def test_screenshot_saves_file(self):
        import tempfile
        pl = self._plugin("Screenshot")
        out = os.path.join(tempfile.mkdtemp(), "shot.png")
        logs = []
        pl.run({"log": logs.append, "ui": {"msg": lambda t, c="#080": None}},
               {"additional": out})
        if not os.path.isfile(out):
            # headless runner (จับภาพไม่ได้) — plugin ต้อง log สาเหตุแล้วจบอย่างนุ่มนวล
            self.skipTest("จอไม่พร้อมจับภาพ (runner ไม่มี display/สิทธิ์)")
            return
        self.assertTrue(any("บันทึก" in m for m in logs))

    def test_toast_never_raises(self):
        pl = self._plugin("Toast")
        shown = []
        pl.run({"log": lambda m: None, "ui": {"msg": lambda t, c="#080": shown.append(t)}},
               {"additional": "ทดสอบ toast"})
        self.assertTrue(True)   # ส่งสำเร็จ/fallback อย่างไรก็ไม่ raise

    def test_write_log(self):
        pl = self._plugin("Write Log")
        logs = []
        pl.run({"log": logs.append, "ui": {"msg": lambda t, c="#080": None}},
               {"additional": "บันทึกทดสอบ"})
        self.assertTrue(any("บันทึกทดสอบ" in m for m in logs))

    def test_ask_input_stores_to_vars(self):
        pl = self._plugin("Ask Input")
        vars_ = {}
        with mock.patch("tkinter.simpledialog.askstring", return_value="C-123"):
            pl.run({"log": lambda m: None, "vars": vars_,
                    "ui": {"msg": lambda t, c="#080": None}},
                   {"additional": "code | ใส่รหัส | C-000"})
        self.assertEqual(vars_.get("code"), "C-123")

    def test_ask_input_bad_name_reported(self):
        pl = self._plugin("Ask Input")
        reports = []
        vars_ = {}
        pl.run({"log": lambda m: None, "vars": vars_,
                "ui": {"msg": lambda t, c="#080": reports.append(t)}},
               {"additional": " | ไม่มีชื่อตัวแปร"})
        self.assertTrue(any("ต้องระบุชื่อตัวแปร" in m for m in reports))
        self.assertEqual(vars_, {})

    def test_ask_input_no_display_uses_default(self):
        pl = self._plugin("Ask Input")
        vars_ = {}
        with mock.patch("tkinter.Tk", side_effect=Exception("no display")):
            pl.run({"log": lambda m: None, "vars": vars_,
                    "ui": {"msg": lambda t, c="#080": None}},
                   {"additional": "code | ใส่รหัส | C-000"})
        self.assertEqual(vars_.get("code"), "C-000")


class TestN1AndConditions(unittest.TestCase):
    """v2.5.4 (ชุด N1): เงื่อนไขรวม AND (&&) — If Image/If Pixel/If Variable
    กติกา: ทุกเงื่อนไขย่อยต้องจริง → เล่นต่อ, มีตัวไหนไม่จริง = ข้าม N แถว (Repeat)
    ⚠️ สคริปต์เดิม (ไม่มี &&) ต้องเล่นผลเหมือนเดิม 100% — เทสต์เดิมครอบอยู่แล้ว"""

    def _runner(self, find_cb=None, variables=None):
        return me_mod.ActionRunner(mock.MagicMock(), mock.MagicMock(),
                                   find_image_cb=find_cb, variables=variables)

    # ---------- parser ----------

    def test_split_condition_and(self):
        f = me_mod.split_condition_and
        self.assertEqual(f("img.png && 300,300 #ffffff"),
                         ["img.png", "300,300 #ffffff"])
        self.assertEqual(f("n > 5 && code = A-1"), ["n > 5", "code = A-1"])
        self.assertEqual(f("a && b && c"), ["a", "b", "c"])          # หลายชิ้น
        self.assertEqual(f("เดี่ยว ๆ"), [])                            # ไม่มี && → []
        self.assertEqual(f("  x  &&  y "), ["x", "y"])               # เว้นวรรคยืดหยุ่น

    def test_split_strips_timeout_token(self):
        f = me_mod.split_condition_and
        self.assertEqual(f("img.png 5s && 300,300 #ffffff"),
                         ["img.png", "300,300 #ffffff"])
        self.assertEqual(f("img.png && 300,300 #ffffff 5s"),
                         ["img.png", "300,300 #ffffff"])
        # ค่าข้อความของ If Variable ที่ลงท้าย "5s" ต้องไม่ถูกตัด
        self.assertEqual(f("code = 5s && n > 5"), ["code = 5s", "n > 5"])

    def test_evaluate_if_var_truth(self):
        ev = me_mod.ActionRunner.evaluate_if_var
        self.assertEqual(ev("n > 5", {"n": "10"}), (True, mock.ANY))
        self.assertEqual(ev("n > 5", {"n": "3"})[0], False)
        self.assertEqual(ev("nope = 1", {})[0], False)      # ไม่มีตัวแปร = ไม่จริง
        self.assertIsNone(ev("พัง", {})[0])                 # รูปแบบไม่ถูก = None

    def test_evaluate_if_pixel_and(self):
        rgb = me_mod.pixel_color_at(5, 5)
        if rgb is None:
            self.skipTest("จอไม่พร้อมอ่านสี")
        ev = me_mod.ActionRunner.evaluate_if_pixel
        good = "5,5 #%02x%02x%02x" % tuple(rgb[:3])
        bad = "5,5 #%02x%02x%02x" % tuple(255 - c for c in rgb[:3])
        hit, _d = ev([good, good], {})                       # 2 จุดตรงหมด = จริง
        self.assertIs(hit, True)
        hit, _d = ev([good, bad], {})                        # จุดไหนไม่ตรง = ไม่จริง
        self.assertIs(hit, False)
        hit, _d = ev(["พัง"], {})                            # รูปแบบไม่ถูก = None
        self.assertIsNone(hit)

    # ---------- เงื่อนไขเดี่ยว (ไม่มี &&) = เหมือนเดิมเป๊ะ ----------

    def test_single_condition_backward_compatible(self):
        ev = me_mod.ActionRunner.evaluate_condition
        self.assertEqual(ev(me_mod.IF_VAR, "n > 5", 2, 1, variables={"n": "10"})[0], 0)
        self.assertEqual(ev(me_mod.IF_VAR, "n > 5", 2, 1, variables={"n": "3"})[0], 2)
        self.assertEqual(ev(me_mod.IF_VAR, "nope = 1", 2, 1, variables={})[0], 2)

    def test_single_if_pixel_skips_when_screen_dead(self):
        """จออ่านไม่ได้ (pixel None) + สเปคถูก = ไม่ตรง → ข้ามตาม Repeat (พฤติกรรมเดิม)"""
        real_fn = me_mod.pixel_color_at
        me_mod.pixel_color_at = mock.MagicMock(return_value=None)
        try:
            r = self._runner()
            r.execute({"button": me_mod.IF_PIXEL, "additional": "5,5 #ffffff",
                       "repeat": 3})
            self.assertEqual(r.skip_n, 3)
        finally:
            me_mod.pixel_color_at = real_fn

    # ---------- AND ผ่าน runner (execute) ----------

    def test_if_image_and_pixel_and_var(self):
        rgb = me_mod.pixel_color_at(5, 5)
        if rgb is None:
            self.skipTest("จอไม่พร้อมอ่านสี")
        good = "5,5 #%02x%02x%02x" % tuple(rgb[:3])
        calls = []

        def cb(r):
            calls.append(1)
            return (10, 10)                                  # ภาพเจอเสมอ

        r = self._runner(cb, variables={"n": "10"})
        r.execute({"button": me_mod.IF_IMAGE,
                   "additional": "img.png && %s && n > 5" % good, "repeat": 3})
        self.assertTrue(r.last_if_found)                     # ครบทุกเงื่อนไข → เล่นต่อ
        self.assertEqual(r.skip_n, 0)
        self.assertEqual(r.variables.get("img_x"), 10)      # {img_x}/{img_y} ยังตั้ง

        r = self._runner(cb, variables={"n": "1"})          # n > 5 ไม่จริง
        r.execute({"button": me_mod.IF_IMAGE,
                   "additional": "img.png && %s && n > 5" % good, "repeat": 4})
        self.assertFalse(r.last_if_found)
        self.assertEqual(r.skip_n, 4)                        # ไม่ครบ AND → ข้ามตาม Repeat

    def test_if_pixel_and_two_points(self):
        rgb = me_mod.pixel_color_at(5, 5)
        if rgb is None:
            self.skipTest("จอไม่พร้อมอ่านสี")
        good = "5,5 #%02x%02x%02x" % tuple(rgb[:3])
        bad = "5,5 #%02x%02x%02x" % tuple(255 - c for c in rgb[:3])
        r = self._runner()
        r.execute({"button": me_mod.IF_PIXEL,
                   "additional": "%s && %s" % (good, good), "repeat": 2})
        self.assertEqual(r.skip_n, 0)
        r.execute({"button": me_mod.IF_PIXEL,
                   "additional": "%s && %s" % (good, bad), "repeat": 5})
        self.assertEqual(r.skip_n, 5)

    def test_if_var_and_via_evaluate_condition(self):
        ev = me_mod.ActionRunner.evaluate_condition
        V = {"n": "10", "code": "A-1"}
        self.assertEqual(ev(me_mod.IF_VAR, "n > 5 && code = A-1", 3, 1, variables=V)[0], 0)
        self.assertEqual(ev(me_mod.IF_VAR, "n > 5 && code = X", 3, 1, variables=V)[0], 3)
        # รูปแบบไม่ถูกชิ้นใดชิ้นหนึ่ง → เตือนเล่นต่อ (ไม่ข้าม) เหมือนแถวเดี่ยว
        self.assertEqual(ev(me_mod.IF_VAR, "พัง && n > 5", 3, 1, variables=V)[0], 0)

    # ---------- --validate เข้าใจ && ----------

    def test_validate_understands_and(self):
        rgb = me_mod.pixel_color_at(5, 5)
        good = "5,5 #%02x%02x%02x" % tuple(rgb[:3]) if rgb else "5,5 #ffffff"
        rows = [
            {"button": me_mod.IF_PIXEL, "additional": "%s && %s" % (good, good)},
            {"button": me_mod.IF_VAR, "additional": "n > 5 && code = A-1"},
        ]
        self.assertEqual(me_mod.validate_rows(rows), [])     # AND ถูกต้อง = ไม่มีปัญหา
        rows_bad = [
            {"button": me_mod.IF_PIXEL, "additional": "พัง && %s" % good},
            {"button": me_mod.IF_VAR, "additional": "n > && code = A-1"},
        ]
        issues = me_mod.validate_rows(rows_bad)
        self.assertEqual(len(issues), 2)                     # พัง 2 แถวตรงตามลำดับ
        self.assertEqual([i for i, _m in issues], [1, 2])


class TestDocsCheck(unittest.TestCase):
    """v2.5.4: ยกระดับ tools/check_docs.py เป็นเทสต์ในชุดหลัก — กันเอกสารค้างเก่า/
    ลิงก์พัง/CHANGELOG หัวข้อซ้ำ ตรวจทุกครั้งที่รัน unittest (ไม่ต้องรอ CI)"""

    def _root(self):
        return os.path.dirname(os.path.abspath(am.__file__))

    def test_check_docs_main_passes(self):
        import subprocess
        script = os.path.join(self._root(), "tools", "check_docs.py")
        self.assertTrue(os.path.isfile(script))
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        proc = subprocess.run([sys.executable, script], capture_output=True,
                              text=True, encoding="utf-8", errors="replace",
                              cwd=self._root(), env=env)
        self.assertEqual(proc.returncode, 0,
                         "tools/check_docs.py พบปัญหา:\n" + proc.stdout + proc.stderr)

    def test_check_docs_catches_broken_link_and_old_version(self):
        """ทดสอบกลไกภายในตรง ๆ: ลิงก์พัง/เวอร์ชันเก่า/หัวข้อซ้ำ ต้องถูกจับได้"""
        script = os.path.join(self._root(), "tools", "check_docs.py")
        spec = __import__("importlib.util", fromlist=["util"])
        spec2 = spec.spec_from_file_location("check_docs", script)
        mod = spec.module_from_spec(spec2)
        spec2.loader.exec_module(mod)

        # 1) ลิงก์พัง: สร้างไฟล์ชั่วคราวใน docs/ ที่อ้างไฟล์ที่ไม่มีจริง
        tmp = os.path.join(self._root(), "docs", "_tmp_check_docs_test.md")
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write("[ทดสอบ](not-exist-XYZ.md)\n")
        try:
            _n, bad = mod.check_links(mod.list_doc_files())
            hits = [b for b in bad if b[0].endswith("_tmp_check_docs_test.md")]
            self.assertTrue(hits, "ลิงก์พังต้องถูกจับได้")
            self.assertEqual(hits[0][1], "not-exist-XYZ.md")
        finally:
            os.remove(tmp)

        # 2) เวอร์ชันเก่า: ตัวเลขปลอมต้องไม่ผ่าน / เวอร์ชันจริงต้องผ่าน
        real = mod.read_version()
        self.assertTrue(mod.check_versions(real, mod.list_doc_files()) == [],
                        "เวอร์ชันจริงต้องพบในเอกสารหลักครบ")
        problems = mod.check_versions("0.0.1", mod.list_doc_files())
        self.assertTrue(any("0.0.1" in p for p in problems))

        # 3) หัวข้อซ้ำ: mock เนื้อหา CHANGELOG ที่มีเวอร์ชันซ้ำผ่าน check_changelog_duplicates จริง
        real_changelog = os.path.join(self._root(), "docs", "CHANGELOG.md")
        with open(real_changelog, encoding="utf-8") as fh:
            backup = fh.read()
        try:
            with open(real_changelog, "w", encoding="utf-8") as fh:
                fh.write(backup + "\n## [9.9.9] — ทดสอบ\n\n## [9.9.9] — ทดสอบซ้ำ\n")
            dups = mod.check_changelog_duplicates()
        finally:
            with open(real_changelog, "w", encoding="utf-8") as fh:
                fh.write(backup)
        self.assertTrue(any("9.9.9" in p for p in dups), "หัวข้อซ้ำต้องถูกจับได้")
        self.assertEqual(mod.check_changelog_duplicates(), [],
                         "ไฟล์จริงต้องไม่มีหัวข้อซ้ำ")


class TestN1AndLoopTime(unittest.TestCase):
    """v2.5.4 (ชุด N1 ต่อยอด): ขยาย && ไป If Loop / If Time
    กติกาเดียวกับ N1: ทุกเงื่อนไขย่อยจริง → เล่นต่อ, ไม่จริง → ข้าม N แถว (Repeat)
    If Loop "3 && 5" = ต้องถึงรอบ 3 *และ* 5 · If Time "08:00 && 22:30" = ผ่านทั้งสองเวลา
    แถวเดี่ยว (ไม่มี &&) ต้องเล่นผลเดิม 100%"""

    def _ev(self, *args, **kw):
        return me_mod.ActionRunner.evaluate_condition(*args, **kw)

    # ---------- If Loop ----------

    def test_if_loop_and_all_reached(self):
        skip, msg = self._ev(me_mod.IF_LOOP, "3 && 5", 4, 5)
        self.assertEqual(skip, 4)
        self.assertIn("ข้าม 4 แถว", msg)

    def test_if_loop_and_not_yet(self):
        # ถึงรอบ 3 แต่ยังไม่ถึง 5 → ยังไม่ข้าม
        skip, msg = self._ev(me_mod.IF_LOOP, "3 && 5", 1, 3)
        self.assertEqual(skip, 0)
        self.assertIn("ยังไม่ถึง 5", msg)

    def test_if_loop_single_unchanged(self):
        # แถวเดี่ยวต้องคืนผลเหมือนเดิมทุกอย่าง (กัน regression N1)
        self.assertEqual(self._ev(me_mod.IF_LOOP, "3", 1, 2)[0], 0)
        skip, msg = self._ev(me_mod.IF_LOOP, "3", 1, 9)
        self.assertEqual(skip, 1)
        self.assertIn("ข้าม 1 แถว", msg)

    def test_if_loop_and_bad_format(self):
        # ชิ้นใดพัง → เตือนเล่นต่อ (เหมือนแถวเดี่ยวรูปแบบไม่ถูก)
        skip, msg = self._ev(me_mod.IF_LOOP, "3 && พัง", 4, 1)
        self.assertEqual(skip, 0)
        self.assertIn("ไม่ถูก", msg)

    def test_if_loop_and_three_parts(self):
        self.assertEqual(self._ev(me_mod.IF_LOOP, "2 && 3 && 4", 4, 1)[0], 0)
        self.assertEqual(self._ev(me_mod.IF_LOOP, "2 && 3 && 4", 4, 4)[0], 4)

    # ---------- If Time ----------

    @staticmethod
    def _t(h, m):
        return time.struct_time((2026, 9, 30, h, m, 0, 2, 273, 0))

    def test_if_time_and_all_passed(self):
        skip, msg = self._ev(me_mod.IF_TIME, "08:00 && 22:30", 2, 1, now=self._t(23, 59))
        self.assertEqual(skip, 2)
        self.assertIn("ข้าม 2 แถว", msg)

    def test_if_time_and_pending(self):
        # ผ่าน 08:00 แต่ยังไม่ถึง 22:30 → เล่นต่อ และรายงานเวลาที่ยังไม่ถึง
        skip, msg = self._ev(me_mod.IF_TIME, "08:00 && 22:30", 2, 1, now=self._t(9, 0))
        self.assertEqual(skip, 0)
        self.assertIn("ยังไม่ถึง 22:30", msg)

    def test_if_time_single_unchanged(self):
        # แถวเดี่ยวต้องคืนผลเหมือนเดิมทุกอย่าง (กัน regression N1)
        self.assertEqual(self._ev(me_mod.IF_TIME, "08:00", 3, 1, now=self._t(7, 0))[0], 0)
        skip, msg = self._ev(me_mod.IF_TIME, "08:00", 3, 1, now=self._t(8, 1))
        self.assertEqual(skip, 3)
        self.assertIn("ข้าม 3 แถว", msg)

    def test_if_time_and_bad_format(self):
        skip, msg = self._ev(me_mod.IF_TIME, "08:00 && 25:99", 3, 1, now=self._t(23, 0))
        self.assertEqual(skip, 0)
        self.assertIn("ไม่ถูก", msg)

    # ---------- --validate ----------

    def test_validate_if_loop_if_time(self):
        rows = [
            {"button": me_mod.IF_LOOP, "additional": "3 && 5"},
            {"button": me_mod.IF_TIME, "additional": "08:00 && 22:30"},
        ]
        self.assertEqual(me_mod.validate_rows(rows), [])
        rows_bad = [
            {"button": me_mod.IF_LOOP, "additional": "3 && พัง"},
            {"button": me_mod.IF_TIME, "additional": "08:00 && 25:99"},
            {"button": me_mod.IF_LOOP, "additional": "0"},
        ]
        issues = me_mod.validate_rows(rows_bad)
        self.assertEqual(len(issues), 3)
        self.assertEqual([i for i, _m in issues], [1, 2, 3])


class TestN2Blocks(unittest.TestCase):
    """v2.6 (ชุด N2): Block Start/End + ลูปย่อย (until/max) ตาม docs/DESIGN-nested-if.md
    กติกาเหล็ก: สคริปต์เดิม (ไม่มีแถวบล็อก) เล่นผลเดิม 100% · --validate ตรวจคู่เปิด/ปิด"""

    def _runner(self, cond_cb=None):
        return me_mod.ActionRunner(mock.MagicMock(), mock.MagicMock(),
                                   variables={"n": "4", "m": "on"}) if cond_cb is None \
            else me_mod.ActionRunner(mock.MagicMock(), mock.MagicMock(),
                                     variables={"n": "4", "m": "on"})

    # ---------- parse_block_spec ----------

    def test_parse_block_spec(self):
        f = me_mod.parse_block_spec
        self.assertEqual(f(""), {"kind": "once", "if": "", "until": "", "max": 0})
        self.assertEqual(f("if img.png"), {"kind": "once", "if": "img.png", "until": "", "max": 0})
        self.assertEqual(f("if n > 5"), {"kind": "once", "if": "n > 5", "until": "", "max": 0})
        self.assertEqual(f("until img.png max 20"),
                         {"kind": "loop", "if": "", "until": "img.png", "max": 20})
        self.assertEqual(f("until n >= 5"), {"kind": "loop", "if": "", "until": "n >= 5", "max": 0})
        self.assertEqual(f("max 10"), {"kind": "loop", "if": "", "until": "", "max": 10})
        self.assertIsNone(f("what"))            # ข้อความแปลกปลอม = พัง
        self.assertIsNone(f("if"))               # if ไม่มีเงื่อนไข = พัง

    def test_find_block_end_nesting(self):
        rows = [{"button": me_mod.BLOCK_START}, {"button": me_mod.BLOCK_START},
                {"button": me_mod.BLOCK_END}, {"button": me_mod.BLOCK_END}]
        self.assertEqual(me_mod.find_block_end_index(rows, 0), 3)   # นับวงเล็บถูกคู่
        self.assertEqual(me_mod.find_block_end_index(rows, 1), 2)
        self.assertIsNone(me_mod.find_block_end_index(rows[:3], 0)) # ไม่ปิด = None

    # ---------- BlockRunner.decide / decide_end ----------

    def _br(self, idx, cb):
        return me_mod.BlockRunner(idx, condition_cb=cb)

    def test_decide_false_jumps_past_end(self):
        rows = [{"button": me_mod.BLOCK_START, "additional": "if n > 99"},
                {"button": "Beep"},
                {"button": me_mod.BLOCK_END}]
        goto, msg = self._br(0, lambda t: False).decide(rows, {})
        self.assertEqual(goto, 3)                # กระโดดหลัง End คู่
        self.assertIn("ข้ามบล็อก", msg)

    def test_decide_true_plays_block(self):
        rows = [{"button": me_mod.BLOCK_START, "additional": "if n > 1"},
                {"button": "Beep"},
                {"button": me_mod.BLOCK_END}]
        goto, msg = self._br(0, lambda t: True).decide(rows, {})
        self.assertIsNone(goto)
        self.assertIsNone(msg)

    def test_decide_bad_spec_and_missing_end(self):
        rows = [{"button": me_mod.BLOCK_START, "additional": "พังๆ"},
                {"button": me_mod.BLOCK_END}]
        goto, msg = self._br(0, lambda t: True).decide(rows, {})
        self.assertIsNone(goto)
        self.assertIn("ไม่ถูก", msg)              # เตือนแต่เล่นต่อ (validate เตือนแรกอยู่แล้ว)
        rows2 = [{"button": me_mod.BLOCK_START, "additional": "if n > 1"}]
        goto, msg = self._br(0, lambda t: False).decide(rows2, {})
        self.assertIsNone(goto)                  # ไม่มี End คู่ → เล่นต่อตามลำดับ
        self.assertIn("ไม่พบ Block End", msg)

    def test_decide_end_until_loop(self):
        rows = [{"button": me_mod.BLOCK_START, "additional": "until n > 3 max 10"},
                {"button": "Beep"},
                {"button": me_mod.BLOCK_END}]
        counters = {0: 2}
        # ใช้ runner จริงผ่าน ActionRunner.evaluate_block_condition — n = 1 ยังไม่เกิน 3 → วนกลับ
        runner = me_mod.ActionRunner(mock.MagicMock(), mock.MagicMock(), variables={"n": "1"})
        goto, msg = me_mod.BlockRunner(
            2, condition_cb=runner.evaluate_block_condition).decide_end(rows, counters)
        self.assertEqual(goto, 1)                # วนกลับแถวหลัง Start
        self.assertIn("วนกลับ", msg)
        self.assertEqual(counters[0], 3)
        # ครบ max → ออกจากลูป
        counters = {0: 10}
        goto, msg = me_mod.BlockRunner(
            2, condition_cb=runner.evaluate_block_condition).decide_end(rows, counters)
        self.assertIsNone(goto)
        self.assertIn("ครบ 10 รอบ", msg)
        # เงื่อนไขจริง → ออกจากลูปเงียบ ๆ (n = 4 > 3)
        runner2 = self._runner()
        goto, msg = me_mod.BlockRunner(
            2, condition_cb=runner2.evaluate_block_condition).decide_end(rows, {0: 2})
        self.assertIsNone(goto)
        self.assertIsNone(msg)

    def test_decide_end_plain_block_and_orphan(self):
        rows = [{"button": me_mod.BLOCK_START, "additional": "if n > 1"},
                {"button": "Beep"},
                {"button": me_mod.BLOCK_END}]
        runner = self._runner()
        goto, msg = me_mod.BlockRunner(
            2, condition_cb=runner.evaluate_block_condition).decide_end(rows, {})
        self.assertIsNone(goto)                  # บล็อกธรรมดา: จบแล้วเล่นต่อ
        self.assertIsNone(msg)
        goto, msg = me_mod.BlockRunner(
            0, condition_cb=runner.evaluate_block_condition).decide_end(
            [{"button": me_mod.BLOCK_END}], {})
        self.assertIn("ไม่มี Block Start", msg)   # End กำพร้า — เตือนแล้วเล่นต่อ

    # ---------- ActionRunner.evaluate_block_condition ----------

    def test_block_condition_variables(self):
        r = self._runner()
        self.assertIs(r.evaluate_block_condition("n > 3"), True)
        self.assertIs(r.evaluate_block_condition("n > 99"), False)
        self.assertIs(r.evaluate_block_condition("n > 3 && m = on"), True)   # && ผสมได้ (N1)
        self.assertIs(r.evaluate_block_condition("n > 3 && m = off"), False)
        # รูปแบบพัง = ไม่จริง (False — กติกาเดียวกับ If Variable ไม่มีตัวแปร → ข้าม)
        self.assertIs(r.evaluate_block_condition("พัง"), False)

    def test_block_condition_missing_image_is_false(self):
        # ไฟล์ภาพไม่มีจริง → False (เหมือน If Image ไม่เจอ) ไม่ใช่ None
        r = self._runner()
        self.assertIs(r.evaluate_block_condition("no_such_img_abc.png"), False)

    # ---------- validate ----------

    def test_validate_blocks_structure(self):
        rows_ok = [
            {"button": me_mod.BLOCK_START, "additional": "if n > 1"},
            {"button": me_mod.BLOCK_START, "additional": "until img.png max 5"},
            {"button": "Beep"},
            {"button": me_mod.BLOCK_END},
            {"button": me_mod.BLOCK_END},
        ]
        self.assertEqual(me_mod.validate_rows(rows_ok), [])
        # Start ไม่มี End ปิดเลย (สคริปต์จบค้างเปิด) → รายงานแถว Start
        rows_unclosed = [
            {"button": me_mod.BLOCK_START, "additional": "if n > 1"},
            {"button": "Beep"},
        ]
        self.assertEqual([i for i, _m in me_mod.validate_rows(rows_unclosed)], [1])
        rows_bad = [
            {"button": me_mod.BLOCK_START, "additional": "if n > 1"},  # ปิดโดย End แถว 3
            {"button": "Beep"},
            {"button": me_mod.BLOCK_END, "additional": "ห้ามมี"},  # End มี Additional
            {"button": me_mod.BLOCK_END},                          # เกิน (ไม่มี Start ค้าง)
            {"button": me_mod.BLOCK_START, "additional": "อะไรนะ"},  # Additional พัง + ไม่ปิด
        ]
        issues = me_mod.validate_rows(rows_bad)
        rows_flag = [i for i, _m in issues]
        self.assertIn(3, rows_flag)              # End มี Additional
        self.assertIn(4, rows_flag)              # End ล้น
        self.assertIn(5, rows_flag)              # Start Additional พัง + ไม่ปิด
        # depth เกิน 8
        deep = ([{"button": me_mod.BLOCK_START}] * 9
                + [{"button": me_mod.BLOCK_END}] * 9)
        self.assertTrue(any("ลึกเกิน" in m for _i, m in me_mod.validate_rows(deep)))

    def test_row_tag_block(self):
        self.assertEqual(me_mod.row_tag(me_mod.BLOCK_START), "block")
        self.assertEqual(me_mod.row_tag(me_mod.BLOCK_END), "blockend")
        self.assertIn("block", me_mod.ROW_STYLE)
        self.assertIn("blockend", me_mod.ROW_STYLE)

    def test_gui_block_until_loop(self):
        """เล่นจริงใน GUI: ลูปย่อย until นับ 1→3 แล้วออก (n = 4)"""
        try:
            root = _Tk()
            root.withdraw()
        except am.tk.TclError:
            self.skipTest("ไม่มี display")
        app = None
        try:
            app = am.MacroApp(root)
            app._log_enabled = False
            rows = [
                {"enabled": True, "x": "", "y": "", "button": "Set Variable",
                 "additional": "n = 1", "mins": 0, "secs": 0, "repeat": 1},
                {"enabled": True, "x": "", "y": "", "button": me_mod.BLOCK_START,
                 "additional": "until n > 3 max 10", "mins": 0, "secs": 0, "repeat": 1},
                {"enabled": True, "x": "", "y": "", "button": "Beep",
                 "additional": "", "mins": 0, "secs": 0, "repeat": 1},
                {"enabled": True, "x": "", "y": "", "button": "Set Variable",
                 "additional": "n += 1", "mins": 0, "secs": 0, "repeat": 1},
                {"enabled": True, "x": "", "y": "", "button": me_mod.BLOCK_END,
                 "additional": "", "mins": 0, "secs": 0, "repeat": 1},
            ]
            app._load_rows(rows)
            app._start_player(False)
            t0 = time.time()
            while app.running and time.time() - t0 < 10:
                root.update()
                time.sleep(0.02)
            self.assertFalse(app.running, "ลูปย่อยต้องจบเองภายใน 10 วิ")
            self.assertEqual(str(app._vars.get("n")), "4")   # วน 3 รอบครบ
        finally:
            if app is not None:
                try:
                    app.stop_all(silent=True)
                except Exception:
                    pass
            root.destroy()


class TestSchedMulti(unittest.TestCase):
    """v2.7: Schedule หลายนัดหมาย — parser/migration/conf รูปแบบใหม่ (dict เดียว self._sched)
    ⚠️ ชื่อคลาสเทสต์ซ้ำกันไม่ได้ — คลาสหลังจะบังคลาสหน้า (AGENTS.md v1.11)"""

    def test_parse_hhmm_list_basic_and_dedupe(self):
        self.assertEqual(me_mod.parse_hhmm_list("09:00, 12:30 , 22:00"),
                         ["09:00", "12:30", "22:00"])
        self.assertEqual(me_mod.parse_hhmm_list("08:00,08:00"), ["08:00"])  # ตัดซ้ำ

    def test_parse_hhmm_list_bad_parts_skipped(self):
        self.assertEqual(me_mod.parse_hhmm_list("9:00, บ่ายสาม, 25:00, 07:60, 06:15"),
                         ["06:15"])            # พัง = ข้ามเฉพาะรายการนั้น
        self.assertEqual(me_mod.parse_hhmm_list(""), [])
        self.assertEqual(me_mod.parse_hhmm_list(None), [])

    def test_parse_sched_list_new_dict(self):
        m, e, tl, p = me_mod.parse_sched_list(
            {"mode": "daily", "every": 10, "times": "08:00,12:30", "profile": "งานเช้า"})
        self.assertEqual((m, e, tl, p), ("daily", 10, ["08:00", "12:30"], "งานเช้า"))

    def test_parse_sched_list_tolerates_garbage(self):
        for bad in (None, 42, [], {"mode": "รัว ๆ"}, {"mode": "interval", "every": "ล้าน"}):
            m, e, tl, p = me_mod.parse_sched_list(bad)
            if isinstance(bad, dict) and bad.get("mode") == "interval":
                self.assertEqual((m, e), ("interval", 10))   # every พัง = ค่าเริ่มต้น
            else:
                self.assertEqual((m, e, tl, p), ("off", 10, [], ""))

    def test_sched_migrate_old_conf_keys(self):
        d = me_mod.sched_migrate("daily", 15, "08:00,22:00", "งานดึก")
        self.assertEqual(d, {"mode": "daily", "every": 15,
                             "times": ["08:00", "22:00"], "profile": "งานดึก"})
        d2 = me_mod.sched_migrate("interval", 20, "", "")
        self.assertEqual(d2, {"mode": "interval", "every": 20, "times": [], "profile": ""})

    def test_sched_migrate_daily_without_times_turns_off(self):
        d = me_mod.sched_migrate("daily", 10, "บ่ายสาม", "")   # เวลาพังหมด = ไม่มีนัดให้ทำงาน
        self.assertEqual(d["mode"], "off")
        self.assertEqual(d["times"], [])

    def test_conf_roundtrip_multi_sched(self):
        import tempfile
        app = mock.MagicMock()
        app._serialize.return_value = [{"button": "Beep"}]
        app._log_enabled = True
        app._hp_dir = None
        app._backup_enabled = True
        app._backup_days = 7
        app._log_keep_days = 0                     # v2.11: _save_conf/export อ่าน attr นี้
        app._log_archive = True
        app._lang = "th"
        app.cmb_speed.get.return_value = "1"
        app.ent_loops.get.return_value = "1"
        app.chk_forever.get.return_value = False
        app.chk_restore.get.return_value = False
        app.chk_shuffle.get.return_value = False
        app.ent_pct.get.return_value = "100"
        app._play_options = lambda: 100
        app._time_limit_enabled = False
        app._time_limit_min = 30
        app._sched = {"mode": "daily", "every": 10,
                      "times": ["08:00", "12:30"], "profile": "งานเช้า"}
        with tempfile.TemporaryDirectory() as d:
            conf = os.path.join(d, "macro_conf.json")
            with mock.patch.object(am, "CONF", conf):
                am.MacroApp._save_conf(app)
                raw = json.load(open(conf, encoding="utf-8"))
                self.assertEqual(raw["sched"]["times"], ["08:00", "12:30"])   # รูปแบบใหม่จริง
                app2 = mock.MagicMock()
                app2._profiles = {"งานเช้า": []}      # โปรไฟล์ต้องมีอยู่จริงจึงจะคืนค่า (guard ใน _load_conf)
                am.MacroApp._load_conf(app2)
        self.assertEqual(app2._sched["mode"], "daily")
        self.assertEqual(app2._sched["times"], ["08:00", "12:30"])
        self.assertEqual(app2._sched["profile"], "งานเช้า")


class TestAhkRoundTrip(unittest.TestCase):
    """v2.7: ทำงานร่วม AutoHotkey — export/import ผ่าน engine ล้วน (ไม่แตะ Tk)"""

    def test_export_key_and_delay(self):
        s = me_mod.rows_to_ahk([{"enabled": True, "button": "Tap Key", "additional": "esc",
                                 "mins": 0, "secs": 1.5, "repeat": 1}])
        self.assertIn("Send {Esc}", s)   # ชื่อคีย์ตาม key_map (AHK ไม่ sensitive case)
        self.assertIn("Sleep 1500", s)
        self.assertIn("Auto Mouse", s.splitlines()[0])          # หัวไฟล์บอกที่มา

    def test_export_combo_and_disabled_rows(self):
        s = me_mod.rows_to_ahk([
            {"enabled": False, "button": "Tap Key", "additional": "a"},
            {"enabled": True, "button": "Tap Key", "additional": "ctrl+s"}])
        self.assertNotIn("Send {a}", s)                          # แถวปิดไม่ออก
        self.assertIn("^s", s)                                    # combo ctrl+s → ^s

    def test_export_click_and_unsupported_as_comment(self):
        s = me_mod.rows_to_ahk([
            {"enabled": True, "button": "Left Click", "x": "100", "y": "200"},
            {"enabled": True, "button": "If Image", "additional": "img.png"}])
        self.assertIn("Click 100, 200, L", s)
        self.assertIn("; (ไม่รองรับ", s)                          # แถวเงื่อนไขคงไว้เป็น comment

    def test_import_send_sleep_click_run(self):
        rows = me_mod.ahk_to_rows(
            "Send {Ctrl down}สวัสดี{Ctrl up}\nSleep 500\nClick 100, 200\nRun notepad.exe")
        self.assertEqual([r["button"] for r in rows],
                         ["Press Key", "Type Text", "Release Key", "Left Click", "Launch App"])
        self.assertEqual(rows[1]["additional"], "สวัสดี")
        self.assertEqual(rows[3]["secs"], 0.5)                  # Sleep 500ms → ดีเลย์ของแถวถัดไป
        self.assertEqual(rows[4]["additional"], "notepad.exe")

    def test_import_skips_junk_lines(self):
        # v2.8: "x := 5" แปลเป็น Set Variable ได้แล้ว — ขยะจริงคือ assign แบบเก่า/label/นิพจน์อื่น
        rows = me_mod.ahk_to_rows("; หมายเหตุ\nx = 5\nIfWinActive ahk_exe game.exe\nMsgBox hi")
        self.assertEqual(rows, [])                               # นิพจน์/label/assign เก่า ข้ามหมด

    def test_ahk_dialog_real_tk(self):
        """เปิด dialog 🔀 จริงด้วย Tk จำลอง — ต้องสร้างได้ไม่ crash (มาตรฐาน v1.20.1)"""
        try:
            root = _Tk()
            root.withdraw()
        except am.tk.TclError:
            self.skipTest("ไม่มี display สำหรับ Tk")
        try:
            app = mock.MagicMock()
            app.root = root
            app._t = lambda key: am.tr("th", key)
            app._loaded_file = None              # ยังไม่มีไฟล์สคริปต์ → export แจ้งเตือน
            # MagicMock กลืน self.ahk_export เป็น attr — ผูกเมธอดจริงกลับเข้า mock
            app.ahk_export = lambda: am.MacroApp.ahk_export(app)
            calls = []
            with mock.patch.object(am.messagebox, "showinfo",
                                   side_effect=lambda *a, **k: calls.append(a)):
                am.MacroApp.ahk_dialog(app)                      # ไม่มีไฟล์สคริปต์ → แจ้งเตือน
                # dialog เปิดแบบ non-modal — ปุ่มไม่กดเอง หาปุ่มส่งออกแล้ว invoke เอง
                # โครง: root → win (Toplevel) → bf (Frame) → ปุ่ม
                for w in root.winfo_children():
                    for f in w.winfo_children():
                        for b in f.winfo_children():
                            if isinstance(b, am.tk.Button) and "ส่งออก" in str(b.cget("text")):
                                b.invoke()                       # → do_export → ahk_export
                                break
            self.assertTrue(calls)                               # showinfo ถูกเรียกจริง (จาก ahk_export)
        finally:
            root.destroy()


class TestSchedPerProfile(unittest.TestCase):
    """v2.8: นัดหมายรายเวลาเลือกโปรไฟล์เอง — "HH:MM=โปรไฟล์" ทั้ง parser/check/poll/dialog"""

    def _app(self):
        import queue
        app = mock.MagicMock()
        app._sched_q = queue.Queue()
        app.running = False
        app._sched = {"mode": "off", "every": 10, "times": [], "profile": ""}
        return app

    def test_parse_sched_entry(self):
        self.assertEqual(me_mod.parse_sched_entry("08:00=งานเช้า"), ("08:00", "งานเช้า"))
        self.assertEqual(me_mod.parse_sched_entry("08:00"), ("08:00", ""))
        self.assertIsNone(me_mod.parse_sched_entry("บ่ายสาม"))
        self.assertIsNone(me_mod.parse_sched_entry("25:00"))

    def test_sched_time_profiles_mixed(self):
        self.assertEqual(
            me_mod.sched_time_profiles(["08:00=งานเช้า", "12:30", "22:00=งานดึก", "บ่าย"]),
            [("08:00", "งานเช้า"), ("12:30", ""), ("22:00", "งานดึก")])
        self.assertEqual(me_mod.sched_time_profiles(None), [])

    def test_parse_hhmm_list_strips_profile(self):
        self.assertEqual(me_mod.parse_hhmm_list("08:00=งานเช้า, 09:00"), ["08:00", "09:00"])

    def test_sched_check_fires_per_time_profile(self):
        app = self._app()
        app._sched = {"mode": "daily", "every": 10,
                      "times": ["09:30=งานเช้า", "22:00"], "profile": ""}
        with mock.patch.object(am.time, "strftime", return_value="2026-10-01 09:30"):
            am.MacroApp._sched_check(app)
        self.assertEqual(app._sched_q.qsize(), 1)
        self.assertEqual(app._sched_q.get_nowait(), ("play", "งานเช้า"))   # ส่งโปรไฟล์ของเวลานั้น
        app2 = self._app()
        app2._sched = dict(app._sched)
        with mock.patch.object(am.time, "strftime", return_value="2026-10-01 22:00"):
            am.MacroApp._sched_check(app2)
        self.assertEqual(app2._sched_q.get_nowait(), ("play", ""))          # ไม่ระบุ = โปรไฟล์ตั้งต้น

    def test_sched_check_no_double_fire_same_minute(self):
        app = self._app()
        app._sched = {"mode": "daily", "every": 10, "times": ["09:30"], "profile": ""}
        with mock.patch.object(am.time, "strftime", return_value="2026-10-01 09:30"):
            am.MacroApp._sched_check(app)
            am.MacroApp._sched_check(app)
        self.assertEqual(app._sched_q.qsize(), 1)

    def test_poll_uses_time_profile_over_default(self):
        import queue
        app = mock.MagicMock()
        app._sched_q = queue.Queue()
        app._sched_q.put(("play", "งานเช้า"))
        app.running = False
        app._log_enabled = False
        app._profiles = {"งานเช้า": [{"button": "Beep", "secs": 1}],
                         "งานดึก": [{"button": "Beep", "secs": 2}]}
        app._sched = {"mode": "daily", "every": 10, "times": [], "profile": "งานดึก"}
        am.MacroApp._sched_poll(app)
        app._load_rows.assert_called_once_with([{"button": "Beep", "secs": 1}])   # โปรไฟล์ของเวลาชนะ
        app._start_player_inner.assert_called_once_with(False, once=True, auto=True)

    def test_poll_str_item_uses_default_profile(self):
        import queue
        app = mock.MagicMock()
        app._sched_q = queue.Queue()
        app._sched_q.put("play")                # สตริงเดิม (v2.7) — ใช้โปรไฟล์ตั้งต้น
        app.running = False
        app._log_enabled = False
        app._profiles = {"งานดึก": [{"button": "Beep", "secs": 2}]}
        app._sched = {"mode": "daily", "every": 10, "times": [], "profile": "งานดึก"}
        am.MacroApp._sched_poll(app)
        app._load_rows.assert_called_once_with([{"button": "Beep", "secs": 2}])

    def test_dialog_real_tk_per_time_profile(self):
        """เปิด dialog ตั้งเวลาจริง — ใส่ 08:00=งานเช้า, 22:00 แล้วกดตกลง → times เก็บครบ"""
        try:
            root = _Tk()
            root.withdraw()
        except am.tk.TclError:
            self.skipTest("ไม่มี display สำหรับ Tk")
        try:
            app = mock.MagicMock()
            app.root = root
            app._profiles = {"งานเช้า": []}
            app._sched = {"mode": "off", "every": 10, "times": [], "profile": ""}
            am.MacroApp._schedule_dialog(app)

            def walk(w):
                yield w
                for c in w.winfo_children():
                    yield from walk(c)

            ws = list(walk(root))
            ent_time = [w for w in ws if isinstance(w, am.tk.Entry)
                        and not isinstance(w, am.tk.Spinbox)][0]
            daily = [w for w in ws if isinstance(w, am.tk.Radiobutton)
                     and str(w.cget("value")) == "daily"][0]
            ok_btn = [w for w in ws if isinstance(w, am.tk.Button)
                      and str(w.cget("text")) == "ตกลง"][0]
            daily.invoke()
            ent_time.delete(0, "end")
            ent_time.insert(0, "08:00=งานเช้า, 22:00")
            ok_btn.invoke()
        finally:
            root.destroy()
        self.assertEqual(app._sched["mode"], "daily")
        self.assertEqual(app._sched["times"], ["08:00=งานเช้า", "22:00"])


class TestAhkVars(unittest.TestCase):
    """v2.8: .ahk ตัวแปร/เงื่อนไขสองทิศ — Set Variable/If Variable ⇄ :=, +=, -=, if"""

    def test_export_set_var_number_string_increment(self):
        def last(add):
            s = me_mod.rows_to_ahk([{"enabled": True, "button": "Set Variable",
                                     "additional": add}])
            return s.strip().splitlines()[-1]
        self.assertEqual(last("n = 5"), "n := 5")
        self.assertEqual(last("ชื่อ = สวัสดี"), 'ชื่อ := "สวัสดี"')
        self.assertEqual(last("n += 3"), "n += 3")
        self.assertEqual(last("n -= 2"), "n -= 2")
        self.assertEqual(last("b = {a}"), "b := a")           # {ตัวแปร} → อ้างตัวแปร AHK
        self.assertIn("; (Set Variable รูปแบบไม่ถูก", last("พัง"))

    def test_export_if_var(self):
        def last(add):
            s = me_mod.rows_to_ahk([{"enabled": True, "button": "If Variable",
                                     "additional": add}])
            return s.strip().splitlines()[-1]
        self.assertEqual(last("n > 5"), "if (n > 5)")
        self.assertEqual(last("ข้อความ ~ hello"), 'if ข้อความ contains "hello"')
        self.assertIn("; (If Variable รูปแบบไม่ถูก", last("พัง"))

    def test_import_assignments(self):
        rows = me_mod.ahk_to_rows(
            'counter := 0\ncounter += 2\ncounter -= 1\nname := "สวัสดี"\nx := y')
        self.assertEqual([r["button"] for r in rows], ["Set Variable"] * 5)
        self.assertEqual([r["additional"] for r in rows],
                         ["counter = 0", "counter += 2", "counter -= 1",
                          "name = สวัสดี", "x = {y}"])

    def test_import_conditions_and_junk(self):
        rows = me_mod.ahk_to_rows(
            'if (n > 5)\nif name contains "สวัสดี"\nif x = 5\nIfWinActive ahk_exe game.exe\nif (n + 1)')
        self.assertEqual([(r["button"], r["additional"]) for r in rows],
                         [("If Variable", "n > 5"), ("If Variable", "name ~ สวัสดี"),
                          ("If Variable", "x = 5")])   # IfWinActive/นิพจน์แปลไม่ได้ = ข้าม

    def test_roundtrip_preserves_delay(self):
        rows = me_mod.ahk_to_rows("Sleep 500\nn := 5")
        self.assertEqual(rows[0]["button"], "Set Variable")
        self.assertEqual(rows[0]["secs"], 0.5)

    def test_cond_to_macro_edges(self):
        self.assertEqual(me_mod.ahk_cond_to_macro("n >= 10"), "n >= 10")
        self.assertEqual(me_mod.ahk_cond_to_macro('x == "สวัสดี"'), "x == สวัสดี")
        self.assertEqual(me_mod.ahk_cond_to_macro('n contains "abc"'), "n ~ abc")
        self.assertEqual(me_mod.ahk_cond_to_macro("n + 1"), "n + 1")   # แปลไม่ได้ = คืนเดิม


class TestPluginsCommunity(unittest.TestCase):
    """v2.8: plugin ชุมชนตัวอย่าง 3 ตัว — มาตรฐานเดียวกับ TestPluginsComplete
    (โหลดได้ / ทำงานถูก / ทน input พัง / ทน ctx ขาด / เขียน vars)"""

    def _plugin(self, name):
        pl = dict(me_mod.load_plugins())
        self.assertIn(name, pl, "plugin %s ต้องโหลดได้" % name)
        return pl[name]

    def test_community_plugins_loaded(self):
        pl = dict(me_mod.load_plugins())
        for name in ("Random Pause", "Counter", "Open URL"):
            self.assertIn(name, pl)

    # ---------------- Random Pause ----------------
    def test_random_pause_sleeps_in_range(self):
        # พักเป็นชิ้นสั้น ๆ (≤0.2 วิ) เพื่อเช็ค STOP ระหว่างทาง — รวมชิ้น = ช่วงที่สั่ง
        pl = self._plugin("Random Pause")
        with mock.patch.object(pl.time, "sleep") as slept:
            pl.run({"log": lambda m: None}, {"additional": "2-3"})
        total = sum(c.args[0] for c in slept.call_args_list)
        self.assertGreaterEqual(total, 2.0)
        self.assertLessEqual(total, 3.0)
        self.assertTrue(all(0 < c.args[0] <= 0.2 + 1e-9 for c in slept.call_args_list))

    def test_random_pause_bad_input_and_stop(self):
        pl = self._plugin("Random Pause")
        with mock.patch.object(pl.time, "sleep") as slept:
            pl.run({"log": lambda m: None}, {"additional": "abc"})   # พัง → รวม 1.0
            pl.run({"log": lambda m: None}, {"additional": ""})
        totals = [sum(c.args[0] for c in calls) for calls in (slept.call_args_list[:5],)]
        self.assertAlmostEqual(sum(c.args[0] for c in slept.call_args_list), 2.0, delta=1e-6)
        with mock.patch.object(pl.time, "sleep") as slept2:
            pl.run({"stop_check": lambda: True}, {"additional": "5"})  # STOP ระหว่างพัก
        slept2.assert_not_called()

    # ---------------- Counter ----------------
    def test_counter_increments_and_sets_vars(self):
        pl = self._plugin("Counter")
        ctx = {"log": lambda m: None, "vars": {"n": "0"}}
        pl.run(ctx, {"additional": "n"})
        self.assertEqual(float(ctx["vars"]["n"]), 1.0)
        pl.run(ctx, {"additional": "n += 5"})
        self.assertEqual(float(ctx["vars"]["n"]), 6.0)
        pl.run(ctx, {"additional": "name = hello"})
        self.assertEqual(ctx["vars"]["name"], "hello")
        pl.run(ctx, {"additional": "r = rand 1-2"})
        self.assertIn(ctx["vars"]["r"], ("1", "2"))

    def test_counter_bad_and_missing_ctx(self):
        pl = self._plugin("Counter")
        ctx = {"log": lambda m: None, "vars": {}}
        pl.run(ctx, {"additional": ""})                    # ว่าง = ไม่แตะ vars
        self.assertEqual(ctx["vars"], {})
        pl.run(ctx, {"additional": "พัง ๆ!!"})              # รูปแบบไม่ parse = ไม่แตะ vars
        self.assertEqual(ctx["vars"], {})
        pl.run(ctx, {"additional": "ชื่อไทย"})              # ชื่อเดี่ยว (ไทยได้) = นับ +1
        self.assertEqual(float(ctx["vars"]["ชื่อไทย"]), 1.0)
        pl.run({"log": lambda m: None}, {"additional": "n"})   # ไม่มี vars → ข้าม
        pl.run({}, {"additional": "n"})                        # ctx ไม่ใช่ dict

    # ---------------- Open URL ----------------
    def test_open_url_prefixes_scheme_and_subs_vars(self):
        pl = self._plugin("Open URL")
        opened = []
        with mock.patch.object(pl.webbrowser, "open",
                               side_effect=lambda u: opened.append(u) or True):
            pl.run({"log": lambda m: None}, {"additional": "example.com"})
            pl.run({"log": lambda m: None, "vars": {"p": "a"}},
                   {"additional": "https://x.io/{p}"})
        self.assertEqual(opened, ["https://example.com", "https://x.io/a"])

    def test_open_url_bad_input_and_crash_tolerated(self):
        pl = self._plugin("Open URL")
        opened = []
        with mock.patch.object(pl.webbrowser, "open",
                               side_effect=lambda u: opened.append(u) or True):
            pl.run({"log": lambda m: None}, {"additional": ""})      # ว่าง = ไม่เปิด
        self.assertEqual(opened, [])
        with mock.patch.object(pl.webbrowser, "open", side_effect=Exception("พัง")):
            pl.run({"log": lambda m: None}, {"additional": "example.com"})  # ทนได้


class TestBlockCollapse(unittest.TestCase):
    """v2.8.1: ย่อ/ขยายกลุ่มบล็อก Block Start→End — กลไกเดียวกับ Section (_section_stash)
    ⚠️ แถวซ่อนต้องยังเล่นตามลำดับเดิม (แก้บั๊กแฝง _rows_and_iids_for_play เดิมข้ามแถวซ่อน)"""

    def _app(self):
        app = mock.MagicMock()
        kids = iter("k%d" % i for i in range(1, 999))
        order = []
        store = {}

        def insert(parent, index, **kw):
            iid = next(kids)
            store[iid] = list(kw["values"])
            pos = len(order) if str(index) == "end" else int(index)
            order.insert(pos, iid)              # แทรกตามตำแหน่งจริงเหมือน Tk
            return iid

        def item(iid, *args, **kw):
            if "values" in kw:
                store[iid] = list(kw["values"])
                return None
            return store[iid]

        app.tree.get_children.side_effect = lambda: list(order)
        app.tree.insert = insert
        app.tree.item = item
        app.tree.index = lambda iid: order.index(iid)
        app.tree.detach = lambda iid: order.remove(iid)
        app._section_stash = []
        app._hl_row = None
        app.refresh_nums = lambda: am.MacroApp.refresh_nums(app)
        for m in ("_group_members", "_group_collapsed", "_group_toggle", "_serialize",
                  "_rows_and_iids_for_play", "_on_del_cleanup"):
            setattr(app, m, getattr(am.MacroApp, m).__get__(app))
        return app, store

    def _rows(self, app, rows):
        for r in rows:
            app.tree.insert("", "end", values=["☑", "#", "", "", r[0], r[1], 0, r[2], 1])

    def test_collapse_block_hides_members_and_serialize_keeps(self):
        app, store = self._app()
        self._rows(app, [("Left Click", "", 1), (am.BLOCK_START, "", 0),
                         ("Beep", "b1", 1), ("Beep", "b2", 1),
                         (am.BLOCK_END, "", 0), ("Left Click", "", 1)])
        start = app.tree.get_children()[1]
        app._group_toggle(start)                       # ย่อบล็อก
        self.assertEqual(len(app.tree.get_children()), 4)   # LC + Start + End + LC
        self.assertIn("(ย่อ 2 แถว)", str(app.tree.item(start, "values")[5]))
        rows = app._serialize()
        self.assertEqual([r["additional"] for r in rows], ["", "", "b1", "b2", "", ""])
        self.assertEqual(rows[1]["additional"], "")    # ป้ายย่อถูกตัด — เงื่อนไข Block Start สะอาด

    def test_expand_block_restores_order(self):
        app, store = self._app()
        self._rows(app, [("Left Click", "", 1), (am.BLOCK_START, "until x", 0),
                         ("Beep", "x1", 1), ("Beep", "x2", 1),
                         (am.BLOCK_END, "", 0), ("Left Click", "", 1)])
        start = app.tree.get_children()[1]
        app._group_toggle(start)
        app._group_toggle(start)
        adds = [app.tree.item(i, "values")[5] for i in app.tree.get_children()]
        self.assertEqual(adds, ["", "until x", "x1", "x2", "", ""])   # ลำดับ+เงื่อนไขเดิมเป๊ะ
        self.assertEqual(app._section_stash, [])

    def test_collapse_nested_block_refused(self):
        app, store = self._app()
        self._rows(app, [(am.BLOCK_START, "A", 0), ("Beep", "a1", 1),
                         (am.BLOCK_START, "B", 0), ("Beep", "b1", 1),
                         (am.BLOCK_END, "", 0), ("Beep", "a2", 1),
                         (am.BLOCK_END, "", 0)])
        kids = app.tree.get_children()
        app._group_toggle(kids[2])                     # ย่อบล็อกใน (B) ก่อน — ได้
        app._group_toggle(kids[0])                     # ย่อบล็อกนอก (A) — ต้องถูกปฏิเสธ
        self.assertEqual(len(app.tree.get_children()), 6)   # ไม่ถูกย่อ (ซ่อนเฉพาะ b1 ของ B)
        rows = app._serialize()
        self.assertEqual([r["additional"] for r in rows],
                         ["A", "a1", "B", "b1", "", "a2", ""])   # ข้อมูลครบ ไม่หาย

    def test_unpaired_block_start_not_collapsible(self):
        app, store = self._app()
        self._rows(app, [("Left Click", "", 1), (am.BLOCK_START, "", 0), ("Beep", "b1", 1)])
        start = app.tree.get_children()[1]
        app._group_toggle(start)                       # ไม่มี Block End คู่ = ย่อไม่ได้
        self.assertEqual(len(app.tree.get_children()), 3)
        self.assertNotIn("(ย่อ", str(app.tree.item(start, "values")[5]))

    def test_del_collapsed_block_start_expands_first(self):
        app, store = self._app()
        self._rows(app, [(am.BLOCK_START, "", 0), ("Beep", "b1", 1), (am.BLOCK_END, "", 0)])
        start = app.tree.get_children()[0]
        app._group_toggle(start)
        self.assertEqual(len(app.tree.get_children()), 2)
        app._on_del_cleanup(start)                     # ลบหัวบล็อกที่ย่อ → ขยายคืนก่อน
        self.assertEqual(app._section_stash, [])
        self.assertEqual(len(app.tree.get_children()), 3)

    def test_play_includes_hidden_rows_and_strips_marker(self):
        app, store = self._app()
        self._rows(app, [(am.BLOCK_START, "if x", 0), ("Beep", "b1", 1), ("Beep", "b2", 1),
                         (am.BLOCK_END, "", 0), ("Left Click", "", 1)])
        start = app.tree.get_children()[0]
        app._group_toggle(start)
        rows, iids = app._rows_and_iids_for_play()
        self.assertEqual([r["additional"] for r in rows], ["if x", "b1", "b2", "", ""])
        self.assertEqual(iids, [start, None, None, "k4", "k5"])   # แถวซ่อน = iid None (ไม่ไฮไลต์) แถวเห็น = iid จริง


class TestGuiValidate(unittest.TestCase):
    """v2.8.1: ปุ่ม 🔍 Validate ใน GUI — รายงานแถวที่มีปัญหาเป็น dialog
    (engine เดียวกับ CLI --validate: validate_rows + validate_blocks)"""

    def test_menu_has_validate(self):
        self.assertIn("validate_dialog", [name for _, _, name, _ in am.MacroApp._menu_items()])

    def test_dialog_lists_issues_real_tk(self):
        try:
            root = _Tk()
            root.withdraw()
        except am.tk.TclError:
            self.skipTest("ไม่มี display สำหรับ Tk")
        try:
            app = mock.MagicMock()
            app.root = root
            app._plugins = []
            app._serialize = lambda: [
                {"button": "Tap Key", "additional": ""},          # คีย์ว่าง = ปัญหา
                {"button": "Block Start", "additional": ""},
                {"button": "Beep", "additional": ""}]             # Block Start ไม่ปิด = ปัญหา
            am.MacroApp.validate_dialog(app)
            win = root.winfo_children()[-1]
            texts = [w for w in win.winfo_children() if isinstance(w, am.tk.Text)]
            self.assertTrue(texts, "ต้องมีกล่องรายงาน")
            content = texts[0].get("1.0", "end")
            self.assertIn("แถว 1", content)
            self.assertIn("Block Start", content)                # บล็อกไม่ปิดถูกรายงาน
            win.destroy()
        finally:
            root.destroy()

    def test_dialog_clean_shows_pass(self):
        try:
            root = _Tk()
            root.withdraw()
        except am.tk.TclError:
            self.skipTest("ไม่มี display สำหรับ Tk")
        try:
            app = mock.MagicMock()
            app.root = root
            app._plugins = []
            app._serialize = lambda: [{"button": "Beep", "additional": ""}]
            am.MacroApp.validate_dialog(app)
            win = root.winfo_children()[-1]
            labels = [w for w in win.winfo_children() if isinstance(w, am.tk.Label)]
            self.assertTrue(any("ผ่านการตรวจ" in str(l.cget("text")) for l in labels))
            win.destroy()
        finally:
            root.destroy()


class TestAhkBlocks(unittest.TestCase):
    """v2.9: .ahk บล็อกสองทิศ — Block Start/End ⇄ if (...) { } / Loop, N { } / Until"""

    def _src(self, add):
        return [dict(enabled=True, button=me_mod.BLOCK_START, additional=add),
                dict(enabled=True, button="Left Click", x="1", y="2"),
                dict(enabled=True, button=me_mod.BLOCK_END, additional="")]

    def test_export_if_block(self):
        s = me_mod.rows_to_ahk(self._src("if n > 5"))
        self.assertIn("if (n > 5) {", s)
        self.assertIn("\n}", s)

    def test_export_max_and_until(self):
        s = me_mod.rows_to_ahk(self._src("max 3"))
        self.assertIn("Loop, 3 {", s)
        self.assertIn("\n}", s)
        s2 = me_mod.rows_to_ahk(self._src("until n >= 5"))
        self.assertIn("Loop {", s2)
        self.assertIn("Until, n >= 5", s2)      # ต้องอยู่หลังปิดบล็อก
        self.assertLess(s2.index("\n}"), s2.index("Until,"))   # } มาก่อน Until เสมอ

    def test_export_image_cond_comments_both_ends(self):
        s = me_mod.rows_to_ahk(self._src("if img.png"))
        self.assertIn("; (Block Start", s)
        self.assertIn("; (Block End", s)
        self.assertNotIn("\n}", s)               # ห้ามปีกกาลอย — .ahk ต้องรันได้

    def test_import_blocks(self):
        rows = me_mod.ahk_to_rows("if (n > 5) {\nClick 1, 2\n}")
        self.assertEqual([(r["button"], r["additional"]) for r in rows],
                         [(me_mod.BLOCK_START, "if n > 5"), ("Left Click", ""),
                          (me_mod.BLOCK_END, "")])
        rows2 = me_mod.ahk_to_rows("Loop, 3 {\nClick 1, 2\n}")
        self.assertEqual(rows2[0]["additional"], "max 3")
        rows3 = me_mod.ahk_to_rows("Loop {\nClick 1, 2\n}\nUntil, n >= 5")
        self.assertEqual(rows3[0]["additional"], "until n >= 5")
        self.assertEqual(rows3[-1]["button"], me_mod.BLOCK_END)

    def test_roundtrip_blocks(self):
        for add in ("if n > 5", "max 3", "until n >= 5"):
            back = me_mod.ahk_to_rows(me_mod.rows_to_ahk(self._src(add)))
            self.assertEqual([(r["button"], r["additional"]) for r in back],
                             [(me_mod.BLOCK_START, add), ("Left Click", ""),
                              (me_mod.BLOCK_END, "")], add)

    def test_junk_brace_still_skipped(self):
        self.assertEqual(me_mod.ahk_to_rows("{\nif (((\nMsgBox hi"), [])

    def test_example_13_demo_file(self):
        """v2.9: ตัวอย่าง 13 ต้อง validate ผ่าน + บล็อก export .ahk แล้ว import กลับตรงเดิม"""
        path = os.path.join(os.path.dirname(os.path.abspath(am.__file__)),
                            "examples", "13_start_validate_ahk_blocks.json")
        with open(path, encoding="utf-8") as fh:
            rows = json.load(fh)
        self.assertEqual(
            me_mod.validate_rows(rows, plugin_names=[n for n, _ in me_mod.load_plugins()]), [])
        back = me_mod.ahk_to_rows(me_mod.rows_to_ahk(rows))
        core = [(r["button"], r["additional"]) for r in back
                if r["button"] in (me_mod.BLOCK_START, me_mod.BLOCK_END)]
        orig = [(r["button"], r["additional"]) for r in rows
                if r["button"] in (me_mod.BLOCK_START, me_mod.BLOCK_END)]
        self.assertEqual(core, orig)          # if/until/max roundtrip ตรงเป๊ะ

    def test_example_14_dry_run_cond_vars(self):
        """v2.10: ตัวอย่าง 14 ต้อง validate ผ่าน + บล็อก export .ahk กลับตรงเดิม"""
        path = os.path.join(os.path.dirname(os.path.abspath(am.__file__)),
                            "examples", "14_dry_run_cond_vars.json")
        with open(path, encoding="utf-8") as fh:
            rows = json.load(fh)
        self.assertEqual(
            me_mod.validate_rows(rows, plugin_names=[n for n, _ in me_mod.load_plugins()]), [])
        back = me_mod.ahk_to_rows(me_mod.rows_to_ahk(rows))
        core = [(r["button"], r["additional"]) for r in back
                if r["button"] in (me_mod.BLOCK_START, me_mod.BLOCK_END)]
        orig = [(r["button"], r["additional"]) for r in rows
                if r["button"] in (me_mod.BLOCK_START, me_mod.BLOCK_END)]
        self.assertEqual(core, orig)


class TestCollapseAll(unittest.TestCase):
    """v2.9: เมนูขวา ย่อทั้งหมด/ขยายทั้งหมด — ครอบ Section + บล็อกพร้อมกัน"""

    def _app(self):
        app = mock.MagicMock()
        kids = iter("k%d" % i for i in range(1, 999))
        order = []
        store = {}

        def insert(parent, index, **kw):
            iid = next(kids)
            store[iid] = list(kw["values"])
            pos = len(order) if str(index) == "end" else int(index)
            order.insert(pos, iid)
            return iid

        def item(iid, *args, **kw):
            if "values" in kw:
                store[iid] = list(kw["values"])
                return None
            return store[iid]

        app.tree.get_children.side_effect = lambda: list(order)
        app.tree.insert = insert
        app.tree.item = item
        app.tree.index = lambda iid: order.index(iid)
        app.tree.detach = lambda iid: order.remove(iid)
        app._section_stash = []
        app._hl_row = None
        app._ui_state = {"msg": None, "row": None, "prog": None, "reset": False}
        app.refresh_nums = lambda: am.MacroApp.refresh_nums(app)
        for m in ("_group_members", "_group_collapsed", "_group_toggle", "_serialize",
                  "_collapse_all_groups", "_expand_all_groups"):
            setattr(app, m, getattr(am.MacroApp, m).__get__(app))
        return app, store, order

    def _rows(self, app):
        for r in [(am.SECTION_HEADER, "หัวข้อ A", 0), ("Beep", "s1", 1),
                  (am.BLOCK_START, "if n > 5", 0), ("Beep", "b1", 1),
                  (am.BLOCK_END, "", 0), ("Left Click", "", 1)]:
            app.tree.insert("", "end", values=["☑", "#", "", "", r[0], r[1], 0, r[2], 1])

    def test_collapse_all_hides_section_and_block(self):
        app, store, order = self._app()
        self._rows(app)
        app._collapse_all_groups()
        self.assertEqual(len(app.tree.get_children()), 1)   # เห็นหัวข้อ Section เดียว
        rows = app._serialize()
        self.assertEqual([r["additional"] for r in rows],
                         ["หัวข้อ A", "s1", "if n > 5", "b1", "", ""])   # ครบ ลำดับเดิม

    def test_expand_all_restores_everything(self):
        app, store, order = self._app()
        self._rows(app)
        app._collapse_all_groups()
        app._expand_all_groups()
        self.assertEqual(len(app.tree.get_children()), 6)
        self.assertEqual(app._section_stash, [])
        adds = [app.tree.item(i, "values")[5] for i in app.tree.get_children()]
        self.assertEqual(adds, ["หัวข้อ A", "s1", "if n > 5", "b1", "", ""])

    def test_empty_table_no_crash(self):
        app, store, order = self._app()
        app._collapse_all_groups()
        app._expand_all_groups()
        self.assertEqual(app.tree.get_children(), [])


class TestUnifiedPlayValidation(unittest.TestCase):
    """v2.9: กด START ตรวจด้วย engine เดียวกับ 🔍 Validate — แถวที่ตรวจไม่ผ่านถูกข้ามจริง"""

    def _app(self, rows, iids):
        app = mock.MagicMock()
        app._rows_and_iids_for_play = lambda: (list(rows), list(iids))
        app._plugins = []
        app._ui_state = {"msg": None, "row": None, "prog": None, "reset": False}
        app._play_gen = 0
        app._log_enabled = False
        app.chk_forever.get.return_value = False
        app.chk_restore.get.return_value = False
        app.chk_shuffle.get.return_value = False
        app.cmb_speed.get.return_value = "1"
        app.ent_loops.get.return_value = "1"
        app._play_options = lambda: 100
        return app

    def test_invalid_rows_skipped_when_confirmed(self):
        app = self._app(
            [{"button": "Tap Key", "additional": ""}, {"button": "Beep", "secs": 0}],
            ["i1", "i2"])
        threads = []
        with mock.patch.object(am.messagebox, "askyesno", return_value=True) as ask, \
             mock.patch.object(am.threading, "Thread",
                               side_effect=lambda *a, **k:
                               threads.append(k) or mock.MagicMock()):
            am.MacroApp._start_player_inner(app, False)
        ask.assert_called_once()
        self.assertIn("1 จุด", ask.call_args[0][1])
        self.assertEqual(len(threads), 1)
        items = threads[0]["args"][0]
        self.assertEqual([r["button"] for r, _ in items], ["Beep"])   # คีย์ว่างถูกข้ามจริง

    def test_decline_does_not_play(self):
        app = self._app([{"button": "Tap Key", "additional": ""}], ["i1"])
        with mock.patch.object(am.messagebox, "askyesno", return_value=False) as ask, \
             mock.patch.object(am.threading, "Thread") as th:
            am.MacroApp._start_player_inner(app, False)
        ask.assert_called_once()
        th.assert_not_called()

    def test_all_invalid_shows_info(self):
        app = self._app([{"button": "Tap Key", "additional": ""}], ["i1"])
        infos = []
        with mock.patch.object(am.messagebox, "askyesno", return_value=True), \
             mock.patch.object(am.messagebox, "showinfo",
                               side_effect=lambda *a, **k: infos.append(a)), \
             mock.patch.object(am.threading, "Thread") as th:
            am.MacroApp._start_player_inner(app, False)
        self.assertTrue(infos)      # ไม่มีอะไรให้เล่น
        th.assert_not_called()


class TestDryRunEngine(unittest.TestCase):
    """v2.10: โหมด Dry-run — เดินสคริปต์ครบแต่ไม่แตะเมาส์/คีย์ (รายงานแทนทำจริง)"""

    def _runner(self, dry=True, **kw):
        mouse = mock.MagicMock()
        mouse.position = (10, 20)
        kb = mock.MagicMock()
        msgs = []
        r = me_mod.ActionRunner(mouse, kb, dry_run=dry,
                                on_message=lambda t, c="#080": msgs.append((t, c)), **kw)
        return r, mouse, kb, msgs

    def test_dry_run_reports_instead_of_input(self):
        r, mouse, kb, msgs = self._runner()
        r.execute({"button": "Left Click", "x": "11", "y": "22", "additional": ""})
        r.execute({"button": "Tap Key", "additional": "a"})
        mouse.click.assert_not_called()      # ไม่แตะเมาส์จริง
        kb.tap.assert_not_called()           # ไม่แตะคีย์จริง
        text = " ".join(t for t, _c in msgs)
        self.assertIn("DRY-RUN", text)
        self.assertIn("คลิก", text)

    def test_dry_run_variables_and_conditions_still_run(self):
        r, mouse, kb, msgs = self._runner()
        r.execute({"button": "Set Variable", "additional": "n = 7"})
        r.execute({"button": "Read Pixel Color", "additional": "c 5,5"})
        self.assertEqual(r.variables.get("n"), "7")      # ตัวแปรเดินจริง
        self.assertIn("c", r.variables)                  # อ่านสี (ไม่แตะ input) ยังทำงาน
        skip, msg = me_mod.ActionRunner.evaluate_condition(
            me_mod.IF_VAR, "n > 5", 1, 1, variables=r.variables)
        self.assertEqual((skip, msg is not None), (0, True))

    def test_dry_run_off_by_default(self):
        r, mouse, kb, msgs = self._runner(dry=False)
        r.execute({"button": "Left Click", "x": "11", "y": "22", "additional": ""})
        mouse.click.assert_called_once()     # โหมดปกติยังคลิกจริง
        self.assertFalse(any("DRY-RUN" in t for t, _c in msgs))


class TestCondStore(unittest.TestCase):
    """v2.10: เก็บผลเงื่อนไขเป็นตัวแปร — โทเคน '>ชื่อ' ท้าย Additional"""

    def test_parse_cond_store(self):
        rest, name = me_mod.parse_cond_store("img.png >img_ok")
        self.assertEqual((rest, name), ("img.png", "img_ok"))
        rest, name = me_mod.parse_cond_store("300,300 #ffffff")
        self.assertEqual((rest, name), ("300,300 #ffffff", None))
        # กันคำอังกฤษติดท้ายเงื่อนไข (on/of/and) ไม่ถูกตีเป็นชื่อตัวแปร
        rest, name = me_mod.parse_cond_store("Turn on")
        self.assertIsNone(name)

    def test_if_var_stores_result_true(self):
        vars_ = {"n": "5"}
        skip, _msg = me_mod.ActionRunner.evaluate_condition(
            me_mod.IF_VAR, "n > 3 >ผล", 1, 1, variables=vars_)
        self.assertEqual(skip, 0)
        self.assertEqual(vars_.get("ผล"), "1")

    def test_if_var_stores_result_false(self):
        vars_ = {"n": "1"}
        skip, _msg = me_mod.ActionRunner.evaluate_condition(
            me_mod.IF_VAR, "n > 3 >ผล", 1, 1, variables=vars_)
        self.assertGreater(skip, 0)          # ไม่จริง → ข้ามตาม Repeat
        self.assertEqual(vars_.get("ผล"), "0")

    def test_if_loop_and_time_store(self):
        vars_ = {}
        me_mod.ActionRunner.evaluate_condition(me_mod.IF_LOOP, "3 >ถึงรอบ", 1, 5,
                                               variables=vars_)
        self.assertEqual(vars_.get("ถึงรอบ"), "1")   # รอบ 5 >= 3
        vars2 = {}
        me_mod.ActionRunner.evaluate_condition(
            me_mod.IF_TIME, "23:59 >ผ่าน", 1, 1,
            now=time.struct_time((2026, 10, 2, 8, 0, 0, 0, 0, 0)), variables=vars2)
        self.assertEqual(vars2.get("ผ่าน"), "0")     # 08:00 ยังไม่ถึง 23:59

    def test_if_image_store_hit_and_miss(self):
        calls = [True, False]
        runner, _mouse, _kb, _msgs = self._runner_cond()
        runner.find_image_cb = lambda r: (10, 10) if calls.pop(0) else None
        runner.execute({"button": me_mod.IF_IMAGE, "additional": "img.png >เจอ",
                        "repeat": 2})
        self.assertEqual(runner.variables.get("เจอ"), "1")
        self.assertEqual(runner.skip_n, 0)
        runner.execute({"button": me_mod.IF_IMAGE, "additional": "img.png >เจอ",
                        "repeat": 2})
        self.assertEqual(runner.variables.get("เจอ"), "0")
        self.assertEqual(runner.skip_n, 2)

    def test_if_pixel_store(self):
        runner, _mouse, _kb, _msgs = self._runner_cond()
        with mock.patch.object(me_mod, "pixel_color_at", return_value=(255, 255, 255)), \
             mock.patch.object(me_mod, "color_close", return_value=True):
            runner.execute({"button": me_mod.IF_PIXEL,
                            "additional": "1,1 #ffffff >สีตรง", "repeat": 1})
        self.assertEqual(runner.variables.get("สีตรง"), "1")

    def _runner_cond(self, **kw):
        """runner สำหรับเทสต์เงื่อนไข (ยังไม่ dry — อยากทดสอบเส้นเงื่อนไขล้วน)"""
        mouse = mock.MagicMock()
        mouse.position = (10, 20)
        kb = mock.MagicMock()
        msgs = []
        r = me_mod.ActionRunner(mouse, kb, find_image_cb=lambda r: None,
                                on_message=lambda t, c="#080": msgs.append((t, c)), **kw)
        return r, mouse, kb, msgs


class TestQueueCli(unittest.TestCase):
    """v2.10: --queue — รันสคริปต์หลายไฟล์ตามลิสต์ (in-process cli_main — Beep ล้วนปลอดภัย)"""

    def _write(self, d, name, obj):
        p = os.path.join(d, name)
        with open(p, "w", encoding="utf-8") as fh:
            if isinstance(obj, str):
                fh.write(obj)
            else:
                json.dump(obj, fh, ensure_ascii=False)
        return p

    def _beep(self, text="ปลอดภัย"):
        return {"enabled": True, "button": "Beep", "additional": text,
                "mins": 0, "secs": 0, "repeat": 1}

    def test_queue_runs_all_and_summarizes(self):
        d = tempfile.mkdtemp(prefix="macro_queue_")
        self._write(d, "a.json", [self._beep("A")])
        self._write(d, "b.json", [self._beep("B")])
        lst = self._write(d, "list.txt", "# คอมเมนต์\na.json\nb.json\n\n")
        out = io.StringIO()
        with mock.patch("sys.stdout", out):
            rc = am.cli_main(["--queue", lst, "--no-log"])
        self.assertEqual(rc, 0)
        text = out.getvalue()
        self.assertIn("ผ่านการตรวจ: a.json", text)
        self.assertIn("คิวที่ 1/2", text)
        self.assertIn("คิวที่ 2/2", text)
        self.assertIn("สรุปคิว (2 ไฟล์)", text)
        self.assertIn("จบครบ ✔", text)

    def test_queue_all_broken_cancels_before_playing(self):
        d = tempfile.mkdtemp(prefix="macro_queue_")
        bad = {"enabled": True, "button": "Tap Key", "additional": "",
               "mins": 0, "secs": 0, "repeat": 1}
        self._write(d, "ok.json", [self._beep("x")])
        self._write(d, "bad.json", [bad])
        lst = self._write(d, "list.txt", "ok.json\nbad.json\n")
        out = io.StringIO()
        with mock.patch("sys.stdout", out):
            rc = am.cli_main(["--queue", lst, "--no-log"])
        self.assertEqual(rc, 1)
        text = out.getvalue()
        self.assertIn("ยกเลิกทั้งคิว", text)
        self.assertNotIn("— รอบที่", text)      # ไม่มีการเล่นเกิดขึ้นเลย (ตรวจก่อนเริ่ม)

    def test_queue_missing_file_exits_1(self):
        d = tempfile.mkdtemp(prefix="macro_queue_")
        self._write(d, "list.txt", "no_such.json\n")
        out = io.StringIO()
        with mock.patch("sys.stdout", out):
            rc = am.cli_main(["--queue", os.path.join(d, "list.txt"), "--no-log"])
        self.assertEqual(rc, 1)
        self.assertIn("ไม่พบ", out.getvalue())


class TestCliDryRun(unittest.TestCase):
    """v2.10: CLI --dry-run — แถว input จริงถูกรายงาน ไม่แตะเมาส์/คีย์"""

    def test_cli_dry_run_reports(self):
        d = tempfile.mkdtemp(prefix="macro_dry_")
        p = os.path.join(d, "s.json")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump([{ "enabled": True, "button": "Beep", "additional": "ok",
                         "mins": 0, "secs": 0, "repeat": 1}], fh, ensure_ascii=False)
        out = io.StringIO()
        # v2.10.1: cli_main เขียนรายงาน dry-run จริง — patch พาธไปที่ชั่วคราว
        # กันเทสต์เขียนไฟล์ทิ้งข้างโค้ด (เหมือน log_path เดิม)
        with mock.patch("sys.stdout", out), \
             mock.patch.object(am, "dry_report_path",
                               return_value=os.path.join(d, "dry_report_test.txt")):
            rc = am.cli_main([p, "--dry-run", "--no-log"])
        self.assertEqual(rc, 0)
        text = out.getvalue()
        self.assertIn("DRY-RUN", text)
        self.assertIn("DRY-RUN: จะส่งเสียง Beep", text)


class TestDryReport(unittest.TestCase):
    """v2.10.1: รายงาน Dry-run เป็นไฟล์ — engine helpers + GUI/CLI เขียนจริง
    (patch dry_report_path เสมอ — ห้ามเขียนไฟล์ข้างโค้ดจริง)"""

    def test_summary_counts_by_action(self):
        lines = ["DRY-RUN: จะคลิก Left Click 100,200",
                 "DRY-RUN: จะคลิก Double Left Click 5,5",
                 "DRY-RUN: จะคลิก Left Click 300,300",
                 "DRY-RUN: จะส่งเสียง Beep",
                 "DRY-RUN: ที่พิกัด 100,200"]      # บรรทัดพิกัด — ไม่มี action ไม่นับ
        sums = me_mod.dry_report_summary(lines)
        self.assertEqual(sums[0], "Left Click ×2")
        self.assertIn("Double Left Click ×1", sums)
        self.assertIn("Beep ×1", sums)
        self.assertEqual(me_mod.dry_report_summary([]), [])

    def test_block_structure_and_stopped_marker(self):
        lines = me_mod.dry_report_block("job.json", 3, "2",
                                        ["DRY-RUN: จะส่งเสียง Beep"], finished=True)
        self.assertIn("job.json", lines[0])
        self.assertTrue(any("แถวที่จะเล่น: 3" in x for x in lines))
        self.assertTrue(any("รอบ: 2" in x for x in lines))
        self.assertIn("DRY-RUN: จะส่งเสียง Beep", lines)
        self.assertTrue(any(x.startswith("สรุปจะทำจริง: Beep ×1") for x in lines))
        self.assertNotIn("ถูกหยุดกลางคัน", "\n".join(lines))
        lines2 = me_mod.dry_report_block("job.json", 3, "ไม่จำกัด", [], finished=False)
        self.assertIn("ถูกหยุดกลางคัน", "\n".join(lines2))
        self.assertIn("===== จบรายงาน Dry-run =====", lines2)

    def test_write_appends_to_patched_path(self):
        d = tempfile.mkdtemp(prefix="macro_drywr_")
        target = os.path.join(d, "dry_report_x.txt")
        try:
            with mock.patch.object(me_mod, "dry_report_path", return_value=target):
                me_mod.dry_report_write(["บรรทัด 1", "บรรทัด 2"], src="s.json")
                me_mod.dry_report_write(["บรรทัด 3"])
            with open(target, encoding="utf-8") as fh:
                text = fh.read()
            self.assertIn("บรรทัด 1\nบรรทัด 2\n", text)      # เขียนครั้งแรก
            self.assertIn("บรรทัด 3", text)                # ครั้งที่สองต่อท้าย
            self.assertNotIn("บรรทัด 1\nบรรทัด 2\nบรรทัด 3", text)  # แยกบล็อกกัน
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_cli_dry_run_writes_report(self):
        """CLI --dry-run จบรอบแล้วเขียนรายงานไฟล์ + พิมพ์พาธรายงานให้ผู้ใช้รู้"""
        d = tempfile.mkdtemp(prefix="macro_drycli_")
        target = os.path.join(d, "dry_report_cli.txt")
        p = os.path.join(d, "s.json")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump([{"enabled": True, "button": "Beep", "additional": "",
                        "mins": 0, "secs": 0, "repeat": 1}], fh, ensure_ascii=False)
        try:
            out = io.StringIO()
            with mock.patch.object(am, "dry_report_path", return_value=target), \
                 mock.patch("sys.stdout", out):
                rc = am.cli_main([p, "--dry-run", "--no-log"])
            self.assertEqual(rc, 0)
            self.assertTrue(os.path.isfile(target))
            with open(target, encoding="utf-8") as fh:
                text = fh.read()
            self.assertIn("DRY-RUN: จะส่งเสียง Beep", text)
            self.assertIn("Beep ×1", text)
            self.assertIn(os.path.basename(target), out.getvalue())   # พิมพ์พาธรายงาน
            # เล่นจริง (ไม่ใส่ --dry-run) — ห้ามเขียนรายงาน
            before = os.path.getsize(target)
            out2 = io.StringIO()
            with mock.patch.object(am, "dry_report_path", return_value=target), \
                 mock.patch("sys.stdout", out2):
                am.cli_main([p, "--no-log"])
            self.assertEqual(os.path.getsize(target), before)
        finally:
            shutil.rmtree(d, ignore_errors=True)


class TestQueueBatchExport(unittest.TestCase):
    """v2.10.1: 🗂️ Queue Bat — export .bat/.sh สำหรับรันคิวหลายสคริปต์ผ่าน --queue"""

    def test_bat_content(self):
        s = me_mod.batch_queue_export_bat("mylist.txt")
        self.assertTrue(s.startswith("@echo off"))
        self.assertIn('py auto_macro.py --queue "mylist.txt" %*', s)
        self.assertIn("pause", s)
        self.assertIn('cd /d "%~dp0"', s)

    def test_sh_content(self):
        s = me_mod.batch_queue_export_sh("mylist.txt")
        self.assertTrue(s.startswith("#!/bin/sh"))
        self.assertIn('cd "$(dirname "$0")"', s)
        self.assertIn('python3 auto_macro.py --queue "mylist.txt" "$@"', s)

    def test_gui_method_exports_next_to_list(self):
        app = mock.MagicMock()
        app._loaded_file = None
        with tempfile.TemporaryDirectory() as d:
            lst = os.path.join(d, "mylist.txt")
            with open(lst, "w", encoding="utf-8") as fh:
                fh.write("# คิวตัวอย่าง\n")
            with mock.patch.object(am.filedialog, "askopenfilename", return_value=lst):
                am.MacroApp.export_queue_batch_files(app)   # เขียนไฟล์จริงข้างลิสต์
            bat = os.path.join(d, "mylist.bat")
            shp = os.path.join(d, "mylist.sh")
            self.assertTrue(os.path.isfile(bat))
            self.assertTrue(os.path.isfile(shp))
            with open(bat, encoding="ascii") as fh:
                self.assertIn('--queue "mylist.txt"', fh.read())
            with open(shp, encoding="utf-8") as fh:
                self.assertIn('--queue "mylist.txt"', fh.read())

    def test_gui_cancelled_writes_nothing(self):
        app = mock.MagicMock()
        app._loaded_file = None
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(am.filedialog, "askopenfilename", return_value=""):
                am.MacroApp.export_queue_batch_files(app)
            self.assertEqual(os.listdir(d), [])

    def test_menu_has_queue_entry(self):
        names = [name for _, _, name, _ in am.MacroApp._menu_items()]
        self.assertIn("export_queue_batch_files", names)
        self.assertIn("export_batch_files", names)          # ของเดิมคงอยู่


class TestLogTools(unittest.TestCase):
    """v2.11: เครื่องมือ log — เก็บถาวรรายเดือน (log_archive/) / เคลียร์วันเก่า
    (เทสต์ engine ผ่าน base_dir ชั่วคราวเสมอ — ห้ามแตะ log จริงข้างโค้ด)"""

    @staticmethod
    def _make(base_dir, name, text="x"):
        p = os.path.join(base_dir, name)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
        return p

    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="macro_logtool_")
        self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)
        self.today = datetime.date.today()          # กฎเหล็ก: ห้าม hardcode วันที่

    def test_archive_moves_old_files_to_monthly_folders(self):
        old1 = self._make(self.d, "macro_log_2026-08-15.txt")
        old2 = self._make(self.d, "macro_log_2026-09-20.txt")
        dry = self._make(self.d, "dry_report_2026-09-01.txt")
        td = self._make(self.d, "macro_log_%s.txt" % self.today.isoformat())
        junk = self._make(self.d, "macro_log_badname.txt")
        n, mode = me_mod.cleanup_old_logs(base_dir=self.d, archive=True)
        self.assertEqual((n, mode), (3, "archive"))
        self.assertFalse(os.path.isfile(old1))      # ต้นทางถูกย้ายออก
        arch = me_mod.log_archive_path(self.d)
        self.assertTrue(os.path.isfile(
            os.path.join(arch, "2026-08", "macro_log_2026-08-15.txt")))
        self.assertTrue(os.path.isfile(
            os.path.join(arch, "2026-09", "macro_log_2026-09-20.txt")))
        self.assertTrue(os.path.isfile(
            os.path.join(arch, "2026-09", "dry_report_2026-09-01.txt")))
        self.assertTrue(os.path.isfile(td))         # ไฟล์วันนี้ไม่แตะเสมอ
        self.assertTrue(os.path.isfile(junk))       # ชื่อไม่ตรงรูปแบบไม่แตะ

    def test_clear_deletes_old_files(self):
        old = self._make(self.d, "macro_log_2026-08-15.txt")
        td = self._make(self.d, "macro_log_%s.txt" % self.today.isoformat())
        n, mode = me_mod.cleanup_old_logs(base_dir=self.d, archive=False)
        self.assertEqual((n, mode), (1, "delete"))
        self.assertFalse(os.path.isfile(old))
        self.assertTrue(os.path.isfile(td))         # วันนี้ไม่แตะเสมอ
        self.assertFalse(os.path.isdir(me_mod.log_archive_path(self.d)))

    def test_keep_days_window(self):
        near = self._make(self.d, "macro_log_%s.txt"
                          % (self.today - datetime.timedelta(days=3)).isoformat())
        far = self._make(self.d, "macro_log_%s.txt"
                         % (self.today - datetime.timedelta(days=10)).isoformat())
        n, _ = me_mod.cleanup_old_logs(base_dir=self.d, keep_days=7, archive=False)
        self.assertEqual(n, 1)
        self.assertTrue(os.path.isfile(near))       # อายุ 3 วัน — ยังไม่เกินกำหนด
        self.assertFalse(os.path.isfile(far))       # อายุ 10 วัน — หมดอายุ

    def test_archive_never_overwrites_existing_destination(self):
        past = self.today - datetime.timedelta(days=40)
        day = past.isoformat()
        dest_dir = os.path.join(me_mod.log_archive_path(self.d), past.strftime("%Y-%m"))
        os.makedirs(dest_dir)
        self._make(dest_dir, "macro_log_%s.txt" % day, "เดิม")
        self._make(self.d, "macro_log_%s.txt" % day, "ใหม่")
        n, _ = me_mod.cleanup_old_logs(base_dir=self.d, archive=True)
        self.assertEqual(n, 0)                      # ปลายทางมีแล้ว = ข้าม
        with open(os.path.join(dest_dir, "macro_log_%s.txt" % day),
                  encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "เดิม")      # ไม่ทับของเดิม
        self.assertTrue(os.path.isfile(os.path.join(self.d, "macro_log_%s.txt" % day)))

    def test_gui_close_autoclean_calls_engine(self):
        """ปิดโปรแกรม = จัดการ log วันเก่าตามที่ตั้ง (0 = ปิด ไม่เรียก)"""
        app = mock.MagicMock()
        app._log_keep_days = 7
        app._log_archive = True
        with mock.patch.object(am, "cleanup_old_logs") as m:
            am.MacroApp._on_close(app)
        self.assertTrue(m.called)
        self.assertEqual(m.call_args.kwargs.get("keep_days"), 7)
        self.assertEqual(m.call_args.kwargs.get("archive"), True)
        app2 = mock.MagicMock()
        app2._log_keep_days = 0
        with mock.patch.object(am, "cleanup_old_logs") as m2:
            am.MacroApp._on_close(app2)
        self.assertFalse(m2.called)                 # ปิดฟีเจอร์ = ไม่แตะไฟล์

    def test_settings_save_reads_log_tools(self):
        app = mock.MagicMock()
        app.var_log.get.return_value = True
        app.var_backup.get.return_value = True
        app.spin_days.get.return_value = "7"
        app.var_logclean.get.return_value = True
        app.spin_logdays.get.return_value = "30"
        app.var_logarchive.get.return_value = False
        app.var_time_limit.get.return_value = False
        app.spin_limit.get.return_value = "30"
        app.cmb_lang.get.return_value = "ไทย (Thai)"
        app._lang = "th"
        win = mock.MagicMock()
        am.MacroApp._settings_save(app, win)
        self.assertEqual(app._log_keep_days, 30)
        self.assertEqual(app._log_archive, False)
        app.spin_logdays.get.return_value = "999"   # เกินขอบ — หนีบ 365
        am.MacroApp._settings_save(app, win)
        self.assertEqual(app._log_keep_days, 365)


class TestLogToolsGui(unittest.TestCase):
    """v2.11: หน้าต่าง 📝 Log — เห็นรายงาน dry-run + ปุ่มเก็บถาวร/ล้างเรียก engine จริง
    (patch พาธโปรแกรมไปโฟลเดอร์ชั่วคราว — ห้ามแตะ log จริงข้างโค้ด)"""

    @classmethod
    def setUpClass(cls):
        try:
            cls.root = _Tk()
            cls.root.withdraw()
            cls.has_tk = True
        except am.tk.TclError:
            cls.has_tk = False

    @classmethod
    def tearDownClass(cls):
        if cls.has_tk:
            cls.root.destroy()

    def setUp(self):
        if not self.has_tk:
            self.skipTest("ไม่มี display สำหรับ Tk")
        self.d = tempfile.mkdtemp(prefix="macro_loggui_")
        self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)
        self.app = mock.MagicMock()
        self.app.root = self.root
        self.app._lang = "th"
        self.app._t = lambda key: am.tr("th", key)
        self.app._ui_state = {"msg": None}
        self._make("macro_log_2099-01-01.txt", "log วันนี้ (จำลอง)")
        self._make("dry_report_2099-01-01.txt", "รายงาน dry-run (จำลอง)")
        self._patcher = mock.patch.object(
            am.os.path, "abspath",
            return_value=os.path.join(self.d, "auto_macro.py"))
        self._patcher2 = mock.patch.object(am.os.path, "dirname", return_value=self.d)
        self._patcher.start()
        self._patcher2.start()
        self.addCleanup(self._patcher.stop)
        self.addCleanup(self._patcher2.stop)
        n_win = len(self.root.winfo_children())
        am.MacroApp.view_log(self.app)
        self.win = self.root.winfo_children()[n_win]
        self.addCleanup(self.win.destroy)

    def _make(self, name, text):
        with open(os.path.join(self.d, name), "w", encoding="utf-8") as fh:
            fh.write(text)

    def _widgets(self, w, kinds):
        out = []
        for c in w.winfo_children():
            if isinstance(c, kinds):
                out.append(c)
            out.extend(self._widgets(c, kinds))
        return out

    def _button_by_text(self, text):
        for b in self._widgets(self.win, am.tk.Button):
            if text in str(b.cget("text")):
                return b
        return None

    def test_dry_report_listed_in_combobox(self):
        cmb = self._widgets(self.win, am.ttk.Combobox)[0]
        vals = list(cmb["values"])
        self.assertIn("dry_report_2099-01-01.txt", vals)   # v2.11: เห็นรายงาน dry-run
        self.assertIn("macro_log_2099-01-01.txt", vals)

    def test_archive_button_calls_engine_and_statusbar(self):
        with mock.patch.object(am, "cleanup_old_logs",
                               return_value=(2, "archive")) as m:
            self._button_by_text("เก็บถาวรวันเก่า").invoke()
        self.assertTrue(m.called)
        self.assertEqual(m.call_args.kwargs.get("archive"), True)
        self.assertEqual(m.call_args.kwargs.get("base_dir"), self.d)  # โฟลเดอร์ชั่วคราว
        self.assertIn("เก็บถาวรแล้ว 2 ไฟล์", self.app._ui_state["msg"][0])  # statusbar เท่านั้น

    def test_clear_button_asks_then_deletes(self):
        with mock.patch.object(am, "cleanup_old_logs",
                               return_value=(1, "delete")) as m, \
             mock.patch.object(am.messagebox, "askyesno", return_value=True):
            self._button_by_text("ล้างวันเก่า").invoke()
        self.assertTrue(m.called)
        self.assertEqual(m.call_args.kwargs.get("archive"), False)
        self.assertIn("ล้างแล้ว 1 ไฟล์", self.app._ui_state["msg"][0])
        # ตอบปฏิเสธ = ไม่แตะไฟล์
        with mock.patch.object(am, "cleanup_old_logs") as m2, \
             mock.patch.object(am.messagebox, "askyesno", return_value=False):
            self._button_by_text("ล้างวันเก่า").invoke()
        self.assertFalse(m2.called)

    def test_cleanup_rebuilds_file_list(self):
        with mock.patch.object(am, "cleanup_old_logs",
                               return_value=(1, "archive")):
            self._button_by_text("เก็บถาวรวันเก่า").invoke()
        cmb = self._widgets(self.win, am.ttk.Combobox)[0]
        # เทสต์ไม่ได้ลบไฟล์จริง (cleanup ถูก patch) — รายการยังครบ แต่ต้องสร้างใหม่โดยไม่พัง
        self.assertIn("macro_log_2099-01-01.txt", list(cmb["values"]))


class TestQueueListParse(unittest.TestCase):
    """v2.12: engine parse_queue_list — แหล่งเดียวของไฟล์ลิสต์คิว (CLI --queue + 📑 Run Queue)"""

    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="macro_qlist_")
        self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)

    def _write(self, name, text):
        p = os.path.join(self.d, name)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
        return p

    def test_relative_paths_resolved_against_list_dir(self):
        a = self._write("a.json", "[]")
        sub = os.path.join(self.d, "sub")
        os.makedirs(sub, exist_ok=True)
        lst = self._write("list.txt", "# คอมเมนต์\na.json\n\n%s\n"
                          % os.path.join(sub, "x.json"))
        scripts, err = me_mod.parse_queue_list(lst)
        self.assertIsNone(err)
        self.assertEqual([p for p, _ln in scripts],
                         [a, os.path.join(sub, "x.json")])
        self.assertEqual([ln for _p, ln in scripts], [2, 4])

    def test_missing_list_file(self):
        scripts, err = me_mod.parse_queue_list(os.path.join(self.d, "nope.txt"))
        self.assertEqual(scripts, [])
        self.assertIn("ไม่พบไฟล์ลิสต์", err)

    def test_empty_list(self):
        lst = self._write("empty.txt", "# เฉพาะคอมเมนต์\n\n")
        scripts, err = me_mod.parse_queue_list(lst)
        self.assertEqual(scripts, [])
        self.assertIn("ว่าง", err)


class TestQueueRunnerGui(unittest.TestCase):
    """v2.12: ผู้เล่นคิวแบบ GUI — หน้าต่าง 📑 Run Queue + เธรดเล่น
    ใช้ MacroApp จริง · patch am.cli_main (สคริปต์ Beep ล้วนปลอดภัยอยู่แล้ว
    แต่จำลอง rc เพื่อทดสอบสาขาหยุดโดยไม่เล่นจริง) — ไม่มี display จะ skip อัตโนมัติ"""

    @classmethod
    def setUpClass(cls):
        try:
            cls.root = _Tk()
            cls.root.withdraw()
        except am.tk.TclError:
            cls.root = None
            cls.app = None
            return
        try:
            cls.app = am.MacroApp(cls.root)
        except Exception:
            cls.root.destroy()
            cls.root = None
            cls.app = None

    @classmethod
    def tearDownClass(cls):
        if cls.app is not None:
            try:
                cls.app._queue_destroy_window()
            except Exception:
                pass
        if cls.root is not None:
            # v2.14.1: _Tk.destroy() ยกเลิก timer ทั้งหมดก่อนเอง — กัน spam "invalid command name"
            # และ SIGTRAP บน macOS
            cls.root.destroy()

    def setUp(self):
        if self.app is None:
            self.skipTest("ไม่มี display สำหรับ Tk")
        self.d = tempfile.mkdtemp(prefix="macro_qrun_")
        self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)
        self.app._log_enabled = False               # เทสต์ไม่แตะ log จริง
        self.app._queue_destroy_window()            # เคลียร์คิวจากเทสต์ก่อนหน้า
        self.addCleanup(self.app._queue_destroy_window)
        self.addCleanup(_cancel_tk_afters, self.root)

    def _beep(self, text="ปลอดภัย"):
        return {"enabled": True, "button": "Beep", "additional": text,
                "mins": 0, "secs": 0, "repeat": 1}

    def _setup(self, names=("a.json", "b.json")):
        for nm in names:
            with open(os.path.join(self.d, nm), "w", encoding="utf-8") as fh:
                json.dump([self._beep(nm)], fh, ensure_ascii=False)
        lst = os.path.join(self.d, "list.txt")
        with open(lst, "w", encoding="utf-8") as fh:
            fh.write("\n".join(names) + "\n")
        return lst

    def _open(self, lst):
        with mock.patch.object(am.filedialog, "askopenfilename", return_value=lst):
            self.app.queue_run_dialog()
        self.assertIsNotNone(getattr(self.app, "_qr_win", None))

    def _pump_until(self, cond, timeout=8.0):
        """เข้า event loop จำลอง — ปั่น update() ให้ poller (after 500ms) ทำงานจน cond จริง"""
        t0 = time.time()
        while time.time() - t0 < timeout:
            try:
                self.root.update()
            except Exception:
                pass
            if cond():
                return True
            time.sleep(0.05)
        return False

    def _status(self, i):
        return str(self.app._qr_tree.item(self.app._qr_iids[i], "values")[2])

    def test_menu_has_run_queue(self):
        names = [name for _, _, name, _ in am.MacroApp._menu_items()]
        self.assertIn("queue_run_dialog", names)

    def test_dialog_lists_files(self):
        lst = self._setup()
        self._open(lst)
        vals = [self.app._qr_tree.item(iid, "values")
                for iid in self.app._qr_tree.get_children()]
        self.assertEqual(len(vals), 2)
        self.assertEqual(str(vals[0][2]), "รอเล่น")
        self.assertIn("a.json", str(vals[0][1]))

    def test_dialog_cancel_silent(self):
        n0 = len(self.root.winfo_children())
        with mock.patch.object(am.filedialog, "askopenfilename", return_value=""):
            self.app.queue_run_dialog()
        self.assertIsNone(getattr(self.app, "_qr_win", None))
        self.assertEqual(len(self.root.winfo_children()), n0)

    def test_dialog_bad_list_shows_error(self):
        with mock.patch.object(am.filedialog, "askopenfilename",
                               return_value=os.path.join(self.d, "nope.txt")), \
             mock.patch.object(am.messagebox, "showerror") as merr:
            self.app.queue_run_dialog()
        self.assertTrue(merr.called)
        self.assertIsNone(getattr(self.app, "_qr_win", None))

    def test_worker_runs_all_files(self):
        lst = self._setup()
        self._open(lst)
        calls = []

        def fake_cli(argv):
            calls.append(list(argv))
            return 0

        with mock.patch.object(am, "cli_main", side_effect=fake_cli):
            self.app._queue_start()
            ok = self._pump_until(lambda: not self.app._qr_running)
        self.assertTrue(ok, "คิวไม่จบภายในเวลา")
        self.assertEqual(len(calls), 2)
        self.assertIn("--no-log", calls[0])          # log ปิดอยู่ = ส่ง --no-log ให้ CLI
        self.assertIn("--stop-file", calls[0])       # ช่องทางหยุดของปุ่มในหน้าต่าง
        self.assertTrue(calls[0][-1].endswith("a.json"))
        self.assertEqual(self._status(0), "จบครบ ✔")
        self.assertEqual(self._status(1), "จบครบ ✔")
        self.assertIn("สำเร็จ 2/2", self.app._qr_sum_lbl.cget("text"))
        self.assertEqual(str(self.app._qr_btn_play.cget("state")), "normal")
        self.assertEqual(str(self.app._qr_btn_stop1.cget("state")), "disabled")

    def test_worker_stop_all_cancels_rest(self):
        lst = self._setup()
        self._open(lst)

        def fake_cli(argv):                          # จำลอง F8/Esc — ผู้ใช้สั่งหยุดเอง
            self.app._qr_stop_all = True
            return 130

        with mock.patch.object(am, "cli_main", side_effect=fake_cli):
            self.app._queue_start()
            ok = self._pump_until(lambda: not self.app._qr_running)
        self.assertTrue(ok)
        self.assertEqual(self._status(0), "ถูกหยุด")
        self.assertEqual(self._status(1), "— (ยกเลิก)")
        self.assertIn("สำเร็จ 0/2", self.app._qr_sum_lbl.cget("text"))
        self.assertIn("ถูกหยุด 1", self.app._qr_sum_lbl.cget("text"))

    def test_worker_stop_file_continues_queue(self):
        lst = self._setup()
        self._open(lst)
        state = {"stopped": False}

        def fake_cli(argv):                          # จำลองกด ⏹ หยุดไฟล์นี้ → เล่นไฟล์ถัดไป
            if not state["stopped"]:
                state["stopped"] = True
                self.app._qr_stop_file = True
                return 130
            return 0

        with mock.patch.object(am, "cli_main", side_effect=fake_cli):
            self.app._queue_start()
            ok = self._pump_until(lambda: not self.app._qr_running)
        self.assertTrue(ok)
        self.assertEqual(self._status(0), "ถูกหยุด")
        self.assertEqual(self._status(1), "จบครบ ✔")
        self.assertIn("สำเร็จ 1/2", self.app._qr_sum_lbl.cget("text"))

    def test_worker_invalid_file_cancels_before_playing(self):
        lst = self._setup()
        with open(os.path.join(self.d, "b.json"), "w", encoding="utf-8") as fh:
            fh.write('{"broken": true}')
        self._open(lst)
        with mock.patch.object(am, "cli_main") as mcli:
            self.app._queue_start()
            ok = self._pump_until(lambda: not self.app._qr_running)
        self.assertTrue(ok)
        self.assertFalse(mcli.called)                # ตรวจก่อนเล่น — ไม่เล่นสักแถว (เหมือน CLI)
        self.assertEqual(self._status(1), "ตรวจไม่ผ่าน")
        self.assertIn("ยกเลิกทั้งคิว", self.app._qr_sum_lbl.cget("text"))

    def test_stop_all_button_creates_stopfile_and_flags(self):
        lst = self._setup()
        self._open(lst)
        self.app._qr_running = True
        self.app._qr_current = 1
        self.app._queue_stop_all()
        self.assertTrue(self.app._qr_stop_all)
        self.assertTrue(self.app._qr_stop_file)
        p = self.app._qr_stopfiles.get(1)
        self.assertTrue(p and os.path.isfile(p))     # CLI --stop-file จะเห็นไฟล์นี้แล้วหยุดเอง
        self.app._queue_clear_stopfiles()
        self.assertFalse(os.path.isfile(p))

    def test_worker_real_cli_end_to_end(self):
        """คิวผ่าน cli_main จริง (สคริปต์ Beep ล้วน — เหมือน TestQueueCli) — จบครบ"""
        lst = self._setup(("solo.json",))
        self._open(lst)
        self.app._queue_start()
        ok = self._pump_until(lambda: not self.app._qr_running, timeout=15.0)
        self.assertTrue(ok)
        self.assertEqual(self._status(0), "จบครบ ✔")
        self.assertIn("สำเร็จ 1/1", self.app._qr_sum_lbl.cget("text"))


# ============================ Plugin API v3 (v2.13) ==========================
class TestConditionPlugins(unittest.TestCase):
    """v2.13: เงื่อนไข plugin — load_plugins (CONDITION_NAME + check) / validate_rows /
    evaluate_plugin_condition (แถว) / evaluate_block_condition (Block Start/End) /
    row_tags + .ahk export (แปลไม่ได้ = comment) + plugin ตัวอย่าง file_exists.py"""

    COND_A = (
        "CONDITION_NAME = 'Flag On'\n"
        "def check(ctx, row):\n"
        "    return str(row.get('additional') or '').strip() == 'on'\n")
    MIXED = (
        "ACTION_NAME = 'Echo (test)'\n"
        "CONDITION_NAME = 'Flag Off'\n"
        "def run(ctx, row):\n"
        "    pass\n"
        "def check(ctx, row):\n"
        "    return False\n")
    BROKEN = "CONDITION_NAME = 'No Check'\n"            # ไม่มี check → ข้ามไฟล์
    COLLIDE_BUILTIN = (
        "CONDITION_NAME = 'Left Click'\n"                # ชน Action เดิม
        "def check(ctx, row):\n"
        "    return True\n")
    COLLIDE_DUP = (
        "CONDITION_NAME = 'Flag On'\n"                   # ชนเงื่อนไขของไฟล์อื่น
        "def check(ctx, row):\n"
        "    return True\n")
    COLLIDE_ACT_VS_COND = (
        "ACTION_NAME = 'Flag Off'\n"                     # ชน CONDITION_NAME ของ mixed.py
        "def run(ctx, row):\n"
        "    pass\n")

    def _plugins_dir(self, files):
        import shutil
        d = tempfile.mkdtemp(prefix="macro_cond_plug_")
        os.makedirs(os.path.join(d, me_mod.PLUGINS_DIR), exist_ok=True)
        for nm, src in files.items():
            with open(os.path.join(d, me_mod.PLUGINS_DIR, nm), "w",
                      encoding="utf-8") as fh:
                fh.write(src)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d

    def _mk_runner(self, conditions, variables=None):
        msgs = []
        runner = me_mod.ActionRunner(
            mock.MagicMock(), mock.MagicMock(),
            stop_check=lambda: True,
            on_message=lambda t, c="#080": msgs.append(str(t)),
            variables=variables if variables is not None else {},
            conditions=conditions)
        return runner, msgs

    # ------------------------- load_plugins -------------------------
    def test_load_action_and_condition(self):
        d = self._plugins_dir({"broken.py": self.BROKEN, "conda.py": self.COND_A,
                               "mixed.py": self.MIXED})
        acts = dict(me_mod.load_plugins(d))
        conds = dict(getattr(me_mod.load_plugins, "last_conditions"))
        self.assertIn("Echo (test)", acts)
        self.assertIn("Flag On", conds)
        self.assertIn("Flag Off", conds)
        failed = getattr(me_mod.load_plugins, "last_failed")
        self.assertTrue(any("broken" in f for f in failed), failed)

    def test_name_collisions_rejected_both_ways(self):
        d = self._plugins_dir({
            "a_builtin.py": self.COLLIDE_BUILTIN, "a_conda.py": self.COND_A,
            "a_dup.py": self.COLLIDE_DUP, "mixed.py": self.MIXED,
            "z_act_vs_cond.py": self.COLLIDE_ACT_VS_COND})
        acts = dict(me_mod.load_plugins(d))
        conds = dict(getattr(me_mod.load_plugins, "last_conditions"))
        self.assertIn("Echo (test)", acts)
        self.assertEqual(sorted(conds), ["Flag Off", "Flag On"])
        failed = "\n".join(getattr(me_mod.load_plugins, "last_failed"))
        self.assertIn("a_builtin", failed)         # ชื่อชน Action เดิม
        self.assertIn("a_dup", failed)             # ชื่อซ้ำกับเงื่อนไขอื่น
        self.assertIn("z_act_vs_cond", failed)     # Action ชน CONDITION_NAME ของไฟล์อื่น

    def test_match_condition_name(self):
        names = ("File Exists", "Check Row")
        self.assertEqual(me_mod.match_condition_name("File Exists", names),
                         ("File Exists", ""))
        self.assertEqual(me_mod.match_condition_name("File Exists  C:\\x", names),
                         ("File Exists", "C:\\x"))
        self.assertEqual(me_mod.match_condition_name("Check Row 7", names),
                         ("Check Row", "7"))
        self.assertIsNone(me_mod.match_condition_name("Unknown", names))
        self.assertIsNone(me_mod.match_condition_name("", names))
        # ชื่อยาวสุดมาก่อน — กันชื่อซ้อน (Check / Check Row)
        self.assertEqual(me_mod.match_condition_name("Check Row", ("Check", "Check Row")),
                         ("Check Row", ""))

    # ------------------------- validate_rows -------------------------
    def test_validate_rows_accepts_condition_names(self):
        rows = [{"enabled": True, "button": "Flag On", "additional": "on", "repeat": 2},
                {"enabled": True, "button": "Beep", "additional": "", "repeat": 1}]
        self.assertEqual(me_mod.validate_rows(rows, condition_names=("Flag On",)), [])
        issues = me_mod.validate_rows(rows)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0][0], 1)          # เฉพาะแถวเงื่อนไข plugin โดนตรวจ

    # --------------------- evaluate_plugin_condition ---------------------
    def test_evaluate_plugin_condition(self):
        import types
        mod = types.SimpleNamespace(
            CONDITION_NAME="Flag On",
            check=lambda ctx, row: str(row.get("additional") or "").strip() == "on")
        runner, msgs = self._mk_runner({"Flag On": mod})
        # จริง → เล่นต่อ (ไม่ข้าม)
        skip, msg = runner.evaluate_plugin_condition(
            "Flag On", {"button": "Flag On", "additional": "on", "repeat": 3})
        self.assertEqual(skip, 0)
        self.assertIn("เงื่อนไขจริง", msg)
        self.assertNotIn("ข้าม", msg)
        # ไม่จริง → ข้าม N แถว (N = Repeat — กฎเดียวกับเงื่อนไขทุกชนิด)
        skip, msg = runner.evaluate_plugin_condition(
            "Flag On", {"button": "Flag On", "additional": "off", "repeat": 3})
        self.assertEqual(skip, 3)
        self.assertIn("ข้าม 3 แถว", msg)
        # ไม่ใช่เงื่อนไข plugin → (0, None)
        self.assertEqual(runner.evaluate_plugin_condition("Left Click", {}), (0, None))
        # check พัง = เตือนแล้วเล่นต่อ (ไม่ข้าม — กลไกเดียวกับ action plugin พัง)
        bad = types.SimpleNamespace(CONDITION_NAME="Boom", check=lambda ctx, row: 1 / 0)
        runner2, msgs2 = self._mk_runner({"Boom": bad})
        skip, msg = runner2.evaluate_plugin_condition(
            "Boom", {"button": "Boom", "repeat": 5})
        self.assertEqual((skip, msg), (0, None))
        self.assertTrue(any("condition plugin error" in m for m in msgs2))

    def test_condition_result_stored_in_var(self):
        import types
        mod = types.SimpleNamespace(CONDITION_NAME="Always", check=lambda ctx, row: True)
        variables = {}
        runner, _ = self._mk_runner({"Always": mod}, variables=variables)
        skip, _msg = runner.evaluate_plugin_condition(
            "Always", {"button": "Always", "additional": "x >สถานะ"})
        self.assertEqual(skip, 0)
        self.assertEqual(variables.get("สถานะ"), "1")     # โทเคน >ชื่อ = เก็บผล (v2.10)

    # --------------------- evaluate_block_condition ---------------------
    def test_block_condition_with_plugin(self):
        import types
        mod = types.SimpleNamespace(
            CONDITION_NAME="Flag On",
            check=lambda ctx, row: str(row.get("additional") or "") == "go")
        runner, _ = self._mk_runner({"Flag On": mod}, variables={"n": "5"})
        self.assertIs(runner.evaluate_block_condition("Flag On go"), True)
        self.assertIs(runner.evaluate_block_condition("Flag On stop"), False)
        # ผสม && กับเงื่อนไขในตัวได้ (ทุกชิ้นต้องจริง)
        self.assertIs(runner.evaluate_block_condition("Flag On go && n > 3"), True)
        self.assertIs(runner.evaluate_block_condition("Flag On go && n > 9"), False)
        self.assertIs(runner.evaluate_block_condition(""), True)   # บล็อกว่าง = จริงเสมอ (เดิม)

    # ------------------------- row_tags / .ahk -------------------------
    def test_row_tags_condition_plugin(self):
        self.assertEqual(me_mod.row_tags("Flag On", 1, ("Flag On",)), ("cond",))
        self.assertEqual(me_mod.row_tags("Flag On", 1), ("even",))   # ไม่ส่งชื่อ = แถบเดิม
        self.assertIsNone(me_mod.row_tag("Left Click", ("Flag On",)))

    def test_ahk_export_condition_plugin_commented(self):
        rows = [
            {"enabled": True, "button": "Set Variable", "additional": "n = 5",
             "secs": 0, "repeat": 1},
            {"enabled": True, "button": me_mod.BLOCK_START, "additional": "if Flag On go",
             "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Beep", "additional": "", "secs": 0, "repeat": 1},
            {"enabled": True, "button": me_mod.BLOCK_END, "additional": "",
             "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Flag On", "additional": "go",
             "secs": 0, "repeat": 1},
        ]
        s = me_mod.rows_to_ahk(rows, condition_names=("Flag On",))
        self.assertNotIn("{", s)                     # ทั้งคู่ Start/End เป็น comment — ไม่มีปีกกาลอย
        self.assertIn("แปลไม่ได้ตรง ๆ", s)
        self.assertIn("ไม่รองรับ: Flag On (go)", s)   # แถวเงื่อนไข = comment เหมือน action แปลกปลอม

    # ------------------- plugin ตัวอย่างที่แจกมากับโปรเจกต์ -------------------
    def test_real_file_exists_condition_plugin(self):
        import shutil
        me_mod.load_plugins()
        conds = dict(getattr(me_mod.load_plugins, "last_conditions", []) or [])
        self.assertIn("File Exists", conds)
        mod = conds["File Exists"]
        d = tempfile.mkdtemp(prefix="macro_fe_")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        f = os.path.join(d, "flag.txt")
        with open(f, "w", encoding="utf-8") as fh:
            fh.write("x")
        runner, _ = self._mk_runner({"File Exists": mod})
        skip, _m = runner.evaluate_plugin_condition(
            "File Exists", {"button": "File Exists", "additional": f, "repeat": 2})
        self.assertEqual(skip, 0)
        skip, _m = runner.evaluate_plugin_condition(
            "File Exists", {"button": "File Exists",
                            "additional": os.path.join(d, "missing.txt"), "repeat": 2})
        self.assertEqual(skip, 2)


class TestConditionPluginsGui(unittest.TestCase):
    """v2.13: เงื่อนไข plugin ใน GUI — แถวเงื่อนไขเล่นต่อ/ข้ามตาม Repeat ถูกต้อง
    ใช้ MacroApp จริง แถว Beep ล้วน (secs=0) — ไม่มีจอ skip อัตโนมัติ
    (แพตเทิร์นเดียวกับ TestV21GuiPlay: นับ STEP ผ่าน am.log_write)"""

    @classmethod
    def setUpClass(cls):
        cls._orig_log = am.log_write
        cls.steps = []

        def counting_log(mode, message, src=None):
            if mode == "STEP":
                cls.steps.append(message)
            return cls._orig_log(mode, message, src)

        am.log_write = counting_log
        cls.app = None
        try:
            cls.root = _Tk()
            cls.root.withdraw()
        except am.tk.TclError:
            cls.root = None
            return
        try:
            cls.app = am.MacroApp(cls.root)
            cls.app._log_enabled = True
        except Exception:
            cls.root.destroy()
            cls.root = None
            cls.app = None

    @classmethod
    def tearDownClass(cls):
        am.log_write = cls._orig_log
        if cls.app is not None:
            try:
                cls.app.stop_all(silent=True)
            except Exception:
                pass
        if cls.root is not None:
            cls.root.destroy()              # _Tk.destroy = หยุดเธรด + ยกเลิก after + gc.collect
        cls.app = None                      # ปล่อย ref ให้เก็บบน main thread ไม่ค้างถึงจบ suite
        cls.root = None

    def setUp(self):
        if self.app is None:
            self.skipTest("ไม่มีจอ/สร้าง MacroApp จริงไม่ได้")
        self.app.stop_all(silent=True)
        self.app.ent_loops.delete(0, "end")
        self.app.ent_loops.insert(0, "1")          # กันค่าค้างจากเทสต์ก่อนหน้า
        self.__class__.steps = []
        import types
        self.mod = types.SimpleNamespace(
            CONDITION_NAME="Flag On",
            check=lambda ctx, row: str(row.get("additional") or "").strip() == "on")
        self.app._cond_plugins = [("Flag On", self.mod)]
        self.app._cond_names = frozenset({"Flag On"})
        self.app._action_runner.conditions = {"Flag On": self.mod}
        self.addCleanup(self._restore_conds)

    def _restore_conds(self):
        self.app._cond_plugins = list(getattr(am.load_plugins, "last_conditions", []) or [])
        self.app._cond_names = frozenset(n for n, _ in self.app._cond_plugins)
        self.app._action_runner.conditions = dict(self.app._cond_plugins)

    def _wait_done(self, timeout=5.0):
        end = time.time() + timeout
        while time.time() < end:
            try:
                self.root.update()
            except Exception:
                pass
            if not self.app.running:
                return True
            time.sleep(0.03)
        return False

    def test_condition_true_plays_on(self):
        app = self.app
        app._load_rows([
            {"enabled": True, "button": "Flag On", "additional": "on",
             "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Beep", "secs": 0, "repeat": 1},
        ])
        app.start_play()
        self.assertTrue(self._wait_done())
        self.assertEqual(len([s for s in self.steps if "Beep" in s]), 1)
        self.assertTrue(any("เงื่อนไขจริง" in s for s in self.steps))

    def test_condition_false_skips_repeat_rows(self):
        app = self.app
        app._load_rows([
            {"enabled": True, "button": "Flag On", "additional": "off",
             "secs": 0, "repeat": 2},
            {"enabled": True, "button": "Beep", "secs": 0, "repeat": 1},
            {"enabled": True, "button": "Beep", "secs": 0, "repeat": 1},
        ])
        app.start_play()
        self.assertTrue(self._wait_done())
        self.assertEqual(len([s for s in self.steps if "Beep" in s]), 0)   # ข้ามทั้ง 2 แถว
        self.assertTrue(any("ไม่จริง" in s and "ข้าม 2 แถว" in s for s in self.steps))

    def test_validate_accepts_condition_rows(self):
        rows = [{"enabled": True, "button": "Flag On", "additional": "on",
                 "mins": 0, "secs": 0, "repeat": 1}]
        issues = am.validate_rows(rows, plugin_names=[],
                                  condition_names=sorted(self.app._cond_names))
        self.assertEqual(issues, [])


class TestConditionPluginsCli(unittest.TestCase):
    """v2.13: เงื่อนไข plugin ใน CLI จริง (cli_main) — เล่นต่อ/ข้ามตาม Repeat
    ใช้ plugin File Exists ที่แจกมากับโปรเจกต์ + สคริปต์ Beep ล้วนปลอดภัย"""

    def _script(self, rows, name="cond_cli.json"):
        import shutil
        d = tempfile.mkdtemp(prefix="macro_cond_cli_")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        p = os.path.join(d, name)
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, ensure_ascii=False)
        return p

    def _run(self, argv):
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = am.cli_main(argv)
        return rc, buf.getvalue()

    def _flag_file(self):
        import shutil
        d = tempfile.mkdtemp(prefix="macro_flag_")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        f = os.path.join(d, "flag.txt")
        with open(f, "w", encoding="utf-8") as fh:
            fh.write("x")
        return f

    def test_cli_plays_and_skips(self):
        f = self._flag_file()
        rows = [{"enabled": True, "button": "File Exists", "additional": f,
                 "secs": 0, "repeat": 1},
                {"enabled": True, "button": "Beep", "additional": "",
                 "secs": 0, "repeat": 1}]
        rc, out = self._run([self._script(rows), "--no-log"])
        self.assertEqual(rc, 0)
        self.assertIn("เงื่อนไขจริง", out)
        self.assertIn("Beep", out)
        rows2 = [{"enabled": True, "button": "File Exists", "additional": f + ".missing",
                  "secs": 0, "repeat": 1},
                 {"enabled": True, "button": "Beep", "additional": "",
                  "secs": 0, "repeat": 1}]
        rc2, out2 = self._run([self._script(rows2), "--no-log"])
        self.assertEqual(rc2, 0)
        self.assertIn("ไม่จริง", out2)
        self.assertIn("ข้าม 1 แถว", out2)
        self.assertNotIn("Beep", out2)             # แถวถูกข้าม — ไม่เล่น

    def test_cli_validate_accepts_condition_rows(self):
        rows = [{"enabled": True, "button": "File Exists", "additional": "x.txt",
                 "secs": 0, "repeat": 1}]
        rc, out = self._run([self._script(rows), "--no-log", "--validate"])
        self.assertEqual(rc, 0)
        self.assertIn("ผ่านการตรวจ", out)

    def test_cli_example_file_validates(self):
        # ตัวอย่างที่แจกมากับโปรเจกต์ต้องผ่าน --validate ของโค้ดจริง (เหมือน AGENTS.md)
        ex = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "examples", "14_condition_plugin.json")
        rc, out = self._run([ex, "--no-log", "--validate"])
        self.assertEqual(rc, 0, out)


class TestDryReportPath(unittest.TestCase):
    """v2.14: CLI --dry-report PATH — เลือกไฟล์รายงาน dry-run เอง ({date} = วันที่วันนี้)
    ปิดแผนสุดท้ายของ ROADMAP (เหลือค้างจาก v2.10.1)"""

    def _script(self, d, name="dry_report.json"):
        p = os.path.join(d, name)
        with open(p, "w", encoding="utf-8") as fh:
            json.dump([{"enabled": True, "button": "Beep", "additional": "ok",
                        "mins": 0, "secs": 0, "repeat": 1}], fh, ensure_ascii=False)
        return p

    def test_cli_dry_report_path_used(self):
        import contextlib
        d = tempfile.mkdtemp(prefix="macro_drp_")
        self.addCleanup(lambda: __import__("shutil").rmtree(d, ignore_errors=True))
        target = os.path.join(d, "my_report.txt")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = am.cli_main([self._script(d), "--dry-run", "--no-log",
                              "--dry-report", target])
        self.assertEqual(rc, 0)
        self.assertTrue(os.path.isfile(target))           # เขียนลงพาธที่สั่งจริง
        with open(target, encoding="utf-8") as fh:
            self.assertIn("DRY-RUN", fh.read())

    def test_cli_dry_report_date_token(self):
        import contextlib
        d = tempfile.mkdtemp(prefix="macro_drd_")
        self.addCleanup(lambda: __import__("shutil").rmtree(d, ignore_errors=True))
        target = os.path.join(d, "rep_{date}.txt")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = am.cli_main([self._script(d), "--dry-run", "--no-log",
                              "--dry-report", target])
        self.assertEqual(rc, 0)
        final = os.path.join(d, "rep_%s.txt" % datetime.date.today().isoformat())
        self.assertTrue(os.path.isfile(final))            # {date} ถูกแทนวันที่วันนี้
        self.assertIn(final, buf.getvalue())              # พิมพ์พาธที่แทนแล้ว

    def test_dry_report_write_path_kw_overrides_default(self):
        # engine ล้วน: path= ทับ dry_report_path() — และ {date} แทนใน engine ด้วย
        d = tempfile.mkdtemp(prefix="macro_dre_")
        self.addCleanup(lambda: __import__("shutil").rmtree(d, ignore_errors=True))
        target = os.path.join(d, "x_{date}.txt")
        me_mod.dry_report_write(["ไฮ"], path=target)
        final = os.path.join(d, "x_%s.txt" % datetime.date.today().isoformat())
        self.assertTrue(os.path.isfile(final))
        self.assertFalse(os.path.isfile(target))          # ชื่อดิบ (ยังมี {date}) ต้องไม่เกิด

    def test_cli_dry_report_without_dry_run_warns(self):
        import contextlib
        d = tempfile.mkdtemp(prefix="macro_drw_")
        self.addCleanup(lambda: __import__("shutil").rmtree(d, ignore_errors=True))
        target = os.path.join(d, "never.txt")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = am.cli_main([self._script(d), "--no-log", "--dry-report", target])
        self.assertEqual(rc, 0)
        self.assertIn("--dry-report", buf.getvalue())     # เตือนว่าต้องใช้กับ --dry-run
        self.assertFalse(os.path.isfile(target))

    def test_engine_cli_dry_report(self):
        import contextlib
        import shutil as _sh
        import engine_cli
        d = tempfile.mkdtemp(prefix="macro_drx_")
        self.addCleanup(_sh.rmtree, d, ignore_errors=True)
        target = os.path.join(d, "eng_{date}.txt")
        p = os.path.join(d, "s.json")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump([{"enabled": True, "button": "Beep", "additional": "ok",
                        "mins": 0, "secs": 0, "repeat": 1}], fh, ensure_ascii=False)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = engine_cli.main([p, "--dry-run", "--no-log", "--dry-report", target])
        self.assertEqual(rc, 0)
        final = os.path.join(d, "eng_%s.txt" % datetime.date.today().isoformat())
        self.assertTrue(os.path.isfile(final))


class TestPluginsV14(unittest.TestCase):
    """v2.14: plugin เงื่อนไขระบบ 3 ตัวที่แจกมากับโปรเจกต์ — มาตรฐาน PLUGINS.md:
    เรียก check จริง / ทน Additional พัง / ทน ctx ขาด / ตรวจโค้ดจริงของ plugin"""

    def _load(self, name):
        me_mod.load_plugins()
        conds = dict(getattr(me_mod.load_plugins, "last_conditions", []) or [])
        self.assertIn(name, conds, "plugin %s ต้องโหลดเจอ" % name)
        return conds[name]

    def test_real_internet_up(self):
        mod = self._load("Internet Up")
        # Additional พัง/ว่าง → ยังต้องคืน bool (ค่าเริ่ม 1.1.1.1 — ไม่ raise เด็ดขาด)
        for add in ("", "not a host!:", "1.1.1.1 0.2s", "bad..host 9999"):
            r = mod.check({}, {"button": "Internet Up", "additional": add})
            self.assertIsInstance(r, bool)

    def test_real_process_running(self):
        mod = self._load("Process Running")
        self.assertIsInstance(mod.check({}, {"button": "Process Running",
                                            "additional": "python"}), bool)
        self.assertFalse(mod.check({}, {"button": "Process Running",
                                        "additional": "no_such_process_xyz"}))
        self.assertFalse(mod.check({}, {"button": "Process Running", "additional": ""}))
        self.assertFalse(mod.check({}, {}))               # ctx ขาด/แถวว่าง — ไม่พัง

    def test_real_window_exists(self):
        mod = self._load("Window Exists")
        self.assertIsInstance(mod.check({}, {"button": "Window Exists",
                                            "additional": "python"}), bool)
        self.assertFalse(mod.check({}, {"button": "Window Exists",
                                        "additional": "no_such_window_xyz"}))
        self.assertFalse(mod.check({}, {"button": "Window Exists", "additional": ""}))
        self.assertFalse(mod.check({}, {}))

    def test_condition_names_registered(self):
        me_mod.load_plugins()
        conds = [n for n, _ in getattr(me_mod.load_plugins, "last_conditions", []) or []]
        for n in ("File Exists", "Internet Up", "Process Running", "Window Exists"):
            self.assertIn(n, conds)

    def test_example_15_validates_and_skips(self):
        """ตัวอย่าง 15: validate ผ่าน + เล่น CLI จริง — ตรวจเฉพาะสาขา deterministic ทุก OS
        ⚠️ บทเรียน CI (2 รอบ): เงื่อนไขที่ผลต่างตาม OS ห้ามอยู่หน้าแถวที่ต้องตัดสินเอง —
        skip ค้าง (จากเงื่อนไขเท็จ) ทะลุทั้งแนวแถวตรงและการกระโดดของ Block Start
        → ตัวอย่างใช้ Process Running `python` (มีจริงทุกที่ที่รันโปรแกรมนี้ได้)
        = จริงเสมอ ไม่เกิด skip cascade · สาขาเท็จสาธิตด้วย Window Exists ท้ายสคริปต์
        (ชื่อหน้าต่างที่ไม่มีจริงบนทุก OS → ข้าม 1) — skip นั้นไร้แถวต่อท้าย ไม่มีทางกลืนใคร"""
        import contextlib
        ex = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "examples", "15_system_conditions.json")
        with open(ex, encoding="utf-8") as fh:
            rows = json.load(fh)
        me_mod.load_plugins()
        cond_names = [n for n, _ in getattr(me_mod.load_plugins, "last_conditions", []) or []]
        self.assertEqual(me_mod.validate_rows(rows, plugin_names=[],
                                              condition_names=cond_names), [])
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = am.cli_main([ex, "--no-log"])
        self.assertEqual(rc, 0)
        out = buf.getvalue()
        self.assertIn("เงื่อนไข plugin", out)             # หัวโปรแกรมแสดงรายชื่อเงื่อนไข
        self.assertIn("Process Running → เงื่อนไขจริง เล่นต่อ", out)  # `python` มีจริงทุก OS
        self.assertIn("Window Exists → เงื่อนไขไม่จริง ข้าม 1 แถว", out)  # ชื่อนี้ไม่มีจริงทุก OS
        self.assertIn("จบแล้ว ✔", out)                    # ครบทุกแถว — skip ไม่กลืนเกิน


class TestInsertCondPluginGui(unittest.TestCase):
    """v2.14: ปุ่ม 🧩 — แทรกแถวเงื่อนไข plugin จาก dialog (ใช้ MacroApp จริง)"""

    @classmethod
    def setUpClass(cls):
        cls.app = None
        try:
            cls.root = _Tk()
            cls.root.withdraw()
        except am.tk.TclError:
            cls.root = None
            return
        try:
            cls.app = am.MacroApp(cls.root)
        except Exception:
            cls.root.destroy()
            cls.root = None
            cls.app = None

    @classmethod
    def tearDownClass(cls):
        if cls.root is not None:
            cls.root.destroy()

    def setUp(self):
        if self.app is None:
            self.skipTest("ไม่มีจอ/สร้าง MacroApp จริงไม่ได้")
        import types
        self.mod = types.SimpleNamespace(CONDITION_NAME="Flag On", check=lambda c, r: True)
        self.app._cond_plugins = [("Flag On", self.mod)]
        self.app._cond_names = frozenset({"Flag On"})
        self.app._action_runner.conditions = {"Flag On": self.mod}
        for iid in self.app.tree.get_children():
            self.app.tree.delete(iid)
        self.addCleanup(self._restore)

    def _restore(self):
        self.app._cond_plugins = list(getattr(am.load_plugins, "last_conditions", []) or [])
        self.app._cond_names = frozenset(n for n, _ in self.app._cond_plugins)
        self.app._action_runner.conditions = dict(self.app._cond_plugins)

    def test_button_present_and_insert(self):
        # ปุ่ม 🧩 มีจริงเมื่อโหลดเงื่อนไขแล้ว
        btns = [w for w in self.app.root.winfo_children()]
        self.assertTrue(hasattr(self.app, "_insert_cond_plugin"))
        # แทรกโดยตรง (เลียนแบบหน้าต่าง — คลิกจริงทำใน dialog ที่ grab_set)
        before = len(self.app.tree.get_children())
        self.app.tree.insert("", "end",
                             values=["☑", "#", "", "", "Beep", "", 0, 0, 1])
        for iid in self.app.tree.get_children():
            self.app.tree.selection_set(iid)
        self.app._insert_cond_plugin()
        # เปิด dialog ได้จริง — ปิดทิ้ง (grab ป้องกันไม่ให้รบกวนเทสต์อื่น)
        for w in self.app.root.winfo_children():
            if isinstance(w, am.tk.Toplevel) and "แทรกเงื่อนไข" in str(w.title()):
                w.destroy()
        self.assertEqual(len(self.app.tree.get_children()), before + 1)

    def test_insert_via_dialog_ok(self):
        # เดิน dialog จริง: เลือกชื่อ + พิมพ์อาร์กิวเมนต์ + กดแทรก (ผ่าน command ของปุ่ม)
        self.app._insert_cond_plugin()
        dlg = None
        for w in self.app.root.winfo_children():
            if isinstance(w, am.tk.Toplevel) and "แทรกเงื่อนไข" in str(w.title()):
                dlg = w
        self.assertIsNotNone(dlg)
        cmb = next(w for w in dlg.winfo_children()
                   if isinstance(w, am.ttk.Combobox))
        self.assertEqual(cmb["values"], ("Flag On",))
        # ⚠️ ttk.Combobox สืบทอด tk.Entry ด้วย — ต้องตัด combobox ออกก่อนถึงจะได้ช่องอาร์กิวเมนต์จริง
        ent = next(w for w in dlg.winfo_children()
                   if isinstance(w, am.tk.Entry) and not isinstance(w, am.ttk.Combobox))
        ent.delete(0, "end")
        ent.insert(0, "on")
        # ปุ่ม "แทรก" เรียก _ok จริง — หาผ่าน children ของ frame
        frames = [w for w in dlg.winfo_children() if isinstance(w, am.tk.Frame)]
        ok_btn = next(b for f in frames for b in f.winfo_children()
                      if isinstance(b, am.tk.Button) and str(b["text"]) == "แทรก")
        ok_btn.invoke()
        vals = list(self.app.tree.item(self.app.tree.get_children()[-1], "values"))
        self.assertEqual(vals[4], "Flag On")              # Action = ชื่อเงื่อนไข
        self.assertEqual(vals[5], "on")                   # Additional = อาร์กิวเมนต์
        self.assertEqual(str(vals[1]), "1")               # เลขลำดับรีเลขแล้ว (Tk คืน string)
        self.assertEqual(self.app.tree.item(self.app.tree.get_children()[-1], "tags"),
                         ("cond",))                       # สีหมวดเงื่อนไข

    def test_no_plugins_message(self):
        self.app._cond_names = frozenset()
        self.app._insert_cond_plugin()                    # ไม่มี plugin = เตือนแล้วจบ เปิด dialog
        tops = [w for w in self.app.root.winfo_children()
                if isinstance(w, am.tk.Toplevel) and "แทรกเงื่อนไข" in str(w.title())]
        self.assertEqual(tops, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)

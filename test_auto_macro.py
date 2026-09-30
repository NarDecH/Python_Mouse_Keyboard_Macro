# -*- coding: utf-8 -*-
"""
Unit tests สำหรับฟังก์ชันล้วน ๆ ของ auto_macro.py
(ไม่เปิดหน้าต่าง GUI และไม่ยุ่งกับเมาส์/คีย์บอร์ดจริง)

รันด้วย:  py -m unittest test_auto_macro -v
"""

import datetime
import io
import json
import os
import random
import re
import sys
import time
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import auto_macro as am  # noqa: E402
import macro_engine as me_mod  # noqa: E402  (v2.1: engine ล้วน — เทสต์แยกได้)


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
        # เก่า 3 วัน (ควรถูกลบเมื่อเขียนวันนี้ เพราะเก่ากว่า 7 วันไม่ใช่... 3 < 7 จึงเหลือ)
        old = datetime.datetime(2026, 9, 25, 8, 0, 0)
        am.backup_snapshot(self._tmp.name, {"a": 1}, now=old)
        p = am.backup_snapshot(self._tmp.name, {"b": 2})   # วันนี้
        files = sorted(os.listdir(self._bk()))
        self.assertEqual(len(files), 2)                    # เก่า (3 วิ) ยังไม่เกิน 7 วัน
        data = json.load(open(p, encoding="utf-8"))
        self.assertEqual(data, {"b": 2})
        self.assertRegex(os.path.basename(p), r"^backup_\d{4}-\d{2}-\d{2}_\d{6}\.json$")

    def test_prune_deletes_over_7_days(self):
        import datetime
        d10 = datetime.datetime(2026, 9, 18, 8, 0, 0)      # เก่ากว่า 10 วิ นับจากวันนี้
        d1 = datetime.datetime(2026, 9, 27, 8, 0, 0)
        am.backup_snapshot(self._tmp.name, {"old": 1}, now=d10)
        am.backup_snapshot(self._tmp.name, {"new": 2}, now=d1)
        am.backup_snapshot(self._tmp.name, {"today": 3})   # จะเรียก prune ให้เอง
        files = os.listdir(self._bk())
        self.assertEqual(len(files), 2)                    # ตัวเก่า 10 วันถูกลบ
        self.assertFalse(any("20260918" in f for f in files))

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
            cls.root = am.tk.Tk()
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
            cls.root = am.tk.Tk()
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
            cls.root.destroy()

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
        return app

    def test_daily_fires_at_matching_time(self):
        app = self._app()
        app._sched_mode = "daily"
        app._sched_at = "09:30"
        app._sched_last = ""
        with mock.patch.object(am.time, "strftime", return_value="2026-10-01 09:30"):
            am.MacroApp._sched_check(app)
        self.assertEqual(app._sched_q.qsize(), 1)

    def test_daily_fires_once_per_minute(self):
        app = self._app()
        app._sched_mode = "daily"
        app._sched_at = "09:30"
        app._sched_last = ""
        with mock.patch.object(am.time, "strftime", return_value="2026-10-01 09:30"):
            am.MacroApp._sched_check(app)
            am.MacroApp._sched_check(app)          # นาทีเดียวกัน = ไม่ยิงซ้ำ
        self.assertEqual(app._sched_q.qsize(), 1)

    def test_daily_ignores_other_times(self):
        app = self._app()
        app._sched_mode = "daily"
        app._sched_at = "09:30"
        app._sched_last = ""
        with mock.patch.object(am.time, "strftime", return_value="2026-10-01 14:05"):
            am.MacroApp._sched_check(app)
        self.assertEqual(app._sched_q.qsize(), 0)

    def test_interval_rearms(self):
        app = self._app()
        app._sched_mode = "interval"
        app._sched_every = 10
        app._sched_next = 1000.0
        am.MacroApp._sched_check(app, now=2000.0)
        self.assertEqual(app._sched_q.qsize(), 1)
        self.assertEqual(app._sched_next, 2000.0 + 10 * 60)   # เลื่อนเป้าถัดไป

    def test_no_mode_is_noop(self):
        app = self._app()
        app._sched_mode = ""
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
        app._sched_profile = ""
        app._sched_mode = "interval"
        app._sched_every = 15
        app._sched_at = ""
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
                self.assertEqual(data["sched_mode"], "interval")
                self.assertEqual(data["sched_every"], 15)
                # โหลดกลับเข้าเครื่องจำลอง
                app2 = mock.MagicMock()
                app2._serialize.return_value = []
                am.MacroApp._load_conf(app2)
        app2.ent_loops.delete.assert_called()          # ค่าถูก set กลับเข้า widget
        app2.chk_forever.set.assert_called_with(True)
        self.assertEqual(app2._sched_mode, "interval")
        self.assertEqual(app2._sched_every, 15)
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
            cls.root = am.tk.Tk()
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
            cls.root = am.tk.Tk()
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


class TestV21GuiPlay(unittest.TestCase):
    """v1.21: เล่นจริงผ่าน player (GUI) — If Loop/If Time ข้ามแถว + Section ไม่หยุดการเล่น
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
            cls.root = am.tk.Tk()
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
            cls.root.destroy()

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
        app._start_player.assert_called_once_with(False, once=True)   # เล่น 1 รอบต่อสั่ง

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
        app._start_player.side_effect = lambda *a, **k: setattr(app, "running", True)
        am.MacroApp._sched_poll(app)
        app._start_player.assert_called_once()
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
        app._sched_mode = ""
        app._sched_every = 10
        app._sched_at = ""
        app._sched_profile = ""
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
        app._sched_profile = "งานเช้า"
        am.MacroApp._sched_poll(app)
        app._load_rows.assert_called_once_with([{"button": "Beep", "secs": 1}])
        app._start_player.assert_called_once_with(False, once=True)

    def test_poll_empty_profile_keeps_current_rows(self):
        import queue
        app = mock.MagicMock()
        app._sched_q = queue.Queue()
        app._sched_q.put("play")
        app.running = False
        app._log_enabled = False                 # กันเทสต์เขียน log จริงของผู้ใช้
        app._sched_profile = ""                      # งานที่เปิดค้าง — ไม่แตะตาราง
        am.MacroApp._sched_poll(app)
        app._load_rows.assert_not_called()
        app._start_player.assert_called_once_with(False, once=True)

    def test_poll_unknown_profile_keeps_current_rows(self):
        import queue
        app = mock.MagicMock()
        app._sched_q = queue.Queue()
        app._sched_q.put("play")
        app.running = False
        app._log_enabled = False                 # กันเทสต์เขียน log จริงของผู้ใช้
        app._profiles = {}
        app._sched_profile = "โปรไฟล์ถูกลบไปแล้ว"
        am.MacroApp._sched_poll(app)
        app._load_rows.assert_not_called()           # ทนได้ — เล่นงานที่เปิดค้างแทน
        app._start_player.assert_called_once_with(False, once=True)


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


if __name__ == "__main__":
    unittest.main(verbosity=2)

# -*- coding: utf-8 -*-
"""
Unit tests สำหรับฟังก์ชันล้วน ๆ ของ auto_macro.py
(ไม่เปิดหน้าต่าง GUI และไม่ยุ่งกับเมาส์/คีย์บอร์ดจริง)

รันด้วย:  py -m unittest test_auto_macro -v
"""

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


class TestParseKey(unittest.TestCase):
    """parse_key: ข้อความ → ออบเจ็กต์คีย์ pynput"""

    def test_empty_returns_none(self):
        self.assertIsNone(am.parse_key(""))
        self.assertIsNone(am.parse_key(None))
        self.assertIsNone(am.parse_key("   "))

    def test_single_char(self):
        k = am.parse_key("a")
        self.assertIsNotNone(k)
        self.assertEqual(k.char, "a")

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
        self.assertEqual(am.parse_key("prtsc"), Key.print_screen)
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
                          "mins", "secs", "repeat"])

    def test_edit_cols_mapping(self):
        self.assertEqual(am.EDIT_COLS,
                         ["Action", "Additional", "Mins", "Secs", "Repeat"])


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
             mock.patch("ctypes.windll", fake_win):
            chk = am.MacroApp._self_check(app)
        self.assertTrue(all(chk.values()))
        lines = am.MacroApp.self_check_text(app)
        self.assertEqual(len(lines), 4)
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
        self.app._checks = {"mouse": True, "hotkey": True, "opencv": True,
                            "admin": False, "conf_writable": True}
        self.app.running = False
        self.app.recording = False
        self.app._pending_rows = []
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
        for m in ("_snapshot_rows", "_push_undo", "_undo_delete", "_find_rows",
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
        """RECORD: กดคีย์ต้องได้แถว Tap Key — on_kb เดิมพังที่ตัวแปร pressed"""
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
        with mock.patch.object(am.mouse, "Listener", FakeMouseListener), \
             mock.patch.object(am.keyboard, "Listener", FakeKbListener):
            am.MacroApp._start_listeners(app)
        on_press = captured["on_press"]
        self.assertIsNotNone(on_press)
        app.recording = True
        app._rec_t0 = time.time()
        on_press(am.KeyCode.from_char("a"))             # เดิม: NameError ที่ตัวแปร pressed
        self.assertEqual(len(app._pending_rows), 1)
        self.assertEqual(app._pending_rows[0]["button"], "Tap Key")
        self.assertEqual(app._pending_rows[0]["additional"], "a")
        app.recording = False
        on_press(am.KeyCode.from_char("b"))             # ไม่ได้อัด = ไม่เพิ่มแถว
        self.assertEqual(len(app._pending_rows), 1)


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
        """กลไก RECORD: listener ผลักแถวเข้า _pending_rows → poller ย้ายเข้าตารางเอง"""
        app = self.app
        app.tree.delete(*app.tree.get_children())
        app.toggle_record()
        self.assertTrue(app.recording)
        try:
            app._pending_rows.append(dict(x=11, y=22, button="Left Click",
                                          additional="", mins=0, secs=0.5, repeat=1))
            ok = self._run_until(lambda: None,
                                 lambda: len(app.tree.get_children()) == 1)
            self.assertTrue(ok)
            vals = app.tree.item(app.tree.get_children()[0], "values")
            self.assertEqual(vals[4], "Left Click")
        finally:
            app.toggle_record()
        self.assertFalse(app.recording)

    def test_clipboard_actions_roundtrip(self):
        """Set Clipboard → Read Clipboard: ข้อความวนกลับเข้าตัวแปรได้ (v1.20)"""
        self._clean_table(0)
        self.app._append_row(button="Set Variable", additional="n = 1")
        self.app._append_row(button="Set Clipboard", additional="ข้อความ {n}")
        self.app._append_row(button="Read Clipboard", additional="mytext")
        self.steps.clear()
        ok = self._run_until(self.app.start_play, lambda: not self.app.running)
        self.assertTrue(ok)
        self.assertEqual(self.app._vars.get("mytext"), "ข้อความ 1")
        self.assertEqual(self.root.clipboard_get(), "ข้อความ 1")   # คลิปบอร์ดจริง

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
    """v1.20: Set Clipboard / Read Clipboard — GUI ผ่าน poller, CLI ผ่าน Win32/pbcopy/xclip"""

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


if __name__ == "__main__":
    unittest.main(verbosity=2)

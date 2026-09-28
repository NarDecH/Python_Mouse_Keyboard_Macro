# -*- coding: utf-8 -*-
"""
Unit tests สำหรับฟังก์ชันล้วน ๆ ของ auto_macro.py
(ไม่เปิดหน้าต่าง GUI และไม่ยุ่งกับเมาส์/คีย์บอร์ดจริง)

รันด้วย:  py -m unittest test_auto_macro -v
"""

import json
import os
import random
import sys
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


if __name__ == "__main__":
    unittest.main(verbosity=2)

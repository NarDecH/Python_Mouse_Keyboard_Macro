# -*- coding: utf-8 -*-
"""
Unit tests สำหรับฟังก์ชันล้วน ๆ ของ auto_macro.py
(ไม่เปิดหน้าต่าง GUI และไม่ยุ่งกับเมาส์/คีย์บอร์ดจริง)

รันด้วย:  py -m unittest test_auto_macro -v
"""

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


class TestMenuItems(unittest.TestCase):
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

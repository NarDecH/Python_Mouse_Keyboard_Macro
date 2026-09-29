#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""engine_cli.py — CLI ย่อยที่ import macro_engine ตรง ๆ (v2.1)

สำหรับผู้ใช้ที่อยากใช้ engine แยกจาก GUI — ไฟล์นี้ไม่ import auto_macro เลย
จึงไม่แตะ tkinter และเป็นตัวอย่างการฝัง engine ในโปรเจกต์อื่น:

    py engine_cli.py script.json
    py engine_cli.py script.json --loops 3 --speed 2 --no-log

รองรับ action เดียวกับ CLI หลัก (v2.1 ใช้ ActionRunner ร่วมกัน) เว้นเฉพาะ
Image Click / Wait for Image ที่ต้องหน้าต่าง GUI จัดการภาพ
หยุดได้: F8/Esc (global hotkey), Ctrl+C
"""
import argparse
import json
import sys
import threading
import time

import macro_engine as me
from macro_engine import (ActionRunner, KEY_ACTIONS, SECTION_HEADER, delay_range,
                          delay_seconds, load_plugins, log_write, pick_play_order,
                          prune_log, subst_row)
from macro_engine import MouseController, KbController, Key


def build_parser():
    ap = argparse.ArgumentParser(
        prog="engine_cli",
        description="เล่นสคริปต์เมาส์/คีย์บอร์ด .json ด้วย engine ล้วน (ไม่เปิด GUI)")
    ap.add_argument("script", help="ไฟล์สคริปต์ .json")
    ap.add_argument("--loops", type=int, default=1, help="จำนวนรอบ (ค่าเริ่มต้น 1; 0=ไม่จำกัด)")
    ap.add_argument("--speed", type=float, default=1.0, help="ตัวคูณความเร็ว (ค่าเริ่มต้น 1)")
    ap.add_argument("--no-log", action="store_true", help="ไม่บันทึก log การเล่น")
    return ap


def load_script(path):
    """โหลดไฟล์สคริปต์ — คืน (rows, error_message)"""
    try:
        with open(path, encoding="utf-8") as fh:
            rows = json.load(fh)
    except OSError as exc:
        return None, "ไม่พบไฟล์สคริปต์: %s" % path
    except ValueError as exc:
        return None, "ไฟล์ JSON พัง: %s" % exc
    if not isinstance(rows, list):
        return None, "ไฟล์ต้องเป็นรายการแถว JSON"
    return rows, None


def main(argv=None):
    args = build_parser().parse_args(argv)
    rows, err = load_script(args.script)
    if err:
        print(err)
        return 1

    speed = max(0.1, min(10.0, args.speed))
    loops = max(0, args.loops)
    log_enabled = not args.no_log
    running = [True]
    vars_ = {}                                  # ตัวแปรของการเล่น เริ่มใหม่ทุกรอบชุด

    plugins = dict(load_plugins())
    if plugins:
        print("  •  plugins: %s" % ", ".join(sorted(plugins)))

    mouse_ctl = MouseController()
    kb_ctl = KbController()
    runner = ActionRunner(
        mouse_ctl, kb_ctl,
        stop_check=lambda: running[0],
        on_beep=lambda: print("\a", end="", flush=True),
        on_message=lambda text, color="#080": print("  " + str(text)),
        on_clipboard_set=lambda text: None if me.clip_set(text)
        else print("  ⚠ Set Clipboard: ตั้งคลิปบอร์ดไม่สำเร็จบนระบบนี้"),
        on_clipboard_read=me.clip_get,
        variables=vars_,
        plugin_lookup=lambda name: plugins.get(name),
        log_src=args.script,
        unsupported_cb=lambda btn: print(
            "  ⚠ ข้ามแถว: action '%s' ยังไม่รองรับใน engine_cli — เปิดใน GUI เพื่อเล่น action นี้" % btn))

    # หยุดด้วย F8/Esc — จับคู่คีย์เองด้วย keyboard.Listener (เหตุผลเดียวกับ CLI หลัก v1.8)
    from pynput import keyboard as _kb

    def _on_key_stop(key):
        if key in (_kb.Key.f8, _kb.Key.esc):
            running[0] = False

    try:
        stopper = _kb.Listener(on_press=_on_key_stop)
        stopper.daemon = True
        stopper.start()
        gk_ok = True
    except Exception:
        gk_ok = False

    play_rows = [r for r in rows if r.get("enabled", True) is not False]
    print("เล่นสคริปต์: %s (%d แถว)  •  ความเร็ว %gx%s" % (
        args.script, len(play_rows), speed,
        "" if loops else "  •  วนไม่จำกัด"))
    if log_enabled:
        log_write("START", "เริ่มเล่น (engine_cli) ความเร็ว %gx รอบ=%s" %
                  (speed, "ไม่จำกัด" if loops == 0 else loops), args.script)

    rc = 1
    skipping = 0                  # ตัวนับข้ามแถวจาก If Loop/If Time (v2.1)
    try:
        n_loop = 0
        while True:
            if loops == 0 and not running[0]:
                break
            n_loop += 1
            if loops and n_loop > loops:
                break
            print("— รอบที่ %d —" % n_loop)
            for i, r in enumerate(pick_play_order(play_rows), 1):
                if not running[0]:
                    break
                r = subst_row(r, vars_)            # แทน {ตัวแปร} ทุกคอลัมน์
                if r.get("button") == SECTION_HEADER:   # แถวจัดระเบียบ — ไม่ทำอะไร
                    continue
                lo, hi = delay_range(r.get("secs", 1))
                base = delay_seconds(r.get("mins", 0), 0) + (lo if lo == hi else me.random.uniform(lo, hi))
                # หยุดทันทีกลางดีเลย์: แบ่ง sleep ชิ้นละ 50 ms
                _end = time.time() + max(0.0, base / speed)
                while running[0]:
                    remain = _end - time.time()
                    if remain <= 0:
                        break
                    time.sleep(min(0.05, remain))
                if not running[0]:
                    break
                t0 = time.time()
                btn = r.get("button", "")
                if btn in (me.IF_IMAGE, me.ELSE_IMAGE, "Image Click", "Wait for Image"):
                    print("  ⚠ ข้ามแถว: action '%s' ยังไม่รองรับใน engine_cli — "
                          "เปิดใน GUI เพื่อเล่น action นี้" % btn)
                    continue
                # เงื่อนไขนับรอบ/เวลา — กลไกเดียวกับ CLI หลัก (v2.1)
                skip_n, cond_msg = ActionRunner.evaluate_condition(
                    btn, r.get("additional", ""), r.get("repeat", 1), n_loop)
                if cond_msg:
                    print("  [%d/%d] %s" % (i, len(play_rows), cond_msg))
                    if log_enabled and skip_n:
                        log_write("STEP", "รอบ %d แถว %d/%d %s → ข้าม %d แถว (%.1f วิ)" %
                                  (n_loop, i, len(play_rows), cond_msg.split("→")[0].strip(),
                                   skip_n, time.time() - t0), args.script)
                    if skip_n > 0:
                        skipping = skip_n
                    continue
                if skipping > 0:               # แถวถูกสั่งข้ามจากเงื่อนไขก่อนหน้า
                    skipping -= 1
                    continue
                ok = runner.execute(r)
                if not ok:
                    running[0] = False
                    break
                print("  [%d/%d] %s %s" % (i, len(play_rows), btn,
                                           r.get("additional", "") or ""))
                if log_enabled:
                    log_write("STEP", "รอบ %d แถว %d/%d %s %s (%.1f วิ)" %
                              (n_loop, i, len(play_rows), btn,
                               r.get("additional", "") or "", time.time() - t0),
                              args.script)
            if not running[0]:
                break
            if loops:                    # รอบสุดท้ายแล้วจบเอง (n_loop > loops เช็คบนหัวลูป)
                if n_loop >= loops:
                    break
        rc = 0
        print("จบแล้ว ✔")
        if log_enabled:
            log_write("END", "เล่นจบเองครบ", args.script)
    except KeyboardInterrupt:
        print("\nถูกหยุดโดยผู้ใช้")
        if log_enabled:
            log_write("STOP", "หยุดโดยผู้ใช้ (Ctrl+C)", args.script)
    finally:
        running[0] = False
        runner.release_all()             # ปล่อยคีย์/ปุ่มค้างทุกกรณี
        try:
            stopper.stop()
        except Exception:
            pass
        if log_enabled:
            prune_log()
    return rc


if __name__ == "__main__":
    sys.exit(main())

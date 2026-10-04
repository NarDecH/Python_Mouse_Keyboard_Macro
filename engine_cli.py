#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""engine_cli.py — CLI ย่อยที่ import macro_engine ตรง ๆ (v2.1)

สำหรับผู้ใช้ที่อยากใช้ engine แยกจาก GUI — ไฟล์นี้ไม่ import auto_macro เลย
จึงไม่แตะ tkinter และเป็นตัวอย่างการฝัง engine ในโปรเจกต์อื่น:

    py engine_cli.py script.json
    py engine_cli.py script.json --loops 3 --speed 2 --no-log
    py engine_cli.py script.jsonl --json-lines      # อ่าน 1 แถวต่อบรรทัด (v2.2)

รองรับ action ครบเหมือน CLI หลัก (v2.2: ค้นภาพ Image Click / If Image /
Wait for Image ก็ทำได้ — find_image_cb ผูกเข้า ActionRunner เหมือน GUI)
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
                          prune_log, subst_row, validate_rows)
from macro_engine import MouseController, KbController, Key


def build_parser():
    ap = argparse.ArgumentParser(
        prog="engine_cli",
        description="เล่นสคริปต์เมาส์/คีย์บอร์ด .json ด้วย engine ล้วน (ไม่เปิด GUI)")
    ap.add_argument("script", help="ไฟล์สคริปต์ .json")
    ap.add_argument("--version", action="version",
                    version="engine_cli " + me.__version__,
                    help="แสดงเวอร์ชันแล้วจบ")
    ap.add_argument("--loops", type=int, default=1, help="จำนวนรอบ (ค่าเริ่มต้น 1; 0=ไม่จำกัด)")
    ap.add_argument("--validate", action="store_true",
                    help="ตรวจสคริปต์อย่างเดียว ไม่เล่น (exit 1 เมื่อพบแถวมีปัญหา)")
    ap.add_argument("--max-minutes", type=float, default=0.0, metavar="นาที",
                    help="Safety timeout: หยุดเองหลังเล่นนานเท่านี้ (0 = ปิด, v2.4)")
    ap.add_argument("--speed", type=float, default=1.0, help="ตัวคูณความเร็ว (ค่าเริ่มต้น 1)")
    ap.add_argument("--no-log", action="store_true", help="ไม่บันทึก log การเล่น")
    ap.add_argument("--json-lines", action="store_true",
                    help="อ่านสคริปต์แบบ JSON Lines (1 แถวต่อบรรทัด — v2.2)")
    ap.add_argument("--dry-run", action="store_true",
                    help="ซ้อมเดินสคริปต์โดยไม่แตะเมาส์/คีย์ (v2.10 — รายงานแทนทำจริง)")
    return ap


def load_script(path, json_lines=False):
    """โหลดไฟล์สคริปต์ — คืน (rows, error_message)
    json_lines=True: อ่าน 1 แถว JSON ต่อ 1 บรรทัด (ข้ามบรรทัดว่าง/#comment — v2.2)"""
    try:
        with open(path, encoding="utf-8") as fh:
            if json_lines:
                rows = []
                for ln, line in enumerate(fh, 1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    try:
                        item = json.loads(line)
                    except ValueError as exc:
                        return None, "บรรทัด %d JSON พัง: %s" % (ln, exc)
                    rows.append(item)
            else:
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
    rows, err = load_script(args.script, json_lines=args.json_lines)
    if err:
        print(err)
        return 1

    # v2.4: --validate — ตรวจสคริปต์อย่างเดียว ไม่เล่น
    if getattr(args, "validate", False):
        plugin_names = sorted(dict(load_plugins()))
        issues = validate_rows(rows, plugin_names=plugin_names)
        if issues:
            print("พบปัญหา %d แถว:" % len(issues))
            for num, reason in issues:
                print("  แถว %d: %s" % (num, reason))
            return 1
        print("สคริปต์ผ่านการตรวจ ✓ (%d แถว)" % len(rows))
        return 0

    speed = max(0.1, min(10.0, args.speed))
    loops = max(0, args.loops)
    log_enabled = not args.no_log
    running = [True]
    vars_ = {}                                  # ตัวแปรของการเล่น เริ่มใหม่ทุกรอบชุด

    plugins = dict(load_plugins())
    if plugins:
        print("  •  plugins: %s" % ", ".join(sorted(plugins)))

    def _find_image(r):
        """v2.2: ค้นภาพให้ runner (เหมือน find_image_cb ของ CLI หลัก)"""
        path, area, thr = me.parse_search_area(r.get("additional"))
        pos = me.find_image_pos(path, area, thr)
        if pos is None and me.find_image_pos.last_error:
            print("  ⚠ %s" % me.find_image_pos.last_error)
        return pos

    def _wait_image(r):
        """v2.2: รอภาพปรากฏ — ตรวจทุก 0.5 วิ จนเจอ/หมด timeout/ผู้ใช้หยุด"""
        raw, timeout = me.parse_wait_timeout(r.get("additional"), 30)
        path, area, thr = me.parse_search_area(raw)
        if not me.HAS_CV:
            print("  ⚠ Wait for Image ต้องติดตั้ง: pip install opencv-python Pillow")
            return
        deadline = time.time() + timeout
        while time.time() < deadline and running[0]:
            pos = me.find_image_pos(path, area, thr)
            if pos is not None:
                print("  Wait for Image: เจอภาพที่ (%d,%d)" % pos)
                return
            time.sleep(0.5)
        if running[0]:
            print("  Wait for Image: ไม่เจอภาพภายใน %d วิ" % timeout)

    mouse_ctl = MouseController()
    kb_ctl = KbController()
    # v2.11: โหมด dry-run เขียนรายงานไฟล์เหมือน CLI หลัก (v2.10.1) — ดักบรรทัด DRY-RUN
    dry_on = bool(getattr(args, "dry_run", False))
    dry_lines = []

    def _message(text, color="#080"):
        s = str(text)
        if dry_on and s.startswith("DRY-RUN:"):
            dry_lines.append(s)
        print("  " + s)

    runner = ActionRunner(
        mouse_ctl, kb_ctl,
        stop_check=lambda: running[0],
        on_beep=lambda: print("\a", end="", flush=True),
        on_message=_message,
        on_clipboard_set=lambda text: None if me.clip_set(text)
        else print("  ⚠ Set Clipboard: ตั้งคลิปบอร์ดไม่สำเร็จบนระบบนี้"),
        on_clipboard_read=me.clip_get,
        variables=vars_,
        dry_run=bool(getattr(args, "dry_run", False)),
        plugin_lookup=lambda name: plugins.get(name),
        log_src=args.script,
        unsupported_cb=lambda btn: print(
            "  ⚠ ข้ามแถว: action '%s' ยังไม่รองรับใน engine_cli — เปิดใน GUI เพื่อเล่น action นี้" % btn),
        find_image_cb=_find_image,        # v2.2: Image Click/If Image ค้นภาพได้จริง
        wait_image_cb=_wait_image)        # v2.2: Wait for Image รอจริง

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
    run_t0 = time.time()          # v2.4: Safety timeout (--max-minutes)
    mx = max(0.0, float(getattr(args, "max_minutes", 0.0) or 0.0))
    try:
        n_loop = 0
        while True:
            if loops == 0 and not running[0]:
                break
            n_loop += 1
            if loops and n_loop > loops:
                break
            print("— รอบที่ %d —" % n_loop)
            play_items = pick_play_order(play_rows)
            block_rounds = {}             # v2.6 (ชุด N2): ตัวนับรอบลูปย่อยรีเซ็ตทุกรอบสคริปต์
            block_head_add = {}           # v2.6: Additional ของ Block Start ที่แทนค่าแล้ว
            pi = 0
            while pi < len(play_items):   # ใช้ index เดินเอง — Block Start/End กระโดดข้าม/วนกลับได้
                i, r = pi + 1, play_items[pi]
                if not running[0]:
                    break
                if mx and time.time() - run_t0 > mx * 60:
                    print("⏱ หยุดอัตโนมัติ — เล่นครบ %g นาทีตามที่ตั้ง (--max-minutes)" % mx)
                    running[0] = False
                    break
                r = subst_row(r, vars_)            # แทน {ตัวแปร} ทุกคอลัมน์
                if r.get("button") == SECTION_HEADER:   # แถวจัดระเบียบ — ไม่ทำอะไร
                    pi += 1
                    continue
                if r.get("button") == me.BLOCK_START:   # v2.6 (ชุด N2): กลไกเดียวกับ GUI
                    block_head_add[pi] = r.get("additional", "")
                    goto, bmsg = me.BlockRunner(
                        pi, condition_cb=runner.evaluate_block_condition
                    ).decide(play_items, block_rounds, row=r)
                    if bmsg:
                        print("  [%d/%d] %s" % (i, len(play_items), bmsg))
                    if goto is not None and goto > pi:
                        pi = goto
                        continue
                    pi += 1
                    continue
                if r.get("button") == me.BLOCK_END:
                    goto, bmsg = me.BlockRunner(
                        pi, condition_cb=runner.evaluate_block_condition
                    ).decide_end(play_items, block_rounds, head_additions=block_head_add)
                    if bmsg:
                        print("  [%d/%d] %s" % (i, len(play_items), bmsg))
                    if goto is not None and 0 < goto < pi:
                        pi = goto
                        continue
                    pi += 1
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
                if btn in (me.IF_IMAGE, me.ELSE_IMAGE, me.IF_PIXEL):
                    # v2.2: เงื่อนไขค้นภาพอยู่ใน runner แล้ว — ตั้ง skip_n แล้วทำต่อ
                    # (ข้อความผลปริ้นผ่าน on_message ของ runner แล้ว)
                    runner.execute(r)
                    skipping = runner.skip_n
                    if log_enabled and skipping:
                        log_write("STEP", "รอบ %d แถว %d/%d %s → ข้าม %d แถว (%.1f วิ)" %
                                  (n_loop, i, len(play_rows), btn, skipping,
                                   time.time() - t0), args.script)
                    pi += 1
                    continue
                # เงื่อนไขนับรอบ/เวลา — กลไกเดียวกับ CLI หลัก (v2.1)
                skip_n, cond_msg = ActionRunner.evaluate_condition(
                    btn, r.get("additional", ""), r.get("repeat", 1), n_loop,
                    variables=vars_)   # v2.5: If Variable
                if cond_msg:
                    print("  [%d/%d] %s" % (i, len(play_rows), cond_msg))
                    if log_enabled and skip_n:
                        log_write("STEP", "รอบ %d แถว %d/%d %s → ข้าม %d แถว (%.1f วิ)" %
                                  (n_loop, i, len(play_rows), cond_msg.split("→")[0].strip(),
                                   skip_n, time.time() - t0), args.script)
                    if skip_n > 0:
                        skipping = skip_n
                    pi += 1
                    continue
                if skipping > 0:               # แถวถูกสั่งข้ามจากเงื่อนไขก่อนหน้า
                    skipping -= 1
                    continue
                ok = runner.execute(r)
                if not ok:
                    running[0] = False
                    break
                print("  [%d/%d] %s %s" % (i, len(play_items), btn,
                                           r.get("additional", "") or ""))
                pi += 1
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
        # v2.11: รายงาน dry-run ลงไฟล์ — หยุดกลางคันก็บันทึกส่วนที่เดินผ่าน (ทน error ทุกจุด)
        if dry_on and dry_lines:
            me.dry_report_write(me.dry_report_block(
                args.script, len(play_rows),
                "ไม่จำกัด" if loops == 0 else loops, dry_lines,
                finished=(rc == 0)), args.script)
            print("รายงาน Dry-run: %s" % me.dry_report_path())
        if log_enabled:
            prune_log()
    return rc


if __name__ == "__main__":
    sys.exit(main())

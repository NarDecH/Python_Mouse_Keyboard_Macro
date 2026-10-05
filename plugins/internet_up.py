# -*- coding: utf-8 -*-
"""Plugin API v3 (v2.13) — เงื่อนไข: Internet Up (v2.14)

เช็คว่าอินเทอร์เน็ต/เน็ตเวิร์กใช้ได้หรือไม่ — เปิด socket ไปที่โฮสต์ที่ระบุ
(ค่าเริ่มต้น 1.1.1.1:443 — ใช้ IP ตรง ๆ ไม่ต้องแก้ DNS และไม่ส่งข้อมูลอะไรเลย)
stdlib ล้วน (socket) — ไม่เพิ่ม dependency

Additional = "host[:พอร์ต]" และ/หรือ "Ns" เช่น
  (ว่าง)      → 1.1.1.1:443 รอเชื่อมต่อ 2 วิ
  8.8.8.8     → โฮสต์เอง ค่าเริ่มต้นพอร์ต 443 รอ 2 วิ
  8.8.8.8:53  → กำหนดพอร์ตเอง
  1.1.1.1 5s  → รอ 5 วิ (token สไตล์เดียวกับ Wait for Image)

ใช้ได้ 2 ทาง:
  1. คอลัมน์ Action = "Internet Up" → เชื่อมได้ = เล่นต่อ, ไม่ได้ = ข้าม N แถว (N = Repeat)
  2. Block Start → Additional: `if Internet Up` (ผสม && กับเงื่อนไขอื่นได้)
     เช่น `if Internet Up && Process Running chrome`

ใช้ {ตัวแปร} ในช่อง Additional ได้ — แทนค่าก่อนส่งเข้ามาแล้ว
"""
import socket

CONDITION_NAME = "Internet Up"

_DEFAULT_HOST = "1.1.1.1"
_DEFAULT_PORT = 443
_DEFAULT_TIMEOUT = 2.0


def check(ctx, row):
    """คืน True เมื่อเชื่อม TCP สำเร็จ — ห้าม raise (engine จับให้อยู่แล้ว แต่กติกา plugin = ทนเอง)"""
    try:
        host, port = _DEFAULT_HOST, _DEFAULT_PORT
        timeout = _DEFAULT_TIMEOUT
        parts = str(row.get("additional") or "").split()
        for tok in parts:
            t = tok.strip()
            if not t:
                continue
            if t.endswith("s") and t[:-1].replace(".", "", 1).isdigit():
                timeout = max(0.2, float(t[:-1]))          # "5s" = รอ 5 วิ
                continue
            if ":" in t:
                h, _, p = t.rpartition(":")
                if p.isdigit():
                    host, port = h or host, int(p)
                    continue
            host = t                                        # host ล้วน (ไม่มีพอร์ต)
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False
    except Exception:
        return False

# -*- coding: utf-8 -*-
"""Plugin API v3 (v2.13) — เงื่อนไข: HTTP Status (v2.16 — Issue #5)

เช็คว่า URL ตอบกลับด้วยรหัส HTTP ที่ต้องการหรือไม่ — เฝ้า API/เว็บก่อนทำงานต่อ
stdlib ล้วน (urllib.request) — ไม่เพิ่ม dependency

Additional = `URL [รหัส] [Ns]` เช่น
  https://example.com/health        → รหัส 2xx ใด ๆ = จริง
  https://example.com/health 200    → ต้องได้รหัส 200 เป๊ะ
  https://example.com/health 204 3s → รอสูงสุด 3 วิ (token สไตล์เดียวกับ Internet Up)

ใช้ได้ 2 ทาง:
  1. คอลัมน์ Action = "HTTP Status" → ตรงเงื่อนไข = เล่นต่อ, ไม่ตรง = ข้าม N แถว (N = Repeat)
  2. Block Start → Additional: `if HTTP Status https://api.local/ping 200`

ใช้ {ตัวแปร} ในช่อง Additional ได้ — แทนค่าก่อนส่งเข้ามาแล้ว
หมายเหตุ: เรียก GET จริงทุกครั้งที่เล่นแถวนี้ (dry-run เรียกด้วย) — ใช้กับ URL ของตัวเอง
"""
import urllib.request
import urllib.error

CONDITION_NAME = "HTTP Status"

_DEFAULT_TIMEOUT = 5.0
_USER_AGENT = "AutoMouseKeyboardMacro"       # หลายเว็บบล็อก UA ว่างของ python


def check(ctx, row):
    """คืน True เมื่อรหัส HTTP ตรงเงื่อนไข — ห้าม raise (network พัง = เท็จ)"""
    try:
        url = ""
        expected = None
        timeout = _DEFAULT_TIMEOUT
        for tok in str(row.get("additional") or "").split():
            t = tok.strip()
            if not t:
                continue
            if t.endswith("s") and t[:-1].replace(".", "", 1).isdigit():
                timeout = max(0.5, float(t[:-1]))        # "3s" = รอ 3 วิ
                continue
            if t.isdigit():
                expected = int(t)                        # "200" = รหัสที่ต้องการ
                continue
            if not url and "://" in t:
                url = t
            elif not url:
                url = "https://" + t                     # ไม่มี scheme = เติม https
        if not url:
            return False
        req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                code = getattr(resp, "status", None) or resp.getcode()
        except urllib.error.HTTPError as e:              # 4xx/5xx = ยังเป็น "การตอบ"
            code = e.code
        if expected is None:
            return 200 <= int(code or 0) < 300           # ไม่ระบุ = 2xx คือจริง
        return int(code or 0) == expected
    except Exception:
        return False

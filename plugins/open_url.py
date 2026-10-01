# -*- coding: utf-8 -*-
"""Open URL — เปิดลิงก์เว็บในเบราว์เซอร์ (v2.8 plugin ชุมชนตัวอย่างที่ 3)

Additional: URL เช่น "https://example.com" (ใส่ {ตัวแปร} ผสมได้)
ใช้ webbrowser ของ stdlib — ทำงานได้ทั้ง Windows/macOS/Linux ไม่เพิ่ม dependency
URL ว่าง/พัง = ไม่ทำอะไร ไม่มีวันพังโปรแกรม
"""

import webbrowser

ACTION_NAME = "Open URL"


def run(ctx, row):
    if not isinstance(ctx, dict):
        return None
    url = str(row.get("additional") or "").strip()
    if not url:
        return None
    vars_ = ctx.get("vars")
    if isinstance(vars_, dict):
        try:
            from macro_engine import substitute_vars
            url = substitute_vars(url, vars_)
        except Exception:
            pass
    if "://" not in url:                        # ไม่มี scheme → เติม https:// ให้
        url = "https://" + url
    try:
        ok = webbrowser.open(url)
    except Exception:
        ok = False
    log = ctx.get("log")
    if callable(log):
        log("open url %s: %s" % ("ok" if ok else "FAIL", url))
    return None

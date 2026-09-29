# -*- coding: utf-8 -*-
"""Custom Action plugin: "Toast" — แจ้งเตือน Windows (toast) ไม่บล็อกการเล่น (v2.5)
ตั้งค่าในตาราง: Additional = ข้อความ (ว่าง = "สคริปต์ทำงานเสร็จแล้ว")
- Windows 10/11: ยิงผ่าน PowerShell (Windows Runtime toast) — ไม่ต้องติดตั้งอะไร
- OS อื่น / ยิงไม่สำเร็จ: fallback เป็น ctx["ui"]["msg"] + ctx["log"]
ต่างจาก Message Box: toast ไม่ต้องกดปิด โปรแกรมเล่นแถวถัดไปต่อทันที
"""
ACTION_NAME = "Toast"


def run(ctx, row):
    msg = str(row.get("additional") or "").strip() or "สคริปต์ทำงานเสร็จแล้ว"
    sent = False
    try:
        import subprocess
        ps = (
            "[void][Windows.UI.Notifications.ToastNotificationManager,"
            "Windows.UI.Notifications,ContentType=WindowsRuntime];"
            "$t=[Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent("
            "[Windows.UI.Notifications.ToastTemplateType]::ToastText02);"
            "$x=$t.GetElementsByTagName('text');"
            "$x.Item(0).AppendChild($t.CreateTextNode('Auto Mouse Macro'));"
            "$x.Item(1).AppendChild($t.CreateTextNode(%r));"
            "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("
            "'{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\WindowsPowerShell\\v1.0\\powershell.exe'"
            ").Show([Windows.UI.Notifications.ToastNotification]::new($t))"
        ) % msg
        p = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
                           capture_output=True, timeout=15)
        sent = (p.returncode == 0)
    except Exception:
        sent = False
    if callable(ctx.get("log")):
        ctx["log"]("toast: %s%s" % (msg, "" if sent else " (ส่ง toast ไม่สำเร็จ — แจ้งใน statusbar แทน)"))
    if not sent:
        ui = ctx.get("ui") or {}
        show = ui.get("msg") if isinstance(ui, dict) else None
        if callable(show):
            show("🔔 " + msg)

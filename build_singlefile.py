# -*- coding: utf-8 -*-
"""build_singlefile.py — รวม macro_engine.py กลับเป็น auto_macro.py ไฟล์เดียว (v2.0)

ตามหลักการ "ไฟล์เดียวจบ" ของโปรเจกต์: โค้ดระหว่างบรรทัดที่ขึ้นต้น
    # === ENGINE-BEGIN (v2.0: แยกไป macro_engine.py — อย่าแก้ในไฟล์นี้ แก้ที่ macro_engine.py)
จนถึงบรรทัด
    # === ENGINE-END
ถูกเก็บเป็น macro_engine.py (พร้อม header คอมเมนต์ข้างบนเป็นบรรทัดแรก)
สคริปต์นี้อ่าน macro_engine.py แล้วแทนบล็อกนั้นใน auto_macro.py ด้วยเนื้อหาล่าสุด

การแยกเป็นสองไฟล์เพื่อเทสต์/นำ engine ไปใช้โดยไม่แตะ Tk — แจกจ่าย/build ยังเป็นไฟล์เดียวเสมอ
ใช้ก่อน build .exe เสมอ:   py build_singlefile.py   &&   py -m PyInstaller auto_macro.spec
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.join(HERE, "auto_macro.py")
ENGINE = os.path.join(HERE, "macro_engine.py")

BEGIN = "# === ENGINE-BEGIN (v2.0: แยกไป macro_engine.py — อย่าแก้ในไฟล์นี้ แก้ที่ macro_engine.py)"
END = "# === ENGINE-END"
ENGINE_HEADER = "# -*- coding: utf-8 -*-\n# macro_engine.py — engine ล้วน (ค่าคงที่/parser/คลิปบอร์ด/unicode/log/stats/plugins)\n# ไม่มี Tk ใด ๆ — นำไปใช้/เทสต์แยกได้ · ซิงก์กลับ auto_macro.py ด้วย: py build_singlefile.py\n"


def main():
    if not os.path.exists(ENGINE):
        sys.exit("ไม่พบ macro_engine.py — ไฟล์ engine ต้องอยู่ข้างสคริปต์นี้")
    body = io.open(MAIN, encoding="utf-8").read()
    eng = io.open(ENGINE, encoding="utf-8").read()
    # ตัด header ที่เขียนไว้ใน macro_engine.py ออก (auto_macro.py มี header ของตัวเอง)
    lines = eng.splitlines()
    while lines and (not lines[0].strip() or lines[0].startswith("#")):
        lines.pop(0)
    core = "\n".join(lines).rstrip() + "\n"
    b = body.find(BEGIN)
    e = body.find(END)
    if b < 0 or e < 0 or e < b:
        sys.exit("หาบล็อก ENGINE-BEGIN/END ใน auto_macro.py ไม่เจอ — โครงไฟล์ผิดปกติ")
    out = body[:b] + BEGIN + "\n" + core + "\n\n" + END + body[e + len(END):]
    io.open(MAIN, "w", encoding="utf-8", newline="").write(out)
    print("รวม engine (%d บรรทัด) กลับเข้า auto_macro.py สำเร็จ" % (core.count("\n") + 1))


if __name__ == "__main__":
    main()

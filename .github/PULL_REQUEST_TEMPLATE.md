## สิ่งที่ PR นี้ทำ

<!-- อธิบายสั้น ๆ: แก้อะไร / เพิ่มอะไร / ทำไม -->

## การเปลี่ยนแปลงหลัก

- 
- 

## ทดสอบแล้วยังไง

- [ ] `py -m py_compile auto_macro.py` ผ่าน
- [ ] `py -m unittest test_auto_macro test_e2e -v` ผ่านทั้งหมด (จำนวนเทสต์: ...)
- [ ] เปิดโปรแกรมจริง `timeout 6 py auto_macro.py` ไม่มี error ที่ stderr
- [ ] อัพเดต `docs/CHANGELOG.md` + `.html` แล้ว
- [ ] ข้อความ UI ใหม่ใส่ใน `TR` ทั้ง th/en แล้ว (ถ้ามี)

## หมายเหตุ

<!-- สิ่งที่ reviewer ควรดูเป็นพิเศษ / ความเสี่ยงที่รู้อยู่ -->

## ถ้าเป็น PR plugin (v2.8) — เกณฑ์รีวิว 6 ข้อ (docs/PLUGINS.md)

- [ ] stdlib/pynput เท่านั้น — ไม่ pip install เพิ่ม
- [ ] ทน input พัง/ctx ขาดโดยไม่ raise
- [ ] ประกาศ `ACTION_NAME` ไม่ซ้ำกับ action ที่มีอยู่
- [ ] เทสต์มาตรฐาน 4 แบบตามแม่แบบ `plugins/_template.py` (ชื่อคลาสไม่ซ้ำ)
- [ ] มีตัวอย่างการใช้ใน docstring หัวไฟล์
- [ ] อัพเดตรายการใน `docs/PLUGINS.md` แล้ว

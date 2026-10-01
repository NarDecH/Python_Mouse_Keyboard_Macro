---
name: "🔌 เสนอ plugin ใหม่ (Plugin submission)"
about: "ส่ง plugin จากชุมชนเข้าโปรแกรม — เปิด PR ที่ plugins/ พร้อม issue นี้เป็นลิงก์อ้างอิง"
title: "[PLUGIN] ชื่อ plugin ของคุณ"
labels: ["plugin"]
---

<!-- วิธีส่ง:
     1) fork → เขียน plugins/ชื่อของคุณ.py ตาม plugins/_template.py
     2) เพิ่มเทสต์ตามแม่แบบท้าย _template.py (4 เทสต์) ใน test_auto_macro.py
        (ชื่อคลาสเทสต์ห้ามซ้ำกับคลาสเดิม — ดู AGENTS.md v1.11)
     3) เปิด PR โดยอ้าง issue นี้ — เกณฑ์รีวิวครบ 6 ข้ออยู่ที่ docs/PLUGINS.md -->

## ชื่อ plugin / หน้าที่

<!-- ACTION_NAME คืออะไร ทำอะไร ใช้กับงานแบบไหน -->

## Additional ที่รับ

<!-- รูปแบบค่าที่ผู้ใช้ใส่ในช่อง Additional เช่น "1.5-4" หรือ "ชื่อ += 1" -->

## เขียนตัวแปรหรือไม่

<!-- ถ้าเขียน ctx["vars"] บอกชื่อตัวแปรและค่าที่ได้ — แถวถัดไปใช้ {ชื่อ} ต่อได้ -->

## เช็คลิสต์ผู้ส่ง

- [ ] stdlib/pynput เท่านั้น (ไม่ pip install เพิ่ม)
- [ ] ทน input พัง/ctx ขาดโดยไม่ raise (ทดสอบด้วยค่า None/""/ตัวอักษร)
- [ ] ไม่มี network/telemetry ซ่อนเร้น (ถ้าต้องยิงเน็ต บอกในไฟล์ชัดเจน)
- [ ] เทสต์ 4 แบบตามแม่แบบ _template.py ผ่าน (`py -m unittest test_auto_macro -v`)
- [ ] มีตัวอย่างการใช้ใน docstring หัวไฟล์
- [ ] เปิด PR ที่เพิ่มไฟล์ใน plugins/ + เทสต์ใน test_auto_macro.py แล้ว

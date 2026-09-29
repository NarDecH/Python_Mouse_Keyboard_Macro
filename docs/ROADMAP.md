# 🗺️ ROADMAP — แผนพัฒนาต่อ

> สถานะ: v2.2.1 (เดือน ก.ย. 2026) — เสนอไอเดีย/โหวตได้ที่ [Issues](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/issues)

## 🌏 v2.3 — ต่อยอดจากสถาปัตยกรรม v2.0 ที่จบสมบูรณ์

> พื้นฐานพร้อมหมดแล้ว: engine ล้วนไม่มี Tk → ActionRunner แหล่งเดียว → GUI/CLI/engine_cli
> สามหน้ากาก · ของชุดนี้เน้นชุมชน + การเข้าถึง ไม่ใช่การรื้อโครงอีก

- [ ] **รวบรวม plugin จากชุมชน (ต่อยอดตลาด v2.1)** — เปิดรับ PR เพิ่ม `plugins/*.py` +
      แนวทางรีวิวใน docs/PLUGINS.md (เกณฑ์: stdlib/pynput เท่านั้น, ทน error, มีตัวอย่างในเอกสาร)
- [x] ~~**ไฟล์ plugin ในโปรเจกต์ทำเทสต์ครบ**~~ ✅ v2.3.0 (TestPluginsComplete — ครบ 5 ตัว
      รัน run(ctx, row) ด้วย ctx จำลอง + ทน input พัง)
- [ ] **Multi-language docs (จีน/ญี่ปุ่น)** — i18n ตัวโปรแกรมรองรับแล้ว · พื้นฐาน EN ครบแล้ว
      (TUTORIAL.en.md) — รอผู้ร่วมแปล แปลจาก TUTORIAL.en.md ได้ทันที
- [x] ~~**cross-platform จริง (Linux/macOS)**~~ ✅ v2.3.0 (CI เพิ่ม job ubuntu/macos —
      unit ทุก OS, E2E ฝั่ง Linux ใต้ xvfb, macOS continue-on-error รอสิทธิ์ accessibility)
- [x] ~~**Schedule ฉบับสมบูรณ์**~~ ✅ v2.4.0 (เลือกโปรไฟล์ที่ตอนตั้งเวลา + แสดง
      นัดหมายปัจจุบันในหน้า Settings — จำค่าลง conf)
- [x] ~~**ส่งออกสคริปต์เป็นแบตช์ (.bat/.sh)**~~ ✅ v2.3.0 (เมนู 📤 Export Bat — สร้าง
      .bat + .sh ข้างสคริปต์ ดับเบิลคลิกรันผ่าน CLI, อาร์กิวเมนต์ส่งต่อด้วย %*/"$@")

## 🚀 v1.17 — ถัดไปอันใกล้ (ประวัติ)

## 🚀 v1.17 — ถัดไปอันใกล้

- [x] ~~**ค้นหา/กรองแถวในตาราง** — ช่องค้นหาเด้งไปแถวที่ตรง (มีปุ่มลัด Ctrl+F)~~ ✅ v1.17
- [x] ~~**Undo แถวที่ลบล่าสุด** (Ctrl+Z — เก็บ snapshot)~~ ✅ v1.17 (50 ชั้น)
- [x] ~~**Import สคริปต์จากคลิปบอร์ด** — ก๊อป JSON จากที่อื่นมาวางเป็นงานได้เลย~~ ✅ v1.17 (เมนู 📋 Paste)
- [x] ~~**Condition พื้นฐาน (If Image)**~~ ✅ v1.17 (ดึงมาจาก v1.18 ก่อนกำหนด)
- [x] ~~**สถิติราย plugin/action** — Stats แยกเวลาที่ใช้ต่อ Action~~ ✅ v1.18 (top_actions_summary)

## 🧩 v1.18 — ขยายความสามารถ

- [x] ~~**Wait for Pixel Color** — รอจุดสีที่กำหนดก่อนทำงานต่อ~~ ✅ v1.18
- [x] ~~**Condition พื้นฐานในสคริปต์** — "ถ้าภาพเจอ → ทำ A, ไม่เจอ → ข้าม"~~ ✅ v1.17 (If Image)
- [x] ~~**If Image / Else** — เงื่อนไขสองทาง: เจอ → กลุ่ม A, ไม่เจอ → กลุ่ม B~~ ✅ v1.18 (Else If Image)
- [x] ~~**ตัวแปรในสคริปต์** — เก็บ/อ่านค่าระหว่างแถว (เช่น นับรอบ, ผลลัพธ์ล่าสุด)~~ ✅ v1.19 (Set Variable + `{ชื่อ}`)
- [x] ~~**คลิปบอร์ด action** — ตั้ง/อ่านคลิปบอร์ด (วางข้อความเร็วกว่า Type Text)~~ ✅ v1.20 (Set/Read Clipboard)

## 🔀 v1.21 — เงื่อนไขขั้นสูง + จัดระเบียบตาราง

- [x] ~~**เงื่อนไขนับรอบ (If Loop)** — รอบที่ N ขึ้นไปข้ามแถวถัดไป~~ ✅ v1.21
- [x] ~~**เงื่อนไขเวลา (If Time)** — ผ่าน HH:MM แล้วข้ามแถวถัดไป~~ ✅ v1.21
- [x] ~~**หัวข้อ Section** — ป้ายชื่อกลุ่มแถว (ไม่เล่น ไม่นับเลข) จัดระเบียบสคริปต์ยาว~~ ✅ v1.21
- [x] ~~**ย่อ/ขยายกลุ่มใต้หัวข้อ** — ซ่อนแถวสมาชิกจากจอ (ยังเล่นปกติ)~~ ✅ v1.22 (แถวซ่อน serialize/save ครบ)
- [x] ~~**สีแถวตามหมวด Action** — เงื่อนไข/คีย์/พิเศษ แยกสีเห็นภาพ~~ ✅ v1.22
- [x] ~~**ปุ่มจับเวลาให้ If Time** — เติม HH:MM ปัจจุบัน+N นาที~~ ✅ v1.22 (แบบเดียวกับปุ่มจับสี)
- [x] ~~**กฎเดียวของเงื่อนไข** — Repeat = จำนวนแถวที่ข้าม ทุกชนิด~~ ✅ v1.21

## 🏗️ v2.0 — ปรับโครงใหญ่ (เมื่อชุมชนโต)

- [x] ~~**แยก engine ออกจาก GUI (phase 1)** — `macro_engine.py` ค่าคงที่/parser/คลิปบอร์ด/unicode/
      log/stats/plugins ล้วน ไม่มี Tk~~ ✅ v2.0 (รักษาสัญญา "ไฟล์เดียวจบ" ด้วย `build_singlefile.py`
      รวมกลับเป็น `auto_macro.py` ก่อน build .exe · phase 2: ย้าย player/recorder ออกจาก MacroApp)
- [x] ~~**phase 2: กลไก "ทำ 1 แถว" (ActionRunner) รวมเป็นแหล่งเดียว GUI+CLI**~~ ✅ v2.1
      (CLI ทำ Move/Cursor/Modifier/Double/Launch ได้จริง + `engine_cli.py` ย่อย)
- [x] ~~**phase 3: Recorder + ค้นภาพย้ายลง engine — engine ไม่พึ่ง Tk ทั้งไฟล์**~~ ✅ v2.2
      (Recorder ล้วน + parse_search_area/find_image_pos ใน engine · CLI ค้นภาพครบ:
      Image Click/If Image/Else/Wait for Image · `engine_cli --json-lines` · plugin ใหม่ 3 ตัว)
- [x] ~~**ตลาด plugin** — หน้ารวม plugin + API เอกสาร + ปุ่มเปิดโฟลเดอร์~~ ✅ v2.1 (docs/PLUGINS.md + ปุ่ม 🔌)
- [x] ~~**Multi-language docs** — เอกสารอังกฤษฉบับเต็ม~~ ✅ v2.1 (TUTORIAL.en.md 12 บท — จีน/ญี่ปุ่นค่อยว่างกันชุมชน)
- [x] ~~**Plugin API v2** — ctx เพิ่ม `stop_check()` (plugin หยุดตาม STOP ได้), `ui` (toast/statusbar)~~ ✅ v1.20
- [x] ~~**รวบรวม plugin จากชุมชน / Multi-language (จีน-ญี่ปุ่น)**~~ ⬆️ ย้ายไปแผน v2.3 (หัวข้อบน)

## 🎯 หลักการที่ห้ามฝ่าฝืน

1. **ความปลอดภัยผู้ใช้มาก่อน** — ฟีเจอร์ใหม่ห้ามทำให้ STOP ใช้ไม่ได้ทุกช่องทาง
2. **stdlib + pynput เท่านั้น** (Image Click ใช้ opencv แบบ optional) — ไม่เพิ่ม dependency โดยไม่จำเป็น
3. **ทุกฟีเจอร์ต้องมีเทสต์** — unit + E2E ผ่านก่อน merge เสมอ
4. **ข้อความใหม่ต้องอยู่ใน `TR` ทั้ง th/en** — และเอกสาร .md/.html อัพเดตพร้อมกัน

---
*อัพเดตล่าสุด: v2.2.1 — ถอดจาก CHANGELOG · สถาปัตยกรรม v2.0 จบ 3 phases แล้ว — ชุดถัดไปเน้นชุมชน/cross-platform*

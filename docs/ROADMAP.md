# 🗺️ ROADMAP — แผนพัฒนาต่อ

> สถานะ: v2.8.1 (เดือน ต.ค. 2026) — เสนอไอเดีย/โหวตได้ที่ [Issues](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/issues)

## 🎯 สถานะปัจจุบัน (v2.8.1)

สถาปัตยกรรม v2.0 จบครบ 3 phases · ชุดเงื่อนไขครบวงจร (If Image/Pixel/Variable/Loop/Time)
+ ตัวแปร + คลิปบอร์ด + ตารางจัดการง่าย (ลากสลับ/Redo/Note/แทนที่) พร้อมใช้งานแล้วทั้งหมด —
ดูรายละเอียดย้อนหลังที่ [CHANGELOG.md](CHANGELOG.md)

## 🚀 แผนถัดไป

- [x] **เงื่อนไขเชิงซ้อน (nested if / ลูปย่อย)** — ชุด N1 (เงื่อนไขรวม `&&`) ✅ v2.5.4 ·
      ชุด N2 (Block Start/End + ลูปย่อย until/max) ✅ v2.6.0 ·
      feedback/ใช้งานจริงแชร์ได้ที่ [Issue #1](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/issues/1)
      · อ่านข้อเสนอฉบับเต็มที่ [DESIGN-nested-if.md](DESIGN-nested-if.md) (เปิดดู [HTML](DESIGN-nested-if.html) ได้)
- [x] ~~**รวบรวม plugin จากชุมชน (ต่อยอดตลาด v2.1)**~~ ✅ v2.8.0 — ประตูรับครบชุด:
      issue template ส่ง plugin + PR checklist ตามเกณฑ์ 6 ข้อใน docs/PLUGINS.md +
      plugin ตัวอย่างจากชุมชน 3 ตัว (Random Pause / Counter / Open URL) พร้อมเทสต์มาตรฐาน
- [x] ~~**Schedule แต่ละนัดหมายเลือกโปรไฟล์เอง**~~ ✅ v2.8.0 — ช่องเวลาใส่ `HH:MM=ชื่อโปรไฟล์`
      ได้ (เช่น `08:00, 12:30=งานเช้า, 22:00`) ถึงเวลาโหลดโปรไฟล์นั้นมาเล่นเอง —
      เวลาที่ไม่ระบุใช้โปรไฟล์ตั้งต้นต่อ (v2.4/v2.7 เข้ากันได้)
- [x] ~~**.ahk ตัวแปร/เงื่อนไขสองทิศ**~~ ✅ v2.8.0 — export `Set Variable` → `n := 5` /
      `If Variable` → `if (n > 5)` · import `n := 0` / `n += 2` / `if (n > 5)` กลับเป็นแถว
      (`x := y` → `x = {y}` อ้างตัวแปร) — เงื่อนไขแปลไม่ได้ข้ามเหมือนเดิม
- [x] ~~**ย่อ/ขยายกลุ่มบล็อก (Block Start→End)**~~ ✅ v2.8.1 — ค้างจาก
      [DESIGN-nested-if.md](DESIGN-nested-if.md) — กลไก `_section_stash` เดิม คลิกขวาที่
      Block Start ย่อ/ขยายได้ (นับวงเล็บซ้อน, กันซ้อนย่อ, แถวซ่อนเล่น/บันทึกครบ) +
      แก้บั๊กแฝง v1.22: แถวซ่อนเดิม "หลุด" จากการเล่นจริง (_rows_and_iids_for_play)
- [x] ~~**ปุ่มตรวจสคริปต์ใน GUI**~~ ✅ v2.8.1 — เมนู 🔍 Validate เรียก engine เดียวกับ
      `--validate` รายงาน "แถว N: เหตุผล" เป็นหน้าต่าง ไม่ต้องเปิด CLI
- [x] ~~**Multi-language docs (จีน/ญี่ปุ่น)**~~ ✅ v2.7.0 (TUTORIAL.zh.md + TUTORIAL.ja.md
      แปลครบทุกบทจาก TUTORIAL.en.md — ฉบับอื่นในอนาคตแปลจาก en ต่อได้)
- [x] ~~**ส่งออก .ahk import/export**~~ ✅ v2.7.0 (เมนู 🔀: ส่งออก .ahk / นำเข้า .ahk —
      Send/Click/MouseMove/Sleep/Run · แถวไม่รองรับเขียนเป็น comment)
- [x] ~~**Schedule หลายนัดหมาย**~~ ✅ v2.7.0 (โหมดทุกวันใส่เวลาได้หลายเวลาคั่น comma +
      migrate ค่าเก่าอัตโนมัติ + ปุ่ม 🕐/＋/ล้าง)
- [x] ~~**cross-platform จริง (Linux/macOS)**~~ ✅ v2.3.0 (CI เพิ่ม job ubuntu/macos —
      unit ทุก OS, E2E ฝั่ง Linux ใต้ xvfb, macOS continue-on-error รอสิทธิ์ accessibility)
- [x] ~~**Safety timeout + self-healing hotkey + --validate**~~ ✅ v2.4.0
- [x] ~~**เงื่อนไขครบวงจร (If Pixel/If Variable/Read Pixel/rand/img vars)**~~ ✅ v2.5.0
- [x] ~~**ลากสลับแถวเต็มรูปแบบ + Redo + Note + แทนที่ทั้งหมด**~~ ✅ v2.5.0–2.5.2

## 📜 ประวัติแผนที่ทำเสร็จแล้ว

## 🚀 v1.17

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
*อัพเดตล่าสุด: v2.8.1 — ถอดจาก CHANGELOG · ย่อ/ขยายบล็อก + ปุ่มตรวจสคริปต์ใน GUI +
แก้บั๊กแฝงแถวซ่อนไม่เล่น — หัวข้อค้าง: รอ PR plugin จากชุมชนจริง*

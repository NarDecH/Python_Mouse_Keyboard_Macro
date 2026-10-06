# 🗺️ ROADMAP — แผนพัฒนาต่อ

> สถานะ: v2.11.0 (เดือน ต.ค. 2026) — เสนอไอเดีย/โหวตได้ที่ [Issues](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/issues)

## 🎯 สถานะปัจจุบัน (v2.9.0)

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
- [x] ~~**START ตรวจก่อนเล่น**~~ ✅ v2.9.0 — กด START ตรวจด้วย `validate_rows` เดียวกับ
      🔍 Validate — พบปัญหาถามยืนยัน ยืนยัน = เล่นเฉพาะแถวที่ผ่าน (แถวพังถูกข้ามจริง)
      · ทุกแถวพัง = ไม่เล่น — กัน "กดแล้วเงียบ"
- [x] ~~**ย่อทั้งหมด / ขยายทั้งหมด**~~ ✅ v2.9.0 — เมนูขวาย่อ Section + บล็อกทุกตัวในครั้งเดียว
      (กลุ่มนอกกลืนกลุ่มใน) / ขยายคืนลำดับเดิมเป๊ะ
- [x] ~~**.ahk บล็อกสองทิศ**~~ ✅ v2.9.0 — export Block Start → `if (…) {` / `Loop, N {` /
      `} Until,` (หลายเงื่อนไข `&&`, `~` → `InStr()`) · import กลับเป็น BLOCK_START/BLOCK_END
      — ภาพ/สีที่แปลไม่ได้ = comment ทั้งบล็อก ไม่มีปีกกาลลอย · roundtrip if/max/until ตรงเป๊ะ
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

## 🧭 ข้อเสนอ v2.10 (โหวต/คอมเมนต์ได้ที่ [Issue #1](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/issues/1)) — เสร็จครบ

- [x] ~~**Dry-run (ทดลองเล่นแบบไม่แตะเมาส์/คีย์)**~~ ✅ v2.10 — เมนู 🧪 + CLI `--dry-run`:
      เดินทั้งสคริปต์จริง (เงื่อนไข/บล็อก/ดีเลย์/ตัวแปรครบ) action จริงถูกแทนด้วยบรรทัด
      "DRY-RUN: จะ…" — จุดเดียวใน ActionRunner GUI/CLI เหมือนกัน
- [x] ~~**ผลเงื่อนไขเป็นตัวแปร**~~ ✅ v2.10 — โทเคน `>ชื่อ` ท้าย Additional ของเงื่อนไขทุกชนิด
      เก็บ "1"/"0" — แถวถัดไปใช้ `{ชื่อ}` / If Variable ต่อได้เลย (ไม่เพิ่ม action ใหม่)
- [x] ~~**Batch runner (CLI หลายสคริปต์ต่อกัน)**~~ ✅ v2.10 — `--queue list.txt` รันเรียงลำดับ
      ตรวจทุกไฟล์ก่อนเริ่ม (พัง = ยกเลิกทั้งคิว) + สรุปรายไฟล์ + log [QUEUE] —
      งานผลักกะ/backup ชุดใหญ่ทำได้ไฟล์เดียว → ระดับ: กลาง
- [x] ~~**ต่อยอด v2.10.1**~~ ✅ v2.10.1 — Dry-run ออกรายงานไฟล์ `dry_report_วันที่.txt`
      (เส้นทาง + สรุปจะทำจริง, หยุดกลางคันก็บันทึกส่วนที่ผ่าน) + เมนู 🗂️ Queue Bat
      export .bat/.sh รันคิวจาก GUI + TUTORIAL บทที่ 14 (เชิงลึก + แบบฝึกหัด)

## 🧭 ข้อเสนอ v2.11 (โหวต/คอมเมนต์ได้ที่ [Issue #1](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/issues/1))

- [x] ~~**Plugin เป็นเงื่อนไขได้ (Plugin API v3)**~~ ✅ v2.13.0 — plugin ประกาศ `CONDITION_NAME` +
      `check(ctx, row) -> bool` ใช้แทน Action/ผสม `&&` ใน Block Start ได้ — ครอบคลุม
      validate/dry-run/ค้นหา + `.ahk` export + ตัวอย่าง `file_exists.py` + TUTORIAL บทที่ 17
- [x] ~~**เครื่องมือ log เพิ่ม**~~ ✅ v2.11.0 — ปุ่มเก็บถาวรวันเก่า (ย้ายลง `log_archive/YYYY-MM/`
      รายเดือน เก็บตลอดไป) / ล้างวันเก่า (ถามยืนยันก่อน) ในหน้าต่าง 📝 Log + เห็นรายงาน
      dry-run ใน dropdown · ตั้งจัดการอัตโนมัติตอนปิดโปรแกรมได้ใน Settings (เก็บย้อนหลัง
      1–365 วัน เก็บถาวร/ลบ — ไฟล์วันนี้ไม่แตะเสมอ) · รวมของค้าง: engine_cli เขียนรายงาน
      dry-run แล้ว
- [x] ~~**ผู้เล่นคิวแบบ GUI ติดตามผล**~~ ✅ v2.12.0 — เมนู 📑 Run Queue: เลือกไฟล์ลิสต์
      (.txt รูปแบบเดียวกับ `--queue`) เล่นทีละไฟล์ในโปรแกรมเลย — หน้าต่างสด ตารางไฟล์
      (สถานะรายไฟล์สีตามผล) + ป้ายไฟล์ปัจจุบัน + ผลลัพธ์ CLI แบบทันที + สรุปท้ายคิว ·
      ปุ่มหยุดไฟล์นี้ (เล่นถัดไปต่อ ผ่าน `--stop-file` รายไฟล์) / หยุดทั้งคิว · ตรวจทุกไฟล์
      ก่อนเล่นเหมือน CLI · เธรดเล่น + queue.Queue + poller ตามข้อตกลง thread-safe

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

## 🚀 v2.15 — แนวโน้มถัดไป ([milestone No.1](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/milestone/1) — ติดตามผ่าน issues)

- [x] ~~**เล่นเฉพาะกลุ่มหัวข้อ (Play section group)**~~ ✅ v2.15.0 (คลิกขวาหัวข้อ → "▶ เล่นกลุ่มนี้อย่างเดียว"
      + CLI `--only-section ชื่อ` — player จริงสายเดียวกับ START, แถวย่อก็เล่นครบ)
- [ ] **ลากจัดลำดับกลุ่ม (Group order)** — สั่งเล่น"ทีละกลุ่มหัวข้อ"ตามลำดับที่จัดไว้ / ลากสลับกลุ่มทั้งก้อน —
      ต่อยอด Section/Block ที่มีอยู่ ครอบงานใหญ่ที่แบ่งเป็นขั้น ๆ ([Issue #2](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/issues/2))
- [ ] **ส่งออก/นำเข้าเป็น .exe คู่สคริปต์** — สร้าง .bat/.lnk ที่เล่นสคริปต์นั้นทันทีผ่าน AutoMouseMacro.exe (ต่อยอด Export Bat/Queue Bat — หนึ่งดับเบิลคลิก = หนึ่งสคริปต์ ไม่ต้องเปิดโปรแกรมหลัก) ([Issue #3](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/issues/3))
- [ ] **ถอดเงื่อนไขซ้อนเป็นลำดับเหตุการณ์ (Event timeline)** — มุมมองใหม่ของสคริปต์: เห็นผลเงื่อนไข/skip ของการเล่นล่าสุดเป็นไทม์ไลน์ต่อแถว (ใช้ log STEP เดิม — ช่วยดีบั๊กสคริปต์เงื่อนไขซ้อนหลายชั้น) ([Issue #4](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/issues/4))
- [ ] **ตลาด plugin จากชุมชนรอบใหม่** — ประกาศ Plugin API v3/v3.5 หา condition-plugin ที่เป็นประโยชน์ (เช่น Window Focused, File Newer Than, HTTP Status) รวมดีๆ ขึ้น Release ถัดไป ([Issue #5](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/issues/5))

---
*อัพเดตล่าสุด: v2.15.0 — ถอดจาก CHANGELOG · เปิด [milestone v2.15](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/milestone/1)
แล้ว (ข้อแรก "เล่นเฉพาะกลุ่มหัวข้อ" สำเร็จใน v2.15.0) — ข้อถัดไปติดตามใน issues #2–#5 ·
ข้อเสนอใหม่เสนอได้ที่ [Issue #1](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/issues/1)*

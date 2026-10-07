# ตัวอย่างสคริปต์ (examples/)

ตัวอย่างสคริปต์สำเร็จรูป โหลดผ่านเมนู **Load** ในโปรแกรม หรือรันผ่าน CLI:

```bash
py auto_macro.py examples/01_auto_typer.json
```

### ตัวอย่าง Custom Action plugins (v1.16+)

```bash
py auto_macro.py examples/06_plugin_demo.json
```

สาธิต plugin ที่มากับโปรเจกต์: **Message Box** (เด้งกล่องข้อความ) + **Sleep (plugin)**
(หน่วง) — เหมาะใช้เป็นแม่แบบเขียน plugin ของคุณเอง ดู `plugins/README.md`

### ตัวอย่างเงื่อนไข (v1.18+)

```bash
py auto_macro.py examples/07_conditions.json
```

สาธิต **If Image → กลุ่ม A/B** (Else If Image) และ **Wait for Pixel Color** —
ลองบัง/เลิกบังหน้าต่างที่มี target.png แล้วเล่นใหม่ เส้นทางจะเปลี่ยน
(แบบฝึกหัดเต็มอยู่ใน TUTORIAL บทที่ 5A)

### ตัวอย่างตัวแปรในสคริปต์ (v1.19+)

```bash
py auto_macro.py examples/08_variables.json
```

สาธิต **Set Variable** (`รอบ = 0`, `รอบ += 1`) และการเรียกใช้ด้วย `{รอบ}`
ในช่องอื่น — ตัวนับ/สรุปค่าระหว่างเล่น ไม่ต้องแก้สคริปต์ทุกรอบ

### ตัวอย่างคลิปบอร์ด (v1.20+)

```bash
py auto_macro.py examples/09_clipboard.json
```

สาธิต **Set Clipboard** (ใส่ข้อความ+ตัวแปรลงคลิปบอร์ด — เขียนทับคลิปเดิมของคุณ)
และ **Read Clipboard** (อ่านกลับเก็บเป็นตัวแปร) — หลังเล่นจบ กด Ctrl+V ที่ไหนก็ได้
เพื่อดูข้อความที่ macro ตั้งไว้

### ตัวอย่างเงื่อนไขนับรอบ/เวลา (v1.21+)

```bash
py auto_macro.py examples/10_conditions_v21.json
```

สาธิต **If Loop** (ข้ามแถวเมื่อถึงรอบ 3) + **If Time** (ก่อน/หลังเที่ยงตัดสินเส้นทาง)
พร้อมหัวข้อ Section จัดระเบียบสคริปต์

### ตัวอย่างเงื่อนไขรวม AND (v2.5.4+)

```bash
py auto_macro.py examples/11_and_conditions.json
```

สาธิตเครื่องหมาย **`&&`** คั่นเงื่อนไขย่อย — ทุกชิ้นต้องจริงจึงเล่นต่อ:
`If Image + If Variable`, `If Pixel Color + If Variable`, `If Loop` หลายเลข,
`If Time` หลายเวลา (ภาพทดสอบ `examples/target.png` — แก้พาธให้ตรงเครื่องคุณได้)

### ตัวอย่าง Block Start/End + ลูปย่อย (v2.6+)

```bash
py auto_macro.py examples/12_blocks.json
```

สาธิตบล็อกเงื่อนไข **`🔷 Block Start` → `🔷 Block End`** — `if ...` ข้ามทั้งบล็อกเมื่อไม่จริง,
`until ... max N` วนเนื้อในซ้ำจนเงื่อนไขจริง (ตัวนับ 1-5 ด้วย Set Variable) และบล็อกซ้อน 2 ชั้น
ตรวจโครงสร้างก่อนเล่นด้วย `--validate`

### ตัวอย่างลำดับกลุ่ม (v2.18+)

```bash
# เล่นทั้งหมดตามลำดับเดิม
py auto_macro.py examples/18_group_order.json
# สุ่มลำดับกลุ่ม (เตรียม/งานหลัก/ล้าง = ก้อนเดิม ไม่สลับแถวภายใน)
py auto_macro.py examples/18_group_order.json --shuffle-groups
# เล่นเฉพาะบางกลุ่มหลายกลุ่มพร้อมกัน
py auto_macro.py examples/18_group_order.json --only-section "เตรียม,ล้าง"
```

สาธิต **ลำดับการเล่นระดับกลุ่ม** — สุ่มลำดับกลุ่มหัวข้อ (แถวภายในกลุ่มเรียงเดิมเสมอ)
เลือกเฉพาะกลุ่มที่ต้องการหลาย ๆ กลุ่มด้วย comma และซ้อมเล่นได้ทั้งกลุ่มด้วย
คลิกขวาหัวข้อ → "🧪 Dry-run กลุ่มนี้" (GUI)

### ตัวอย่างงานเฝ้าระบบ (v1.10+)

```bash
py auto_macro.py examples/05_watchdog_monitor.json --watchdog 5
# จบรอบ → พัก 5 วิ → เริ่มใหม่เอง วนไม่จำกัด (หยุดถาวร: F8/Esc/Ctrl+C)
# หรือดับเบิลคลิก examples/run_watchdog.bat
```

ทุกการรีสตาร์ตบันทึก `[WATCHDOG]` ลง log — เปิดดูย้อนหลังได้ที่เมนู 📊 Stats

> ⚠️ สคริปต์ที่มีการคลิก (เช่น 02) ให้ตรวจสอบพิกัดกับหน้าจอของคุณก่อนเล่นเสมอ —
> พิกัดในตัวอย่างเป็นแค่ค่าตัวอย่าง

| ไฟล์ | สอนอะไร | ความปลอดภัย |
|---|---|---|
| `01_auto_typer.json` | Type Text ไทย/อังกฤษ, คีย์พิเศษ, ดีเลย์สุ่ม, Repeat, Save/Restore Cursor | ✅ ไม่คลิก |
| `02_form_filler.json` | เปิด Notepad, พิมพ์ลงฟอร์ม, Tab ระหว่างช่อง, Launch App | ✅ ไม่คลิก |
| `03_image_click.json` | **Image Click + Search Area** (`@x,y,w,h`), Wait for Image, Beep | ✅ ไม่คลิกจริง (ปิด enabled ไว้) |
| `04_scroll_gallery.json` | Scroll ดูรูป/เว็บ, Move Mouse, Double Click (ปิด enabled) | ⚠️ มีแถวคลิกที่ปิดไว้ |
| `05_watchdog_monitor.json` | งานเฝ้าระบบ: Beep + พิมพ์สถานะ + Save/Restore Cursor + Scroll | ✅ ไม่คลิก |
| `06_plugin_demo.json` | **Custom Action plugins**: Message Box + Sleep (plugin) — แม่แบบเขียน plugin | ✅ ไม่คลิก |
| `07_conditions.json` | **เงื่อนไข (v1.18)**: If Image → กลุ่ม A/B (Else If Image) + Wait for Pixel Color | ✅ ไม่คลิก |
| `08_variables.json` | **ตัวแปร (v1.19)**: Set Variable (`=`, `+=`) + เรียกใช้ `{รอบ}` ในช่องอื่น | ✅ ไม่คลิก |
| `09_clipboard.json` | **คลิปบอร์ด (v1.20)**: Set Clipboard + Read Clipboard (เขียนทับคลิปเดิม) | ✅ ไม่คลิก |
| `10_conditions_v21.json` | **เงื่อนไข (v1.21)**: If Loop / If Time + หัวข้อ Section | ✅ ไม่คลิก |
| `11_and_conditions.json` | **เงื่อนไขรวม AND (v2.5.4)**: `&&` ผสมภาพ+สีจุด+ตัวแปร+รอบ+เวลา | ✅ ไม่คลิก |
| `12_blocks.json` | **Block Start/End (v2.6.0)**: บล็อกเงื่อนไข + ลูปย่อย until/max + ซ้อน 2 ชั้น | ✅ ไม่คลิก |
| `13_start_validate_ahk_blocks.json` | **v2.9**: START ตรวจก่อนเล่น + บล็อก if/until/max ที่ export .ahk ได้ครบ — ลอง 🔀 Export แล้วนำเข้ากลับ | ✅ ไม่คลิก |
| `14_dry_run_cond_vars.json` | **v2.10**: เก็บผลเงื่อนไขเป็นตัวแปร (โทเคน `>ชื่อ`) + ลอง 🧪 Dry-run ซ้อมเดินสคริปต์ไม่แตะเมาส์/คีย์ | ✅ ไม่คลิก |
| `14_condition_plugin.json` | **v2.13**: เงื่อนไข plugin จาก `plugins/file_exists.py` (File Exists) — ใช้เป็น Action + Block Start | ✅ ไม่คลิก |
| `15_system_conditions.json` | **v2.14**: เงื่อนไขระบบ Internet Up / Process Running / Window Exists + Block Start ผสม `&&` | ✅ ไม่คลิก |
| `16_condition_plugins_v216.json` | **v2.16**: เงื่อนไขใหม่ File Newer Than / Window Focused / HTTP Status — รันจากโฟลเดอร์ examples (`cd examples` ก่อน เพื่อให้เจอ README.md) แล้วเปิด ⏱ ไทม์ไลน์ดูผลทีละแถว | ✅ ไม่คลิก |
| `17_condition_plugins_v217.json` | **v2.17**: เงื่อนไขใหม่ Disk Space Low / Process CPU / Window Closed — ตัวอย่างขอบเขตตัดสินแน่นอนทุกเครื่อง + เปิด ⏱ ไทม์ไลน์ดูผลทีละแถว | ✅ ไม่คลิก |
| `18_group_order.json` | **v2.18**: ลำดับกลุ่ม — `--shuffle-groups` สุ่มลำดับกลุ่ม + `--only-section "เตรียม,ล้าง"` เลือกหลายกลุ่ม + คลิกขวาหัวข้อ Dry-run กลุ่ม | ✅ ไม่คลิก |
| `queue_sample.txt` | ลิสต์ตัวอย่าง `--queue` — `py auto_macro.py --queue examples/queue_sample.txt` เล่น 13+14 ต่อกัน | ✅ ไม่คลิก |
| `run_watchdog.bat` | ดับเบิลคลิกรัน 05 แบบ watchdog (จบ = พัก 5 วิ = เริ่มใหม่เอง) | ✅ |

ทุกสคริปต์แถวแรกคือ `Save Cursor` และแถวสุดท้าย `Restore Cursor` เสมอ
(แนวปฏิบัติที่แนะนำ: เมาส์จะกลับมาที่เดิมหลังจบสคริปต์)

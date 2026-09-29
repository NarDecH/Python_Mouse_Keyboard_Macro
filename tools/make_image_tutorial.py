# -*- coding: utf-8 -*-
"""สร้างคลิปสอนใช้งานกลุ่ม IMAGE ของโปรแกรม (docs/images/tutorial_image.mp4)

รัน:  py tools/make_image_tutorial.py
- เปิดโปรแกรมจริง (auto_macro) บนฉากหลังสีเข้ม ขับเคลื่อนเป็นฉาก ๆ แล้วจับหน้าจอ
- คำบรรยายไทยวาดลงแถบล่างของทุกเฟรม (เลือกฟอนต์ที่มี glyph ไทยจริงอัตโนมัติ)
- เขียนเฟรมลงไฟล์ทันที (incremental — ไม่กิน RAM)
- ⚠️ ระหว่างบันทึก (~60 วิ) เมาส์จะถูกขยับจริง — อย่าใช้เมาส์/คีย์บอร์ดช่วงนั้น
ต้องมี: pip install imageio imageio-ffmpeg (+ opencv-python Pillow สำหรับค้นภาพ)
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageDraw, ImageFont, ImageGrab  # noqa: E402
import imageio.v2 as imageio                            # noqa: E402

import auto_macro as am                                 # noqa: E402
import macro_engine as me                               # noqa: E402
import tkinter as tk                                    # noqa: E402

OUT = os.path.join(BASE, "docs", "images", "tutorial_image.mp4")
FPS = 4
REGION = (0, 80, 1176, 840)                 # กรอบบันทึก — 1176x760 (หาร 8 ลงตัว)
CAPTION = [""]


def _has_thai_glyphs(path):
    """ฟอนต์มี glyph ไทยจริงไหม — สองตัวอักษรไทยต่างรูป = มีจริง (notdef จะเหมือนกัน)"""
    try:
        f = ImageFont.truetype(path, 40)
        return f.getmask("ก").size != f.getmask("ฆ").size
    except OSError:
        return False


FONT_PATH = next((c for c in ("leelawui.ttf", "tahoma.ttf", "segoeui.ttf",
                              "angsa.ttf") if _has_thai_glyphs(c)), "segoeui.ttf")


def font(size, bold=False):
    cands = (("leelawbd.ttf", "tahomabd.ttf", "segoeuib.ttf")
             if bold else (FONT_PATH,))
    for c in cands:
        try:
            return ImageFont.truetype(c, size)
        except OSError:
            continue
    return ImageFont.truetype(FONT_PATH, size)


def annotate(img, text):
    """วาดแถบคำบรรยายด้านล่างเฟรม"""
    d = ImageDraw.Draw(img)
    w, h = img.size
    d.rectangle([0, h - 74, w, h], fill=(16, 24, 16))
    f = font(28)
    bb = d.textbbox((0, 0), text, font=f)
    d.text(((w - (bb[2] - bb[0])) // 2, h - 74 + (74 - (bb[3] - bb[1])) // 2 - bb[1]),
           text, font=f, fill=(240, 255, 240))
    return img


def card(text_lines, hold=2.5):
    """การ์ดพื้นเข้ม (ปก/สรุป) — เขียนลงไฟล์ทันที"""
    hold *= 1.6                    # จังหวะช้าลงให้ตามอ่านทัน
    img = Image.new("RGB", (REGION[2] - REGION[0], REGION[3] - REGION[1]), (18, 32, 22))
    d = ImageDraw.Draw(img)
    y = 170
    for line, size, color in text_lines:
        f = font(size, bold=size >= 40)
        bb = d.textbbox((0, 0), line, font=f)
        d.text(((img.size[0] - (bb[2] - bb[0])) // 2, y), line, font=f, fill=color)
        y += size + 26
    for _ in range(max(1, int(hold * FPS))):
        writer.append_data(np.asarray(img))


def cap(hold=0.8):
    """จับหน้าจอปัจจุบัน ~hold วินาที"""
    hold *= 1.6                    # จังหวะช้าลงให้ตามอ่านทัน (v2.4)
    for _ in range(max(1, int(hold * FPS))):
        time.sleep(1 / FPS)
        img = ImageGrab.grab(bbox=REGION)
        emit(annotate(img, CAPTION[0]))


def emit(img):
    """เขียน 1 เฟรมลง MP4 ทันที (incremental — ไม่กิน RAM)"""
    global frame_count
    writer.append_data(np.asarray(img))
    frame_count += 1


def ui(sec=0.05):
    root.update()
    time.sleep(sec)


def say(text):
    CAPTION[0] = text
    ui()


# ---------------------------------------------------------------- เตรียมฉาก --
frame_count = 0
root = tk.Tk()
root.withdraw()
app = am.MacroApp(root)
app._log_enabled = False
app._sched_mode = ""
app.tree.delete(*app.tree.get_children())     # ตารางว่างสำหรับถ่ายทำ
root.geometry("760x680+10+120")

# ฉากหลังสีเข้มปิดเต็มกรอบบันทึก (กันหน้าจองานอื่นหลุดเข้าคลิป)
backdrop = tk.Toplevel(root)
backdrop.geometry("%dx%d+%d+%d" % (REGION[2] - REGION[0], REGION[3] - REGION[1],
                                   REGION[0], REGION[1]))
backdrop.overrideredirect(True)
backdrop.configure(bg="#0f1a12")
backdrop.attributes("-topmost", True)
backdrop.update()

root.deiconify()
root.attributes("-topmost", True)
root.title("Auto Mouse & Keyboard Macro — ถ่ายทำคลิป")
root.lift()

# หน้าต่างเป้าหมาย: ป้ายใหญ่ที่จะถูกค้นด้วยภาพ แล้วโดนคลิก (กระพริบเมื่อโดนคลิก)
demo = tk.Toplevel(root)
demo.geometry("390x300+770+150")
demo.attributes("-topmost", True)
demo.title("หน้าต่างเป้าหมาย")
tgt = tk.Button(demo, text="TARGET\nกดฉันสิ", font=("Segoe UI", 22, "bold"),
                bg="#ffd54f", activebackground="#ffb300", relief="ridge", bd=4)
tgt.pack(fill="both", expand=True, padx=16, pady=16)


def on_target_click(_e=None):
    tgt.config(bg="#ff7043", text="โดนคลิกแล้ว!\n✔")
    demo.after(1200, lambda: tgt.config(bg="#ffd54f", text="TARGET\nกดฉันสิ"))


tgt.bind("<Button-1>", on_target_click)
root.update()
demo.update()
demo.lift()

os.makedirs(os.path.dirname(OUT), exist_ok=True)
writer = imageio.get_writer(OUT, fps=FPS, codec="libx264", quality=7,
                            macro_block_size=8)

# ------------------------------------------------------------------ ถ่ายทำ --
card([("สอนใช้งานกลุ่ม IMAGE", 44, (140, 255, 160)),
      ("Image Click · Search Area · Threshold", 28, (230, 230, 230)),
      ("If Image (A/B) · Wait for Image · Multi Image Click", 26, (230, 230, 230)),
      ("Auto Mouse & Keyboard Macro v" + am.__version__, 22, (150, 200, 150))],
     hold=3.2)

say("ขั้นที่ 1: เตรียมหน้าต่างเป้าหมาย — ป้าย TARGET ที่เราต้องการให้โปรแกรมคลิก")
ui(); cap(2.4)

say("ขั้นที่ 2: จับภาพป้ายด้วยปุ่ม 📸 (ลากกรอบครอบป้าย → เซฟเป็น target_auto.png)")
ui()
bx, by = tgt.winfo_rootx(), tgt.winfo_rooty()
bw, bh = tgt.winfo_width(), tgt.winfo_height()
pad = 4
target_png = os.path.join(BASE, "target_auto.png")
ImageGrab.grab(bbox=(bx - pad, by - pad, bx + bw + pad, by + bh + pad)).save(target_png)
tgt_img = Image.open(target_png)
tgt_img.thumbnail((220, 160))
pal = Image.new("RGB", (REGION[2] - REGION[0], REGION[3] - REGION[1]), (18, 32, 22))
pal.paste(tgt_img, (REGION[2] - REGION[0] - 280, 140))
d = ImageDraw.Draw(pal)
d.text((60, 160), "ได้ไฟล์ภาพ: target_auto.png", font=font(30, True), fill=(140, 255, 160))
d.text((60, 220), "ภาพนี้คือ 'ลายนิ้วมือ' ที่โปรแกรมใช้ค้นหาบนหน้าจอ", font=font(24),
       fill=(230, 230, 230))
for _ in range(int(2.5 * FPS)):
    writer.append_data(np.asarray(pal))

say("ขั้นที่ 3: เพิ่มแถว Image Click — Additional = ชื่อไฟล์ภาพ (ค้นทั้งจอ, threshold 80%)")
app._append_row(button="Image Click", additional=target_png, secs=0.5)
ui(); cap(2.6)

# ตรวจว่า Search Area ตรงจริง (กัน DPI/scaling เพี้ยน) — ไม่ตรงจะสอนแบบค้นทั้งจอแทน
area = (bx - 40, by - 40, bx + bw + 40, by + bh + 40)
pos = me.find_image_pos(target_png, area, 0.8)
if pos is not None:
    say("ขั้นที่ 4: Search Area @x,y,กว้าง,สูง + threshold #90 — ค้นเฉพาะกรอบ เร็วขึ้น แม่นขึ้น")
    last = app.tree.get_children()[-1]
    am.MacroApp._apply_edit(app, last, 5, "%s@%d,%d,%d,%d#90" % (
        target_png, area[0], area[1], area[2] - area[0], area[3] - area[1]))
    ui(); cap(2.8)
else:
    say("ขั้นที่ 4: Search Area @x,y,กว้าง,สูง + threshold #90 (ตัวอย่าง: img.png@100,80,400,300#90)")
    cap(2.8)

say("ขั้นที่ 5: กด START — โปรแกรมค้นเจอป้ายแล้วคลิกกึ่งกลางให้เอง (ดูเมาส์/สีปุ่ม)")
run_t0 = time.time()
app.start_play()
while app.running and time.time() - run_t0 < 25:
    ui(0.05)
    cap(0.25)
app.stop_all(silent=True)
say("✔ ป้ายกระพริบ = โดนคลิกจริง — ตำแหน่งคำนวณจากกึ่งกลางภาพที่เจอ")
cap(1.8)

say("ขั้นที่ 6: If Image — เจอ → เล่นกลุ่ม A ต่อ · ไม่เจอ → ข้ามไป Else เล่นกลุ่ม B")
app._append_row(button=am.IF_IMAGE, additional=target_png, mins=0, secs=0.2, repeat=3)
app._append_row(button=am.SECTION_HEADER, additional="กลุ่ม A — เจอภาพ (BEEP 2 ครั้ง)", secs=0)
app._append_row(button="Beep", additional="", mins=0, secs=0.2)
app._append_row(button="Beep", additional="", mins=0, secs=0.2)
app._append_row(button=am.ELSE_IMAGE, additional="", mins=0, secs=0.2, repeat=2)
app._append_row(button=am.SECTION_HEADER, additional="กลุ่ม B — ไม่เจอ (BEEP 1 ครั้ง)", secs=0)
app._append_row(button="Beep", additional="", mins=0, secs=0.5)
ui(); cap(2.4)

say("ทดสอบ A: ภาพยังอยู่ → ถ้าเจอ เล่นกลุ่ม A (BEEP 2 ครั้ง) แล้วข้ามกลุ่ม B")
run_t0 = time.time()
app.start_play()
while app.running and time.time() - run_t0 < 25:
    ui(0.05)
    cap(0.25)
app.stop_all(silent=True)
cap(0.8)

say("ซ่อนหน้าต่างเป้าหมาย (จำลองภาพ/หน้าจอหายไป)…")
demo.withdraw()
ui(); cap(1.6)
say("ทดสอบ B: ภาพหาย → If Image ข้ามกลุ่ม A → Else เล่นกลุ่ม B (BEEP 1 ครั้ง)")
run_t0 = time.time()
app.start_play()
while app.running and time.time() - run_t0 < 25:
    ui(0.05)
    cap(0.25)
app.stop_all(silent=True)
demo.deiconify(); ui(); cap(1.2)

say("ขั้นที่ 7: Wait for Image — รอจนภาพปรากฏก่อนทำแถวถัดไป (timeout ตั้งได้ เช่น 60s)")
app._append_row(button="Wait for Image", additional=target_png, mins=0, secs=1)
ui(); cap(2.0)
demo.withdraw()
say("ซ่อนเป้าหมาย → โปรแกรมรอ… (ระหว่างรอกด F8 หยุดได้ทันที)")
app.start_play()
t0 = time.time()
demo.after(2500, demo.deiconify)
while app.running and time.time() - t0 < 20:
    ui(0.05)
    cap(0.3)
app.stop_all(silent=True)
cap(1.0)

say("ขั้นที่ 8: Multi Image Click — คลิกหลายภาพต่อกัน: a.png|b.png@กรอบ#threshold")
app._append_row(button="Multi Image Click",
                additional="%s|%s" % (target_png, target_png), secs=0.5)
ui(); cap(2.6)

card([("สรุป", 40, (140, 255, 160)),
      ("📸 จับภาพ → Additional = ไฟล์ภาพ (ใส่ @กรอบ#threshold ได้)", 26, (235, 235, 235)),
      ("▶ START → ค้นเจอแล้วคลิกกึ่งกลางให้", 26, (235, 235, 235)),
      ("🔀 If Image + Else = ทางแยก A/B · ⏳ Wait for Image = รอก่อนทำต่อ", 24, (235, 235, 235)),
      ("ดูเพิ่ม: TUTORIAL บทที่ 5 และ 5A", 24, (150, 200, 150))], hold=3.5)

# ------------------------------------------------------------- ปิด/สรุป --
root.destroy()
writer.close()
try:
    os.remove(target_png)              # ไฟล์ภาพทดสอบ — ถ่ายเสร็จลบทิ้ง
except OSError:
    pass
print("สร้างคลิปแล้ว: %s (%d เฟรม, %.1f MB, %d วิ)" % (
    OUT, frame_count, os.path.getsize(OUT) / 1024 / 1024,
    frame_count // FPS))

# -*- coding: utf-8 -*-
"""ตรวจสุขภาพเอกสาร (docs/*.md + *.html) — ใช้ในเครื่องและ CI (.github/workflows/docs-check.yml)

ตรวจ 3 อย่าง:
1. ลิงก์ไฟล์ภายในพัง — [ข้อความ](เส้นทาง) และ href/src ใน HTML ต้องชี้ไฟล์ที่มีจริง
   (ตัดโค้ดบล็อก/inline code ออกก่อนเพื่อไม่จับตัวอย่าง syntax เป็นลิงก์)
2. เวอร์ชันค้างเก่า — __version__ ปัจจุบันต้องปรากฏในเอกสารหลักทุกไฟล์
   และ CHANGELOG.md ต้องมีหัวข้อ [เวอร์ชันนั้น]
3. หัวข้อ CHANGELOG ซ้ำ — เวอร์ชันเดียวกันห้ามมีหัวข้อมากกว่า 1 รายการ (เคยพลิกซ้ำตอน v2.5.x)

รัน: py tools/check_docs.py   (exit 1 เมื่อพบปัญหา)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = (".git", "__pycache__", "backups", "build", "dist", ".github")
SKIP_PREFIX = ("http://", "https://", "mailto:", "data:", "ftp://")

MD_LINK = re.compile(r"\[[^\]]+\]\(([^)\s]+)\)")
HTML_LINK = re.compile(r'(?:href|src)="([^"#]+)(?:#[^"]*)?"')
CHANGELOG_HEAD = re.compile(r"^## \[(\d+\.\d+\.\d+)\]", re.M)

# เอกสารหลักที่ต้องโชว์เวอร์ชันปัจจุบัน (path แบบ relative จาก root)
VERSION_DOC_FILES = [
    "docs/README.md",
    "docs/README.html",
    "docs/README.en.md",
    "docs/TUTORIAL.md",
    "docs/TUTORIAL.html",
    "docs/TUTORIAL.en.md",
]


def read_version():
    """อ่าน __version__ จาก macro_engine.py (แหล่งเดียวกับเทสต์)"""
    path = os.path.join(ROOT, "macro_engine.py")
    with open(path, encoding="utf-8") as fh:
        m = re.search(r'^__version__\s*=\s*"([^"]+)"', fh.read(), re.M)
    if not m:
        raise SystemExit("หา __version__ ใน macro_engine.py ไม่เจอ")
    return m.group(1)


def list_doc_files():
    out = []
    for d, dirs, files in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for f in files:
            if f.endswith((".md", ".html")):
                out.append(os.path.join(d, f))
    return sorted(out)


def strip_code(text):
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"<pre>.*?</pre>", "", text, flags=re.S)
    text = re.sub(r"<code>.*?</code>", "", text, flags=re.S)
    text = re.sub(r"`[^`]*`", "", text)
    return text


def check_links(files):
    bad = []
    n = 0
    for path in files:
        rel = os.path.relpath(path, ROOT)
        raw = open(path, encoding="utf-8", errors="replace").read()
        text = strip_code(raw)
        # html: ตัดส่วน <style>/<script> ทิ้งก่อนจับ href
        links = MD_LINK.findall(text)
        for m in HTML_LINK.finditer(text):
            links.append(m.group(1))
        for link in links:
            link = link.strip()
            if not link or link.startswith(SKIP_PREFIX):
                continue
            if re.match(r"^[A-Za-z]:[\\/]", link):  # พาธ Windows สัมบูรณ์ = ตัวอย่าง
                continue
            n += 1
            target = os.path.normpath(
                os.path.join(os.path.dirname(path), link.split("?")[0])
            )
            if not os.path.exists(target):
                bad.append((rel, link))
    return n, bad


def check_versions(version, files):
    problems = []
    for rel in VERSION_DOC_FILES:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            problems.append(f"ไม่พบไฟล์เอกสารหลัก: {rel}")
            continue
        text = open(path, encoding="utf-8", errors="replace").read()
        if version not in text:
            problems.append(f"{rel} ยังไม่มีเวอร์ชัน {version} — เอกสารค้างเก่า?")
    chg = os.path.join(ROOT, "docs", "CHANGELOG.md")
    if os.path.exists(chg):
        text = open(chg, encoding="utf-8").read()
        if f"## [{version}]" not in text:
            problems.append(f"docs/CHANGELOG.md ยังไม่มีหัวข้อ [{version}]")
    return problems


def check_changelog_duplicates():
    chg = os.path.join(ROOT, "docs", "CHANGELOG.md")
    problems = []
    if os.path.exists(chg):
        text = open(chg, encoding="utf-8").read()
        seen = {}
        for m in CHANGELOG_HEAD.finditer(text):
            seen[m.group(1)] = seen.get(m.group(1), 0) + 1
        for ver, count in sorted(seen.items()):
            if count > 1:
                problems.append(f"docs/CHANGELOG.md หัวข้อ [{ver}] ซ้ำ {count} ครั้ง")
    return problems


def main():
    version = read_version()
    files = list_doc_files()

    n_links, bad_links = check_links(files)
    ver_problems = check_versions(version, files)
    dup_problems = check_changelog_duplicates()

    print(f"ตรวจเอกสาร {len(files)} ไฟล์ · ลิงก์ภายใน {n_links} จุด · เวอร์ชันอ้างอิง {version}")
    for rel, link in bad_links:
        print(f"  [ลิงก์พัง] {rel} -> {link}")
    for p in ver_problems + dup_problems:
        print(f"  [เอกสาร] {p}")

    total = len(bad_links) + len(ver_problems) + len(dup_problems)
    if total:
        print(f"พบปัญหา {total} จุด")
        return 1
    print("เอกสารสุขภาพดี ✔")
    return 0


if __name__ == "__main__":
    sys.exit(main())

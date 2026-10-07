# -*- coding: utf-8 -*-
"""Plugin API v3 (v2.13) — เงื่อนไข: Process CPU (v2.17 — Issue #6)

เช็คว่าโปรเซสใช้ CPU สูงกว่า/ต่ำกว่าเกณฑ์ที่กำหนดหรือยัง — เฝ้างานหนัก:
"เบราว์เซอร์ยังทำงานอยู่" (CPU > 5%) · "เรนเดอร์เสร็จแล้ว" (CPU ร่วงต่ำกว่า 2%)
Windows: ctypes ล้วน (Win32 API) — Linux: /proc/<pid>/stat — ไม่เพิ่ม dependency

Additional = `ชื่อโปรเซส [เกณฑ์%] [Ns]` เช่น
  chrome 5%     → โปรเซสชื่อมี "chrome" ใช้ CPU เฉลี่ย > 5% = จริง
  chrome 5% 3s  → สุ่มวัด 2 จุดห่างกัน 3 วิ เฉลี่ยแล้วเทียบ
  python 1%     → ใช้กับโปรเซสใดก็ได้ที่ชื่อตรง (ไม่สนตัวพิมพ์/นามสกุล .exe)

ค่าเริ่มต้นเกณฑ์ 3% · CPU ของ "โปรเซส" คือค่าเฉลี่ยของทุก instance ที่ชื่อตรง
(โปรเซสเปิดใหม่ CPU ยังไม่เต็มได้ — ใส่ Ns เพื่อวัดจุดห่างกันให้ค่าเสถียร)

ใช้ได้ 2 ทาง:
  1. คอลัมน์ Action = "Process CPU" → ตรงเกณฑ์ = เล่นต่อ, ไม่ตรง = ข้าม N แถว (N = Repeat)
  2. Block Start → Additional: `if Process CPU chrome 5%` (ผสม && กับเงื่อนไขอื่นได้)
"""
import sys

CONDITION_NAME = "Process CPU"

_CPU_MEASURE = {}          # name -> (timestamp, cpu_seconds รวมทุก pid) — จุดวัดครั้งก่อน


def _pids_by_name(name):
    """pid ทั้งหมดของโปรเซสที่ชื่อตรง (ไม่สนตัวพิมพ์/นามสกุล .exe)"""
    n = name.strip().lower().removesuffix(".exe")
    pids = []
    if sys.platform == "win32":
        import ctypes
        import ctypes.wintypes

        pe32 = ctypes.c_ulong(0)
        snap = ctypes.windll.kernel32.CreateToolhelp32Snapshot(2, 0)   # TH32CS_SNAPPROCESS
        if snap == -1:
            return pids

        class PROCESSENTRY32(ctypes.Structure):
            _fields_ = [("dwSize", ctypes.c_ulong), ("cntUsage", ctypes.c_ulong),
                        ("th32ProcessID", ctypes.c_ulong),
                        ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
                        ("th32ModuleID", ctypes.c_ulong), ("cntThreads", ctypes.c_ulong),
                        ("th32ParentProcessID", ctypes.c_ulong), ("pcPriClassBase", ctypes.c_long),
                        ("dwFlags", ctypes.c_ulong), ("szExeFile", ctypes.c_char * 260)]

        entry = PROCESSENTRY32()
        entry.dwSize = ctypes.sizeof(PROCESSENTRY32)
        ok = ctypes.windll.kernel32.Process32First(snap, ctypes.byref(entry))
        while ok:
            exe = entry.szExeFile.decode("utf-8", "replace")
            if exe.lower().removesuffix(".exe") == n:
                pids.append(entry.th32ProcessID)
            ok = ctypes.windll.kernel32.Process32Next(snap, ctypes.byref(entry))
        ctypes.windll.kernel32.CloseHandle(snap)
    else:
        import glob as _glob
        import os
        for stat in _glob.glob("/proc/[0-9]*/stat"):
            try:
                with open(stat, "r") as fh:
                    data = fh.read()
                comm = data[data.index("(") + 1:data.rindex(")")]
                if comm.lower().removesuffix(".exe") == n:
                    pids.append(int(stat.split("/")[2]))
            except (OSError, ValueError):
                continue
    return pids


def _cpu_seconds(pids):
    """cpu time รวม (วินาที) ของ pid ทั้งชุด · Windows ใช้ GetProcessTimes · Linux /proc/<pid>/stat"""
    total = 0.0
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes

        class FILETIME(ctypes.Structure):
            _fields_ = [("dwLowDateTime", wintypes.DWORD), ("dwHighDateTime", wintypes.DWORD)]

        k64 = ctypes.c_ulonglong(0)
        for pid in pids:
            h = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)   # PROCESS_QUERY_LIMITED_INFORMATION
            if not h:
                continue
            try:
                ft_create, ft_exit, ft_kernel, ft_user = (FILETIME() for _ in range(4))
                if ctypes.windll.kernel32.GetProcessTimes(
                        h, ctypes.byref(ft_create), ctypes.byref(ft_exit),
                        ctypes.byref(ft_kernel), ctypes.byref(ft_user)):
                    for ft in (ft_kernel, ft_user):
                        k64.value = ft.dwHighDateTime
                        k64.value = (k64.value << 32) | ft.dwLowDateTime
                        total += k64.value / 1e7                          # 100ns → วินาที
            finally:
                ctypes.windll.kernel32.CloseHandle(h)
    else:
        import os
        clk = os.sysconf("SC_CLK_TCK") or 100
        for pid in pids:
            try:
                with open("/proc/%d/stat" % pid, "r") as fh:
                    data = fh.read()
                rest = data[data.rindex(")") + 2:].split()
                utime, stime = int(rest[11]), int(rest[12])              # ฟิลด์ 14/15 รวมกัน
                total += (utime + stime) / clk
            except (OSError, ValueError, IndexError):
                continue
    return total


def _cpu_count():
    try:
        import os
        return max(1, os.cpu_count() or 1)
    except Exception:
        return 1


def check(ctx, row):
    """คืน True เมื่อ CPU เฉลี่ยของโปรเซส > เกณฑ์ — ห้าม raise (ไม่เจอโปรเซส/วัดไม่ได้ = เท็จ)

    กลไก: จุดแรกจดค่า cpu_seconds (คืน False — ยังไม่มีฐานเทียบ) จุดถัดไปเทียบกับจุดก่อน
    ใส่ `Ns` = เฝ้าหน่วงจนครบ N วิแล้ววัดจุดสองเทียบ (เหมาะกับโปรเซสเปิดใหม่)"""
    import time
    try:
        parts = str(row.get("additional") or "").split()
        if not parts:
            return False
        name = parts[0]
        threshold = 3.0                                  # ค่าเริ่มต้น 3%
        wait = 0.0
        for tok in parts[1:]:
            t = tok.strip()
            if t.endswith("%") and t[:-1].replace(".", "", 1).isdigit():
                threshold = max(0.0, float(t[:-1]))
            elif t.endswith("s") and t[:-1].replace(".", "", 1).isdigit():
                wait = max(0.2, float(t[:-1]))
        pids = _pids_by_name(name)
        if not pids:
            return False                                 # ไม่มีโปรเซส = ไม่จริง
        now = time.monotonic()
        prev = _CPU_MEASURE.get(name)
        if wait > 0 and (prev is None or now - prev[0] < wait):
            time.sleep(min(0.5, wait))                   # พักสั้น ๆ ให้ช่วงวัดมีความหมาย
            now = time.monotonic()
        cur = _cpu_seconds(pids)
        if prev is None or now - prev[0] <= 0.05:
            _CPU_MEASURE[name] = (now, cur)              # จุดแรก = จดฐาน ยังไม่ตัดสิน
            return False
        dt = now - prev[0]
        _CPU_MEASURE[name] = (now, cur)
        pct = max(0.0, (cur - prev[1]) / dt * 100.0 / _cpu_count())
        return pct > threshold
    except Exception:
        return False

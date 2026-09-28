@echo off
chcp 65001 >nul
title Watchdog Monitor - Auto Mouse ^& Keyboard Macro
echo ============================================
echo  เฝ้าระบบตัวอย่าง: จบรอบ = พัก 5 วิ = เริ่มใหม่เอง
echo  หยุดถาวร: กด F8 / Esc / Ctrl+C
echo ============================================
py "%~dp0..\auto_macro.py" "%~dp005_watchdog_monitor.json" --watchdog 5 %*
pause

@echo off
chcp 65001 >nul
title Build AutoMouseMacro.exe

echo ============================================
echo   Build Auto Mouse ^& Keyboard Macro -^> .exe
echo ============================================
echo.

where py >nul 2>nul
if errorlevel 1 (
    echo [ERROR] ไม่พบ Python launcher (py)  กรุณาติดตั้ง Python ก่อน
    pause
    exit /b 1
)

echo [1/3] ติดตั้งไลบรารีที่ต้องใช้...
py -m pip install -r requirements.txt pyinstaller || goto :err

echo.
echo [2/3] Build ด้วย PyInstaller (onefile)...
py -m PyInstaller auto_macro.spec --noconfirm --clean || goto :err

echo.
echo [3/3] สำเร็จ!
echo   ไฟล์ .exe อยู่ที่:  dist\AutoMouseMacro.exe
echo.
explorer dist
exit /b 0

:err
echo.
echo [ERROR] Build ไม่สำเร็จ  ดูรายละเอียดด้านบน
pause
exit /b 1

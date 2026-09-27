@echo off
chcp 65001 >nul
title Auto Mouse ^& Keyboard Macro
python auto_macro.py
if errorlevel 1 pause

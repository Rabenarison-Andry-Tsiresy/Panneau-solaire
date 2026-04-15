@echo off
setlocal

if not exist .venv (
  call dependance.bat
)

call .venv\Scripts\activate.bat
python GUI\main.py

@echo off
pip list | findstr appdirs > nul
if %errorlevel% == 1 (
    echo Module appdirs is missing, installing
    pip install appdirs
)
python %~dp0\%~n0.py %*
@echo on

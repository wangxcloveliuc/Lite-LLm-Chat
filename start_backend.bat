@echo off
REM 激活虚拟环境并启动后端服务
cd /d %~dp0backend
call ..\venv\Scripts\activate.bat
python main.py

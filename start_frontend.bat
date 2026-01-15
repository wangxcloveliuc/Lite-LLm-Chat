@echo off
REM 激活虚拟环境并启动前端服务
cd /d %~dp0frontend
call ..\venv\Scripts\activate.bat
npm run dev

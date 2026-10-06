@echo off
title CAY LUA AI Server
echo ==============================================
echo BẬT MÁY CHỦ AI CAY LUA (YOLOv8)
echo ==============================================
echo.

echo Đang kiem tra phu thuoc...
python -m pip install fastapi uvicorn python-multipart ultralytics opencv-python

echo.
echo ==============================================
echo Khởi động Server...
echo API Health Check: http://localhost:8000/health
echo Dong cua so nay de tat server.
echo ==============================================
python server.py

pause

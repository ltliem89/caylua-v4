@echo off
title CAY LUA Web App (Frontend)
echo ==============================================
echo KHOI DONG TRINH DUYET WEB CHO CAY LUA V3
echo ==============================================
echo.
echo De Service Worker (PWA) va ban do hoat dong tot nhat,
echo Giao dien HTML can duoc mo qua may chu cuc bo (localhost) thay vi file://
echo.
echo Dang mo cong 8080 cho giao dien...
echo Truc tiep truy cap: http://localhost:8080/index.html
echo ==============================================
start http://localhost:8080/index.html
python -m http.server 8080
pause

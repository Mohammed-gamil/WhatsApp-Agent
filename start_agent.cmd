@echo off
title WhatsApp AI Agent - Complete Launch
color 0B

echo ====================================================
echo    🤖 WhatsApp AI Agent 🤖
echo    Starting Backend, Frontend, and Ngrok Tunnel...
echo ====================================================

echo.
echo [1/2] Starting Streamlit UI in a new window...
start "WhatsApp UI" cmd /k "streamlit run ui_app.py"

echo.
echo [2/2] Starting Backend and Webhook Tunnel...
echo.
python tunnel_manager.py

pause

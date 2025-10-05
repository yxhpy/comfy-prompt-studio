@echo off
echo Stopping Flask application...

REM Kill processes using port 5000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000') do (
    taskkill /F /PID %%a 2>nul
)

echo.
echo Starting Flask application...
cd /d E:\project\comfyui
start /min python app.py

echo.
echo Flask application restarted!
echo Access at: http://localhost:5000

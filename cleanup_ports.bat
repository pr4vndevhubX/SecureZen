@echo off
echo 🧹 Cleaning up SecureZen ports (5000, 3030, 5173)...

echo killing processes on port 5000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000') do taskkill /f /pid %%a 2>nul

echo killing processes on port 3030...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3030') do taskkill /f /pid %%a 2>nul

echo killing processes on port 5173...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173') do taskkill /f /pid %%a 2>nul

echo Re-checking...
netstat -ano | findstr ":5000 :3030 :5173"

echo Done. You can now run start_standalone.bat or start_overlay.bat
pause

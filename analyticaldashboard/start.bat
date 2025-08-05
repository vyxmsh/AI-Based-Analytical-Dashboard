@echo off
echo Starting YouTube Analytics Dashboard...
echo.

echo Starting Python Backend...
cd backend
start "Backend Server" cmd /k "python app.py"
cd ..

echo.
echo Starting React Frontend...
cd analyticaldashboard
start "Frontend Server" cmd /k "npm run dev"
cd ..

echo.
echo Both servers are starting...
echo Backend will be available at: http://localhost:5000
echo Frontend will be available at: http://localhost:5173
echo.
echo Press any key to exit this window...
pause > nul 
@echo off
REM FAI-Farm Setup and Run Script for Windows

echo ==========================================
echo FAI-Farm Multi-Agent System
echo ==========================================
echo.

REM Check Python version
python --version
echo.

:menu
echo What would you like to do?
echo.
echo 1) Install dependencies
echo 2) Run tests
echo 3) Train ML model
echo 4) Run Mesa visualization (original)
echo 5) Run Streamlit dashboard (recommended)
echo 6) Full setup (install + train + dashboard)
echo 7) Exit
echo.

set /p choice="Enter choice [1-7]: "

if "%choice%"=="1" goto install
if "%choice%"=="2" goto test
if "%choice%"=="3" goto train
if "%choice%"=="4" goto mesa
if "%choice%"=="5" goto dashboard
if "%choice%"=="6" goto full
if "%choice%"=="7" goto end
echo Invalid choice!
goto menu

:install
echo Installing dependencies...
pip install -r requirements.txt
echo Dependencies installed!
echo.
pause
goto menu

:test
echo Running tests...
python tests/test_simulation.py
echo.
pause
goto menu

:train
echo Training ML disease classifier...
python ml/disease_classifier.py
echo.
pause
goto menu

:mesa
echo Starting Mesa visualization...
echo Opening at http://127.0.0.1:8521
python run.py
goto end

:dashboard
echo Starting Streamlit dashboard...
echo Opening at http://localhost:8501
streamlit run dashboard/streamlit_app.py
goto end

:full
echo Full setup starting...
call :install
call :train
call :dashboard
goto end

:end
echo Goodbye!
pause

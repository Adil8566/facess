@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Membuat virtual environment Python...
    py -m venv .venv
)
call ".venv\Scripts\activate.bat"
echo Memasang dependency yang diperlukan...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo.
echo Menjalankan aplikasi web pada http://127.0.0.1:5000
python web_app.py
pause

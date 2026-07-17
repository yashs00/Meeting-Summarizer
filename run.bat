@echo off
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Error installing dependencies. Please check your python installation.
    pause
    exit /b %ERRORLEVEL%
)
echo Launching Streamlit application...
streamlit run app.py
pause

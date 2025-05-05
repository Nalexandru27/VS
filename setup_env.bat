@echo off
REM Creează un mediu virtual numit tf-env
python -m venv tf-env

REM Activează mediul virtual (doar în cmd)
call tf-env\Scripts\activate.bat

REM Verifică versiunea Python
python --version

REM Instalează TensorFlow (versiune compatibilă cu Python <= 3.11)
pip install tensorflow==2.15.0

REM Poți instala și alte pachete aici
REM 
pip install streamlit pandas matplotlib

echo.
echo 🔁 Mediu virtual creat și TensorFlow instalat cu succes!
echo.
pause

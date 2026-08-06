@echo off
cd /d "%~dp0"

if not exist logs mkdir logs
echo [%date% %time%] Iniciado pelo Agendador de Tarefas >> logs\agendador.log

call .venv\Scripts\activate.bat

python src\main.py

echo [%date% %time%] Finalizado (codigo de saida: %errorlevel%) >> logs\agendador.log

echo.
echo ==========================================
echo Processo finalizado.
echo ==========================================
pause

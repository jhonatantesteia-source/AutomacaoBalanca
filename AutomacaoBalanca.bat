@echo off
setlocal
cd /d "%~dp0"

if not exist logs mkdir logs
if not exist .venv\Scripts\python.exe (
    echo Ambiente virtual nao encontrado: .venv
    echo Execute: py -m venv .venv ^&^& .venv\Scripts\python -m pip install -r requirements.txt
    exit /b 10
)

.venv\Scripts\python.exe -m src.main
set "RESULTADO=%ERRORLEVEL%"
echo [%date% %time%] Finalizado (codigo de saida: %RESULTADO%) >> logs\agendador.log
exit /b %RESULTADO%

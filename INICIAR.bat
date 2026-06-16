@echo off
chcp 65001 >nul
title TBH Bot — Configurando...
color 0A
cls

echo.
echo  ============================================================
echo   TBH: Task Bar Hero — Bot de Automacao
echo  ============================================================
echo.

:: ── Verificar Python ────────────────────────────────────────────
echo  [1/3] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  [ERRO] Python nao foi encontrado no seu computador!
    echo.
    echo  Instale Python 3.10 ou superior em:
    echo  https://www.python.org/downloads/
    echo.
    echo  IMPORTANTE: Marque a opcao "Add Python to PATH" na instalacao.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo  [OK] %PYVER% encontrado.
echo.

:: ── Ir para a pasta do script ───────────────────────────────────
cd /d "%~dp0"

:: ── Instalar dependencias ───────────────────────────────────────
echo  [2/3] Instalando/atualizando dependencias...
echo        (Isso pode demorar alguns segundos na primeira vez)
echo.
pip install -r requirements.txt --quiet --disable-pip-version-check 2>&1
if errorlevel 1 (
    echo.
    echo  [AVISO] Houve um problema ao instalar algumas dependencias.
    echo  Verifique sua conexao com a internet e tente novamente.
    echo.
    choice /c SN /m "  Tentar continuar mesmo assim? (S/N)"
    if errorlevel 2 exit /b 1
)
echo  [OK] Dependencias prontas.
echo.

:: ── Verificar se o jogo esta aberto ────────────────────────────
echo  [3/3] Verificando se o TBH esta aberto...
python -c "
import sys
try:
    import win32gui
    found = []
    win32gui.EnumWindows(lambda h, l: l.append(h) if win32gui.IsWindowVisible(h) and 'Task Bar Hero' in win32gui.GetWindowText(h) else None, found)
    if found:
        print('  [OK] TBH detectado!')
    else:
        print('  [AVISO] TBH nao detectado. Abra o jogo antes de usar o bot.')
except:
    print('  [INFO] Verificacao de janela indisponivel (pywin32).')
" 2>nul
echo.

:: ── Iniciar o painel ────────────────────────────────────────────
echo  Iniciando o painel de automacao...
echo  ============================================================
echo.
timeout /t 1 /nobreak >nul

python launcher.py

if errorlevel 1 (
    echo.
    echo  O bot encerrou com erro. Veja a mensagem acima.
    pause
)

@echo off
setlocal EnableDelayedExpansion
title WhisperPlus - Instalador

echo.
echo  ===========================================================
echo    WhisperPlus - Instalacao de Ambiente
echo    (Execute isto apenas uma vez)
echo  ===========================================================
echo.

set "PROJECT_DIR=%~dp0"
set "BIN_DIR=%PROJECT_DIR%bin"

:: Add bin to PATH for this session
if not exist "%BIN_DIR%" mkdir "%BIN_DIR%"
set "PATH=%BIN_DIR%;%PATH%"

:: ---------------------------------------------------------------
:: STEP 1: Download uv.exe (package manager)
:: ---------------------------------------------------------------
if exist "%BIN_DIR%\uv.exe" (
    echo  [1/5] Gerenciador UV ja instalado.
) else (
    echo  [1/5] Baixando o gerenciador de pacotes UV...
    powershell -NoProfile -Command ^
        "try { " ^
        "  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; " ^
        "  Invoke-WebRequest -Uri 'https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip' -OutFile '%TEMP%\uv.zip' -UseBasicParsing; " ^
        "  Expand-Archive -Path '%TEMP%\uv.zip' -DestinationPath '%TEMP%\uv_temp' -Force; " ^
        "  Copy-Item '%TEMP%\uv_temp\uv.exe' '%BIN_DIR%\uv.exe' -Force; " ^
        "  Remove-Item '%TEMP%\uv_temp' -Recurse -Force; " ^
        "  Remove-Item '%TEMP%\uv.zip' -Force; " ^
        "  Write-Host '  UV instalado com sucesso.' " ^
        "} catch { Write-Host ('  ERRO ao baixar UV: ' + $_.Exception.Message); exit 1 }"
    if errorlevel 1 (
        echo  ERRO: Nao foi possivel baixar o UV. Verifique sua conexao.
        pause
        exit /b 1
    )
)

:: ---------------------------------------------------------------
:: STEP 2: Install Python 3.11 via uv (isolated, does not pollute PATH)
:: ---------------------------------------------------------------
echo  [2/5] Verificando Python 3.11...
"%BIN_DIR%\uv.exe" python install 3.11 >nul 2>&1
if errorlevel 1 (
    echo  ERRO: Falha ao instalar Python 3.11 via UV.
    pause
    exit /b 1
)
echo  Python 3.11 disponivel.

:: ---------------------------------------------------------------
:: STEP 3: Create virtual environment
:: ---------------------------------------------------------------
if exist "%PROJECT_DIR%.venv\Scripts\python.exe" (
    echo  [3/5] Ambiente virtual ja existe.
) else (
    echo  [3/5] Criando ambiente virtual...
    "%BIN_DIR%\uv.exe" venv --python 3.11 "%PROJECT_DIR%.venv"
    if errorlevel 1 (
        echo  ERRO: Falha ao criar o ambiente virtual.
        pause
        exit /b 1
    )
)

:: ---------------------------------------------------------------
:: STEP 4: Install dependencies (GPU or CPU)
:: ---------------------------------------------------------------
echo.
echo  =================================================
echo    Selecione o tipo de instalacao:
echo  =================================================
echo.
echo    [1] GPU (NVIDIA com CUDA) - Recomendado
echo    [2] CPU (sem placa de video)
echo.
set /p GPU_CHOICE="  Sua escolha (1 ou 2): "

if "%GPU_CHOICE%"=="2" (
    echo.
    echo  [4/5] Instalando dependencias para CPU...
    echo  Isso pode demorar bastante (3GB+ de bibliotecas)...
    "%BIN_DIR%\uv.exe" sync --extra cpu --extra diarization-diart
) else (
    echo.
    echo  [4/5] Instalando dependencias para GPU (CUDA)...
    echo  Isso pode demorar bastante (4GB+ de bibliotecas)...
    "%BIN_DIR%\uv.exe" sync --extra cu129 --extra diarization-diart
)

if errorlevel 1 (
    echo.
    echo  ERRO: Falha na instalacao de dependencias.
    echo  Verifique os logs acima para detalhes.
    pause
    exit /b 1
)

:: ---------------------------------------------------------------
:: STEP 5: Download FFmpeg portable
:: ---------------------------------------------------------------
if exist "%BIN_DIR%\ffmpeg.exe" (
    echo  [5/5] FFmpeg ja instalado.
) else (
    echo  [5/5] Baixando FFmpeg portable (~130MB)...
    powershell -NoProfile -Command ^
        "try { " ^
        "  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; " ^
        "  Invoke-WebRequest -Uri 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' -OutFile '%TEMP%\ffmpeg.zip' -UseBasicParsing; " ^
        "  Expand-Archive -Path '%TEMP%\ffmpeg.zip' -DestinationPath '%TEMP%\ffmpeg_temp' -Force; " ^
        "  Get-ChildItem -Path '%TEMP%\ffmpeg_temp' -Recurse -Filter 'ffmpeg.exe' | Select-Object -First 1 | " ^
        "    ForEach-Object { Copy-Item $_.FullName '%BIN_DIR%\ffmpeg.exe' -Force }; " ^
        "  Get-ChildItem -Path '%TEMP%\ffmpeg_temp' -Recurse -Filter 'ffprobe.exe' | Select-Object -First 1 | " ^
        "    ForEach-Object { Copy-Item $_.FullName '%BIN_DIR%\ffprobe.exe' -Force }; " ^
        "  Remove-Item '%TEMP%\ffmpeg_temp' -Recurse -Force; " ^
        "  Remove-Item '%TEMP%\ffmpeg.zip' -Force; " ^
        "  Write-Host '  FFmpeg instalado com sucesso.' " ^
        "} catch { Write-Host ('  ERRO ao baixar FFmpeg: ' + $_.Exception.Message); exit 1 }"
    if errorlevel 1 (
        echo  AVISO: FFmpeg nao foi baixado. O modo Folder Watch pode nao funcionar.
        echo  Voce pode instalar manualmente colocando ffmpeg.exe na pasta bin\.
    )
)

:: ---------------------------------------------------------------
:: DONE
:: ---------------------------------------------------------------
echo.
echo  ===========================================================
echo    Instalacao Concluida!
echo  ===========================================================
echo.
echo    Para iniciar o WhisperPlus:
echo      - Duplo clique em WhisperPlus.exe
echo      - Ou execute start.bat
echo.
echo    Na primeira gravacao, o modelo de IA sera baixado
echo    automaticamente (pode demorar alguns minutos).
echo.
pause

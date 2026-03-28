@echo off
echo.
echo ============================================================
echo   WhisperPlus - Servidor de Transcricao
echo ============================================================
echo.

call .venv\Scripts\activate

set HF_HOME=%~dp0.hf_cache
set HUGGINGFACE_HUB_CACHE=%~dp0.hf_cache

:: Add local bin to PATH (ffmpeg, uv, etc.)
set "PATH=%~dp0bin;%PATH%"

:: Load variables from .env file if it exists
if exist .env (
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        if not "%%a"=="" set "%%a=%%~b"
    )
)

set WLK_OUTPUT_FILE=transcription_live.txt

echo   Servidor:    http://localhost:8000
echo   Modelo:      (carregado sob demanda pelo painel)
echo   Idioma:      Portugues (fixo)
echo   Output:      transcription_live.txt
echo   Ctrl+C para parar
echo.

python server_with_export.py

pause

@echo off
echo.
echo ============================================================
echo   WhisperLiveKit - Transcricao em Tempo Real (PT)
echo ============================================================
echo.

call .venv\Scripts\activate

set HF_HOME=e:\Dev\Whisper Live Kit\.hf_cache
set HUGGINGFACE_HUB_CACHE=e:\Dev\Whisper Live Kit\.hf_cache
set HF_TOKEN=YOUR_HUGGINGFACE_TOKEN_HERE
set WLK_OUTPUT_FILE=transcription_live.txt

echo   Iniciando servidor...
echo   Abra http://localhost:8000 no navegador
echo   Transcricao salva em: transcription_live.txt
echo   Idioma: Portugues (fixo)
echo   Pressione Ctrl+C para parar
echo.

python server_with_export.py --model large-v3-turbo --diarization --diarization-backend diart

pause

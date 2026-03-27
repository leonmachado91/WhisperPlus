@echo off
echo Compilando WhisperPlus Launcher...
call .venv\Scripts\activate
pip install pyinstaller
pyinstaller --onefile --icon=NONE --name WhisperPlus launcher.py
echo.
echo Compilacao concluida! O executavel esta na pasta "dist".
echo Pode copiar WhisperPlus.exe da pasta dist para a raiz do projeto.
pause

"""WhisperPlus Launcher — Silent mode (no visible terminal).

When compiled with PyInstaller using console=False, this launcher:
1. Sets up environment variables (HF_HOME, PATH with bin/)
2. Starts the server process with CREATE_NO_WINDOW
3. Polls /health until the server responds
4. Opens the default browser at http://localhost:8000
5. Waits for the server process to exit
"""
import os
import sys
import subprocess
import webbrowser
import time
import urllib.request


CREATE_NO_WINDOW = 0x08000000


def main():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    # Setup environment
    env = os.environ.copy()
    env["HF_HOME"] = os.path.join(base_dir, ".hf_cache")
    env["HUGGINGFACE_HUB_CACHE"] = os.path.join(base_dir, ".hf_cache")
    env["WLK_OUTPUT_FILE"] = "transcription_live.txt"
    env["PATH"] = os.path.join(base_dir, "bin") + os.pathsep + env.get("PATH", "")

    # Load .env file
    env_path = os.path.join(base_dir, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    env[key.strip()] = value.strip()

    # Find Python in the venv
    venv_python = os.path.join(base_dir, ".venv", "Scripts", "python.exe")
    if not os.path.exists(venv_python):
        # Fallback: try system python
        venv_python = "python"

    server_script = os.path.join(base_dir, "server_with_export.py")
    if not os.path.exists(server_script):
        # If running from a different location, try relative
        server_script = "server_with_export.py"

    # Start server process silently (no console window)
    try:
        proc = subprocess.Popen(
            [venv_python, server_script],
            cwd=base_dir,
            env=env,
            creationflags=CREATE_NO_WINDOW,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        # If venv python not found, show error
        import ctypes
        ctypes.windll.user32.MessageBoxW(
            0,
            "Python não encontrado.\n\nExecute install.bat primeiro.",
            "WhisperPlus - Erro",
            0x10,  # MB_ICONERROR
        )
        return

    # Poll /health until server is ready (up to 30 seconds)
    server_ready = False
    for _ in range(60):
        try:
            r = urllib.request.urlopen("http://localhost:8000/health", timeout=2)
            if r.status == 200:
                server_ready = True
                break
        except Exception:
            # Check if process died
            if proc.poll() is not None:
                import ctypes
                ctypes.windll.user32.MessageBoxW(
                    0,
                    "O servidor falhou ao iniciar.\n\nExecute start.bat para ver os logs de erro.",
                    "WhisperPlus - Erro",
                    0x10,
                )
                return
            time.sleep(0.5)

    if server_ready:
        webbrowser.open("http://localhost:8000")
    else:
        # Open anyway, maybe it's still loading
        webbrowser.open("http://localhost:8000")

    # Keep alive until server exits
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()


if __name__ == "__main__":
    main()

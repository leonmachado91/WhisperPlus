import os
import sys
import subprocess
import webbrowser
import time

def main():
    # Caminho do executável ou script real
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
    start_bat = os.path.join(base_dir, "start.bat")
    
    if not os.path.exists(start_bat):
        print(f"Erro: Não foi possível encontrar o arquivo {start_bat}")
        input("Pressione Enter para sair...")
        return
        
    print("Iniciando o servidor WhisperPlus (pode levar alguns segundos)...")
    
    # Executa o start.bat mantendo o console aberto
    proc = subprocess.Popen([start_bat], cwd=base_dir)
    
    # Aguarda o servidor responder no /health antes de abrir o navegador
    import urllib.request
    print("Aguardando servidor ficar pronto...")
    server_ready = False
    for i in range(120):  # até 2 minutos
        try:
            r = urllib.request.urlopen("http://localhost:8000/health", timeout=2)
            if r.status == 200:
                server_ready = True
                break
        except Exception:
            time.sleep(1)
    
    if server_ready:
        print("Abrindo a interface local no navegador: http://localhost:8000")
        webbrowser.open("http://localhost:8000")
    else:
        print("Servidor demorou mais de 2 minutos para iniciar.")
        print("Tente abrir manualmente: http://localhost:8000")
    
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()

if __name__ == "__main__":
    main()

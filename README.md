# WhisperPlus

O **WhisperPlus** é uma versão customizada e focada em produtividade do [WhisperLiveKit](https://github.com/QuentinFuxa/WhisperLiveKit). Ele foi adaptado para rodar localmente no Windows de forma simplificada, fornecendo transcrição ultra-rápida (com suporte a GPU) em tempo real, especificamente otimizada para a língua portuguesa.

## Principais Recursos e Modificações

*   **Exportação em Tempo Real `.txt`**: O servidor grava continuamente o estado completo da transcrição em `transcription_live.txt` (não apenas logs no console).
*   **Ajustes de Interação Frontend**: Suporte ao envio de `initial_prompt` (para guiar o modelo) e `word_replacements` (correção em tempo real de termos específicos).
*   **Modo Folder-Watch (Offline)**: Processamento em lote colocando arquivos de áudio/vídeo na pasta `input/`, com as transcrições salvas automaticamente na pasta `output/`.
*   **Launcher Local**: Ferramenta `WhisperPlus.exe` que inicializa o servidor FastAPI e abre automaticamente a interface no navegador.
*   **Foco Local em Português**: Configurado nativamente para focar na detecção e compreensão do idioma português (`pt`).

---

## 🚀 Como Iniciar

### Pré-requisitos
1.  **Python 3.11** ou superior
2.  **FFmpeg**: Necessário para decodificar streams de áudio. Garanta que o comando `ffmpeg` esteja no seu `PATH` do Windows.
3.  *(Opcional, mas Recomendado)* **NVIDIA GPU + CUDA**: Placa de vídeo Nvidia moderna para transcrição em tempo real sem atrasos.

### Instalação

1.  Clone o repositório:
    ```bash
    git clone https://github.com/leonmachado91/WhisperPlus.git
    cd WhisperPlus
    ```
2.  Crie um ambiente virtual e instale as dependências (utilizando `uv` é recomendado por ser mais rápido, mas `pip` também funciona):
    ```bash
    uv venv
    call .venv\Scripts\activate
    uv sync --extra cu129 --extra diarization-diart
    ```
    > _Nota: Se você não tiver GPU, utilize a flag `--extra cpu`._

3.  Login no HuggingFace (Opcional, apenas necessário para **Diarização com Diart/Pyannote**):
    ```bash
    huggingface-cli login
    ```
    *(Você também precisará aceitar os termos de uso dos modelos `pyannote/segmentation-3.0` e `pyannote/embedding` no HuggingFace).*

### Uso Diário

Você pode iniciar o servidor de duas maneiras:

**1. Usando o executável (Mais Fácil)**
Dê um duplo clique no arquivo **`WhisperPlus.exe`**.
Ele abrirá um terminal rodando o servidor em plano de fundo e carregará a interface web no seu navegador padrão (`http://localhost:8000`).

**2. Pelo script base**
```cmd
start.bat
```
*(Abra `http://localhost:8000` no seu navegador manualmente).*

---

## 📂 Modo Folder Watch (Arquivos Offline)

O WhisperPlus não é apenas para gravação ao vivo pelo microfone. Se você possui longas gravações ou vídeos e quer processá-los automaticamente:

1.  Abra a interface web do WhisperPlus.
2.  Desça até a seção "Offline File Transcription (Folder Watch)".
3.  Clique em **Start Folder Watch Mode**.
4.  Jogue qualquer arquivo `.wav`, `.mp3`, `.m4a`, `.mp4` na pasta raiz **`input/`**.
5.  O servidor começará a processá-los um a um e salvará o resultado (junto com timestamps e divisão de oradores, se ativa) na pasta **`output/`**. Os arquivos processados são movidos para a subpasta `input/done/`.

---

## 🛠️ Configurações Avançadas

A partir da Interface Web, você tem acesso aos seguintes parâmetros:
*   **Modelo de Transcrição**: Escolha o tamanho do modelo (ex: `medium`, `large-v3`, `large-v3-turbo`). Modelos maiores oferecem precisão incomparável, mas requerem mais VRAM na GPU.
*   **Identificação de Oradores (Diarização)**: Separa as vozes "Speaker 0", "Speaker 1" etc.
*   **Correção de Nomes**: O Whisper pode errar o nome da sua empresa. Use esta aba para criar regras `"errado:Correto"`.
*   **Prompt de Contexto**: Ensine gírias ou jargões da sua área passando um contexto que ajudará na decodificação, sem forçar regras estritas sobre as palavras.

---

## 📦 Desenvolvedores: Como Gerar um novo `.exe`

Se você modificar o arquivo `launcher.py`, basta compilar um novo executável:

```cmd
build_launcher.bat
```
O novo `WhisperPlus.exe` será gerado dentro da pasta `dist/`. Basta copiá-lo para a raiz e deletar as pastas geradas `build/` e `dist/`.

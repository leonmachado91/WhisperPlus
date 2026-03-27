# WhisperLiveKit — Instalação Local com GPU, Diarização e Exportação .txt em Tempo Real

## Contexto

Instalar o [WhisperLiveKit](https://github.com/QUENTINFUXA/WHISPERLIVEKIT) localmente com suporte a GPU (CUDA), diarização por speaker via modelos HuggingFace (pyannote/Diart), e exportação automática da transcrição para um arquivo `.txt` atualizado em tempo real.

**Ambiente confirmado:**

| Item | Valor |
|------|-------|
| Python | 3.13.7 ✅ (requer >=3.11, <3.14) |
| GPU | NVIDIA RTX 2060 SUPER, 8 GB VRAM |
| Driver NVIDIA | 595.79 (suporta CUDA 12.9) |
| CUDA Target | cu129 |
| Backend Whisper | faster-whisper (padrão do projeto) ✅ |
| Backend Diarização | Diart (Opção B — pip manual) |
| Token HuggingFace | Disponível em `docs/API.md` |
| SO | Windows |

**Caso de uso:** Transcrição de reuniões, podcasts e sessões de RPG com identificação de speakers e exportação em tempo real para consulta pelo Antigravity.

---

## Proposed Changes

### Fase 1 — Ambiente Virtual e Clone

#### Passo 1.1 — Verificar estado do repositório

O diretório `e:\Dev\Whisper Live Kit` já existe. Verificar se já tem o clone ou precisa clonar:

```bash
# Se pasta vazia (só .agent):
git clone https://github.com/QuentinFuxa/WhisperLiveKit.git .

# Se já clonado:
git pull
```

#### Passo 1.2 — Criar venv local

```bash
python -m venv .venv
.venv\Scripts\activate
```

---

### Fase 2 — Instalação de Dependências (pip manual, Opção B)

#### Passo 2.1 — Instalar WhisperLiveKit base

```bash
pip install -e .
```

Isso já instala `faster-whisper>=1.2.0` (backend padrão), `torch`, `torchaudio`, `fastapi`, `uvicorn`, etc.

#### Passo 2.2 — Reinstalar PyTorch com CUDA 12.9

```bash
pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu129
```

#### Passo 2.3 — Reinstalar ctranslate2 com CUDA

```bash
pip uninstall -y ctranslate2
pip install ctranslate2 -f https://opennmt.net/ctranslate2/whl/cu129
```

#### Passo 2.4 — Instalar Diart

```bash
pip install diart
```

#### Passo 2.5 — Instalar sounddevice (captura de microfone)

```bash
pip install sounddevice
```

#### Passo 2.6 — Verificação

```bash
python -c "import torch; print('CUDA:', torch.cuda.is_available(), torch.cuda.get_device_name(0))"
python -c "import ctranslate2; print('CT2 CUDA:', ctranslate2.get_cuda_device_count())"
python -c "import diart; print('diart OK')"
python -c "from whisperlivekit import TranscriptionEngine; print('WLK OK')"
```

---

### Fase 3 — HuggingFace Login + Cache Local

#### Passo 3.1 — Login com token

```bash
huggingface-cli login --token <TOKEN_DO_ARQUIVO>
```

#### Passo 3.2 — Aceitar termos dos modelos (manual, no browser)

- https://huggingface.co/pyannote/segmentation
- https://huggingface.co/pyannote/segmentation-3.0
- https://huggingface.co/pyannote/embedding

#### Passo 3.3 — Configurar cache na pasta do projeto

Definir no `start.bat` e no ambiente:

```bash
set HF_HOME=e:\Dev\Whisper Live Kit\.hf_cache
set HUGGINGFACE_HUB_CACHE=e:\Dev\Whisper Live Kit\.hf_cache
```

---

### Fase 4 — Servidor Web com Exportação .txt em Tempo Real

**Essa é a parte central.** O usuário quer DUAS coisas ao mesmo tempo:

1. **Interface web no navegador** — para visualizar a transcrição ao vivo (UI padrão do WhisperLiveKit)
2. **Arquivo `.txt` atualizado em tempo real** — para o Antigravity consultar a transcrição

**Como funciona:**

O WhisperLiveKit já tem um servidor FastAPI (`basic_server.py`) que serve a página HTML e recebe áudio via WebSocket. Vou criar um **servidor customizado** que herda esse comportamento mas adiciona um hook de escrita no `.txt`:

```
┌─────────────┐    WebSocket     ┌──────────────────────┐
│  Navegador  │ ◄──────────────► │  server_with_export  │
│  (UI live)  │   áudio/texto    │                      │
└─────────────┘                  │  TranscriptionEngine │
                                 │  + Diarization       │
       ┌─────────────────┐       │                      │
       │  transcription   │ ◄─── │  FileExporter hook   │
       │  _live.txt       │      │  (flush a cada linha) │
       └─────────────────┘       └──────────────────────┘
              │                           ▲
              ▼                           │
       ┌─────────────┐            ┌──────────────┐
       │ Antigravity  │            │  Microfone   │
       │ (lê o .txt)  │            │  do usuário  │
       └─────────────┘            └──────────────┘
```

**Fluxo:**
1. O usuário abre `http://localhost:8000` no navegador
2. Clica "Start" — o browser captura áudio do microfone e envia via WebSocket
3. O servidor transcreve com faster-whisper + diarização (Diart)
4. Os resultados vão para o browser (UI) **E** são gravados no `.txt` simultaneamente
5. O `.txt` tem flush imediato — cada linha nova aparece instantaneamente
6. O Antigravity pode ler o `.txt` a qualquer momento para acompanhar a conversa

#### [NEW] [server_with_export.py](file:///e:/Dev/Whisper%20Live%20Kit/server_with_export.py)

Servidor FastAPI customizado baseado no `basic_server.py` do WhisperLiveKit. Diferenças:

- Intercepta cada resultado de transcrição antes de enviar pelo WebSocket
- Grava no arquivo `transcription_live.txt` com formato:
  ```
  [18:05:32] [Speaker 1] Olá, bem-vindos à sessão de hoje.
  [18:05:35] [Speaker 2] Obrigado por participar.
  ```
- Flush imediato (`file.flush()`) — o Antigravity vê cada linha assim que ela é gerada
- Ao iniciar, cria um novo arquivo ou limpa o anterior (configurável)

**Parâmetros CLI do servidor:**
- `--language pt` — idioma da transcrição
- `--model medium` — modelo Whisper (recomendado para 8GB VRAM)
- `--output transcription_live.txt` — arquivo de saída
- `--diarization` — ativa identificação de speakers
- `--diarization-backend diart` — usa Diart

---

### Fase 5 — Script de Início Rápido

#### [NEW] [start.bat](file:///e:/Dev/Whisper%20Live%20Kit/start.bat)

```bat
@echo off
echo === WhisperLiveKit - Transcricao em Tempo Real ===
call .venv\Scripts\activate
set HF_HOME=e:\Dev\Whisper Live Kit\.hf_cache
set HUGGINGFACE_HUB_CACHE=e:\Dev\Whisper Live Kit\.hf_cache
python server_with_export.py --language pt --model medium --diarization --diarization-backend diart --output transcription_live.txt
```

Uso:
1. Dar duplo-clique no `start.bat`
2. Abrir `http://localhost:8000` no navegador
3. Clicar "Start" para começar a transcrever
4. O arquivo `transcription_live.txt` vai sendo atualizado em tempo real

---

## Estrutura Final

```
e:\Dev\Whisper Live Kit\
├── .venv\                          # Ambiente virtual (~3 GB)
├── .hf_cache\                      # Modelos HuggingFace (~2 GB)
├── whisperlivekit\                 # Código fonte do WLK
├── server_with_export.py           # Servidor web + export .txt [NOVO]
├── start.bat                       # Atalho de início [NOVO]
├── transcription_live.txt          # Saída em tempo real (gerado)
├── docs\
│   ├── API.md                      # Token HuggingFace
│   └── PLAN-whisperlivekit-setup.md
└── pyproject.toml
```

---

## Verification Plan

### Teste 1: Dependências e GPU
```bash
.venv\Scripts\activate
python -c "import torch; print('CUDA:', torch.cuda.is_available(), torch.cuda.get_device_name(0))"
python -c "import ctranslate2; print('CT2 CUDA:', ctranslate2.get_cuda_device_count())"
python -c "import diart; print('diart OK')"
python -c "from whisperlivekit import TranscriptionEngine; print('WLK OK')"
```
**Esperado:** Todas prints sem erros, CUDA disponível, CT2 com 1+ device.

### Teste 2: Servidor inicia sem crash
```bash
python server_with_export.py --language pt --model base --diarization --diarization-backend diart
```
**Esperado:** Servidor sobe em `http://localhost:8000` sem erros. Usar `base` no primeiro teste pra download rápido.

### Teste 3: Transcrição via browser + export .txt
1. Abrir `http://localhost:8000` no navegador
2. Clicar "Start" e falar no microfone por ~15 segundos
3. Verificar que a transcrição aparece no browser
4. Abrir `transcription_live.txt` — confirmar que as falas estão gravadas com timestamps e speakers
5. Continuar falando — confirmar que novas linhas aparecem no `.txt` sem precisar reiniciar nada

### Teste 4 (Manual - Usuário)
Abrir o `transcription_live.txt` no VS Code e verificar que ele atualiza ao vivo enquanto se fala no microfone. O Antigravity pode ser instruído a ler esse arquivo para contexto da conversa.

---

## Estimativa de Espaço

| Item | Tamanho |
|------|---------|
| `.venv` (torch CUDA + deps) | ~3 GB |
| Modelo Whisper `medium` | ~1.5 GB |
| Modelos pyannote (diart) | ~500 MB |
| ctranslate2 CUDA | ~200 MB |
| **Total estimado** | **~5-6 GB** |

Tudo em `e:\Dev\Whisper Live Kit\` — basta deletar a pasta pra limpar tudo.

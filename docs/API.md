# API Referência - WhisperPlus

O WhisperPlus expõe uma API WebSocket modificada para transcrição em tempo real (baseada no código original FastAPI do WhisperLiveKit).

### Servidor Principal
- A API hospeda um endpoint de WebSocket em: `ws://localhost:8000/asr`
- Health check API: `http://localhost:8000/health`

---

## 1. Conexão WebSocket e Parâmetros

A conexão inicial pode aceitar parâmetros via **Query String** (via URL). É aqui que o WhisperPlus injeta recursos dinâmicos.

| Query Parameter | Descrição | Exemplo |
| --- | --- | --- |
| `model` | Tamanho do modelo Whisper a ser carregado (sobrescreve o default). | `large-v3-turbo` |
| `diarization` | Habilita identificação de oradores (true/false) | `true` |
| `initial_prompt` | Texto opcional fornecido antes da transcrição começar. Direciona o modelo para entender contexto, formatação ou presença de jargões locais. | `Este é um podcast de tecnologia.` |
| `word_replacements` | Pares de palavras submetidos no formato `erro:Acerto,erro2:Acerto2` aplicados através de Regex pela classe AudioProcessor no momento em que os tokens são gerados. Útil para forçar o acerto de nomes próprios. | `Uisp:Whisper,laiv:Live` |
| `op_mode` | Modo de operação do socket atual. Pode ser `live` (padrão, para captura de mic do browser) ou `folder` (ativa a monitoração do diretório `/input` local do servidor). | `folder` |
| `output_file` | Define o nome do arquivo texto que salvará a transcrição de forma agnóstica na raíz. | `transcription_live.txt` |
| `mode` | Modo do diff protocol para atualizações parciais do frontend. Valores possíveis: `full`, `diff` | `full` |

### Exemplo de String de Conexão Frontend:
```javascript
const wsUrl = `ws://localhost:8000/asr?model=medium&diarization=true&op_mode=live&initial_prompt=Reunião&word_replacements=erru:acerto`;
websocket = new WebSocket(wsUrl);
```

---

## 2. Eventos Cliente → Servidor (Envio de Áudio)

Após a conexão ser estabelecida, o servidor espera chunks binários de áudio.

Na versão frontend, utilizamos a _Web Audio API_ ou o _PCM Worklet_ para amostrar o áudio e enviá-lo pelo socket como ArrayBuffers.

```javascript
// Exemplo JS de envio:
websocket.send(audioDataChunk); 
```

O WhisperPlus acumula esse áudio (seja de microfone ou do ffmpeg que processa arquivos da pasta `input`) e aplica detecção de voz antes da decodificação, evitando cargas de GPU desnecessárias por ruído silencioso.

---

## 3. Eventos Servidor → Cliente (Retornos JSON)

À medida que o servidor traduz o áudio, ele devolve JSON com a transcrição completa montada na tela.

O JSON contém uma propriedade `"lines"` com listas de segmentos definidos, além de texto em buffer temporário `"buffer_transcription"`:

```json
{
  "lines": [
    {
      "start": "0.0",
      "end": "2.5",
      "text": " Olá, bem vindo ao sistema",
      "speaker": 0
    }
  ],
  "buffer_transcription": " de transcrição em tem"
}
```

O frontend customizado (`live_transcription.js`) é responsável por atualizar continuamente a tela usando essas informações, enquanto o backend simultaneamente as exporta formatadas para o `.txt` em disco.

"""
WhisperLiveKit — Servidor com exportação .txt em tempo real.

Baseado no basic_server.py do WhisperLiveKit, adiciona gravação
automática da transcrição em um arquivo .txt com flush imediato.

Uso:
    python server_with_export.py [--model medium] [--diarization --diarization-backend diart]

A linguagem está fixada em pt (português).
"""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from whisperlivekit import AudioProcessor, TranscriptionEngine, get_inline_ui_html, parse_args

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.getLogger().setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# --------------------------------------------------------------------------- #
# Parse CLI args (reuses WhisperLiveKit's argparse)
# --------------------------------------------------------------------------- #
config = parse_args()

# Force language to Portuguese
config.language = "pt"
config.lan = "pt"

# Extra arg: output file (env var or default)
OUTPUT_FILE = os.environ.get("WLK_OUTPUT_FILE", "transcription_live.txt")

transcription_engine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global transcription_engine
    transcription_engine = TranscriptionEngine(config=config)
    logger.info("TranscriptionEngine initialized. Model: %s | Language: %s | Diarization: %s",
                getattr(config, 'model_size', 'default'),
                getattr(config, 'lan', 'pt'),
                getattr(config, 'diarization', False))
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------- #
# File exporter — overwrites .txt with current full transcription state
# --------------------------------------------------------------------------- #

class TranscriptionFileExporter:
    """Writes the current transcription state to a .txt file on every update.

    Uses an overwrite strategy: the file always contains the complete,
    up-to-date transcription. This avoids issues with partial/rewritten
    lines from WhisperLiveKit's local agreement algorithm.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.session_start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.last_content = ""

        # Create / clear the file at start
        with open(self.filepath, "w", encoding="utf-8") as f:
            f.write(f"# Transcription started at {self.session_start}\n\n")
        logger.info("Transcription file created: %s", os.path.abspath(self.filepath))

    def process_response(self, response) -> None:
        """Write the full current transcription state to the file.

        WhisperLiveKit rebuilds the entire lines list on every update
        (local agreement can modify older lines). We overwrite the file
        with the complete current state to keep it accurate.
        """
        data = response.to_dict()
        lines = data.get("lines", [])
        buffer_text = data.get("buffer_transcription", "")
        buffer_diar = data.get("buffer_diarization", "")

        # Build the full text content
        text_lines = []
        for line in lines:
            text = line.get("text", "")
            speaker = line.get("speaker", -1)
            start = line.get("start", "")
            end = line.get("end", "")

            # Skip silence segments (speaker == -2) and empty text
            if speaker == -2 or not text or not text.strip():
                continue

            speaker_label = f"Speaker {speaker}" if speaker >= 0 else "Speaker ?"
            text_lines.append(f"[{start} → {end}] [{speaker_label}] {text.strip()}")

        # Add buffer (partial/unconfirmed text being processed)
        if buffer_text and buffer_text.strip():
            text_lines.append(f"[...processing...] {buffer_text.strip()}")

        content = "\n".join(text_lines)

        # Only write if content changed
        if content == self.last_content:
            return

        self.last_content = content

        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                f.write(f"# Transcription - {self.session_start}\n\n")
                f.write(content)
                if content:
                    f.write("\n")
                f.flush()
        except Exception as e:
            logger.error("Failed to write transcription file: %s", e)


import copy

# --------------------------------------------------------------------------- #
# WebSocket handler (same as basic_server + file export hook)
# --------------------------------------------------------------------------- #

async def handle_websocket_results(websocket, results_generator, exporter, diff_tracker=None):
    """Consumes results and sends them via WebSocket + writes to .txt file."""
    try:
        async for response in results_generator:
            # 1) Send to browser (original behavior)
            try:
                if diff_tracker is not None:
                    await websocket.send_json(diff_tracker.to_message(response))
                else:
                    await websocket.send_json(response.to_dict())
            except (WebSocketDisconnect, RuntimeError):
                logger.info("WebSocket closed while sending data.")
                break

            # 2) Write current state to .txt file
            exporter.process_response(response)

        logger.info("Results generator finished. Sending 'ready_to_stop' to client.")
        try:
            await websocket.send_json({"type": "ready_to_stop"})
        except (WebSocketDisconnect, RuntimeError):
            pass
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected while handling results.")
    except asyncio.CancelledError:
        logger.info("Results handler cancelled.")
    except Exception as e:
        logger.exception(f"Error in WebSocket results handler: {e}")


# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #

@app.get("/")
async def get():
    return HTMLResponse(get_inline_ui_html())


@app.get("/health")
async def health():
    global transcription_engine
    return {
        "status": "ok",
        "ready": transcription_engine is not None,
        "output_file": os.path.abspath(OUTPUT_FILE),
        "language": "pt",
    }


@app.websocket("/asr")
async def websocket_endpoint(websocket: WebSocket):
    global transcription_engine

    # Force Portuguese regardless of what the client sends
    session_language = "pt"
    mode = websocket.query_params.get("mode", "full")
    
    # Extract custom client settings
    client_model = websocket.query_params.get("model", getattr(config, 'model_size', 'medium'))
    client_diarization = websocket.query_params.get("diarization", "false").lower() == "true"
    client_output_file = websocket.query_params.get("output_file", OUTPUT_FILE)
    client_initial_prompt = websocket.query_params.get("initial_prompt", "")

    current_model = getattr(transcription_engine.config, 'model_size', None)
    current_diarization = getattr(transcription_engine.config, 'diarization', False)

    if current_model != client_model or current_diarization != client_diarization:
        logger.info(f"Reloading TranscriptionEngine: model={client_model}, diarization={client_diarization}")
        TranscriptionEngine.reset()
        new_config = copy.copy(config)
        new_config.model_size = client_model
        new_config.model_path = client_model # Often same as model_size for WhisperLiveKit
        new_config.diarization = client_diarization
        transcription_engine = TranscriptionEngine(config=new_config)

    audio_processor = AudioProcessor(
        transcription_engine=transcription_engine,
        language=session_language,
    )
    
    if client_initial_prompt and hasattr(audio_processor, 'transcription') and audio_processor.transcription:
        orig_prompt_method = audio_processor.transcription.prompt
        def custom_prompt():
            prompt_text, context_text = orig_prompt_method()
            new_prompt = f"{client_initial_prompt} {prompt_text}".strip()
            return new_prompt, context_text
        audio_processor.transcription.prompt = custom_prompt

    await websocket.accept()
    logger.info(f"WebSocket connection opened. language=pt, model={client_model}, diarization={client_diarization}")

    diff_tracker = None
    if mode == "diff":
        from whisperlivekit.diff_protocol import DiffTracker
        diff_tracker = DiffTracker()

    # Create a per-session file exporter
    exporter = TranscriptionFileExporter(client_output_file)

    try:
        await websocket.send_json({"type": "config", "useAudioWorklet": bool(config.pcm_input), "mode": mode})
    except Exception as e:
        logger.warning(f"Failed to send config to client: {e}")

    if mode == "folder":
        # =====================================================================
        # Folder Watch Mode
        # =====================================================================
        from pathlib import Path
        input_dir = Path("input")
        output_dir = Path("output")
        input_dir.mkdir(exist_ok=True)
        output_dir.mkdir(exist_ok=True)
        
        supported_extensions = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".mp4", ".mkv", ".webm"}
        try:
            await websocket.send_json({"type": "status", "message": "Watching 'input/' folder for new audio/video files..."})
        except Exception:
            return
            
        try:
            while True:
                files_to_process = sorted([f for f in input_dir.iterdir() if f.is_file() and f.suffix.lower() in supported_extensions])
                
                if not files_to_process:
                    # Check if client disconnected while we are idle
                    try:
                        msg = await asyncio.wait_for(websocket.receive(), timeout=1.0)
                        if msg["type"] == "websocket.disconnect":
                            break
                    except asyncio.TimeoutError:
                        continue
                    except Exception:
                        break
                        
                for file_path in files_to_process:
                    logger.info(f"Processing offline file: {file_path.name}")
                    try:
                        await websocket.send_json({"type": "status", "message": f"Processing {file_path.name}..."})
                    except Exception:
                        raise WebSocketDisconnect()
                        
                    # Create new audio_processor for this file
                    file_processor = AudioProcessor(
                        transcription_engine=transcription_engine,
                        language=session_language,
                    )
                    
                    if client_initial_prompt and hasattr(file_processor, 'transcription') and file_processor.transcription:
                        orig_prompt_method = file_processor.transcription.prompt
                        def file_custom_prompt(orig=orig_prompt_method):
                            prompt_text, context_text = orig()
                            new_prompt = f"{client_initial_prompt} {prompt_text}".strip()
                            return new_prompt, context_text
                        file_processor.transcription.prompt = file_custom_prompt

                    file_output_path = output_dir / f"{file_path.stem}.txt"
                    file_exporter = TranscriptionFileExporter(str(file_output_path))
                    
                    file_results_generator = await file_processor.create_tasks()
                    file_ws_task = asyncio.create_task(
                        handle_websocket_results(websocket, file_results_generator, file_exporter, None)
                    )
                    
                    # Convert audio and stream to processor
                    command = [
                        "ffmpeg", "-i", str(file_path),
                        "-f", "s16le", "-ac", "1", "-ar", "16000", "pipe:1"
                    ]
                    import subprocess
                    process = await asyncio.create_subprocess_exec(
                        *command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.DEVNULL
                    )
                    
                    chunk_size = 32000 # ~1 second
                    while True:
                        chunk = await process.stdout.read(chunk_size)
                        if not chunk:
                            break
                        await file_processor.process_audio(chunk)
                        await asyncio.sleep(0.005) # Yield control
                        
                    await process.wait()
                    
                    # Cleanup processor for this file
                    file_processor.is_stopping = True
                    await asyncio.sleep(0.5)
                    if not file_ws_task.done():
                        file_ws_task.cancel()
                        try:
                            await file_ws_task
                        except asyncio.CancelledError:
                            pass
                    await file_processor.cleanup()
                    
                    # Move to done
                    done_dir = input_dir / "done"
                    done_dir.mkdir(exist_ok=True)
                    try:
                        file_path.rename(done_dir / file_path.name)
                    except Exception as e:
                        logger.error(f"Failed to move {file_path.name} to done: {e}")
                        
                    try:
                        await websocket.send_json({"type": "status", "message": f"Finished {file_path.name}"})
                    except Exception:
                        raise WebSocketDisconnect()
                        
        except WebSocketDisconnect:
            logger.info("Folder Watch websocket disconnected by client.")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in folder watch mode: {e}", exc_info=True)
        finally:
            logger.info("Folder Watch mode exiting.")
            return

    # =====================================================================
    # Live Mode (Microphone / Real-time)
    # =====================================================================
    results_generator = await audio_processor.create_tasks()
    websocket_task = asyncio.create_task(
        handle_websocket_results(websocket, results_generator, exporter, diff_tracker)
    )

    try:
        while True:
            message = await websocket.receive_bytes()
            await audio_processor.process_audio(message)
    except KeyError as e:
        if 'bytes' in str(e):
            logger.warning("Client closed the connection.")
        else:
            logger.error(f"Unexpected KeyError: {e}", exc_info=True)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected by client.")
    except Exception as e:
        logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
    finally:
        logger.info("Cleaning up WebSocket endpoint...")

        # Signal the audio processor to stop
        audio_processor.is_stopping = True

        # Give results_formatter a moment to detect stopping state
        await asyncio.sleep(0.5)

        if not websocket_task.done():
            websocket_task.cancel()
        try:
            await asyncio.wait_for(websocket_task, timeout=5.0)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass
        except Exception as e:
            logger.warning(f"Exception while awaiting cleanup: {e}")

        await audio_processor.cleanup()
        logger.info("Session ended. Transcription saved to: %s", os.path.abspath(client_output_file))


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main():
    import uvicorn

    print("\n" + "=" * 60)
    print("  WhisperLiveKit — Server with Real-time .txt Export")
    print("=" * 60)
    print(f"  Model:        {getattr(config, 'model_size', 'default')}")
    print(f"  Language:     pt (fixed)")
    print(f"  Diarization:  {getattr(config, 'diarization', False)}")
    print(f"  Output file:  {os.path.abspath(OUTPUT_FILE)}")
    print(f"  Server:       http://{config.host}:{config.port}")
    print("=" * 60 + "\n")

    uvicorn.run(
        "server_with_export:app",
        host=config.host,
        port=config.port,
        reload=False,
        log_level="info",
        lifespan="on",
    )


if __name__ == "__main__":
    main()

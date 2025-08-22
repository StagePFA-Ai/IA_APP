# meetings/consumers.py
import io
import json
import re
from typing import List

import numpy as np
from channels.generic.websocket import AsyncWebsocketConsumer
from faster_whisper import WhisperModel
from pydub import AudioSegment
from transformers import pipeline

# ---------- Modèles chargés une seule fois ----------
class _Models:
    # adapte: "small" / "medium" / "large-v3", device="cuda" si GPU
    asr = WhisperModel("medium", device="cpu", compute_type="int8")
    summarizers = {
        "fr": pipeline("summarization", model="csebuetnlp/mT5_multilingual_XLSum"),
        "en": pipeline("summarization", model="facebook/bart-large-cnn"),
        "ar": pipeline("summarization", model="csebuetnlp/mT5_multilingual_XLSum"),
    }

def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def _chunk(text: str, n=1800) -> List[str]:
    parts, i = [], 0
    while i < len(text):
        parts.append(text[i:i+n])
        i += n
    return parts

class TranscriptionConsumer(AsyncWebsocketConsumer):
    """
    Reçoit des segments webm/opus depuis le navigateur (MediaRecorder),
    décode en PCM 16k mono -> faster-whisper -> renvoie le texte.
    """
    # seuil (~1.5s à 2s) avant un passage ASR
    BUFFER_MIN_BYTES = 60000

    async def connect(self):
        await self.accept()
        self.recording = False
        self.audio_buffer = bytearray()
        self.collected_text: List[str] = []

    async def disconnect(self, code):
        self.recording = False

    async def receive(self, text_data=None, bytes_data=None):
        # --- audio binaire ---
        if bytes_data:
            if self.recording:
                self.audio_buffer.extend(bytes_data)
                if len(self.audio_buffer) >= self.BUFFER_MIN_BYTES:
                    await self._flush_asr()
            return

        # --- messages texte ---
        if text_data:
            msg = json.loads(text_data)
            action = msg.get("action")

            if action == "start":
                self.recording = True
                await self.send(json.dumps({"type": "info", "message": "🎤 Transcription démarrée"}))

            elif action == "stop":
                self.recording = False
                if self.audio_buffer:
                    await self._flush_asr()
                await self.send(json.dumps({"type": "info", "message": "⏹️ Transcription arrêtée"}))

            elif action == "summarize":
                lang = (msg.get("lang") or "fr").lower()
                full = _clean(" ".join(self.collected_text))
                if not full:
                    return await self.send(json.dumps({"type": "summary", "message": "⚠️ Aucun texte à résumer"}))
                summarizer = _Models.summarizers.get(lang, _Models.summarizers["fr"])
                pieces = []
                for ch in _chunk(full, 1800):
                    out = summarizer(ch, max_length=220, min_length=60, do_sample=False)
                    pieces.append(out[0]["summary_text"])
                summary = _clean(" ".join(pieces))
                await self.send(json.dumps({"type": "summary", "message": summary}))

    async def _flush_asr(self):
        try:
            # webm/opus -> PCM 16k mono (ffmpeg requis sur la machine)
            audio = AudioSegment.from_file(io.BytesIO(self.audio_buffer), format="webm")
            audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
            samples = np.array(audio.get_array_of_samples()).astype(np.float32) / 32768.0

            segments, _ = _Models.asr.transcribe(
                samples, language="fr", vad_filter=True, beam_size=1
            )
            text = _clean(" ".join(seg.text for seg in segments))
            if text:
                self.collected_text.append(text)
                await self.send(json.dumps({"type": "transcription", "message": text}))
        except Exception as e:
            await self.send(json.dumps({"type": "info", "message": f"Erreur transcription: {e}"}))
        finally:
            self.audio_buffer.clear()

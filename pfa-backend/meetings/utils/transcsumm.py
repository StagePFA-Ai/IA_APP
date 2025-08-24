# meetings/consumers.py
import json, re
from typing import List
import numpy as np
from channels.generic.websocket import AsyncWebsocketConsumer
from faster_whisper import WhisperModel
from transformers import pipeline

def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()

def _chunk(text: str, n=1800) -> List[str]:
    return [text[i:i+n] for i in range(0, len(text), n)]

class _Models:
    asr = WhisperModel("small", device="cpu", compute_type="int8")  # commence petit pour tester
    summarizers = {
        "fr": pipeline("summarization", model="csebuetnlp/mT5_multilingual_XLSum"),
        "en": pipeline("summarization", model="facebook/bart-large-cnn"),
        "ar": pipeline("summarization", model="csebuetnlp/mT5_multilingual_XLSum"),
    }

class TranscriptionConsumer(AsyncWebsocketConsumer):
    """
    Reçoit des buffers Float32Array (PCM mono 16 kHz) depuis le navigateur.
    Accumule, puis lance Whisper sur la partie nouvelle avec un léger recouvrement.
    """
    SR = 16000
    MIN_NEW_SEC = 2.0
    OVERLAP_SEC = 0.5
    MIN_NEW_SAMPLES = int(SR * MIN_NEW_SEC)
    OVERLAP_SAMPLES = int(SR * OVERLAP_SEC)

    async def connect(self):
        await self.accept()
        self.recording = False
        self.lang = "fr"
        self.pcm = np.empty(0, dtype=np.float32)   # tout le flux PCM
        self.processed = 0                         # samples déjà passés à l'ASR
        self.collected_text: List[str] = []

    async def disconnect(self, code):
        self.recording = False

    async def receive(self, text_data=None, bytes_data=None):
        # --- audio binaire (Float32) ---
        if bytes_data and self.recording:
            try:
                chunk = np.frombuffer(bytes_data, dtype=np.float32)
                if chunk.size == 0:
                    return
                # concatène au tampon global
                self.pcm = np.concatenate([self.pcm, chunk])

                # si assez de nouveauté, lance ASR
                await self._flush_if_enough()
            except Exception as e:
                await self._info(f"Erreur PCM: {e}")
            return

        # --- messages texte ---
        if text_data:
            msg = json.loads(text_data)
            action = msg.get("action")

            if action == "start":
                self.recording = True
                self.lang = (msg.get("lang") or "fr").lower()
                self.pcm = np.empty(0, dtype=np.float32)
                self.processed = 0
                self.collected_text.clear()
                await self._info("🎤 Transcription démarrée")

            elif action == "stop":
                self.recording = False
                try:
                    await self._flush(final=True)
                except Exception as e:
                    await self._info(f"Erreur flush final: {e}")
                await self._info("⏹️ Transcription arrêtée")

            elif action == "summarize":
                full = _clean(" ".join(self.collected_text))
                if not full:
                    return await self.send(json.dumps({"type": "summary", "message": "⚠️ Aucun texte à résumer"}))
                summarizer = _Models.summarizers.get(self.lang, _Models.summarizers["fr"])
                parts = []
                for ch in _chunk(full, 1800):
                    out = summarizer(ch, max_length=220, min_length=60, do_sample=False)
                    parts.append(out[0]["summary_text"])
                await self.send(json.dumps({"type": "summary", "message": _clean(" ".join(parts))}))

    async def _flush_if_enough(self):
        new = self.pcm.size - self.processed
        if new >= self.MIN_NEW_SAMPLES:
            await self._run_asr()

    async def _flush(self, final=False):
        if self.pcm.size > self.processed:
            await self._run_asr(final=final)

    async def _run_asr(self, final=False):
        start = max(0, self.processed - self.OVERLAP_SAMPLES)
        chunk = self.pcm[start:]
        if chunk.size <= 0:
            return

        segments, _ = _Models.asr.transcribe(
            chunk, language=self.lang, vad_filter=True, beam_size=1
        )
        text = _clean(" ".join(s.text for s in segments))
        if text:
            self.collected_text.append(text)
            await self.send(json.dumps({"type": "transcription", "message": text}))

        # on garde un petit tail pour éviter de couper un mot
        self.processed = max(self.processed, self.pcm.size - self.OVERLAP_SAMPLES)
        if final:
            self.processed = self.pcm.size

    async def _info(self, m: str):
        await self.send(json.dumps({"type": "info", "message": m}))

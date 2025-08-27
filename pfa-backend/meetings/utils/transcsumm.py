# meetings/consumers.py
import json, re
from typing import List
import numpy as np
from channels.generic.websocket import AsyncWebsocketConsumer
from faster_whisper import WhisperModel
from transformers import pipeline

def _clean(s: str) -> str:
    """Nettoie le texte en supprimant les espaces multiples et en trimant"""
    return re.sub(r"\s+", " ", s or "").strip()

def _chunk(text: str, n=1800) -> List[str]:
    """Découpe un texte en morceaux de taille maximale n caractères"""
    return [text[i:i+n] for i in range(0, len(text), n)]

class _Models:
    """Classe contenant les modèles de ML chargés en mémoire (singleton implicite)"""
    # Modèle de reconnaissance vocale (ASR) - Whisper
    asr = WhisperModel("small", device="cpu", compute_type="int8")  # commence petit pour tester
    
    # Modèles de résumé pour différentes langues
    summarizers = {
        "fr": pipeline("summarization", model="csebuetnlp/mT5_multilingual_XLSum"),
        "en": pipeline("summarization", model="facebook/bart-large-cnn"),
        "ar": pipeline("summarization", model="csebuetnlp/mT5_multilingual_XLSum"),
    }

class TranscriptionConsumer(AsyncWebsocketConsumer):
    """
    Consumer WebSocket pour la transcription en temps réel.
    
    Reçoit des buffers Float32Array (PCM mono 16 kHz) depuis le navigateur.
    Accumule, puis lance Whisper sur la partie nouvelle avec un léger recouvrement.
    """
    
    # Constantes pour le traitement audio
    SR = 16000  # Sample rate (16 kHz)
    MIN_NEW_SEC = 2.0  # Seuil minimal de secondes avant traitement
    OVERLAP_SEC = 0.5  # Recouvrement entre les segments pour éviter les coupures
    MIN_NEW_SAMPLES = int(SR * MIN_NEW_SEC)  # Seuil en samples
    OVERLAP_SAMPLES = int(SR * OVERLAP_SEC)  # Recouvrement en samples

    async def connect(self):
        """Établit la connexion WebSocket et initialise les variables d'état"""
        await self.accept()
        self.recording = False  # État d'enregistrement
        self.lang = "fr"  # Langue par défaut
        self.pcm = np.empty(0, dtype=np.float32)   # Tampon pour tout le flux PCM
        self.processed = 0  # Nombre de samples déjà traités par l'ASR
        self.collected_text: List[str] = []  # Texte transcrit accumulé

    async def disconnect(self, code):
        """Gère la déconnexion WebSocket"""
        self.recording = False

    async def receive(self, text_data=None, bytes_data=None):
        """
        Reçoit les données du client WebSocket.
        
        Deux types de données :
        - bytes_data : données audio binaires (Float32)
        - text_data : messages de contrôle JSON
        """
        # --- Traitement des données audio binaires (Float32) ---
        if bytes_data and self.recording:
            try:
                # Conversion des données binaires en tableau numpy
                chunk = np.frombuffer(bytes_data, dtype=np.float32)
                if chunk.size == 0:
                    return
                
                # Concaténation au tampon global
                self.pcm = np.concatenate([self.pcm, chunk])

                # Vérification s'il y a assez de nouvelles données pour traitement
                await self._flush_if_enough()
            except Exception as e:
                await self._info(f"Erreur PCM: {e}")
            return

        # --- Traitement des messages texte (JSON) ---
        if text_data:
            msg = json.loads(text_data)
            action = msg.get("action")

            # Démarrage de la transcription
            if action == "start":
                self.recording = True
                self.lang = (msg.get("lang") or "fr").lower()
                self.pcm = np.empty(0, dtype=np.float32)
                self.processed = 0
                self.collected_text.clear()
                await self._info("🎤 Transcription démarrée")

            # Arrêt de la transcription
            elif action == "stop":
                self.recording = False
                try:
                    # Traitement final des données restantes
                    await self._flush(final=True)
                except Exception as e:
                    await self._info(f"Erreur flush final: {e}")
                await self._info("⏹️ Transcription arrêtée")

            # Demande de résumé du texte transcrit
            elif action == "summarize":
                # Concaténation et nettoyage de tout le texte transcrit
                full = _clean(" ".join(self.collected_text))
                if not full:
                    return await self.send(json.dumps({"type": "summary", "message": "⚠️ Aucun texte à résumer"}))
                
                # Sélection du modèle de résumé approprié
                summarizer = _Models.summarizers.get(self.lang, _Models.summarizers["fr"])
                parts = []
                
                # Découpage et résumé par morceaux (limitations de contexte des modèles)
                for ch in _chunk(full, 1800):
                    out = summarizer(ch, max_length=220, min_length=60, do_sample=False)
                    parts.append(out[0]["summary_text"])
                
                # Envoi du résumé final
                await self.send(json.dumps({"type": "summary", "message": _clean(" ".join(parts))}))

    async def _flush_if_enough(self):
        """Vérifie s'il y a assez de nouvelles données pour lancer la transcription"""
        new = self.pcm.size - self.processed
        if new >= self.MIN_NEW_SAMPLES:
            await self._run_asr()

    async def _flush(self, final=False):
        """Force le traitement des données audio restantes"""
        if self.pcm.size > self.processed:
            await self._run_asr(final=final)

    async def _run_asr(self, final=False):
        """
        Exécute la reconnaissance vocale sur les données audio accumulées
        
        Utilise un recouvrement pour éviter de couper les mots en fin de segment
        """
        # Calcul du segment à traiter avec recouvrement
        start = max(0, self.processed - self.OVERLAP_SAMPLES)
        chunk = self.pcm[start:]
        
        if chunk.size <= 0:
            return

        # Transcription avec Whisper
        segments, _ = _Models.asr.transcribe(
            chunk, language=self.lang, vad_filter=True, beam_size=1
        )
        
        # Extraction et nettoyage du texte
        text = _clean(" ".join(s.text for s in segments))
        
        if text:
            # Ajout au texte accumulé et envoi au client
            self.collected_text.append(text)
            await self.send(json.dumps({"type": "transcription", "message": text}))

        # Mise à jour du pointeur de traitement avec recouvrement
        self.processed = max(self.processed, self.pcm.size - self.OVERLAP_SAMPLES)
        
        # En mode final, traite tout le reste
        if final:
            self.processed = self.pcm.size

    async def _info(self, m: str):
        """Envoie un message d'information au client"""
        await self.send(json.dumps({"type": "info", "message": m}))
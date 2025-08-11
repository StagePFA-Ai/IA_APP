import threading
import logging
from .models import Meeting
from .utils.transcribe_summarize import transcribe_audio, summarize_text

def _process_meeting(meeting_id):
    try:
        meeting = Meeting.objects.get(id=meeting_id)
        meeting.status = "processing"
        meeting.save()

        if not meeting.audio:
            meeting.status = "failed"
            meeting.save()
            return

        audio_path = meeting.audio.path

        # Transcription
        transcription = transcribe_audio(audio_path, language="fr")  # ou None pour auto-detect
        meeting.transcription = transcription

        # Summarization (attention aux textes très longs -> chunk si besoin)
        try:
            summary = summarize_text(transcription, max_length=150, min_length=30)
        except Exception:
            # fallback: simple extractive summary (first N chars)
            summary = (transcription[:500] + "...") if transcription else ""

        meeting.summary = summary
        meeting.status = "done"
        meeting.save()
    except Exception as e:
        logging.exception("Error in processing meeting")
        try:
            m = Meeting.objects.get(id=meeting_id)
            m.status = "failed"
            m.save()
        except Exception:
            pass

def process_meeting_async(meeting_id):
    thread = threading.Thread(target=_process_meeting, args=(meeting_id,), daemon=True)
    thread.start()
    return thread

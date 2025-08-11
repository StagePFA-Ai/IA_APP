import os
from pathlib import Path
import logging

# lazy load heavy models to avoid slow import at startup if not used
whisper_model = None
summarizer = None

def get_whisper_model(device="cpu", compute_type="int8", model_name="small"):
    global whisper_model
    if whisper_model is None:
        from faster_whisper import WhisperModel
        whisper_model = WhisperModel(model_name, device=device, compute_type=compute_type)
    return whisper_model

def get_summarizer(device=-1, model_name="csebuetnlp/mT5_multilingual_XLSum"):
    global summarizer
    if summarizer is None:
        from transformers import pipeline
        summarizer = pipeline("summarization", model=model_name, device=device)
    return summarizer

def transcribe_audio(file_path, language=None):
    """
    file_path: path to audio file
    returns: full transcription text
    """
    try:
        model = get_whisper_model()
        segments, info = model.transcribe(str(file_path), language=language, vad_filter=True)
        text = " ".join([seg.text.strip() for seg in segments if seg.text.strip()])
        return text
    except Exception as e:
        logging.exception("Transcription failed")
        raise

def summarize_text(text, max_length=128, min_length=20):
    try:
        summarizer = get_summarizer()
        # transformers summarizer expects shorter sequences; may need chunking for long texts
        out = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
        return out[0]["summary_text"]
    except Exception as e:
        logging.exception("Summarization failed")
        raise

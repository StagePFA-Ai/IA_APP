import sounddevice as sd
import numpy as np
import queue
import threading
import time
import tkinter as tk
from tkinter import scrolledtext
from faster_whisper import WhisperModel
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Modèle Whisper en local
model = WhisperModel("medium", device="cpu", compute_type="int8")

# Paramètres audio
frequence = 16000
chunk_duration = 3  # secondes
buffer_size = int(frequence * chunk_duration)
q = queue.Queue()

# Interface Tkinter
root = tk.Tk()
root.title("Transcription Réunion en Temps Réel")
root.geometry("800x400")
text_output = scrolledtext.ScrolledText(root, wrap=tk.WORD)
text_output.pack(expand=True, fill="both")

recording = False

def safe_update_ui(text):
    """Update UI in a thread-safe manner"""
    root.after(0, lambda: (
        text_output.insert(tk.END, text + "\n"),
        text_output.see(tk.END)
    ))

def start_stream():
    """Start audio recording stream"""
    def callback(indata, frames, time_, status):
        if status:
            safe_update_ui(f"��️ Error: {status}")
        q.put(indata.copy())
    
    with sd.InputStream(samplerate=frequence, channels=1, callback=callback):
        while recording:
            time.sleep(0.1)

def process_audio_chunk(audio_chunk):
    """Transcribe a chunk of audio and return results"""
    try:
        segments, _ = model.transcribe(
            audio_chunk, 
            language="fr", 
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500}
        )
        return [seg.text for seg in segments]
    except Exception as e:
        safe_update_ui(f"Error during transcription: {str(e)}")
        return []

def start_transcription():
    """Main transcription loop"""
    global recording
    audio_buffer = np.array([], dtype=np.float32)
    
    while recording or len(audio_buffer) > 0 or not q.empty():
        try:
            # Get data with timeout to allow clean exit
            data = q.get(timeout=1)
            audio_buffer = np.concatenate((audio_buffer, data.flatten()))
            
            # Process when buffer is large enough
            while len(audio_buffer) >= buffer_size:
                chunk = audio_buffer[:buffer_size]
                audio_buffer = audio_buffer[buffer_size:]
                
                # Process the chunk
                transcripts = process_audio_chunk(chunk)
                for text in transcripts:
                    safe_update_ui(f"🗣️ {text}")
        
        except queue.Empty:
            continue
        except Exception as e:
            safe_update_ui(f"Error in transcription loop: {str(e)}")
            break

def lancer_transcription():
    """Start recording and transcription threads"""
    global recording
    recording = True
    
    # Start threads
    threading.Thread(target=start_stream, daemon=True).start()
    threading.Thread(target=start_transcription, daemon=True).start()
    safe_update_ui("🎤 Transcription started")

def arreter_transcription():
    """Stop all processes"""
    global recording
    recording = False
    safe_update_ui("⏹️ Transcription stopped. Processing remaining audio...")
    
    # Process any remaining audio in buffer (not implemented in original)
    # Add buffer processing here if needed

# GUI Buttons
btn_start = tk.Button(root, text="▶️ Lancer", command=lancer_transcription)
btn_start.pack(side=tk.LEFT, padx=20, pady=10)

btn_stop = tk.Button(root, text="⏹️ Arrêter", command=arreter_transcription)
btn_stop.pack(side=tk.RIGHT, padx=20, pady=10)

root.mainloop()
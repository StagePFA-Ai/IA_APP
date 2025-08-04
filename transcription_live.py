import sounddevice as sd
import soundfile as sf
import whisper
import keyboard
from pydub import AudioSegment
import os
# Paramètres
fichier = "enregistrement.wav"
duree = 5  # durée en secondes
frequence = 44100  # taux d'échantillonnage
fichier_final = "audio_final.wav"
#1# pour parler 5 seconde et fait l'enregistrement de cette tranche d'audio
def enregistrer_tranche(nom_fichier,duree):
    print("Enregistrement en cours...")
    audio = sd.rec(int(duree * frequence), samplerate=frequence, channels=2)
    sd.wait()  # attendre la fin de l'enregistrement
    sf.write(nom_fichier, audio, frequence)
    print(f"Tranche sauvegardée : {nom_fichier}")
#2# en fait la transcription de cette tranche d'audio & en fait l engistremet de prochaine tranche d'audio 
def transcription_tranche(audio_file):
# Charger le modèle Whisper
    model = whisper.load_model("base")
# Transcription
    result = model.transcribe(audio_file)
# Sauvegarde du texte transcrit
    with open("transcription.txt", "a", encoding="utf-8") as f:
        f.write(result["text"])
    print(result["text"])
    print("Transcription terminée et sauvegardée dans transcription.txt")
#3# ajouter cette tranche a les tranche transcript pour a la fin en fait l enregistrement d audio 
def ajouter_tranche(tranche):
    global fichier_final
    if os.path.exists(fichier_final):
        # Charger l'audio final et la nouvelle tranche
        final = AudioSegment.from_wav(fichier_final)
        nouveau = AudioSegment.from_wav(tranche)
        # Concaténer
        final += nouveau
        final.export(fichier_final, format="wav")
    else:
        # Si c'est la première tranche, on la copie directement
        AudioSegment.from_wav(tranche).export(fichier_final, format="wav")

# --- Utilisation ---
while True:
    if keyboard.is_pressed('esc'):
        print("Programme arrêté.")
        break
    nom_temp = "temporairement.wav"
    enregistrer_tranche(fichier, duree=5)  # enregistrement d'une tranche de (5 secondes )
    transcription_tranche(fichier)
    ajouter_tranche(fichier)
    print("Tranche ajoutée au fichier final.")

print(f"Fichier final créé : {fichier_final}")
print("la transcription)")


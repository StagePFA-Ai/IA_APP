import sounddevice as sd
import soundfile as sf
import whisper
from pydub import AudioSegment
import keyboard
import os

# Paramètres
fichier_temp = "enregistrement.wav"
fichier_final = "audio_final.wav"
fichier_transcription = "transcription.txt"
duree = 5  # durée d'une tranche en secondes
frequence = 44100  # taux d'échantillonnage

# Charger Whisper une seule fois
print("Chargement du modèle Whisper...")
model = whisper.load_model("base", device="cpu")  # Utiliser le modèle large pour une meilleure précision
print("Modèle chargé.")

# Fonction d'enregistrement d'une tranche
def enregistrer_tranche(nom_fichier, duree):
    print("Enregistrement en cours...")
    audio = sd.rec(int(duree * frequence), samplerate=frequence, channels=2)
    sd.wait()
    sf.write(nom_fichier, audio, frequence)
    print(f"Tranche sauvegardée : {nom_fichier}")

# Fonction de transcription d'une tranche
def transcription_tranche(audio_file):
    result = model.transcribe(audio_file)
    texte = result["text"].strip()
    with open(fichier_transcription, "a", encoding="utf-8") as f:
        f.write(texte + "\n")  # Ajouter retour à la ligne
    print("Transcrit :", texte)
    return texte

# Fonction pour ajouter une tranche au fichier final
def ajouter_tranche(tranche):
    global fichier_final
    if os.path.exists(fichier_final):
        final = AudioSegment.from_wav(fichier_final)
        nouveau = AudioSegment.from_wav(tranche)
        final += nouveau
        final.export(fichier_final, format="wav")
    else:
        AudioSegment.from_wav(tranche).export(fichier_final, format="wav")

# Boucle principale
print("Appuyez sur 'ESC' pour arrêter.")
while True:
    if keyboard.is_pressed('esc'):
        print("Programme arrêté par l'utilisateur.")
        break
    enregistrer_tranche(fichier_temp, duree)
    transcription_tranche(fichier_temp)
    ajouter_tranche(fichier_temp)
    print("Tranche ajoutée au fichier final.\n")

print(f"Fichier final créé : {fichier_final}")
print(f"Transcription disponible dans : {fichier_transcription}")

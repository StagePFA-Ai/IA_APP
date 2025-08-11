
import tkinter as tk
from tkinter import scrolledtext, messagebox
from transformers import pipeline
from langdetect import detect, LangDetectException
import re

# Charger le modèle multilingue de résumé
try:
    summarizer = pipeline("summarization", model="csebuetnlp/mT5_multilingual_XLSum")
except Exception as e:
    messagebox.showerror("Erreur", f"Impossible de charger le modèle : {str(e)}")
    exit()

# Nettoyage du texte
def clean_text(text):
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Détection de langue avec fallback
def safe_detect(text):
    try:
        return detect(text)
    except LangDetectException:
        return 'unknown'

# Résumé structuré
def summarize_structured():
    raw_text = input_text.get("1.0", tk.END).strip()
    cleaned_text = clean_text(raw_text)

    if not cleaned_text:
        summary_text.delete("1.0", tk.END)
        summary_text.insert(tk.END, "⚠️ Veuillez entrer du texte à résumer.")
        return

    if len(cleaned_text.split()) < 10:
        summary_text.delete("1.0", tk.END)
        summary_text.insert(tk.END, "⚠️ Le texte est trop court pour générer un résumé.")
        return

    try:
        lang = safe_detect(cleaned_text)
        print(f"[INFO] Langue détectée : {lang.upper() if lang != 'unknown' else 'Non détectée'}")

        prompt = f"""
        Résume ce texte en extrayant :
        - Les grands points abordés
        - Les décisions prises
        - Les actions à entreprendre
        - Les responsables désignés
        - Les dates limites

        Texte : {cleaned_text}
        """

        input_length = len(prompt.split())
        max_length = min(130, max(40, int(input_length * 0.6)))
        min_length = max(20, int(input_length * 0.3))

        result = summarizer(
            prompt,
            max_length=max_length,
            min_length=min_length,
            do_sample=False,
            truncation=True
        )

        summary = result[0]['summary_text']
        summary_text.delete("1.0", tk.END)
        summary_text.insert(tk.END, summary)

    except Exception as e:
        summary_text.delete("1.0", tk.END)
        summary_text.insert(tk.END, f"❌ Erreur lors du résumé : {str(e)}")

# Interface Tkinter
root = tk.Tk()
root.title("Résumé Structuré Multilingue")
root.geometry("900x700")

# Zone de texte d'entrée
tk.Label(root, text="Texte à résumer", font=("Arial", 12, "bold")).pack(pady=5)
input_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15, font=("Arial", 12))
input_text.pack(pady=5, padx=10, fill="both", expand=True)

# Zone de résumé structuré
tk.Label(root, text="Résumé Structuré", font=("Arial", 12, "bold")).pack(pady=5)
summary_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15, font=("Arial", 12))
summary_text.pack(pady=5, padx=10, fill="both", expand=True)

# Bouton pour résumer
tk.Button(
    root,
    text="📝 Résumer",
    width=15,
    command=summarize_structured,
    bg="lightblue",
    font=("Arial", 12)
).pack(pady=10)

# Démarrer l'interface
root.mainloop()


Application Web de Résumé Automatique de Réunions
Description
Cette application web permet de transcrire et résumer automatiquement des réunions audio, en garantissant la confidentialité via un traitement local ou serveur privé.
Elle est développée en React pour le front-end et Django pour le back-end, assurant une interface moderne et une API robuste.

Fonctionnalités
Enregistrement audio et envoi des fichiers via l’interface React.

Transcription automatique des fichiers audio sur le serveur Django avec un modèle local (ex: Whisper).

Génération de résumé automatique des transcriptions.

Interface utilisateur intuitive en React pour contrôler l’enregistrement, voir la transcription et le résumé.

Export des transcriptions et résumés en formats TXT et PDF.

Gestion des utilisateurs et sessions (si applicable).

Architecture modulaire avec API RESTful entre React et Django.

Technologies
Front-end : React, Axios, Tailwind CSS (ou autre)

Back-end : Django, Django REST Framework

Traitement audio et NLP : Python, Whisper/Faster Whisper, Transformers

Base de données : SQLite / PostgreSQL (configurable)

Authentification (optionnelle) : JWT ou sessions Django

Installation
Back-end (Django)
bash
Copier
Modifier
cd backend
python -m venv env
source env/bin/activate      # Linux/Mac
env\Scripts\activate         # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
Front-end (React)
bash
Copier
Modifier
cd frontend
npm install
npm start
L’application React tourne par défaut sur http://localhost:3000 et communique avec Django sur http://localhost:8000.

Structure du projet
bash
Copier
Modifier
/backend/                 # code Django, API, gestion modèles, transcriptions
/frontend/                # application React (UI, appels API)
/audio/                   # stockage local fichiers audio (backend)
/transcripts/             # transcriptions stockées (backend)
/summaries/               # résumés générés (backend)
README.md                 # documentation du projet
Usage
Lance le serveur Django

Lance le front React

Accède à l’interface utilisateur via le navigateur

Enregistre ou importe un fichier audio

Le backend traite la transcription et génère un résumé

Visualise ou télécharge les résultats

Contribution
Les contributions sont les bienvenues via pull requests.

Licence
MIT License

Contact
email@example.com

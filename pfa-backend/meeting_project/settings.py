# Importations des modules nécessaires
import os
from pathlib import Path
from datetime import timedelta

# Définition du répertoire de base du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Clé secrète pour les sessions et le hachage - À CHANGER EN PRODUCTION
SECRET_KEY = "replace-me-in-production"

# Mode debug activé (désactiver en production)
DEBUG = True

# Hôtes autorisés à accéder à l'application (tous en développement)
ALLOWED_HOSTS = ["*"]

# Configuration des redirections de connexion/déconnexion
LOGIN_REDIRECT_URL = '/dashboard/'  # Redirection après connexion réussie
LOGOUT_REDIRECT_URL = '/login/'     # Redirection après déconnexion

# Applications Django installées
INSTALLED_APPS = [
    "django.contrib.admin",           # Interface d'administration
    'django.contrib.admindocs',       # Documentation automatique de l'admin
    "django.contrib.auth",            # Système d'authentification (obligatoire)
    "django.contrib.contenttypes",    # Système de types de contenu (obligatoire)
    "django.contrib.sessions",        # Gestion des sessions
    "django.contrib.messages",        # Système de messages
    "django.contrib.staticfiles",     # Gestion des fichiers statiques
    
    # Applications tierces
    "rest_framework",                 # Framework REST pour les API
    'rest_framework_simplejwt',       # Authentification JWT pour DRF
    "corsheaders",                    # Gestion des CORS (Cross-Origin Resource Sharing)
    
    # Applications locales
    "meetings.apps.MeetingsConfig",   # Application meetings
    'channels',                       # Support WebSocket et protocoles asynchrones
]

# Middleware - couches de traitement des requêtes
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",      # Sécurité
    "django.middleware.common.CommonMiddleware",          # Traitement des requêtes communes
    "django.contrib.sessions.middleware.SessionMiddleware", # Gestion des sessions
    "django.middleware.csrf.CsrfViewMiddleware",          # Protection CSRF
    "django.contrib.auth.middleware.AuthenticationMiddleware", # Authentification
    "django.contrib.sessions.middleware.SessionMiddleware", # Sessions (dupliqué)
    "django.contrib.messages.middleware.MessageMiddleware", # Messages
    'django.middleware.security.SecurityMiddleware',      # Sécurité (dupliqué)
    'corsheaders.middleware.CorsMiddleware',              # CORS - doit être placé tôt
    # 'django.contrib.sessions.middleware.SessionMiddleware',  # Commenté
]

# Modèle utilisateur personnalisé (décommenter après création)
# AUTH_USER_MODEL = 'meetings.Utilisateur'

# Configuration des URLs racines
ROOT_URLCONF = "meeting_project.urls"

# Configuration des templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates", 
        "DIRS": [os.path.join(BASE_DIR, 'meeting/templates')],  # Dossiers supplémentaires de templates
        "APP_DIRS": True,  # Recherche des templates dans les apps
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",  # Utilisateur dans le contexte
                "django.contrib.messages.context_processors.messages"  # Messages dans le contexte
            ]
        }
    }
]

# Application WSGI (synchronne)
WSGI_APPLICATION = "meeting_project.wsgi.application"

# Configuration de la base de données
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Utilisation de SQLite
        'NAME': BASE_DIR / 'db.sqlite3',         # Chemin vers le fichier de base de données
    }
}

# Désactivation des validateurs de mot de passe (déconseillé en production)
AUTH_PASSWORD_VALIDATORS = []

# Configuration internationale
LANGUAGE_CODE = "en-us"  # Langue par défaut
TIME_ZONE = "UTC"        # Fuseau horaire par défaut
USE_I18N = True          # Activation de l'internationalisation
USE_TZ = True            # Utilisation des timezones

# Configuration des fichiers statiques
STATIC_ROOT = os.path.join(BASE_DIR, 'static')  # Dossier de collecte des fichiers statiques
STATIC_URL = "/static/"  # URL pour servir les fichiers statiques
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'meeting_project/static'),  # Dossiers supplémentaires de fichiers statiques
] 

# Configuration des fichiers média (uploads)
MEDIA_URL = "/media/"    # URL pour servir les fichiers média
MEDIA_ROOT = BASE_DIR / "media"  # Dossier de stockage des fichiers uploadés

# Type de champ auto-incrémenté par défaut
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Configuration de Django REST Framework avec JWT
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # Authentification JWT
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',  # Permission par défaut: authentifié requis
    )
}

# Configuration de Simple JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # Durée de vie des tokens d'accès
}

# Configuration CORS (Cross-Origin Resource Sharing)
CORS_ALLOW_ALL_ORIGINS = True  # Autorise toutes les origines (développement seulement)
CORS_ALLOW_CREDENTIALS = True  # Autorise l'envoi de cookies entre origines
CORS_ALLOWED_ORIGINS = [       # Liste des origines autorisées (en plus de ALLOW_ALL_ORIGINS)
    "http://localhost:5173",   # Origine locale pour le développement frontend
    "http://127.0.0.1:5173",   # Autre origine locale
]
CORS_ALLOW_METHODS = [         # Méthodes HTTP autorisées
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [         # En-têtes HTTP autorisés
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Configuration de Channels (WebSockets)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",  # Couche de canaux en mémoire (développement)
    }
}

# Application ASGI (asynchrone) pour le support WebSocket
ASGI_APPLICATION = "meeting_project.asgi.application"

###########################################################################################
# Configuration supplémentaire pour le tunneling avec ngrok

DEBUG = True  # Mode debug activé pour la démonstration

# Hôtes autorisés incluant les domaines ngrok
ALLOWED_HOSTS = ["127.0.0.1", "localhost", ".ngrok-free.app", ".ngrok.app", ".ngrok.io"]

# Origines de confiance pour la protection CSRF
CSRF_TRUSTED_ORIGINS = [
    "https://*.ngrok-free.app",  # Tous les sous-domaines ngrok-free
    "https://*.ngrok.app",       # Tous les sous-domaines ngrok
    "https://*.ngrok.io",        # Tous les sous-domaines ngrok
]

# Configuration pour le proxy inversé ngrok
USE_X_FORWARDED_HOST = True  # Utilise l'en-tête X-Forwarded-Host
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")  # Détection du protocole HTTPS via proxy

# Configuration des cookies pour la sécurité
CSRF_COOKIE_SAMESITE = "Lax"      # Politique SameSite pour le cookie CSRF
SESSION_COOKIE_SAMESITE = "Lax"   # Politique SameSite pour le cookie de session

# Note pour le développement: servir les fichiers média/statiques
# Dans urls.py (développement uniquement):
# from django.conf import settings
# from django.conf.urls.static import static
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
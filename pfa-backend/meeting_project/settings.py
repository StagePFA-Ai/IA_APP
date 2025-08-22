import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "replace-me-in-production"
DEBUG = True
ALLOWED_HOSTS = ["*"]

# Désactivez les redirections par défaut car vous allez gérer ça dans vos vues
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

INSTALLED_APPS = [
    "django.contrib.admin",
    'django.contrib.admindocs',
    "django.contrib.auth",         # Obligatoire
    "django.contrib.contenttypes", # Obligatoire
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    'rest_framework_simplejwt',
    "corsheaders",
    "meetings.apps.MeetingsConfig",
    'channels',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
   "django.contrib.sessions.middleware.SessionMiddleware",
    # "django.contrib.auth.middleware.AuthenticationMiddleware",  # Commenté
    "django.contrib.messages.middleware.MessageMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    # 'django.contrib.sessions.middleware.SessionMiddleware',  # Commenté
]

# Spécifiez votre modèle utilisateur personnalisé
# AUTH_USER_MODEL = 'meetings.Utilisateur'  # Décommentez après avoir créé votre modèle

ROOT_URLCONF = "meeting_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates", 
        "DIRS": [os.path.join(BASE_DIR, 'meeting/templates')],  # Correction du chemin
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                 "django.contrib.auth.context_processors.auth",  # Commenté
                "django.contrib.messages.context_processors.messages"
            ]
        }
    }
]


WSGI_APPLICATION = "meeting_project.wsgi.application"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Base de données SQLite
        'NAME': BASE_DIR / 'db.sqlite3',        # Fichier DB dans ton projet
    }
}


# Désactivez les validateurs de mot de passe par défaut
AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'meeting_project/static'), ] 
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Configuration REST Framework avec JWT
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
}

# Configuration CORS
CORS_ALLOW_ALL_ORIGINS = True  # Pour le développement seulement
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
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

# Configuration Channels
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}
ASGI_APPLICATION = "meeting_project.asgi.application"
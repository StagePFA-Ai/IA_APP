from django.urls import path, include
from . import views
from django.urls import re_path
from .utils import transcsumm
# Définition des patterns d'URL de l'application
urlpatterns = [
    # Page d'accueil/racine de l'application (page de connexion)
    path("", views.home, name="home"),
    # URL pour la page de connexion
    path("login/",  views.login_view,  name="login"),
    # URL pour la déconnexion
    path("logout/", views.logout_view, name="logout"),
    # URL pour le tableau de bord
    path('dashboard/', views.dashboard, name='dashboard'),
    # URLs liées au calendrier
    path("calendar/", views.calendar, name="calendar"),
    path("calendar/events/", views.calendar_events, name="calendar_events"),
    path("calendar/day/", views.calendar_day, name="calendar_day"),
    path("calendar/create/", views.calendar_create, name="calendar_create"),
    # URL pour visualiser les détails d'une réunion spécifique (via son ID)
    path("calendar/meeting/<int:pk>/", views.calendar_meeting_info, name="calendar_meeting_info"),
    # URL pour mettre à jour une réunion
    path("calendar/meeting/update/", views.calendar_meeting_update, name="calendar_meeting_update"),
    # URL pour démarrer le calendrier
    path("calendar/start/", views.calendar_start, name="calendar_start"),
    # URL dupliquée pour la vue quotidienne du calendrier (à vérifier)
    path("calendar/day/", views.calendar_day, name="calendar_day"),
    # URL pour visualiser une réunion spécifique
    path("meetings/<int:meeting_id>/view/", views.view_meeting, name="view_meeting"),
    # URL pour la page des réunions
    path('meetings/', views.meetings_page, name='meetings'),
    # URL pour la page des paramètres
    path('settings/', views.settings_page, name='settings'),
    # URL pour créer une nouvelle réunion (en français)
    path("nouvelle-reunion/", views.reunion_nouvelle, name="nouvelle-reunion"),
    # URL pour créer une réunion (en français)
    path("reunions/creer/", views.creer_reunion, name="creer_reunion"),
    # URL pour modifier une réunion existante
    path("reunions/<int:reunion_id>/maj/", views.modifier_reunion, name="modifier_reunion"),
    # URL pour accéder à la page de transcription d'une réunion
    path("transcription/<int:reunion_id>/", views.transcription_page, name="transcription"),
    # URL pour sauvegarder une transcription
    path("transcription/<int:reunion_id>/save/", views.save_transcription, name="save_transcription"),
    # URL pour prévisualiser le rapport d'une réunion
    path("transcription/<int:pk>/report/preview/", views.meeting_report_view, name="meeting_report_view"),
    # URL pour générer un rapport au format DOCX
    path("transcription/<int:reunion_id>/report/docx/", views.generate_report, name="generate_report"),
]
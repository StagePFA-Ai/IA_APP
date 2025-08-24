from django.urls import path, include
from . import views
from django.urls import re_path
from .utils import transcsumm



urlpatterns = [
    path("", views.home, name="home"),   # Page de connexion  # Page de connexion
    path("login/",  views.login_view,  name="login"),
    path("logout/", views.logout_view, name="logout"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("calendar/", views.calendar, name="calendar"),
    path("calendar/events/", views.calendar_events, name="calendar_events"),
    path("calendar/day/", views.calendar_day, name="calendar_day"),
    path("calendar/create/", views.calendar_create, name="calendar_create"),
    path("calendar/meeting/<int:pk>/", views.calendar_meeting_info, name="calendar_meeting_info"),
    path("calendar/meeting/update/", views.calendar_meeting_update, name="calendar_meeting_update"),
    path("calendar/start/", views.calendar_start, name="calendar_start"),
    path("calendar/day/",views.calendar_day, name="calendar_day"),
    







    path("meetings/<int:meeting_id>/view/", views.view_meeting, name="view_meeting"),
    path('meetings/', views.meetings_page, name='meetings'),
    path('settings/', views.settings_page, name='settings'),
    path("nouvelle-reunion/", views.reunion_nouvelle, name="nouvelle-reunion"),

    # Traitements POST
    path("reunions/creer/", views.creer_reunion, name="creer_reunion"),
    path("reunions/<int:reunion_id>/maj/", views.modifier_reunion, name="modifier_reunion"),

 
    path("transcription/<int:reunion_id>/", views.transcription_page, name="transcription"),
    path("transcription/<int:reunion_id>/save/", views.save_transcription, name="save_transcription"),
    
    path("transcription/<int:pk>/report/preview/", views.meeting_report_view, name="meeting_report_view"),
    path("transcription/<int:reunion_id>/report/docx/", views.generate_report, name="generate_report"),
  #'transcription/<int:meeting_id>/
   
 
]

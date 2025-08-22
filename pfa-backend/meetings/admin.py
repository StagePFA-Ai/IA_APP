from django.contrib import admin
from .models import  Reunion, Audio, Transcription, Resume, Rapport
from django.apps import AppConfig


# admin.py
class MeetingConfig(AppConfig):
    name= 'meetings'
    list_display = ('id', 'title', 'date', 'time', 'location')
    search_fields = ('title', 'location')
    list_filter = ('date', 'time')
# Register your models here.

admin.site.register(Reunion)
admin.site.register(Audio)
admin.site.register(Transcription)
admin.site.register(Resume)
admin.site.register(Rapport)
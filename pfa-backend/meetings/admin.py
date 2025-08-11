from django.contrib import admin
from .models import Meeting

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "datetime", "created_at")
    readonly_fields = ("transcription", "summary")

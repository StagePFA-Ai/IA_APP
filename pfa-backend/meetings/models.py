from django.db import models

class Meeting(models.Model):
    title = models.CharField(max_length=255)
    datetime = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)  # seconds
    audio = models.FileField(upload_to="uploads/", null=True, blank=True)
    transcription = models.TextField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50, default="pending")  # pending, processing, done, failed
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.title}"

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
from datetime import datetime
import os

# ─────────────────────────────────────────────────────────────
# Choices statut (évite les fautes dans la DB)
class ReunionStatus(models.TextChoices):
    PLANIFIE = "planifie", "Planifié"
    EN_COURS = "en_cours", "En cours"
    TERMINE = "termine", "Terminé"
    ANNULE = "annule", "Annulé"
    REPORTE = "reporte", "Reporté"

# Langues supportées pour résumé/transcription
class Lang(models.TextChoices):
    FR = "fr", "Français"
    EN = "en", "English"
    AR = "ar", "العربية"

# ─────────────────────────────────────────────────────────────
class Reunion(models.Model):
    titre = models.CharField(max_length=255)
    date_r = models.DateField()
    heure_r = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=ReunionStatus.choices,
        default=ReunionStatus.PLANIFIE,
    )

    # propriétaire / créateur
    utilisateur = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reunions_creees"
    )

    # participants (simple). Si tu veux gérer les rôles par participant,
    # remplace par un through=Participation (voir note plus bas).
    participants = models.ManyToManyField(
        User, related_name="reunions_participees", blank=True
    )

    date_creation = models.DateTimeField(auto_now_add=True)
    date_maj = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_r", "-heure_r", "-date_creation"]
        indexes = [
            models.Index(fields=["utilisateur", "date_r", "heure_r"]),
            models.Index(fields=["status"]),
        ]
        constraints = [
            # Unicité souple : même user, même horaire exact, même titre
            models.UniqueConstraint(
                fields=["utilisateur", "date_r", "heure_r", "titre"],
                name="uniq_reunion_owner_datetime_title",
            ),
        ]

    def __str__(self):
        return self.titre

    @property
    def start_at(self):
        """Datetime combinant date_r + heure_r (timezone aware)."""
        dt_naive = datetime.combine(self.date_r, self.heure_r)
        return timezone.make_aware(dt_naive, timezone.get_current_timezone())

    @property
    def is_past(self):
        return self.start_at < timezone.now()

    @property
    def is_now(self):
        now = timezone.now()
        # fenêtre "maintenant" de 15 minutes autour du start (à adapter)
        return abs((self.start_at - now).total_seconds()) < 15 * 60

    def full_text_transcription(self):
        """Concatène tous les segments en texte complet (si pas de Transcription OneToOne)."""
        return " ".join(s.text for s in self.segments.order_by("id").all()).strip()

# ─────────────────────────────────────────────────────────────
def _audio_upload_to(instance, filename):
    base, ext = os.path.splitext(filename)
    return f"uploads/audio/r{instance.reunion_id}/{timezone.now():%Y%m%d_%H%M%S}{ext.lower()}"

class Audio(models.Model):
    reunion = models.ForeignKey(Reunion, on_delete=models.CASCADE, related_name="audios")
    chemin_fichier = models.FileField(upload_to=_audio_upload_to)
    format = models.CharField(max_length=15, blank=True)  # ex: webm/opus, wav
    duree = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], help_text="Durée en secondes", null=True, blank=True
    )
    date_upload = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_upload"]
        indexes = [models.Index(fields=["reunion"])]

    def __str__(self):
        return f"Audio {self.id} - {self.reunion.titre}"

# ─────────────────────────────────────────────────────────────
class TranscriptSegment(models.Model):
    """Segments live (stream) → utile avec WebRTC/HTTP chunks."""
    reunion = models.ForeignKey(
        Reunion, on_delete=models.CASCADE, related_name="segments"
    )
    text = models.TextField()
    start_sec = models.FloatField(default=0)
    end_sec = models.FloatField(default=0)
    speaker = models.CharField(max_length=80, blank=True)  # si diarization plus tard
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["reunion"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Segment {self.id} - {self.reunion.titre}"

# ─────────────────────────────────────────────────────────────
class Transcription(models.Model):
    reunion = models.OneToOneField(
        Reunion, on_delete=models.CASCADE, related_name="transcription"
    )
    text_transcrit = models.TextField()
    langue = models.CharField(max_length=5, choices=Lang.choices, default=Lang.FR)
    heure_date = models.DateTimeField(auto_now_add=True)  # horodatage génération

    class Meta:
        indexes = [models.Index(fields=["reunion"]), models.Index(fields=["langue"])]

    def __str__(self):
        return f"Transcription {self.id} - {self.reunion.titre}"

# ─────────────────────────────────────────────────────────────
class Resume(models.Model):
    transcription = models.OneToOneField(
        Transcription, on_delete=models.CASCADE, related_name="resume"
    )
    text_resume = models.TextField()
    date_generation = models.DateTimeField(auto_now_add=True)
    langue = models.CharField(max_length=5, choices=Lang.choices, default=Lang.FR)

    class Meta:
        indexes = [models.Index(fields=["transcription"]), models.Index(fields=["date_generation"])]

    def __str__(self):
        return f"Résumé {self.id} - {self.transcription.reunion.titre}"

# ─────────────────────────────────────────────────────────────
def _rapport_upload_to(instance, filename):
    base, ext = os.path.splitext(filename)
    return f"uploads/rapports/r{instance.resume.transcription.reunion_id}/{timezone.now():%Y%m%d_%H%M%S}{ext.lower()}"

class Rapport(models.Model):
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE, related_name="rapport")
    fichier = models.FileField(upload_to=_rapport_upload_to)

    def __str__(self):
        return f"Rapport {self.id} - {self.resume.transcription.reunion.titre}"

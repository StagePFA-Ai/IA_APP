# models.py
# =============================================================================
# MeetingAI — Modèles Django (corrigés & commentés)
# - Statuts harmonisés avec les vues : planifier / en_cours / terminer / annuler / reporter
# - Index & contrainte d’unicité utiles pour les recherches et la cohérence
# - Uploads rangés par réunion (répertoires par ID) avec horodatage dans le fichier
# =============================================================================

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
from datetime import datetime
import os


# =============================================================================
# Choices
# =============================================================================
class ReunionStatus(models.TextChoices):
    """Statuts harmonisés (⚠︎ doivent matcher les tests côté vues/permissions)."""
    PLANIFIER = "planifier", "Planifié"
    EN_COURS  = "en_cours",  "En cours"
    TERMINER  = "terminer",  "Terminé"
    ANNULER   = "annuler",   "Annulé"
    REPORTER  = "reporter",  "Reporté"


class Lang(models.TextChoices):
    """Langues supportées pour transcription/résumé."""
    FR = "fr", "Français"
    EN = "en", "English"
    AR = "ar", "العربية"


# =============================================================================
# Réunion
# =============================================================================
class Reunion(models.Model):
    """
    Entité centrale : planification et suivi d’une réunion.
    - 'utilisateur' = propriétaire/créateur
    - 'participants' = utilisateurs invités (M2M simple)
    """

    titre   = models.CharField(max_length=255)
    date_r  = models.DateField()
    heure_r = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=ReunionStatus.choices,
        default=ReunionStatus.PLANIFIER,
        help_text="Statut métier de la réunion."
    )

    # Propriétaire / créateur (cascade : si l'utilisateur est supprimé, supprimer ses réunions)
    utilisateur = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reunions_creees"
    )

    # Participants (simple). Pour des rôles par participant, utiliser un through=Participation.
    participants = models.ManyToManyField(
        User, related_name="reunions_participees", blank=True
    )

    date_creation = models.DateTimeField(auto_now_add=True)
    date_maj      = models.DateTimeField(auto_now=True)

    class Meta:
        # Tri par défaut : plus récentes en premier
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

    def __str__(self) -> str:
        return f"{self.titre} [{self.date_r} {self.heure_r}]"

    @property
    def start_at(self):
        """
        Datetime 'aware' combinant date_r + heure_r.
        Utile pour comparer avec timezone.now().
        """
        dt_naive = datetime.combine(self.date_r, self.heure_r)
        return timezone.make_aware(dt_naive, timezone.get_current_timezone())

    @property
    def is_past(self) -> bool:
        """Renvoie True si la réunion a démarré dans le passé."""
        return self.start_at < timezone.now()

    @property
    def is_now(self) -> bool:
        """
        Fenêtre 'maintenant' de 15 minutes autour du début (à adapter si besoin).
        Sert, par ex., à mettre en avant une réunion imminente.
        """
        now = timezone.now()
        return abs((self.start_at - now).total_seconds()) < 15 * 60

    def full_text_transcription(self) -> str:
        """
        (Optionnel) Si vous utilisez des segments live (TranscriptSegment),
        concatène les segments pour reconstituer un texte complet.
        """
        return " ".join(s.text for s in self.segments.order_by("id").all()).strip()


# =============================================================================
# Audio
# =============================================================================
def _audio_upload_to(instance, filename: str) -> str:
    """
    Chemin d’upload des fichiers audio :
      uploads/audio/r<id_reunion>/<timestamp><ext>
    """
    _base, ext = os.path.splitext(filename)
    ts = timezone.now().strftime("%Y%m%d_%H%M%S")
    return f"uploads/audio/r{instance.reunion_id}/{ts}{ext.lower()}"


class Audio(models.Model):
    """
    Métadonnées et fichier audio associé à une réunion.
    'duree' en secondes (optionnelle si calculée plus tard par un worker).
    """
    reunion        = models.ForeignKey(Reunion, on_delete=models.CASCADE, related_name="audios")
    chemin_fichier = models.FileField(upload_to=_audio_upload_to)
    format         = models.CharField(max_length=15, blank=True, help_text="Ex : webm/opus, wav")
    duree          = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Durée en secondes",
        null=True, blank=True
    )
    date_upload    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_upload"]
        indexes = [models.Index(fields=["reunion"])]

    def __str__(self) -> str:
        return f"Audio {self.id} — {self.reunion.titre}"


# =============================================================================
# Segments de transcription (stream temps réel)
# =============================================================================
class TranscriptSegment(models.Model):
    """
    Segments de transcription live (WebSocket/stream).
    Utile si vous affichez la transcription incrémentale côté UI,
    tout en conservant une trace temporelle (start_sec, end_sec).
    """
    reunion   = models.ForeignKey(Reunion, on_delete=models.CASCADE, related_name="segments")
    text      = models.TextField()
    start_sec = models.FloatField(default=0)
    end_sec   = models.FloatField(default=0)
    speaker   = models.CharField(max_length=80, blank=True, help_text="Diarisation future (optionnel)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["reunion"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"Segment {self.id} — {self.reunion.titre}"


# =============================================================================
# Transcription (texte final agrégé)
# =============================================================================
class Transcription(models.Model):
    """
    Transcription finale (OneToOne avec Réunion).
    Peut être alimentée à partir d’un assemblage de segments et/ou directement
    par le pipeline d’ASR.
    """
    reunion        = models.OneToOneField(Reunion, on_delete=models.CASCADE, related_name="transcription")
    text_transcrit = models.TextField()
    langue         = models.CharField(max_length=5, choices=Lang.choices, default=Lang.FR)
    heure_date     = models.DateTimeField(auto_now_add=True, help_text="Horodatage de génération")

    class Meta:
        indexes = [
            models.Index(fields=["reunion"]),
            models.Index(fields=["langue"]),
        ]

    def __str__(self) -> str:
        return f"Transcription {self.id} — {self.reunion.titre}"


# =============================================================================
# Résumé (OneToOne Transcription)
# =============================================================================
class Resume(models.Model):
    """
    Résumé structuré (points clés, décisions, actions).
    OneToOne avec Transcription.
    """
    transcription   = models.OneToOneField(Transcription, on_delete=models.CASCADE, related_name="resume")
    text_resume     = models.TextField()
    date_generation = models.DateTimeField(auto_now_add=True)
    langue          = models.CharField(max_length=5, choices=Lang.choices, default=Lang.FR)

    class Meta:
        indexes = [
            models.Index(fields=["transcription"]),
            models.Index(fields=["date_generation"]),
        ]

    def __str__(self) -> str:
        return f"Résumé {self.id} — {self.transcription.reunion.titre}"


# =============================================================================
# Rapport (DOCX/PDF) attaché au Résumé
# =============================================================================
def _rapport_upload_to(instance, filename: str) -> str:
    """
    Chemin d’upload des rapports :
      uploads/rapports/r<id_reunion>/<timestamp><ext>
    """
    _base, ext = os.path.splitext(filename)
    ts = timezone.now().strftime("%Y%m%d_%H%M%S")
    reunion_id = instance.resume.transcription.reunion_id
    return f"uploads/rapports/r{reunion_id}/{ts}{ext.lower()}"


class Rapport(models.Model):
    """
    Rapport bureautique (DOCX/PDF) généré à partir du résumé/transcription.
    OneToOne avec Résumé.
    """
    resume  = models.OneToOneField(Resume, on_delete=models.CASCADE, related_name="rapport")
    fichier = models.FileField(upload_to=_rapport_upload_to)

    def __str__(self) -> str:
        return f"Rapport {self.id} — {self.resume.transcription.reunion.titre}"

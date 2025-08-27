from rest_framework import serializers
from .models import Utilisateur, Reunion, Audio, Transcription, Resume, Rapport

class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = "__all__"

class ReunionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reunion
        fields = "__all__"

class AudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audio
        fields = "__all__"

class TranscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transcription
        fields = "__all__"

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = "__all__"

class RapportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rapport
        fields = "__all__"


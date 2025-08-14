from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Meeting
from django.contrib.auth import authenticate
from .serializers import MeetingSerializer
from .tasks import process_meeting_async
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all().order_by("-created_at")
    serializer_class = MeetingSerializer
    permission_classes = [permissions.IsAuthenticated]
    @action(detail=True, methods=["post"])
    def upload(self, request, pk=None):
        meeting = self.get_object()
        file = request.FILES.get("file")
        if not file:
            return Response({"detail":"No file"}, status=status.HTTP_400_BAD_REQUEST)
        meeting.audio.save(file.name, file, save=True)
        meeting.status = "pending"
        meeting.save()
        return Response({"audio": meeting.audio.url})

    @action(detail=True, methods=["post"])
    def process(self, request, pk=None):
        meeting = self.get_object()
        # start background processing
        process_meeting_async(meeting.id)
        return Response({"status":"processing_started"})
class ProtectedView(APIView):
    permission_classes = ["IsAuthenticated"]

    def get(self, request):
        return Response({"message": "Vous êtes connecté"})
class CustomLoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        # Vérifier si l’utilisateur existe et mot de passe valide
        user = authenticate(username=username, password=password)

        if user is not None:
            # Générer un token JWT
            refresh = RefreshToken.for_user(user)
            return Response({
                "success": True,
                "message": "Utilisateur authentifié",
                "username": user.username,
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "success": False,
                "error": "Nom d'utilisateur ou mot de passe invalide"
            }, status=status.HTTP_401_UNAUTHORIZED)
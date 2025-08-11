from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Meeting
from .serializers import MeetingSerializer
from .tasks import process_meeting_async

class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all().order_by("-created_at")
    serializer_class = MeetingSerializer

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

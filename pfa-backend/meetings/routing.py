from django.urls import re_path
from  .utils.transcsumm import TranscriptionConsumer

websocket_urlpatterns = [
     re_path(r"^ws/transcription/$", TranscriptionConsumer.as_asgi()),
]

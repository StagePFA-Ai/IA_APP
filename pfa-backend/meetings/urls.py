from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MeetingViewSet
from .views import ProtectedView
from .views import CustomLoginView
router = DefaultRouter()
router.register(r"meetings", MeetingViewSet, basename="meeting")

urlpatterns = [
    path("", include(router.urls)),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('login-check/', CustomLoginView.as_view(), name='login_check'),
]

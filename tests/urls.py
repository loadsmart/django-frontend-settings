from django.urls import path

from frontend_settings import views

urlpatterns = [path("settings", views.settings, name="settings")]

"""Url patterns manage app"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from decouple import config

urlpatterns = [
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path(config('ADMIN_URL'), admin.site.urls),
    path('accounts/',include('accounts.urls')),
    path('',include('session_client.urls')),
    path('calendar/',include('room_calendar_app.urls')),
    path("__reload__/", include("django_browser_reload.urls")), # to use django reload

              ]+  static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


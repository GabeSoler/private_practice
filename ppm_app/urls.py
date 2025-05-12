"""Url patterns manage app"""
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path("admin/", admin.site.urls),
    path('accounts/',include('accounts.urls')),
    path('',include('session_client.urls')),
    path('calendar/',include('room_calendar_app.urls')),
    path("__reload__/", include("django_browser_reload.urls")), # to use django reload



]

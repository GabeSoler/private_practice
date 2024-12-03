"""Url patterns manage app"""
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path("admin/", admin.site.urls),
    path('accounts/',include('accounts.urls')),
    path('',include('tools.urls')),
    path('calendar/',include('room_calendar_app.urls')),

#third party
    path("unicorn/", include("django_unicorn.urls")),


]

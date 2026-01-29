"""Url patterns manage app"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from decouple import config
from django.conf.urls.i18n import i18n_patterns
from django.contrib.auth.decorators import login_not_required

urlpatterns = [
                  path('admin/doc/', include('django.contrib.admindocs.urls')),

                  path(config('ADMIN_URL'), admin.site.urls),

                  path("__reload__/", include("django_browser_reload.urls")),  # to use django reload
                  path("i18n/", login_not_required(include("django.conf.urls.i18n"))),

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += i18n_patterns(
    path('', include('base.urls')),
    path('accounts/', include('accounts.urls')),

    path('clients/', include('session_client.urls')),

    path('calendar/', include('room_calendar_app.urls')),

)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

"""urls for the account app"""
from django.urls import path, include
from . import views

app_name = 'accounts'

urlpatterns = [
    # include default authorisation urls
    # path('', include('django.contrib.auth.urls')),
    path("profile/", views.profile_view, name='account_profile'),  # using allauth system, to integrate a account centre
    path("delete_account/", views.delete_account_view, name='delete_account'),
]

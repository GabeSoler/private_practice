"""urls for the account app"""
from django.urls import path,include
from . import views

app_name = 'accounts'

urlpatterns = [
    #include default authorisation urls
    path('',include('django.contrib.auth.urls')),
    #registration page
    # path('register/',views.register,name='register'),


]


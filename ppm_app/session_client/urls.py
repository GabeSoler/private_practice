"""Defines URL patterns for session_client."""

from django.urls import path

from . import views

app_name = 'session_client'

urlpatterns = [
    #Home page
    path('', views.index_view, name='index'),

    #client-session app

    # index
    path('session_home/', views.session_home_view, name='session_home'),

    # items
    path('client/<uuid:client_pk>/', views.client_view, name='client'),
    path('session/<uuid:session_pk>/', views.session_view, name='session'),

    # add 
    path('add_client/', views.add_client_view, name='add_client'),
    path('add_session/', views.add_session_view, name='add_session'),

    # lists
    path('client_list/', views.clients_view, name='client_list'),
    path('session_list/', views.sessions_view, name='session_list'),
    path('session_list_by_client/<uuid:client_pk>/', views.sessions_by_client_view, name='session_list_by_client'),

    # edit
    path('edit_client/<uuid:client_pk>/', views.edit_client_view, name='edit_client'),
    path('edit_session/<uuid:session_pk>/', views.edit_session_view, name='edit_session'),

]
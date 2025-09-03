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
    path('client-hx/<uuid:client_pk>/', views.client_hx_item, name='client_hx_item'),

    path('session/<uuid:session_pk>/', views.session_view, name='session'),
    path('session-hx/<uuid:session_pk>/', views.session_hx_item, name='session_hx_item'),

    # add 
    path('add_client/', views.add_client_view, name='add_client'),
    path('add_session/', views.add_session_view, name='add_session'),

    # lists
    path('client_list/', views.clients_view, name='client_list'),
    path('client_search/', views.client_search_view, name='client_search'),
    path('session_list/', views.sessions_view, name='session_list'),
    path('session_search/', views.sessions_search, name='session_search'),
    path('client_archived/', views.client_archived_view, name='client_archived'),

    # edit
    path('edit_client/<uuid:client_pk>/', views.edit_client_view, name='edit_client'),
    path('edit_session/<uuid:session_pk>/', views.edit_session_view, name='edit_session'),

# hx auxiliar 
    path('clients_edit/<uuid:client_pk>/', views.clients_hx_edit, name='clients_edit'),
    path('sessions_hx_edit_open/<uuid:session_pk>/', views.sessions_hx_edit_open, name='sessions_hx_edit_open'),
    path('sessions_hx_edit_paid/<uuid:session_pk>/', views.sessions_hx_edit_paid, name='sessions_hx_edit_paid'),
    path('hx_client_short_form/', views.hx_client_short_form, name='hx_client_short_form'),
    path('hx_delete_session/<uuid:session_pk>/', views.hx_delete_session, name='hx_delete_session'),

# data
    path('sessions_search_csv/', views.sessions_search_csv, name='sessions_search_csv'),



]
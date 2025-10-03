"""Defines URL patterns for session_client."""

from django.urls import path

from . import views_session, views_client

app_name = 'session_client'

urlpatterns = [
    #Home page
    path('', views_session.index_view, name='index'),

    # Client views

    path('client-hx/<uuid:client_pk>/',
         views_client.client_hx_item, name='client_hx_item'),
    path('add_client/',
         views_client.add_client_view, name='add_client'),
    path('client_list/',
         views_client.clients_view, name='client_list'),
    path('client_search/',
         views_client.client_search_view, name='client_search'),
    path('client_archived/',
         views_client.client_archived_view, name='client_archived'),
    path('edit_client/<uuid:client_pk>/',
         views_client.edit_client_view, name='edit_client'),
    path('hx_client_short_form/',
         views_client.hx_client_short_form, name='hx_client_short_form'),
    path('clients_edit/<uuid:client_pk>/',
         views_client.clients_hx_edit, name='clients_edit'),

    # Session Views

    path('session-hx/<uuid:session_pk>/',
         views_session.session_hx_item, name='session_hx_item'),
    path('add_session/',
         views_session.add_session_view, name='add_session'),
    path('session_list/',
         views_session.sessions_view, name='session_list'),
    path('session_search/',
         views_session.sessions_search, name='session_search'),
    path('edit_session/<uuid:session_pk>/',
         views_session.edit_session_view, name='edit_session'),
    path('sessions_hx_edit_open/<uuid:session_pk>/',
         views_session.sessions_hx_edit_open, name='sessions_hx_edit_open'),
    path('sessions_hx_edit_paid/<uuid:session_pk>/',
         views_session.sessions_hx_edit_paid, name='sessions_hx_edit_paid'),
    path('hx_delete_session/<uuid:session_pk>/',
         views_session.hx_delete_session, name='hx_delete_session'),



]
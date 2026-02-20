"""Defines URL patterns for session_client."""

from django.urls import path

from . import views_session, views_client, views_time

app_name = 'session_client'

urlpatterns = [

    # Client views

    path('client-hx/<uuid:client_uuid>/',
         views_client.client_hx_item, name='client_hx_item'),
    path('add_client/',
         views_client.add_client_view, name='add_client'),
    path('client_list/',
         views_client.clients_view, name='client_list'),
    path('client_search/',
         views_client.client_search_view, name='client_search'),
    path('client_review/',
         views_session.sessions_search, {"review": True},
         name='client_review'),  # same view, different HTML
    path('client_archived/',
         views_client.client_archived_view, name='client_archived'),
    path('edit_client/<uuid:client_uuid>/',
         views_client.edit_client_view, name='edit_client'),
    path('hx_client_short_form/',
         views_client.hx_client_short_form, name='hx_client_short_form'),
    path('clients_edit/<uuid:client_uuid>/',
         views_client.clients_toggle_active, name='client_toggle_active'),

    path('clients_week_add/',
         views_client.week_view_add_client, name='week_view_add_client'),
    path('clients_week_add/<int:weekday>/<str:time>/',
         views_client.week_view_add_client, name='week_view_add_client'),
    path('clients_week_add/<int:weekday>/<str:time>/<uuid:calendar>/',
         views_client.week_view_add_client, name='week_view_add_client_with_calendar'),

    # Session Views

    path('session-hx/<uuid:session_uuid>/',
         views_session.session_hx_item, name='session_hx_item'),
    path('add_session/',
         views_session.add_session_view, name='add_session'),
    path('session_list/',
         views_session.sessions_view, name='session_list'),
    path('session_list/<uuid:client_uuid>/',
         views_session.sessions_view, name='session_list_with_client'),
    path('session_list/<uuid:client_uuid>/<str:add_forward>/',
         views_session.sessions_view, name='session_list_with_client_and_forward'),
    path('session_search/',
         views_session.sessions_search, name='session_search'),
    path('session_list_modal/<uuid:client_uuid>/',
         views_session.session_list_forward_modal, name='session_list_modal'),
    path('session_pending_list_modal/<uuid:client_uuid>/',
         views_session.session_pending_list_modal, name='session_pending_list_modal'),
    path('edit_session/<uuid:session_uuid>/',
         views_session.edit_session_view, name='edit_session'),
    path('sessions_hx_edit_open/<uuid:session_uuid>/',
         views_session.sessions_hx_edit_open, name='sessions_hx_edit_open'),
    path('sessions_hx_edit_paid/<uuid:session_uuid>/',
         views_session.sessions_hx_edit_paid, name='sessions_hx_edit_paid'),
    path('sessions_hx_edit_attendance/<uuid:session_uuid>/<str:attendance>',
         views_session.sessions_hx_edit_attendance, name='sessions_hx_edit_attendance'),
    path('sessions_patch_attendance/<uuid:session_uuid>/',
         views_session.sessions_patch_attendance, name='session_patch_attendance'),
    path('hx_delete_session/<uuid:session_uuid>/',
         views_session.hx_delete_session, name='hx_delete_session'),
    path('patch_brief_session/<uuid:session_uuid>/',
         views_session.patch_brief_view, name='session_patch_brief'),
    path('add_copy_session/<uuid:session_uuid>/',
         views_session.add_copy_forward_view, name='session_add_copy'),
    path('add_series/<uuid:client_uuid>/<int:number>/',
         views_session.add_series_view, name='add_series'),

    # create a htmx response that sends back a modal with forms to add a quick sessin reference
    path("hx-week_view_add_session_client/",
         views_session.week_view_add_session_client, name="week_view_add_session_client"),
    path("hx-week_view_add_session_client/<int:year>/<int:week>/<int:week_day>/<str:time>/",
         views_session.week_view_add_session_client, name="week_view_add_session_client"),
    path("hx-week_view_add_session_client/<int:year>/<int:week>/<int:week_day>/<str:time>/<uuid:calendar_uuid>/",
         views_session.week_view_add_session_client, name="week_view_add_session_client"),

    # time views
    path("add-client-time/", views_time.add_time, name="add_client_time"),
    path("add-client-time/<int:week_day>/<str:time>", views_time.add_time, name="add_client_time_with_time"),
    path("edit-client-time/<int:time_pk>", views_time.edit_time, name="edit_client_time"),
    path("manage-client-times/<uuid:client_uuid>", views_time.manage_times, name="manage_client_times"),
]

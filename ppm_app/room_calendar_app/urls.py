from django.urls import path
from room_calendar_app import views

app_name = 'room_calendar_app'

urlpatterns = [

    path("", views.index_view , name="calendar_index"),
    path("event/<uuid:event_pk>/", views.event_occurrence_view, name="event"),


    path("event-add-list/", views.event_listing_view, name="event_list"),
    path("occurrence-list/", views.occurrence_listing_view, name="occurrence_list"),
    path("room-calendar/<uuid:calendar_pk>/", views.room_calendar_view, name="room_calendar"),
    path("room-calendar-list/", views.room_calendar_listing_view, name="room_calendar_list"),
    path("tenant-list/", views.tenant_listing_view, name="tenant_list"),
    path("tenant/<uuid:tenant_pk>/", views.tenant_view, name="tenant"),
    
    path("event-add/", views.event_add_view, name="add_event"),
    path("event-edit/<uuid:event_pk>/", views.event_edit_view, name="edit_event"),
    
    path("tenant-add/", views.tenant_add_view, name="add_tenant"),
    path("tenant-edit/<uuid:tenant_pk>/", views.tenant_edit_view, name="edit_tenant"),
   
    path("room-calendar-add/", views.room_calendar_add_view, name="add_room_calendar"),
    path("room-calendar-edit/<uuid:room_calendar_pk>/", views.room_calendar_edit_view, name="edit_room_calendar"),
     
    path("occurrence-edit/<uuid:occurrence_pk>", views.edit_occurrence_list, name="edit_occurrence_list"),
    path("occurrence-multiple_add/", views.occurrence_multiple_add_view, name="add_occurrence_multiple"),
    path("occurrence-multiple-edit/", views.occurrence_multiple_edit_view, name="edit_occurrence_multiple"),

    path("day-view/", views.occurrence_multiple_edit_view, name="day-view"), #todo
    path("week-view/", views.week_view, name="week_view"),#todo

    path("link-tenant/<uuid:calendar_pk>/", views.tenant_link_view, name="link_tenant"),

]
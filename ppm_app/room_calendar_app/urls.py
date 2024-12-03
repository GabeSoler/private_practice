from django.urls import path
from room_calendar_app import views

app_name = 'room_calendar_app'

urlpatterns = [

    path("/", views.room_calendars_view , name="calendar_index"),
    path("event", views.event_view, name="event"),
    path("event-list", views.event_listing, name="event_list"),
    
    path("event-add", views.event_add_view, name="event_add"),
    path("event-multiple", views.event_multiple_view, name="event_multiple"),
    path("event-multiple-edit", views.event_multiple_view, name="event_multiple_edit"),
    path("event-list", views.event_listing, name="event_list"),
    path("event-list", views.event_listing, name="event_list"),

]
from django.urls import path
from room_calendar_app import views

app_name = 'room_calendar_app'

urlpatterns = [

    path("room-calendar/<uuid:calendar_pk>/", views.room_calendar_view, name="room_calendar"),
    path("room-calendar-list/", views.room_calendar_listing_view, name="room_calendar_list"),
    path("room-calendar-manage/", views.room_calendar_manage_view, name="room_calendar_manage"),
    path("profile-list/", views.tenant_listing_view, name="tenant_list"),
    path("profile/<uuid:tenant_pk>/", views.tenant_view, name="tenant"),
    
    
    path("profile-add/", views.tenant_add_view, name="add_tenant"),
    path("profile-edit/<uuid:tenant_pk>/", views.tenant_edit_view, name="edit_tenant"),
   
    path("room-calendar-add/", views.room_calendar_add_view, name="add_room_calendar"),
    path("room-calendar-edit/<uuid:room_calendar_pk>/", views.room_calendar_edit_view, name="edit_room_calendar"),
     

    path("week-view/", views.week_view, name="week_view"),#todo

    path("link-tenant/<uuid:calendar_pk>/", views.tenant_link_view, name="link_tenant"),
    path("unlink-tenant/<uuid:tenant_pk>/", views.tenant_unlink_view, name="unlink_tenant"),


    path("hx-client-list/", views.week_view_auxiliary, name="client_list_auxiliary"),


]
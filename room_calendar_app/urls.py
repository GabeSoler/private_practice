from django.urls import path
from room_calendar_app import views

app_name = 'room_calendar_app'

urlpatterns = [

    path("room-calendar-list/", views.room_calendar_listing_view, name="room_calendar_list"),
    path("room-list-refresh/", views.room_list_refresh_view, name="room_list_refresh"),
    path("room-calendar-manage/", views.room_calendar_manage_view, name="room_calendar_manage"),
    path("room-manage-refresh/<uuid:cal_uuid>", views.room_manage_refresh_view, name="room_manage_refresh"),
    path("room-calendar-report/", views.room_report_view, name="room_report"),

    path("profile-list/", views.tenant_listing_view, name="tenant_list"),
    path("profile/<uuid:tenant_uuid>/", views.tenant_view, name="tenant"),
    path("duplicate-profile/<uuid:tenant_uuid>/", views.tenant_duplicate_hx, name="duplicate_tenant"),
    path("delete-profile/<uuid:tenant_uuid>/", views.tenant_delete_hx, name="delete_tenant"),

    path("profile-add/", views.tenant_add_view, name="add_tenant"),
    path("profile-edit/<uuid:tenant_uuid>/", views.tenant_edit_view, name="edit_tenant"),

    path("room-calendar-add/", views.room_calendar_add_view, name="add_room_calendar"),
    path("room-calendar-edit/<uuid:room_calendar_uuid>/", views.room_calendar_edit_view, name="edit_room_calendar"),

    path("week-view/", views.week_view, name="week_view"),
    path("week-blocks-view/", views.week_blocks_view, name="week_blocks_view"),
    path("week-schedule-view/", views.week_schedule_view, name="week_schedule_view"),

    path("link-tenant/<uuid:tenant_uuid>/", views.tenant_link_view, name="link_tenant"),
    path("unlink-tenant/<uuid:tenant_uuid>/", views.tenant_unlink_view, name="unlink_tenant"),

    path("block-edit/<int:block_pk>/", views.block_edit_view, name="block_edit"),
    path("block-add/", views.block_add_view, name="block_add_view"),
    path("block-add/<int:day>/<str:time>", views.block_add_view, name="block_add_with_day_time"),
    path("block-add/<int:day>/<str:time>/<int:room>", views.block_add_view, name="block_add_with_room_day_time"),
    path("block-add-with-room/<int:room>", views.block_add_view, name="block_add_with_room"),

    path("block-delete/<uuid:block_uuid>/", views.block_delete_view, name="delete_block"),

]

from django.contrib import admin
from room_calendar_app.models import RoomCalendarModel,TenantModel





class RoomCalendarAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "description")
    list_filter = ("name",)
    search_fields = ("name",)

admin.site.register(RoomCalendarModel,RoomCalendarAdmin)


class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "description","id")


admin.site.register(TenantModel,TenantAdmin)

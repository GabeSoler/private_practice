from django.contrib import admin
from room_calendar_app.models import *




class OccurrenceInline(admin.TabularInline):
    model = OccurrenceModel
    extra = 1

class MultiOccurrenceInline(admin.TabularInline):
    model = MultiOccurrenceModel


class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "event_type", "description")
    list_filter = ("event_type",)
    search_fields = ("title", "description")
    inlines = [MultiOccurrenceInline, OccurrenceInline]



admin.site.register(Event, EventAdmin)



class RoomCalendarAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "description")
    list_filter = ("name",)
    search_fields = ("name",)

admin.site.register(RoomCalendarModel,RoomCalendarAdmin)


class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "description","id")


admin.site.register(TenantModel,TenantAdmin)

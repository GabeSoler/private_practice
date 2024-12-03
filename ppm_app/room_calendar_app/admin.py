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


class TenantInline(admin.TabularInline):
    model = TenantModel


class RoomCalendarAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "description","tenants")
    list_filter = ("name",)
    search_fields = ("name", "tenants")
    inlines = [RoomCalendarModel, TenantInline]


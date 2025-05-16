from django.contrib import admin
from .models import ClientModel,SessionModel



class SessionAdmin(admin.ModelAdmin):
    list_display = ("updated_at", "client", "title")
    list_filter = ("updated_at",)
    search_fields = ("updated_at", "client","notes","title")

class ClientAdmin(admin.ModelAdmin):
    list_display = ("updated_at", "code", "type")
    list_filter = ("updated_at",)
    search_fields = ("code", "type","nick_name","updated_at")



admin.site.register(ClientModel, ClientAdmin)
admin.site.register(SessionModel, SessionAdmin)


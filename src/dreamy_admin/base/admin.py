from django.contrib import admin
from .models import Page


# Register your models here.

class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "modified")
    list_filter = ("modified",)
    search_fields = ("modified", "title")


admin.site.register(Page, PageAdmin)

from django.contrib import admin

from gallery.models import ActivityPhoto
from .models import Activity, ActivityLink, ActivityFile


class LinkInline(admin.StackedInline):
    model = ActivityLink


class FileInline(admin.StackedInline):
    model = ActivityFile


class PhotoInline(admin.StackedInline):
    model = ActivityPhoto


class ActivityAdmin(admin.ModelAdmin):
    inlines = [LinkInline, FileInline, PhotoInline]


admin.site.register(Activity, ActivityAdmin)

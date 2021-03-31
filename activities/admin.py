from django.contrib import admin

from activities_files.models import ActivityFile
from activities_links.models import ActivityLink
from gallery.models import ActivityPhoto
from .models import Activity


class LinkInline(admin.StackedInline):
    model = ActivityLink


class FileInline(admin.StackedInline):
    model = ActivityFile


class PhotoInline(admin.StackedInline):
    model = ActivityPhoto


class ActivityAdmin(admin.ModelAdmin):
    inlines = [LinkInline, FileInline, PhotoInline]


admin.site.register(Activity, ActivityAdmin)

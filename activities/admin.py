from django.contrib import admin

from .models import Activity, ActivityLink


class LinkInline(admin.StackedInline):
    model = ActivityLink


class ActivityAdmin(admin.ModelAdmin):
    inlines = [LinkInline]


admin.site.register(Activity, ActivityAdmin)

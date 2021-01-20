from django.contrib import admin
from .models import Activity, Presenter, Attender, ActivityRelatedLink
from gallery.models import Picture

class PresenterInline(admin.StackedInline):
    model = Presenter


class AttenderInline(admin.StackedInline):
    model = Attender


class ActivityRelatedLinkInline(admin.StackedInline):
    model = ActivityRelatedLink


class PictureInline(admin.StackedInline):
    model = Picture


class ActivityAdmin(admin.ModelAdmin):
    inlines = [PresenterInline, AttenderInline, ActivityRelatedLinkInline, PictureInline]


admin.site.register(Activity, ActivityAdmin)

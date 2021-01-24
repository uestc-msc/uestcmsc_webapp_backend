from django.contrib import admin
from .models import Activity, ActivityRelatedLink
from gallery.models import Photo

# class PresenterInline(admin.StackedInline):
#     model = Presenter
#
#
# class AttenderInline(admin.StackedInline):
#     model = Attender


class ActivityRelatedLinkInline(admin.StackedInline):
    model = ActivityRelatedLink


class PictureInline(admin.StackedInline):
    model = Photo


class ActivityAdmin(admin.ModelAdmin):
    inlines = [ActivityRelatedLinkInline, PictureInline]


admin.site.register(Activity, ActivityAdmin)

from django.contrib import admin
from .models import Activity, ActivityURL
from gallery.models import Photo

# class PresenterInline(admin.StackedInline):
#     model = Presenter
#
#
# class AttenderInline(admin.StackedInline):
#     model = Attender


class ActivityURLInline(admin.StackedInline):
    model = ActivityURL


class PictureInline(admin.StackedInline):
    model = Photo


class ActivityAdmin(admin.ModelAdmin):
    inlines = [ActivityURLInline, PictureInline]


admin.site.register(Activity, ActivityAdmin)

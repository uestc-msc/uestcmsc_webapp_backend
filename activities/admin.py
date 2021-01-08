from django.contrib import admin
from .models import Activity, Presenter, Attender


# Register your models here.
class PresenterInline(admin.StackedInline):
    model = Presenter


class AttenderInline(admin.StackedInline):
    model = Attender


class ActivityAdmin(admin.ModelAdmin):
    inlines = [PresenterInline, AttenderInline]


admin.site.register(Activity, ActivityAdmin)

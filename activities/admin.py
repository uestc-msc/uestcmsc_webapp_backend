from django.contrib import admin
from .models import Activity, Presenter, Attender
# Register your models here.

admin.site.register(Activity)
admin.site.register(Presenter)
admin.site.register(Attender)
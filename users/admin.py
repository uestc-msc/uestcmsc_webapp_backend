from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import *


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


class UserAdmin(admin.ModelAdmin):
    read_only_fields = ('last_login', 'date_joined')
    fields = ('username',
              'first_name', 'last_name',
              'is_staff', 'is_superuser',
              'last_login', 'date_joined')
    inlines = [UserProfileInline]


# Register your models here.
admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
admin.site.register(ResetPasswordRequest)

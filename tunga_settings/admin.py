from django.contrib import admin

from tunga_settings.models import UserSwitchSetting


@admin.register(UserSwitchSetting)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'setting', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('body',)

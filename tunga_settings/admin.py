from django.contrib import admin

from tunga_settings.models import UserSwitchSetting, SwitchSetting


@admin.register(UserSwitchSetting)
class UserSwitchSettingAdmin(admin.ModelAdmin):
    list_display = ('user', 'setting', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user',)


@admin.register(SwitchSetting)
class SwitchSettingAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name',)

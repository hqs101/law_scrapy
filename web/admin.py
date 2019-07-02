from django.contrib import admin
from web.models import LawNature, SettingItem
# Register your models here.


class LawNatureAdmin(admin.ModelAdmin):
    list_display = ['source', 'title']
    list_display_links = list_display


class SettingItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_url']
    list_display_links = list_display


admin.site.register(LawNature, LawNatureAdmin)
admin.site.register(SettingItem, SettingItemAdmin)

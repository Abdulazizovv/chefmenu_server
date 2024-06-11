from django.contrib import admin
from .models import BotUsers
# Register your models here.

class BotUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username', 'phone_number', 'first_name', 'last_name', 'language_code', 'is_bot')
    search_fields = ('user_id', 'username', 'phone_number', 'first_name', 'last_name', 'language_code', 'is_bot')
    list_filter = ('is_bot', 'language_code', 'created', 'updated', 'phone_number')
    list_per_page = 20
    list_display_links = ('user_id', 'username')
    list_editable = ('phone_number', 'first_name', 'last_name', 'language_code', 'is_bot')

admin.site.register(BotUsers, BotUserAdmin)
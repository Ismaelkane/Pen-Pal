# translator/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Conversation, UserConversation, Message, groupConversation, GroupMessage

class CustomUserAdmin(UserAdmin):
    # Extend the default fieldsets to include the language field on the user detail page
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('language', 'language_text')}),
    )
    # Also add the language field when creating a new user
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('language', 'language_text')}),
    )
    # Display language in the user list view
    list_display = UserAdmin.list_display + ('language','language_text')

class CustomAdminSite(admin.AdminSite):
    site_header = "Custom Admin"

custom_admin_site = CustomAdminSite(name='custom_admin')
custom_admin_site.register(CustomUser, UserAdmin)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'text', 'translated_text', 'language', 'timestamp')
    search_fields = ('sender__username', 'receiver__username', 'text')

admin.site.register(Conversation)
admin.site.register(UserConversation)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Message)
admin.site.register(groupConversation)
admin.site.register(GroupMessage)

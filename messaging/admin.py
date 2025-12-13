"""
Admin configuration for messaging app
"""
from django.contrib import admin
from .models import MessageThread, Message


@admin.register(MessageThread)
class MessageThreadAdmin(admin.ModelAdmin):
    """Message Thread admin."""
    list_display = ['id', 'order', 'created_at']
    filter_horizontal = ['participants']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Message admin."""
    list_display = ['thread', 'sender', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['content', 'sender__username']

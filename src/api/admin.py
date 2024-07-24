from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Conversation, Message


class ConversationAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at", "updated_at", "reset"]
    list_filter = ["reset", "created_at", "updated_at"]
    search_fields = ["user__email"]


class MessageAdmin(admin.ModelAdmin):
    list_display = ["conversation", "role", "content", "created_at"]
    list_filter = ["role", "created_at"]
    search_fields = ["conversation__user__email", "content"]


admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Message, MessageAdmin)

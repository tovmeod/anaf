"""
Messaging module: Admin page
"""
from treeio.messaging.models import Message, MessageStream
from django.contrib import admin


class MessageStreamAdmin(admin.ModelAdmin):

    """ Message stream admin """
    list_display = ('name', 'last_checked')
    search_fields = ('name', 'last_checked')


class MessageAdmin(admin.ModelAdmin):

    """ Message admin """
    list_display = ('title', 'body', 'author', 'stream', 'reply_to')
    search_fields = ('title', 'author')

admin.site.register(MessageStream, MessageStreamAdmin)
admin.site.register(Message, MessageAdmin)

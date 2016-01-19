"""
Change management: admin page
"""
from models import Change, ChangeSet
from django.contrib import admin


class ChangeAdmin(admin.ModelAdmin):
    """ Change admin """
    list_display = (
        'change_set', 'change_type', 'field', 'change_from', 'change_to')


class ChangeSetAdmin(admin.ModelAdmin):

    """ Change request admin """
    list_display = (
        'object', 'author', 'resolved_by', 'resolved_on', 'status', 'name')
    list_filter = ['status']

admin.site.register(Change, ChangeAdmin)
admin.site.register(ChangeSet, ChangeSetAdmin)

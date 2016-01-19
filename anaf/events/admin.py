"""
Events: admin page
"""
from models import Event
from django.contrib import admin


class EventAdmin(admin.ModelAdmin):

    """ Event admin """
    list_display = ('name', 'start', 'end')

admin.site.register(Event, EventAdmin)

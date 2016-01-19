# -*- coding: utf-8 -*-

from __future__ import absolute_import, with_statement

__all__ = ['EventHandler']

from anaf.events.models import Event
from anaf.events.forms import EventForm
from anaf.core.api.handlers import ObjectHandler


class EventHandler(ObjectHandler):
    "Entrypoint for Event model."
    model = Event
    form = EventForm

    @classmethod
    def resource_uri(cls, obj=None):
        object_id = "id"
        if obj is not None:
            object_id = obj.id
        return ('api_events', [object_id])

    def check_create_permission(self, request, mode):
        return True

    def flatten_dict(self, request):
        dct = super(self.__class__, self).flatten_dict(request)
        dct["date"] = None
        dct["hour"] = None
        return dct

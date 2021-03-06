# -*- coding: utf-8 -*-

from __future__ import absolute_import, with_statement

__all__ = ['UpdateRecordHandler']

from anaf.core.api.utils import rc
from piston3.handler import BaseHandler
from anaf.core.models import UpdateRecord
from anaf.news.forms import UpdateRecordForm
from anaf.news.views import _get_filter_query


class UpdateRecordHandler(BaseHandler):
    "Entrypoint for UpdateRecord model."

    model = UpdateRecord
    form = UpdateRecordForm
    allowed_methods = ('GET', 'DELETE')
    fields = ('id', 'full_message', 'author', 'sender')

    @classmethod
    def resource_uri(cls, obj=None):
        object_id = "id"
        if obj is not None:
            object_id = obj.id
        return ('api_news_update_records', [object_id])

    def read(self, request, record_id=None, *args, **kwargs):
        "Function shows messages in the news"
        profile = request.user.profile
        query = _get_filter_query(profile, filters=request.GET)
        try:
            if record_id:
                return UpdateRecord.objects.filter(query).get(id=record_id)
            else:
                return UpdateRecord.objects.filter(query).distinct()
        except self.model.DoesNotExist:
            return rc.NOT_FOUND
        # should never happen, since we're using a PK
        except self.model.MultipleObjectsReturned:
            return rc.BAD_REQUEST

    def delete(self, request, record_id=None, *args, **kwargs):
        "Function deletes object with record_id"
        if not record_id:
            return rc.BAD_REQUEST
        try:
            inst = self.model.objects.get(pk=record_id)
            inst.delete()
            return rc.DELETED
        except self.model.MultipleObjectsReturned:
            return rc.DUPLICATE_ENTRY
        except self.model.DoesNotExist:
            return rc.NOT_HERE

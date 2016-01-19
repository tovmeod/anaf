# -*- coding: utf-8 -*-

import handlers
from django.conf.urls import *
from anaf.core.api.auth import auth_engine
from anaf.core.api.doc import documentation_view
from anaf.core.api.resource import CsrfExemptResource

ad = {'authentication': auth_engine}

# news resources
updateRecordsResource = CsrfExemptResource(
    handler=handlers.UpdateRecordHandler, **ad)

urlpatterns = patterns('',
                       # News
                       url(r'^doc$', documentation_view, kwargs={
                           'module': handlers}, name="api_news_doc"),
                       url(r'^records$', updateRecordsResource,
                           name="api_news_update_records"),
                       url(r'^record/(?P<record_id>\d+)', updateRecordsResource,
                           name="api_news_update_records"),
                       )

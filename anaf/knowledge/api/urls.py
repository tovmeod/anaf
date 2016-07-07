# -*- coding: utf-8 -*-

import handlers
from django.conf.urls import url, patterns
from anaf.core.api.auth import auth_engine
from anaf.core.api.doc import documentation_view
from anaf.core.api.resource import CsrfExemptResource

ad = {'authentication': auth_engine}

# knowledge resources
folderResource = CsrfExemptResource(
    handler=handlers.KnowledgeFolderHandler, **ad)
categoryResource = CsrfExemptResource(
    handler=handlers.KnowledgeCategoryHandler, **ad)
itemResource = CsrfExemptResource(handler=handlers.KnowledgeItemHandler, **ad)

urlpatterns = patterns('',
                       # Knowledge
                       url(r'^doc$', documentation_view, kwargs={'module': handlers}, name="api_knowledge_doc"),
                       url(r'^folders$', folderResource, name='api_knowledge_folders'),
                       url(r'^folder/(?P<object_ptr>\d+)', folderResource, name='api_knowledge_folders'),
                       url(r'^categories$', categoryResource, name='api_knowledge_categories'),
                       url(r'^category/(?P<object_ptr>\d+)', categoryResource, name='api_knowledge_categories'),
                       url(r'^items$', itemResource, name='api_knowledge_items'),
                       url(r'^item/(?P<object_ptr>\d+)', itemResource, name='api_knowledge_items'),
                       )

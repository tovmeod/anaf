# -*- coding: utf-8 -*-

import handlers
from django.conf.urls import url, patterns
from anaf.core.api.auth import auth_engine
from anaf.core.api.doc import documentation_view
from anaf.core.api.resource import CsrfExemptResource

ad = {'authentication': auth_engine}

# documents resources
folderResource = CsrfExemptResource(handler=handlers.FolderHandler, **ad)
fileResource = CsrfExemptResource(handler=handlers.FileHandler, **ad)
documentResource = CsrfExemptResource(handler=handlers.DocumentHandler, **ad)
weblinkResource = CsrfExemptResource(handler=handlers.WebLinkHandler, **ad)

urlpatterns = patterns('',
                       # Documents
                       url(r'^doc$', documentation_view, kwargs={'module': handlers}, name="api_documents_doc"),
                       url(r'^folders$', folderResource, name="api_documents_folders"),
                       url(r'^folder/(?P<object_ptr>\d+)', folderResource, name="api_documents_folders"),
                       url(r'^files$', fileResource, name="api_documents_files"),
                       url(r'^file/(?P<object_ptr>\d+)', fileResource, name="api_documents_files"),
                       url(r'^documents$', documentResource, name="api_documents_documents"),
                       url(r'^document/(?P<object_ptr>\d+)', documentResource, name="api_documents_documents"),
                       url(r'^weblinks$', weblinkResource, name="api_documents_weblinks"),
                       url(r'^weblink/(?P<object_ptr>\d+)', weblinkResource, name="api_documents_weblinks"),
                       )

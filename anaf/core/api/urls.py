from django.conf.urls import *

urlpatterns = patterns('',
                       (r'^auth/', include('anaf.core.api.auth.urls')),
                       (r'^news/', include('anaf.news.api.urls')),
                       (r'^core/', include('anaf.core.administration.api.urls')),
                       (r'^projects/', include('anaf.projects.api.urls')),
                       (r'^services/', include('anaf.services.api.urls')),
                       (r'^sales/', include('anaf.sales.api.urls')),
                       (r'^finance/', include('anaf.finance.api.urls')),
                       (r'^knowledge/', include('anaf.knowledge.api.urls')),
                       (r'^messaging/', include('anaf.messaging.api.urls')),
                       (r'^infrastructure/', include('anaf.infrastructure.api.urls')),
                       (r'^calendar/', include('anaf.events.api.urls')),
                       (r'^documents/', include('anaf.documents.api.urls')),
                       (r'^identities/', include('anaf.identities.api.urls')),
                       )

from django.conf.urls import url, patterns, include
from django.contrib import admin
from dajaxice.core import dajaxice_autodiscover, dajaxice_config

admin.autodiscover()
dajaxice_autodiscover()


urlpatterns = patterns('',
                       url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
                       url(r'^(\.(?P<response_format>\w+))?$', 'anaf.core.dashboard.views.index', name='home'),

                       # modules
                       (r'^user/', include('anaf.core.urls')),
                       (r'^accounts/', include('anaf.core.urls')),
                       (r'^account/', include('anaf.account.urls')),
                       (r'^search/', include('anaf.core.search.urls')),
                       (r'^dashboard/', include('anaf.core.dashboard.urls')),
                       (r'^admin/', include('anaf.core.administration.urls')),
                       (r'^trash', include('anaf.core.trash.urls')),
                       (r'^documents/', include('anaf.documents.urls')),
                       (r'^calendar/', include('anaf.events.urls')),
                       (r'^finance/', include('anaf.finance.urls')),
                       (r'^contacts', include('anaf.identities.urls', namespace='contacts')),
                       (r'^infrastructure/', include('anaf.infrastructure.urls')),
                       (r'^knowledge/', include('anaf.knowledge.urls')),
                       (r'^messaging/', include('anaf.messaging.urls')),
                       (r'^news/', include('anaf.news.urls')),
                       (r'^projects', include('anaf.projects.urls')),
                       (r'^sales/', include('anaf.sales.urls')),
                       (r'^services/', include('anaf.services.urls')),
                       (r'^reports/', include('anaf.reports.urls')),

                       # API handlers
                       (r'^api/', include('anaf.core.api.urls')),
                       # Mobile handler
                       url(r'^m(?P<url>.+)?$', 'anaf.core.views.mobile_view',
                           name='core_mobile_view'),
                       # Help handler
                       url(r'^help(?P<url>[a-zA-Z0-9-_/]+)?(\.(?P<response_format>\w+))?$',
                           'anaf.core.views.help_page', name='core_help_page_view'),
                       # Close iframe
                       url(r'^iframe/?$', 'anaf.core.views.iframe_close',
                           name='core_iframe_close'),

                       # Captcha Config
                       url(r'^captcha/', include('captcha.urls')),

                       url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),

                       # Change django admin to backend (because it's backend!)
                       (r'^backend/', include(admin.site.urls)),

                       )

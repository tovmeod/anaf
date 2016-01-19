from django.conf.urls import *
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin

from dajaxice.core import dajaxice_autodiscover, dajaxice_config

dajaxice_autodiscover()


def if_installed(appname, *args, **kwargs):
    ret = url(*args, **kwargs)
    if appname not in settings.INSTALLED_APPS:
        ret = url(r'^(\.(?P<response_format>\w+))?$',
                  'anaf.core.dashboard.views.index', name='home')
        # ret.resolve = lambda *args: None
    return ret

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
                       url(r'^(\.(?P<response_format>\w+))?$', 'anaf.core.dashboard.views.index', name='home'),
                       (r'^user/', include('anaf.core.urls')),
                       (r'^accounts/', include('anaf.core.urls')),
                       (r'^account/', include('anaf.account.urls')),
                       (r'^search/', include('anaf.core.search.urls')),
                       (r'^dashboard/', include('anaf.core.dashboard.urls')),
                       (r'^admin/', include('anaf.core.administration.urls')),
                       (r'^trash/', include('anaf.core.trash.urls')),
                       (r'^documents/', include('anaf.documents.urls')),
                       (r'^calendar/', include('anaf.events.urls')),
                       (r'^finance/', include('anaf.finance.urls')),
                       (r'^contacts/', include('anaf.identities.urls')),
                       (r'^infrastructure/', include('anaf.infrastructure.urls')),
                       (r'^knowledge/', include('anaf.knowledge.urls')),
                       (r'^messaging/', include('anaf.messaging.urls')),
                       (r'^news/', include('anaf.news.urls')),
                       (r'^projects/', include('anaf.projects.urls')),
                       (r'^sales/', include('anaf.sales.urls')),
                       (r'^services/', include('anaf.services.urls')),
                       (r'^reports/', include('anaf.reports.urls')),

                       # API handlers
                       (r'^api/', include('anaf.core.api.urls')),

                       # Forest
                       # if_installed('treeio.forest', r'^forest/', include('treeio.forest.urls')),

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

                       # Changed to backend (because it's backend!)
                       (r'^backend/', include(admin.site.urls)),
                       )

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
                            url(r'^rosetta/', include('rosetta.urls')),
                            )
if settings.DEBUG:
    # Dajaxice depends on django.contrib.staticfiles to handle it.
    # <STATIC_URL>/dajaxice.core.js is rendered by its DajaxiceFinder.
    urlpatterns += staticfiles_urlpatterns()
else:
    # django.contrib.staticfiles won't work if DEBUG = False, we need to handle
    # static files via django.views.static.serve.
    urlpatterns += patterns('',
                            (r'^static/(?P<path>.*)$', 'django.views.static.serve', {
                                'document_root': settings.STATIC_DOC_ROOT
                            }),
                            )

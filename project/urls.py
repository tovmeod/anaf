from django.conf.urls import url, patterns, include
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
                       (r'^', include('anaf.urls')),
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

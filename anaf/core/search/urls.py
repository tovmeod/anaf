"""
Core Search module URLs
"""

from django.conf.urls import patterns, url

urlpatterns = patterns('anaf.core.search.views',
                       url(r'^(\.(?P<response_format>\w+))?/?$',
                           'search_query', name='core_search_query'),
                       )

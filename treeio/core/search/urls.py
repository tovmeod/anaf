"""
Core Search module URLs
"""

from django.conf.urls import patterns, url

urlpatterns = patterns('treeio.core.search.views',
                       url(r'^(\.(?P<response_format>\w+))?/?$',
                           'search_query', name='core_search_query'),
                       )

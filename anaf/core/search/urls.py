"""
Core Search module URLs
"""

from django.conf.urls import patterns, url

from anaf.core.search import views

urlpatterns = patterns('anaf.core.search.views',
                       url(r'^(\.(?P<response_format>\w+))?/?$', views.search_query, name='core_search_query'),
                       )

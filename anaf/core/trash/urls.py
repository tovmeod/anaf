"""
Core module Administration panel URLs
"""

from django.conf.urls import patterns, url

urlpatterns = patterns('anaf.core.trash.views',
                       url(r'^(\.(?P<response_format>\w+))?/?$',
                           'index', name='core_trash'),
                       url(r'^index(\.(?P<response_format>\w+))?/?$',
                           'index', name='core_trash_index'),

                       # Actions
                       url(r'^delete/(?P<object_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           'object_delete', name='core_trash_object_delete'),
                       url(r'^untrash/(?P<object_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           'object_untrash', name='core_trash_object_untrash'),
                       )

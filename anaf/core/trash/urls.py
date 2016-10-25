"""
Core module Administration panel URLs
"""

from django.conf.urls import patterns, url, include

from anaf.core.trash import views

urlpatterns = patterns('anaf.core.trash.views',
                       url(r'^/?(\.(?P<response_format>\w+))?/?$', 'index', name='core_trash'),
                       url(r'^/', include(patterns('',
                           url(r'^index(\.(?P<response_format>\w+))?/?$', views.index, name='core_trash_index'),

                           # Actions
                           url(r'^delete/(?P<object_id>\d+)(\.(?P<response_format>\w+))?/?$',
                               views.object_delete, name='core_trash_object_delete'),
                           url(r'^untrash/(?P<object_id>\d+)(\.(?P<response_format>\w+))?/?$',
                               views.object_untrash, name='core_trash_object_untrash'),
                                                   )
                                          )
                           )
                       )

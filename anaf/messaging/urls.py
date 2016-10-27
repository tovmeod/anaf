"""
Messaging module URLs
"""
from django.conf.urls import url, patterns

from anaf.messaging import views

urlpatterns = patterns('anaf.messaging.views',
                       url(r'^(\.(?P<response_format>\w+))?$', views.index, name='messaging'),
                       url(r'^index(\.(?P<response_format>\w+))?$', views.index, name='messaging_index'),
                       url(r'^sent(\.(?P<response_format>\w+))?/?$', views.index_sent, name='messaging_sent'),
                       url(r'^inbox(\.(?P<response_format>\w+))?/?$', views.index_inbox, name='messaging_inbox'),
                       url(r'^unread(\.(?P<response_format>\w+))?/?$', views.index_unread, name='messaging_unread'),

                       # Messages
                       url(r'^compose(\.(?P<response_format>\w+))?/?$', views.messaging_compose,
                           name='messaging_message_compose'),
                       url(r'^view/(?P<message_id>\d+)(\.(?P<response_format>\w+))?/?$', views.messaging_view,
                           name='messaging_message_view'),
                       url(r'^delete/(?P<message_id>\d+)(\.(?P<response_format>\w+))?/?$', views.messaging_delete,
                           name='messaging_message_delete'),

                       # Streams
                       url(r'^stream/add(\.(?P<response_format>\w+))?/?$', views.stream_add,
                           name='messaging_stream_add'),
                       url(r'^stream/view/(?P<stream_id>\d+)(\.(?P<response_format>\w+))?/?$', views.stream_view,
                           name='messaging_stream_view'),
                       url(r'^stream/edit/(?P<stream_id>\d+)(\.(?P<response_format>\w+))?/?$', views.stream_edit,
                           name='messaging_stream_edit'),
                       url(r'^stream/delete/(?P<stream_id>\d+)(\.(?P<response_format>\w+))?/?$', views.stream_delete,
                           name='messaging_stream_delete'),
                       url(r'^stream/checkmail/(?P<stream_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           views.stream_checkmail, name='messaging_stream_checkmail'),

                       # Mailing Lists
                       url(r'^mlist/add(\.(?P<response_format>\w+))?/?$', views.mlist_add, name='messaging_mlist_add'),
                       url(r'^mlist/view/(?P<mlist_id>\d+)(\.(?P<response_format>\w+))?/?$', views.mlist_view,
                           name='messaging_mlist_view'),
                       url(r'^mlist/edit/(?P<mlist_id>\d+)(\.(?P<response_format>\w+))?/?$', views.mlist_edit,
                           name='messaging_mlist_edit'),
                       url(r'^mlist/delete/(?P<mlist_id>\d+)(\.(?P<response_format>\w+))?/?$', views.mlist_delete,
                           name='messaging_mlist_delete'),

                       # Administration
                       url(r'^settings/view(\.(?P<response_format>\w+))?/?$', views.settings_view,
                           name='messaging_settings_view'),
                       url(r'^settings/edit(\.(?P<response_format>\w+))?/?$', views.settings_edit,
                           name='messaging_settings_edit'),
                       )

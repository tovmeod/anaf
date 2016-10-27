"""
Events module URLs
"""
from django.conf.urls import patterns, url

from anaf.events import views

urlpatterns = patterns('anaf.events.views',
                       url(r'^(\.(?P<response_format>\w+))?$', views.month_view, name='events'),

                       url(r'^index(\.(?P<response_format>\w+))?$', views.index, name='events_index'),
                       url(r'^upcoming(\.(?P<response_format>\w+))?/?$', views.upcoming, name='events_upcoming'),

                       url(r'^month(\.(?P<response_format>\w+))?/?$', views.month_view, name='events_month'),
                       url(r'^week(\.(?P<response_format>\w+))?/?$', views.week_view, name='events_week'),
                       url(r'^day(\.(?P<response_format>\w+))?/?$', views.day_view, name='events_day'),

                       # Events
                       url(r'^event/add(\.(?P<response_format>\w+))?/?$', views.event_add, name='events_event_add'),
                       url(r'^event/add/(?P<date>[0-9\-]+)/(?P<hour>[0-9]+)?(\.(?P<response_format>\w+))?/?$',
                           views.event_add, name='events_event_add_to_date'),
                       url(r'^event/view/(?P<event_id>\d+)(\.(?P<response_format>\w+))?/?$', views.event_view,
                           name='events_event_view'),
                       url(r'^event/edit/(?P<event_id>\d+)(\.(?P<response_format>\w+))?/?$', views.event_edit,
                           name='events_event_edit'),
                       url(r'^event/delete/(?P<event_id>\d+)(\.(?P<response_format>\w+))?/?$', views.event_delete,
                           name='events_event_delete'),


                       # Export iCalendar
                       url(r'^ical/?$', views.ical_all_event, name='events_all_ical'),
                       )

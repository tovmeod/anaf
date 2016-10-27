"""
Core module Dashboard URLs
"""

from django.conf.urls import patterns, url

from anaf.core.dashboard import views

urlpatterns = patterns('anaf.core.dashboard.views',
                       url(r'^(\.(?P<response_format>\w+))?$', views.index, name='core_dashboard_index'),

                       # Widgets
                       url(r'^widget/add(\.(?P<response_format>\w+))?$', views.dashboard_widget_add,
                           name='core_dashboard_widget_add'),
                       url(r'^widget/add/(?P<module_name>[a-z\.]+)/(?P<widget_name>\w+)(\.(?P<response_format>\w+))?$',
                           views.dashboard_widget_add, name='core_dashboard_widget_add_selected'),
                       url(r'^widget/edit/(?P<widget_id>\d+)(\.(?P<response_format>\w+))?$',
                           views.dashboard_widget_edit, name='core_dashboard_widget_edit'),
                       url(r'^widget/delete/(?P<widget_id>\d+)(\.(?P<response_format>\w+))?$',
                           views.dashboard_widget_delete, name='core_dashboard_widget_delete'),

                       url(r'^widget/arrange/(?P<panel>\w+)?(\.(?P<response_format>\w+))?$',
                           views.dashboard_widget_arrange, name='core_dashboard_widget_arrange'),
                       )

"""
Reporting module URLs
"""
from django.conf.urls import patterns, url

from anaf.reports import views

urlpatterns = patterns('anaf.reports.views',
                       # Index pages
                       url(r'^(\.(?P<response_format>\w+))?$', views.index, name='reports'),
                       url(r'^index(\.(?P<response_format>\w+))?$', views.index, name='reports_index'),
                       url(r'^index/owned(\.(?P<response_format>\w+))?$', views.index_owned,
                           name='reports_index_owned'),

                       # Charts
                       url(r'^chart/(?P<chart_id>\d+)/options/(?P<div_id>[a-zA-Z0-9-]+)$', views._get_chart_ajax,
                           name='reports_get_chart_ajax'),
                       url(r'^chart/add/(?P<report_id>\d+)(\.(?P<response_format>\w+))?$', views.chart_add,
                           name='reports_chart_add'),
                       url(r'^chart/add/(\.(?P<response_format>\w+))?$', views.chart_add, name='reports_chart_add'),
                       url(r'^chart/edit/(?P<chart_id>\d+)(\.(?P<response_format>\w+))?$', views.chart_edit,
                           name='reports_chart_edit'),
                       url(r'^chart/delete/(?P<chart_id>\d+)(\.(?P<response_format>\w+))?/?$', views.chart_delete,
                           name='reports_chart_delete'),

                       # Reports
                       url(r'^report/edit/(?P<report_id>\d+)(\.(?P<response_format>\w+))?$', views.report_edit,
                           name='reports_report_edit'),
                       url(r'^report/add(\.(?P<response_format>\w+))?$', views.report_add, name='reports_report_add'),
                       url(r'^report/filter/(?P<report_id>\d+)/(?P<field_name>\w+)(\.(?P<response_format>\w+))?/?$',
                           views.report_filter, name='reports_report_filter'),
                       url(r'^report/filter/(?P<report_id>\d+)/(?P<field_name>\w+)/(?P<filter_index>\w+)(\.(?P<response_format>\w+))?/?$',
                           views.report_filter_remove, name='reports_report_filter_remove'),
                       url(r'^report/group/(?P<report_id>\d+)/(?P<field_name>\w+)(\.(?P<response_format>\w+))?/?$',
                           views.report_group, name='reports_report_group'),
                       url(r'^report/view/(?P<report_id>\d+)(\.(?P<response_format>\w+))?/?$', views.report_view,
                           name='reports_report_view'),
                       url(r'^report/delete/(?P<report_id>\d+)(\.(?P<response_format>\w+))?/?$', views.report_delete,
                           name='reports_report_delete'),
                       )

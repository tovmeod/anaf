"""
Infrastructure module URLs
"""
from django.conf.urls import patterns, url

from anaf.infrastructure import views

urlpatterns = patterns('anaf.infrastructure.views',
                       url(r'^(\.(?P<response_format>\w+))?$', views.index, name='infrastructure'),

                       url(r'^index(\.(?P<response_format>\w+))?$', views.index, name='infrastructure_index'),
                       url(r'^owned(\.(?P<response_format>\w+))?/?$', views.index_owned,
                           name='infrastructure_index_owned'),

                       # Types
                       url(r'^type/view/(?P<type_id>\d+)(\.(?P<response_format>\w+))?/?$', views.type_view,
                           name='infrastructure_type_view'),
                       url(r'^type/edit/(?P<type_id>\d+)(\.(?P<response_format>\w+))?/?$', views.type_edit,
                           name='infrastructure_type_edit'),
                       url(r'^type/delete/(?P<type_id>\d+)(\.(?P<response_format>\w+))?/?$', views.type_delete,
                           name='infrastructure_type_delete'),
                       url(r'^type/add(\.(?P<response_format>\w+))?/?$', views.type_add,
                           name='infrastructure_type_add'),

                       # Fields
                       url(r'^field/view/(?P<field_id>\d+)(\.(?P<response_format>\w+))?/?$', views.field_view,
                           name='infrastructure_field_view'),
                       url(r'^field/edit/(?P<field_id>\d+)(\.(?P<response_format>\w+))?/?$', views.field_edit,
                           name='infrastructure_field_edit'),
                       url(r'^field/delete/(?P<field_id>\d+)(\.(?P<response_format>\w+))?/?$',views.field_delete,
                           name='infrastructure_field_delete'),
                       url(r'^field/add(\.(?P<response_format>\w+))?/?$', views.field_add,
                           name='infrastructure_field_add'),

                       # Statuses
                       url(r'^status/view/(?P<status_id>\d+)(\.(?P<response_format>\w+))?/?$', views.status_view,
                           name='infrastructure_status_view'),
                       url(r'^status/edit/(?P<status_id>\d+)(\.(?P<response_format>\w+))?/?$', views.status_edit,
                           name='infrastructure_status_edit'),
                       url(r'^status/delete/(?P<status_id>\d+)(\.(?P<response_format>\w+))?/?$', views.status_delete,
                           name='infrastructure_status_delete'),
                       url(r'^status/add(\.(?P<response_format>\w+))?/?$', views.status_add,
                           name='infrastructure_status_add'),

                       # Items
                       url(r'^item/view/(?P<item_id>\d+)(\.(?P<response_format>\w+))?/?$', views.item_view,
                           name='infrastructure_item_view'),
                       url(r'^item/edit/(?P<item_id>\d+)(\.(?P<response_format>\w+))?/?$', views.item_edit,
                           name='infrastructure_item_edit'),
                       url(r'^item/delete/(?P<item_id>\d+)(\.(?P<response_format>\w+))?/?$', views.item_delete,
                           name='infrastructure_item_delete'),
                       url(r'^item/add(\.(?P<response_format>\w+))?/?$', views.item_add,
                           name='infrastructure_item_add'),
                       url(r'^item/add/(?P<type_id>\d+)(\.(?P<response_format>\w+))?/?$', views.item_add_typed,
                           name='infrastructure_item_add_typed'),

                       url(r'^settings/view(\.(?P<response_format>\w+))?/?$', views.settings_view,
                           name='infrastructure_settings_view'),
                       url(r'^settings/edit(\.(?P<response_format>\w+))?/?$', views.settings_edit,
                           name='infrastructure_settings_edit'),

                       # Service Records
                       url(r'^service_record/index(\.(?P<response_format>\w+))?/?$', views.service_record_index,
                           name='infrastructure_service_record_index'),
                       url(r'^service_record/view/(?P<service_record_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           views.service_record_view, name='infrastructure_service_record_view'),
                       url(r'^service_record/edit/(?P<service_record_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           views.service_record_edit, name='infrastructure_service_record_edit'),
                       url(r'^service_record/delete/(?P<service_record_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           views.service_record_delete, name='infrastructure_service_record_delete'),
                       url(r'^service_record/add(\.(?P<response_format>\w+))?/?$', views.service_record_add,
                           name='infrastructure_service_record_add'),

                       # Location
                       url(r'^location/view/(?P<location_id>\d+)(\.(?P<response_format>\w+))?/?$', views.location_view,
                           name='infrastructure_location_view'),
                       url(r'^location/edit/(?P<location_id>\d+)(\.(?P<response_format>\w+))?/?$', views.location_edit,
                           name='infrastructure_location_edit'),
                       url(r'^location/delete/(?P<location_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           views.location_delete, name='infrastructure_location_delete'),
                       url(r'^location/add(\.(?P<response_format>\w+))?/?$', views.location_add,
                           name='infrastructure_location_add'),
                       )

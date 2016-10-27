from django.conf.urls import patterns, url, include
from anaf.identities.api import views
from rest_framework.routers import DefaultRouter

from anaf.identities import views as oldviews

router = DefaultRouter()
router.include_root_view = False
router.register(r'contactfield', views.ContactField)
router.register(r'contacttype', views.ContactType)
router.register(r'contact', views.Contact)
router.register(r'contactvalue', views.ContactValue)

urlpatterns = patterns('anaf.identities.views',
                       url(r'^', include(router.urls)),
                       url(r'^(\.(?P<response_format>\w+))?$', oldviews.index, name='identities'),

                       url(r'^index(\.(?P<response_format>\w+))?$', oldviews.index, name='identities_index'),
                       url(r'^users(\.(?P<response_format>\w+))?/?$', oldviews.index_users,
                           name='identities_index_users'),
                       url(r'^groups(\.(?P<response_format>\w+))?/?$', oldviews.index_groups,
                           name='identities_index_groups'),
                       url(r'^types/(?P<type_id>\d+)(\.(?P<response_format>\w+))?/?$', oldviews.type_view,
                           name='identities_index_by_type'),

                       # Types
                       url(r'^type/view/(?P<type_id>\d+)(\.(?P<response_format>\w+))?/?$', oldviews.type_view,
                           name='identities_type_view'),
                       url(r'^type/edit/(?P<type_id>\d+)(\.(?P<response_format>\w+))?/?$', oldviews.type_edit,
                           name='identities_type_edit'),
                       url(r'^type/delete/(?P<type_id>\d+)(\.(?P<response_format>\w+))?/?$', oldviews.type_delete,
                           name='identities_type_delete'),
                       url(r'^type/add(\.(?P<response_format>\w+))?/?$', oldviews.type_add,
                           name='identities_type_add'),

                       # Fields
                       url(r'^field/view/(?P<field_id>\d+)(\.(?P<response_format>\w+))?/?$', oldviews.field_view,
                           name='identities_field_view'),
                       url(r'^field/edit/(?P<field_id>\d+)(\.(?P<response_format>\w+))?/?$', oldviews.field_edit,
                           name='identities_field_edit'),
                       url(r'^field/delete/(?P<field_id>\d+)(\.(?P<response_format>\w+))?/?$', oldviews.field_delete,
                           name='identities_field_delete'),
                       url(r'^field/add(\.(?P<response_format>\w+))?/?$', oldviews.field_add,
                           name='identities_field_add'),

                       # Contacts
                       url(r'^contact/add(\.(?P<response_format>\w+))?/?$', oldviews.contact_add,
                           name='identities_contact_add'),
                       url(r'^contact/add/(?P<type_id>\d+)(\.(?P<response_format>\w+))?/?$', oldviews.contact_add_typed,
                           name='identities_contact_add_typed'),

                       url(r'^me(\.(?P<response_format>\w+))?/?$', oldviews.contact_me, name='identities_contact_me'),
                       url(r'^me/objects/(?P<attribute>[a-z_.]+)/list(\.(?P<response_format>\w+))?/?$',
                           oldviews.contact_me, name='identities_contact_me_objects'),
                       url(r'^contact/view/(?P<contact_id>\d+)(\.(?P<response_format>\w+))?/?$', oldviews.contact_view,
                           name='identities_contact_view'),
                       url(r'^contact/view/(?P<contact_id>\d+)/objects/(?P<attribute>[a-z_.]+)/list(\.(?P<response_format>\w+))?/?$',
                           oldviews.contact_view, name='identities_contact_view_objects'),
                       url(r'^contact/view/(?P<contact_id>\d+)/picture/?$', oldviews.contact_view_picture,
                           name='identities_contact_view_picture'),
                       url(r'^contact/edit/(?P<contact_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           oldviews.contact_edit, name='identities_contact_edit'),
                       url(r'^contact/delete/(?P<contact_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           oldviews.contact_delete, name='identities_contact_delete'),

                       url(r'^user/view/(?P<user_id>\d+)(\.(?P<response_format>\w+))?/?$', oldviews.user_view,
                           name='identities_user_view'),

                       url(r'^group/view/(?P<group_id>\d+)(\.(?P<response_format>\w+))?/?$', oldviews.group_view,
                           name='identities_group_view'),

                       url(r'^settings/view(\.(?P<response_format>\w+))?/?$', oldviews.settings_view,
                           name='identities_settings_view'),

                       # Locations
                       # url(r'^location/index(\.(?P<response_format>\w+))?/?$',
                       #     'location_index', name='identities_location_index'),
                       url(r'^location/view/(?P<location_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           oldviews.location_view, name='identities_location_view'),
                       url(r'^location/edit/(?P<location_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           oldviews.location_edit, name='identities_location_edit'),
                       url(r'^location/delete/(?P<location_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           oldviews.location_delete, name='identities_location_delete'),
                       url(r'^location/add(\.(?P<response_format>\w+))?/?$', oldviews.location_add,
                           name='identities_location_add'),

                       # AJAX callbacks
                       url(r'^ajax/users(\.(?P<response_format>\w+))?/?$', oldviews.ajax_user_lookup,
                           name='identities_ajax_user_lookup'),
                       url(r'^ajax/access(\.(?P<response_format>\w+))?/?$', oldviews.ajax_access_lookup,
                           name='identities_ajax_access_lookup'),
                       url(r'^ajax/contacts(\.(?P<response_format>\w+))?/?$', oldviews.ajax_contact_lookup,
                           name='identities_ajax_contact_lookup'),
                       url(r'^ajax/locations(\.(?P<response_format>\w+))?/?$', oldviews.ajax_location_lookup,
                           name='identities_ajax_location_lookup'),
                       )

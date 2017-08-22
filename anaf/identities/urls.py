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
                       url(r'^/', include(router.urls)),
                       url(r'^/$', oldviews.index, name='identities'),
                       url(r'^\.(?P<response_format>\w+)$', oldviews.index, name='identities'),
                       url(r'^/index(\.(?P<response_format>\w+))?$', oldviews.index, name='index'),
                       url(r'^/users(\.(?P<response_format>\w+))?/?$', oldviews.index_users, name='index_users'),
                       url(r'^/groups(\.(?P<response_format>\w+))?/?$', oldviews.index_groups, name='index_groups'),
                       url(r'^/types/(?P<type_id>\d+)(\.(?P<response_format>\w+))?/?$', oldviews.type_view,
                           name='index_by_type'),

                       # Types
                       url(r'^/type/view/(?P<type_id>\d+)(\.(?P<response_format>\w+))?/?$', oldviews.type_view,
                           name='type_view'),
                       url(r'^/type/edit/(?P<type_id>\d+)(\.(?P<response_format>\w+))?/?$', oldviews.type_edit,
                           name='type_edit'),
                       url(r'^/type/delete/(?P<type_id>\d+)(\.(?P<response_format>\w+))?/?$', oldviews.type_delete,
                           name='type_delete'),
                       url(r'^/type/add(\.(?P<response_format>\w+))?/?$', oldviews.type_add,
                           name='type_add'),

                       # Fields
                       url(r'^/field/view/(?P<field_id>\d+)(\.(?P<response_format>\w+))?/?$', oldviews.field_view,
                           name='field_view'),
                       url(r'^/field/edit/(?P<field_id>\d+)(\.(?P<response_format>\w+))?/?$', oldviews.field_edit,
                           name='field_edit'),
                       url(r'^/field/delete/(?P<field_id>\d+)(\.(?P<response_format>\w+))?/?$', oldviews.field_delete,
                           name='field_delete'),
                       url(r'^/field/add(\.(?P<response_format>\w+))?/?$', oldviews.field_add,
                           name='field_add'),

                       # Contacts
                       url(r'^/contact/add/(?P<type_id>\d+)/$', oldviews.contact_add_typed,
                           name='contact_add_typed'),

                       url(r'^/contact/add/(?P<type_id>\d+).(?P<response_format>\w+)$', oldviews.contact_add_typed,
                           name='contact_add_typed'),

                       url(r'^/me(\.(?P<response_format>\w+))?/?$', oldviews.contact_me, name='contact_me'),
                       url(r'^/me/objects/(?P<attribute>[a-z_.]+)/list(\.(?P<response_format>\w+))?/?$',
                           oldviews.contact_me, name='identities_contact_me_objects'),
                       url(r'^/contact/view/(?P<contact_id>\d+)(\.(?P<response_format>\w+))?/?$', oldviews.contact_view,
                           name='contact_view'),
                       url(r'^/contact/view/(?P<contact_id>\d+)/objects/(?P<attribute>[a-z_.]+)/list(\.(?P<response_format>\w+))?/?$',
                           oldviews.contact_view, name='identities_contact_view_objects'),
                       url(r'^/contact/view/(?P<contact_id>\d+)/picture/?$', oldviews.contact_view_picture,
                           name='contact_view_picture'),
                       url(r'^/contact/edit/(?P<contact_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           oldviews.contact_edit, name='contact_edit'),
                       url(r'^/contact/delete/(?P<contact_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           oldviews.contact_delete, name='contact_delete'),

                       url(r'^/user/view/(?P<user_id>\d+)(\.(?P<response_format>\w+))?/?$', oldviews.user_view,
                           name='user_view'),

                       url(r'^/group/view/(?P<group_id>\d+)(\.(?P<response_format>\w+))?/?$', oldviews.group_view,
                           name='group_view'),

                       url(r'^/settings/view(\.(?P<response_format>\w+))?/?$', oldviews.settings_view,
                           name='settings_view'),

                       # Locations
                       # url(r'^location/index(\.(?P<response_format>\w+))?/?$',
                       #     'location_index', name='identities_location_index'),
                       url(r'^/location/view/(?P<location_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           oldviews.location_view, name='identities_location_view'),
                       url(r'^/location/edit/(?P<location_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           oldviews.location_edit, name='identities_location_edit'),
                       url(r'^/location/delete/(?P<location_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           oldviews.location_delete, name='identities_location_delete'),
                       url(r'^/location/add(\.(?P<response_format>\w+))?/?$', oldviews.location_add,
                           name='location_add'),

                       # AJAX callbacks
                       url(r'^/ajax/users(\.(?P<response_format>\w+))?/?$', oldviews.ajax_user_lookup,
                           name='ajax_user_lookup'),
                       url(r'^/ajax/access(\.(?P<response_format>\w+))?/?$', oldviews.ajax_access_lookup,
                           name='ajax_access_lookup'),
                       url(r'^/ajax/contacts(\.(?P<response_format>\w+))?/?$', oldviews.ajax_contact_lookup,
                           name='ajax_contact_lookup'),
                       url(r'^/ajax/locations(\.(?P<response_format>\w+))?/?$', oldviews.ajax_location_lookup,
                           name='ajax_location_lookup'),
                       )

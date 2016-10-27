from django.conf.urls import patterns, url, include
from anaf.core.api import views
from rest_framework.routers import DefaultRouter

from anaf.core import views as oldviews

router = DefaultRouter()
router.include_root_view = False
router.register(r'user', views.ProfileView)
router.register(r'group', views.GroupView)
router.register(r'perspective', views.PerspectiveView)
router.register(r'accessentity', views.AccessEntityView)
# router.register(r'object', views.ObjectView)
# router.register(r'module', views.ModuleView)

urlpatterns = patterns('anaf.core.views',
                       url(r'^', include(router.urls)),
                       url(r'^logout(\.(?P<response_format>\w+))?/?$', oldviews.user_logout, name='user_logout'),
                       url(r'^login(\.(?P<response_format>\w+))?/?$', oldviews.user_login, name='user_login'),
                       url(r'^denied(\.(?P<response_format>\w+))?/?$', oldviews.user_denied, name='user_denied'),
                       url(r'setup(\.(?P<response_format>\w+))?/?$', oldviews.database_setup, name='database_setup'),

                       # Switch perspective
                       url(r'^perspective(\.(?P<response_format>\w+))?/?$', oldviews.user_perspective,
                           name='user_perspective'),

                       # Popup handler
                       url(r'^popup(\.json)?/(?P<popup_id>[a-z0-9\-_]+)/url=(?P<url>.+)/?$', oldviews.ajax_popup,
                           name='core_ajax_popup'),

                       # AJAX handlers
                       url(r'^ajax/objects(\.(?P<response_format>\w+))?/?$', oldviews.ajax_object_lookup,
                           name='core_ajax_object_lookup'),
                       url(r'^ajax/tags(\.(?P<response_format>\w+))?/?$', oldviews.ajax_tag_lookup,
                           name='core_ajax_tag_lookup'),

                       # Attachments
                       url(r'^ajax/upload/(?P<object_id>\d+)/$', oldviews.ajax_upload, name="ajax_upload"),
                       url(r'^ajax/upload/record/(?P<record_id>\d+)/$', oldviews.ajax_upload_record,
                           name="ajax_upload_record"),
                       url(r'^attachment/download/(?P<attachment_id>\d+)/?$', oldviews.attachment_download,
                           name='core_attachment_download'),

                       # Reset password
                       url(r'^password_reset/$', oldviews.password_reset, name='password_reset'),
                       url(r'^password_reset/done/$', oldviews.password_reset_done, name='password_reset_done'),
                       url(r'^invitation/$', oldviews.invitation_retrieve, name='invitation_retrieve'),

                       # Custom logo
                       url(r'^logo/image/$', oldviews.logo_image, name='core_logo_image', kwargs={'gif': False}),
                       url(r'^logo/image/ie/$', oldviews.logo_image, name='core_logo_image_ie', kwargs={'gif': True}),
                       )

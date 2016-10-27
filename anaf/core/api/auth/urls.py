from django.conf.urls import patterns, url

from anaf.core.api.auth import views

urlpatterns = patterns('anaf.core.api.auth.views',
                       url(r'^get_request_token$', views.get_request_token, name="api_get_request_token"),
                       url(r'^authorize_request_token$', views.authorize_request_token,
                           name="api_authorize_request_token"),
                       url(r'^get_access_token$', views.get_access_token, name="api_get_access_token"),
                       )

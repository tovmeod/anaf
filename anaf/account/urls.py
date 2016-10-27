"""
Core Account module URLs
"""

from django.conf.urls import patterns, url

from anaf.account import views

urlpatterns = patterns('anaf.account.views',
                       url(r'^(\.(?P<response_format>\w+))?/?$', views.account_view, name='account'),
                       url(r'^view(\.(?P<response_format>\w+))?/?$', views.account_view, name='account_view'),
                       url(r'^password(\.(?P<response_format>\w+))?/?$', views.account_password,
                           name='account_password'),
                       url(r'^watchlist(\.(?P<response_format>\w+))?/?$', views.watchlist, name='account_watchlist'),

                       # Settings
                       url(r'^settings(\.(?P<response_format>\w+))?/?$', views.settings_view, name='account_settings'),
                       url(r'^settings/view(\.(?P<response_format>\w+))?/?$', views.settings_view,
                           name='account_settings_view'),
                       url(r'^settings/edit(\.(?P<response_format>\w+))?/?$', views.settings_edit,
                           name='account_settings_edit'),
                       )

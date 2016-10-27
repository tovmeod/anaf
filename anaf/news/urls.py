"""
News module URLs
"""
from django.conf.urls import patterns, url

from anaf.news import views

urlpatterns = patterns('anaf.news.views',
                       url(r'^(\.(?P<response_format>\w+))?$', views.index, name='news'),
                       url(r'^all(\.(?P<response_format>\w+))?$', views.index, name='news_index'),
                       url(r'^top(\.(?P<response_format>\w+))?$', views.top_news, name='news_top'),
                       url(r'^social(\.(?P<response_format>\w+))?$', views.index_social, name='news_social'),
                       url(r'^my(\.(?P<response_format>\w+))?$', views.my_activity, name='news_my_activity'),
                       url(r'^(?P<module_name>[a-z.]+)/news(\.(?P<response_format>\w+))?$', views.index_by_module,
                           name='news_index_by_module'),
                       url(r'^watchlist(\.(?P<response_format>\w+))?$', views.my_watchlist, name='news_my_watchlist'),

                       url(r'^widget/index(\.(?P<response_format>\w+))?$', views.widget_news_index,
                           name='news_widget_index'),
                       url(r'^widget/social(\.(?P<response_format>\w+))?$', views.widget_news_social,
                           name='news_widget_social'),
                       )

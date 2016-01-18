"""
News module widgets
"""

WIDGETS = {'widget_news_index': {'title': 'News: All Activity',
                                 'size': "95%"},
           'widget_news_social': {'title': 'News: Social Activity',
                                  'size': "95%"},
           'widget_my_watchlist': {'title': 'News: My Watchlist',
                                   'size': "95%"}}


def get_widgets(request):
    "Returns a set of all available widgets"

    widgets = {}
    widgets.update(WIDGETS)

    return widgets

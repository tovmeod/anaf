"""
Messaging module widgets
"""

WIDGETS = {'widget_new_messages': {'title': 'New Messages',
                                   'size': "95%"}}


def get_widgets(request):
    "Returns a set of all available widgets"

    return WIDGETS

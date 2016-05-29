"""Projects module widgets."""

WIDGETS = {'widget_tasks_assigned_to_me': {'title': 'Tasks Assigned To Me',
                                           'size': "95%"}}


def get_widgets(request):
    """Return a set of all available widgets."""

    return WIDGETS

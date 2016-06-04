"""
Sales integration with Events module
"""
import datetime
import time
from django.db.models import Q
from anaf.core.models import Object
from anaf.events.rendering import EventRenderer
from anaf.sales.models import Opportunity


def get_events(request):
    """Return a list of EventRenderers from available Sales"""
    events = []

    query = Q(expected_date__isnull=False)
    sales = Object.filter_by_request(
        request, manager=Opportunity.objects.filter(query))

    for sale in sales:
        # event = EventRenderer(sale.contact.name, None, sale.expected_date, sale.get_absolute_url())
        event = EventRenderer(sale.contact.name, None, datetime.datetime.fromtimestamp(time.mktime(
            time.strptime(str(sale.expected_date), "%Y-%m-%d"))), sale.get_absolute_url())  # bad code
        event.css_class += " projects-calendar-task"
        events.append(event)

    return events

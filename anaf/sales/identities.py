"""
Handle objects from this module relevant to a Contact or a User
"""
from copy import deepcopy

from anaf.core.models import Object
from anaf.sales.templatetags.sales import sales_order_list, sales_lead_list, sales_opportunity_list

CONTACT_OBJECTS = {'saleorder_set': {
    'label': 'Sale Orders',
    'objects': [],
    'templatetag': sales_order_list
}, 'lead_set': {
    'label': 'Leads',
    'objects': [],
    'templatetag': sales_lead_list
}, 'opportunity_set': {
    'label': 'Opportunities',
    'objects': [],
    'templatetag': sales_opportunity_list
}}

USER_OBJECTS = {'sales_saleorder_assigned': {'label': 'Assigned Orders',
                                             'objects': [],
                                             'templatetag': sales_order_list}}


def get_contact_objects(current_user, contact):
    """
    Returns a dictionary with keys specified as contact attributes
    and values as dictionaries with labels and set of relevant objects.
    """

    objects = deepcopy(CONTACT_OBJECTS)

    for key in objects:
        if hasattr(contact, key):
            objects[key]['objects'] = Object.filter_permitted(
                current_user, getattr(contact, key))

    return objects


def get_user_objects(current_user, user):
    """
    Returns a dictionary with keys specified as contact attributes
    and values as dictionaries with labels and set of relevant objects.
    """

    objects = deepcopy(USER_OBJECTS)

    for key in objects:
        if hasattr(user, key):
            objects[key]['objects'] = Object.filter_permitted(
                current_user, getattr(user, key))

    return objects

import sys
from rest_framework.utils.field_mapping import get_relation_kwargs as drfget_relation_kwargs
from rest_framework.utils import field_mapping


def get_relation_kwargs(field_name, relation_info):
    """
    DRF view_name doesn't know about namespaces
    """
    field_kwargs = drfget_relation_kwargs(field_name, relation_info)
    view_name = field_kwargs['view_name']

    namespace = getattr(sys.modules[relation_info.related_model.__module__], 'namespace', '')
    if namespace:
        field_kwargs['view_name'] = '%s:%s' % (namespace, view_name)
    return field_kwargs

field_mapping.get_relation_kwargs = get_relation_kwargs

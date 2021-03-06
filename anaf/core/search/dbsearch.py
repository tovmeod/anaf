from django.db.models import Q, CharField, TextField
from django.apps import apps

from anaf.core.models import Object

params = []

for model in apps.get_models():
    if issubclass(model, Object) and getattr(model, 'searcheable', True):
        for field in model._meta.fields:
            if isinstance(field, (CharField, TextField)) and 'password' not in field.name and \
                            'object_name' not in field.name and 'object_type' not in field.name \
                    and 'nuvius' not in field.name:
                params.append('{0!s}__{1!s}'.format(model._meta.model_name, field.name))


def search(term):
    "Use database backend for searching"
    query = Q()
    # query_dict = {}
    attr = 'search'
    if term and term[0] == '*':
        attr = 'icontains'
        term = term[1:]
    for param in params:
        kwargs = {'{0!s}__{1!s}'.format(param, attr): term}
        # query_dict[param] = term
        query = query | Q(**kwargs)

    # from pprint import pprint
    # pprint(query_dict)

    return Object.objects.filter(query)

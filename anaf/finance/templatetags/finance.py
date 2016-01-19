"""
Finance templatetags
"""
from coffin import template
from anaf.core.rendering import render_to_string
from jinja2 import contextfunction, Markup
from django.template import RequestContext

register = template.Library()


@contextfunction
def finance_transaction_list(context, transactions, skip_group=False):
    "Print a list of orders"
    request = context['request']

    response_format = 'html'
    if 'response_format' in context:
        response_format = context['response_format']

    return Markup(render_to_string('finance/tags/transaction_list',
                                   {'transactions': transactions,
                                       'skip_group': skip_group},
                                   context_instance=RequestContext(request),
                                   response_format=response_format))


@contextfunction
def finance_liability_list(context, liabilities, skip_group=False):
    "Print a list of orders"
    request = context['request']

    response_format = 'html'
    if 'response_format' in context:
        response_format = context['response_format']

    return Markup(render_to_string('finance/tags/liability_list',
                                   {'liabilities': liabilities,
                                       'skip_group': skip_group},
                                   context_instance=RequestContext(request),
                                   response_format=response_format))


register.object(finance_transaction_list)
register.object(finance_liability_list)

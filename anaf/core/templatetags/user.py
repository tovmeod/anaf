"""
User-related Core templatetags
"""
from coffin import template
from django.core.context_processors import csrf
from anaf.core.rendering import render_to_string
from jinja2 import contextfunction, Markup
from anaf.core.models import Object, Perspective
from anaf.core.conf import settings

register = template.Library()


@contextfunction
def user_block(context):
    """User block
    :param Context context:
    """
    request = context['request']

    user = request.user.profile
    modules = user.get_perspective().get_modules()
    account = modules.filter(name='anaf.account')
    admin = modules.filter(name='anaf.core')
    if admin:
        admin = admin[0]

    response_format = 'html'
    if 'response_format' in context:
        response_format = context['response_format']

    trial = False
    if settings.ANAF_SUBSCRIPTION_USER_LIMIT == 3:
        trial = True

    active = context.get('active')

    return Markup(render_to_string('core/tags/user_block',
                  {'user': user,
                   'account': account,
                   'admin': admin,
                   'active': active,
                   'trial': trial},
                  response_format=response_format))

register.object(user_block)


@contextfunction
def demo_user(context):
    "Print demo block if demo"

    response_format = 'html'

    demo = settings.ANAF_DEMO_MODE

    return Markup(render_to_string('core/tags/demo_user',
                  {'demo': demo},
                  response_format=response_format))

register.object(demo_user)


@contextfunction
def core_perspective_switch(context):
    "Quick perspective switcher"

    response_format = 'html'
    request = context['request']
    try:
        user = request.user.profile

        current = user.get_perspective()
        perspectives = Object.filter_by_request(request, Perspective.objects)
    except:
        current = None
        perspectives = []

    context = {'current': current, 'perspectives': perspectives}
    context.update(csrf(request))

    return Markup(render_to_string('core/tags/perspective_switch', context,
                  response_format=response_format))

register.object(core_perspective_switch)

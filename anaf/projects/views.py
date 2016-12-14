import warnings

from django.template import RequestContext
from django.db.models import Q
from anaf.core.models import Object
from anaf.core.rendering import render_to_response
from anaf.core.decorators import mylogin_required, handle_response_format
from anaf.projects.models import Project, Milestone, Task, TaskStatus
from anaf.projects.forms import FilterForm, MassActionForm


def _get_filter_query(args):
    """Creates a query to filter Tasks based on FilterForm arguments"""
    query = Q()

    for arg in args:
        if hasattr(Task, arg) and args[arg]:
            kwargs = {str(arg + '__id'): int(args[arg])}
            query = query & Q(**kwargs)

    return query


def _get_default_context(request):
    """Returns default context as a dict()"""

    projects = Object.filter_by_request(request, Project.objects)
    statuses = Object.filter_by_request(request, TaskStatus.objects)
    massform = MassActionForm(request.user.profile)

    context = {'projects': projects,
               'statuses': statuses,
               'massform': massform}

    return context


def _process_mass_form(f):
    """Pre-process request to handle mass action form for Tasks and Milestones"""

    def wrap(request, *args, **kwargs):
        """Wrap"""
        if 'massform' in request.POST:
            for key in request.POST:
                if 'mass-milestone' in key:
                    try:
                        milestone = Milestone.objects.get(pk=request.POST[key])
                        form = MassActionForm(request.user.profile, request.POST, instance=milestone)
                        if form.is_valid() and request.user.profile.has_permission(milestone, mode='w'):
                            form.save()
                    except Exception:
                        pass
                elif 'mass-task' in key:
                    try:
                        task = Task.objects.get(pk=request.POST[key])
                        form = MassActionForm(request.user.profile, request.POST, instance=task)
                        if form.is_valid() and request.user.profile.has_permission(task, mode='w'):
                            form.save()
                    except Exception:
                        pass

        return f(request, *args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__

    return wrap


@handle_response_format
@mylogin_required
@_process_mass_form
def index(request, response_format='html'):
    """Deprecated Project Management index page"""
    warnings.warn("using old project index page, use project-list instead", DeprecationWarning, stacklevel=2)
    query = Q(parent__isnull=True)
    if request.GET:
        if 'status' in request.GET and request.GET['status']:
            query = query & _get_filter_query(request.GET)
        else:
            query = query & Q(status__hidden=False) & _get_filter_query(request.GET)
    else:
        query = query & Q(status__hidden=False)

    tasks = Object.filter_by_request(request, Task.objects.filter(query))
    milestones = Object.filter_by_request(
        request, Milestone.objects.filter(status__hidden=False))
    filters = FilterForm(request.user.profile, '', request.GET)

    context = _get_default_context(request)
    context.update({'milestones': milestones,
                    'tasks': tasks,
                    'filters': filters})

    return render_to_response('projects/index', context,
                              context_instance=RequestContext(request), response_format=response_format)


#
# Widgets
#

@mylogin_required
def widget_tasks_assigned_to_me(request, response_format='html'):
    "A list of tasks assigned to current user"

    query = Q(parent__isnull=True) & Q(status__hidden=False)

    tasks = Object.filter_by_request(request, Task.objects.filter(query))

    return render_to_response('projects/widgets/tasks_assigned_to_me',
                              {'tasks': tasks},
                              context_instance=RequestContext(request), response_format=response_format)

from coffin.template import loader
from django.http import HttpResponse
def dojo_view(request):
    """Project Management index page"""

    query = Q(parent__isnull=True)
    if request.GET:
        if 'status' in request.GET and request.GET['status']:
            query = query & _get_filter_query(request.GET)
        else:
            query = query & Q(status__hidden=False) & _get_filter_query(request.GET)
    else:
        query = query & Q(status__hidden=False)

    tasks = Object.filter_by_request(request, Task.objects.filter(query))
    milestones = Object.filter_by_request(
        request, Milestone.objects.filter(status__hidden=False))
    filters = FilterForm(request.user.profile, '', request.GET)

    context = _get_default_context(request)
    context.update({'milestones': milestones,
                    'tasks': tasks,
                    'filters': filters})

    rendered_string = loader.render_to_string('html/dojo/project_index.html',context,
                                              context_instance=RequestContext(request))
    return HttpResponse(rendered_string)

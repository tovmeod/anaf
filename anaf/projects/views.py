import warnings

from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.db.models import Q
from anaf import long_type
from anaf.core.models import Object, ModuleSetting, UpdateRecord
from anaf.core.views import user_denied
from anaf.core.rendering import render_to_response
from anaf.core.decorators import mylogin_required, handle_response_format, require_response_format
from anaf.projects.models import Project, Milestone, Task, TaskStatus, TaskTimeSlot
from anaf.projects.forms import ProjectForm, MilestoneForm, TaskForm, FilterForm, TaskRecordForm, \
    MassActionForm, TaskTimeSlotForm, TaskStatusForm, SettingsForm
from django.utils.translation import ugettext as _
from datetime import datetime
import json


def _get_filter_query(args):
    """Creates a query to filter Tasks based on FilterForm arguments"""
    query = Q()

    for arg in args:
        if hasattr(Task, arg) and args[arg]:
            kwargs = {str(arg + '__id'): long_type(args[arg])}
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


@handle_response_format
@mylogin_required
@_process_mass_form
def index_by_status(request, status_id, response_format='html'):
    """Sort tasks by status"""

    status = get_object_or_404(TaskStatus, pk=status_id)

    if not request.user.profile.has_permission(status):
        return user_denied(request, message="You don't have access to this Task Status")

    query = Q(parent__isnull=True, status=status)
    if request.GET:
        query = query & _get_filter_query(request.GET)
    tasks = Object.filter_by_request(request, Task.objects.filter(query))

    milestones = Object.filter_by_request(
        request, Milestone.objects.filter(task__status=status).distinct())
    filters = FilterForm(request.user.profile, 'status', request.GET)

    context = _get_default_context(request)
    context.update({'milestones': milestones,
                    'tasks': tasks,
                    'status': status,
                    'filters': filters})

    return render_to_response('projects/index_by_status', context,
                              context_instance=RequestContext(request), response_format=response_format)

#
# Task Statuses
#


@handle_response_format
@mylogin_required
def task_status_edit(request, status_id, response_format='html'):
    """TaskStatus edit"""

    status = get_object_or_404(TaskStatus, pk=status_id)
    if not request.user.profile.has_permission(status, mode='w'):
        return user_denied(request, message="You don't have access to this Task Status")

    if request.POST:
        if 'cancel' not in request.POST:
            form = TaskStatusForm(
                request.user.profile, request.POST, instance=status)
            if form.is_valid():
                status = form.save()
                return HttpResponseRedirect(reverse('projects_index_by_status', args=[status.id]))
        else:
            return HttpResponseRedirect(reverse('projects_index_by_status', args=[status.id]))
    else:
        form = TaskStatusForm(request.user.profile, instance=status)

    context = _get_default_context(request)
    context.update({'form': form,
                    'status': status})

    return render_to_response('projects/status_edit', context,
                              context_instance=RequestContext(request), response_format=response_format)


@handle_response_format
@mylogin_required
def task_status_delete(request, status_id, response_format='html'):
    """TaskStatus delete"""

    status = get_object_or_404(TaskStatus, pk=status_id)
    if not request.user.profile.has_permission(status, mode='w'):
        return user_denied(request, message="You don't have access to this Task Status")

    if request.POST:
        if 'delete' in request.POST:
            if 'trash' in request.POST:
                status.trash = True
                status.save()
            else:
                status.delete()
            return HttpResponseRedirect(reverse('project-list'))
        elif 'cancel' in request.POST:
            return HttpResponseRedirect(reverse('projects_index_by_status', args=[status.id]))

    milestones = Object.filter_by_request(request, Milestone.objects)

    context = _get_default_context(request)
    context.update({'status': status,
                    'milestones': milestones})

    return render_to_response('projects/status_delete', context,
                              context_instance=RequestContext(request), response_format=response_format)


#
# Settings
#

@handle_response_format
@mylogin_required
def settings_view(request, response_format='html'):
    """Settings"""

    if not request.user.profile.is_admin('anaf.projects'):
        return user_denied(request, message="You don't have administrator access to the Projects module")

    # default task status
    try:
        conf = ModuleSetting.get_for_module(
            'anaf.projects', 'default_task_status')[0]
        default_task_status = TaskStatus.objects.get(
            pk=long(conf.value), trash=False)
    except Exception:
        default_task_status = None

    statuses = TaskStatus.objects.filter(trash=False)
    context = _get_default_context(request)
    context.update({'default_task_status': default_task_status,
                    'statuses': statuses})

    return render_to_response('projects/settings_view', context,
                              context_instance=RequestContext(request), response_format=response_format)


@handle_response_format
@mylogin_required
def settings_edit(request, response_format='html'):
    """Settings"""

    if not request.user.profile.is_admin('anaf.projects'):
        return user_denied(request, message="You don't have administrator access to the Projects module")

    form = None
    if request.POST:
        if 'cancel' not in request.POST:
            form = SettingsForm(request.user.profile, request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('projects_settings_view'))
        else:
            return HttpResponseRedirect(reverse('projects_settings_view'))
    else:
        form = SettingsForm(request.user.profile)

    context = _get_default_context(request)
    context.update({'form': form})

    return render_to_response('projects/settings_edit', context,
                              context_instance=RequestContext(request), response_format=response_format)

#
# AJAX lookups
#


@require_response_format(['json'])
@mylogin_required
def ajax_task_lookup(request, response_format='json'):
    """Returns a list of matching tasks"""

    if request.GET and 'term' in request.GET:
        tasks = Task.objects.filter(name__icontains=request.GET['term'])[:10]
    else:
        tasks = []

    return render_to_response('projects/ajax_task_lookup',
                              {'tasks': tasks},
                              context_instance=RequestContext(request),
                              response_format=response_format)


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

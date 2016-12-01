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
# Projects
#


@handle_response_format
@mylogin_required
def project_add_typed(request, project_id, response_format='html'):
    """Project add to preselected parent project"""

    parent_project = None
    if project_id:
        parent_project = get_object_or_404(Project, pk=project_id)
        if not request.user.profile.has_permission(parent_project, mode='x'):
            parent_project = None

    if request.POST:
        if 'cancel' not in request.POST:
            project = Project()
            form = ProjectForm(
                request.user.profile, project_id, request.POST, instance=project)
            if form.is_valid():
                project = form.save()
                project.set_user_from_request(request)
                return HttpResponseRedirect(reverse('projects_project_view', args=[project.id]))
        else:
            return HttpResponseRedirect(reverse('projects'))
    else:
        form = ProjectForm(request.user.profile, project_id)

    context = _get_default_context(request)
    context.update({'form': form, 'project': parent_project})

    return render_to_response('projects/project_add_typed', context,
                              context_instance=RequestContext(request), response_format=response_format)


@handle_response_format
@mylogin_required
@_process_mass_form
def project_view(request, project_id, response_format='html'):
    """Single project view page"""

    project = get_object_or_404(Project, pk=project_id)
    if not request.user.profile.has_permission(project):
        return user_denied(request, message="You don't have access to this Project")

    query = Q(parent__isnull=True, project=project)
    if request.GET:
        if 'status' in request.GET and request.GET['status']:
            query = query & _get_filter_query(request.GET)
        else:
            query = query & Q(
                status__hidden=False) & _get_filter_query(request.GET)
    else:
        query = query & Q(status__hidden=False)

    if request.user.profile.has_permission(project, mode='r'):
        if request.POST:
            record = UpdateRecord()
            record.record_type = 'manual'
            form = TaskRecordForm(
                request.user.profile, request.POST, instance=record)
            if form.is_valid():
                record = form.save()
                record.set_user_from_request(request)
                record.save()
                record.about.add(project)
                project.set_last_updated()
                return HttpResponseRedirect(reverse('projects_project_view', args=[project.id]))
        else:
            form = TaskRecordForm(request.user.profile)
    else:
        form = None

    tasks = Object.filter_by_request(request, Task.objects.filter(query))

    tasks_progress = float(0)
    tasks_progress_query = Object.filter_by_request(
        request, Task.objects.filter(Q(parent__isnull=True, project=project)))
    if tasks_progress_query:
        for task in tasks_progress_query:
            if not task.status.active:
                tasks_progress += 1
        tasks_progress = (tasks_progress / len(tasks_progress_query)) * 100
        tasks_progress = round(tasks_progress, ndigits=1)

    filters = FilterForm(request.user.profile, 'project', request.GET)

    milestones = Object.filter_by_request(request,
                                          Milestone.objects.filter(project=project).filter(status__hidden=False))
    subprojects = Project.objects.filter(parent=project)

    context = _get_default_context(request)
    context.update({'project': project,
                    'milestones': milestones,
                    'tasks': tasks,
                    'tasks_progress': tasks_progress,
                    'record_form': form,
                    'subprojects': subprojects,
                    'filters': filters})

    return render_to_response('projects/project_view', context,
                              context_instance=RequestContext(request), response_format=response_format)


@handle_response_format
@mylogin_required
def project_edit(request, project_id, response_format='html'):
    """Project edit page"""

    project = get_object_or_404(Project, pk=project_id)
    if not request.user.profile.has_permission(project, mode='w'):
        return user_denied(request, message="You don't have access to this Project")

    if request.POST:
        if 'cancel' not in request.POST:
            form = ProjectForm(
                request.user.profile, None, request.POST, instance=project)
            if form.is_valid():
                project = form.save()
                return HttpResponseRedirect(reverse('projects_project_view', args=[project.id]))
        else:
            return HttpResponseRedirect(reverse('projects_project_view', args=[project.id]))
    else:
        form = ProjectForm(request.user.profile, None, instance=project)

    context = _get_default_context(request)
    context.update({'form': form, 'project': project})

    return render_to_response('projects/project_edit', context,
                              context_instance=RequestContext(request), response_format=response_format)


@handle_response_format
@mylogin_required
def project_delete(request, project_id, response_format='html'):
    """Project delete"""

    project = get_object_or_404(Project, pk=project_id)
    if not request.user.profile.has_permission(project, mode='w'):
        return user_denied(request, message="You don't have access to this Project")

    if request.POST:
        if 'delete' in request.POST:
            if 'trash' in request.POST:
                project.trash = True
                project.save()
            else:
                project.delete()
            return HttpResponseRedirect(reverse('projects_index'))
        elif 'cancel' in request.POST:
            return HttpResponseRedirect(reverse('projects_project_view', args=[project.id]))

    context = _get_default_context(request)
    context.update({'project': project})

    return render_to_response('projects/project_delete', context,
                              context_instance=RequestContext(request), response_format=response_format)

#
# Task Time Slots
#


@handle_response_format
@mylogin_required
def task_time_slot_start(request, task_id, response_format='html'):
    """Start TaskTimeSlot for preselected Task"""

    task = get_object_or_404(Task, pk=task_id)
    if not request.user.profile.has_permission(task, mode='x'):
        return user_denied(request, message="You don't have access to this Task")

    if not task.is_being_done_by(request.user.profile):
        task_time_slot = TaskTimeSlot(
            task=task, time_from=datetime.now(), user=request.user.profile)
        task_time_slot.save()
        task_time_slot.set_user_from_request(request)

    return HttpResponseRedirect(reverse('task-detail', args=[task_id]))


@handle_response_format
@mylogin_required
def task_time_slot_stop(request, slot_id, response_format='html'):
    """Stop TaskTimeSlot for preselected Task"""

    slot = get_object_or_404(TaskTimeSlot, pk=slot_id)
    if not request.user.profile.has_permission(slot, mode='w'):
        return user_denied(request, message="You don't have access to this TaskTimeSlot")

    if request.POST and 'stop' in request.POST:
        slot.time_to = datetime.now()
        slot.details = request.POST['details']
        slot.save()

    return HttpResponseRedirect(reverse('task-detail', args=[slot.task_id]))


@handle_response_format
@mylogin_required
def task_time_slot_add(request, task_id, response_format='html'):
    """Time slot add to preselected task"""

    task = get_object_or_404(Task, pk=task_id)
    if not request.user.profile.has_permission(task, mode='x'):
        return user_denied(request, message="You don't have access to this Task")

    if request.POST:
        task_time_slot = TaskTimeSlot(
            task=task, time_to=datetime.now(), user=request.user.profile)
        form = TaskTimeSlotForm(
            request.user.profile, task_id, request.POST, instance=task_time_slot)
        if 'cancel' in request.POST:
            return HttpResponseRedirect(reverse('task-detail', args=[task.id]))
        elif form.is_valid():
            task_time_slot = form.save()
            task_time_slot.set_user_from_request(request)
            return HttpResponseRedirect(reverse('task-detail', args=[task.id]))
    else:
        form = TaskTimeSlotForm(request.user.profile, task_id)

    subtasks = Object.filter_by_request(
        request, Task.objects.filter(parent=task))
    time_slots = Object.filter_by_request(
        request, TaskTimeSlot.objects.filter(task=task))

    context = _get_default_context(request)
    context.update({'form': form,
                    'task': task,
                    'subtasks': subtasks,
                    'time_slots': time_slots})

    return render_to_response('projects/task_time_add', context,
                              context_instance=RequestContext(request), response_format=response_format)


@handle_response_format
@mylogin_required
def task_time_slot_view(request, time_slot_id, response_format='html'):
    """Task time slot view page"""

    task_time_slot = get_object_or_404(TaskTimeSlot, pk=time_slot_id)
    task = task_time_slot.task
    if not request.user.profile.has_permission(task_time_slot) \
            and not request.user.profile.has_permission(task):
        return user_denied(request, message="You don't have access to this Task Time Slot")

    context = _get_default_context(request)
    context.update({'task_time_slot': task_time_slot,
                    'task': task})

    return render_to_response('projects/task_time_view', context,
                              context_instance=RequestContext(request), response_format=response_format)


@handle_response_format
@mylogin_required
def task_time_slot_edit(request, time_slot_id, response_format='html'):
    """Task time slot edit page"""

    task_time_slot = get_object_or_404(TaskTimeSlot, pk=time_slot_id)
    task = task_time_slot.task

    if not request.user.profile.has_permission(task_time_slot, mode='w') \
            and not request.user.profile.has_permission(task, mode='w'):
        return user_denied(request, message="You don't have access to this Task Time Slot")

    if request.POST:
        form = TaskTimeSlotForm(
            request.user.profile, None, request.POST, instance=task_time_slot)
        if form.is_valid():
            task_time_slot = form.save()
            return HttpResponseRedirect(reverse('task-detail', args=[task.id]))

        elif 'cancel' in request.POST:
            return HttpResponseRedirect(reverse('task-detail', args=[task.id]))
    else:
        form = TaskTimeSlotForm(
            request.user.profile, None, instance=task_time_slot)

    context = _get_default_context(request)
    context.update({'form': form,
                    'task_time_slot': task_time_slot,
                    'task': task})

    return render_to_response('projects/task_time_edit', context,
                              context_instance=RequestContext(request), response_format=response_format)


@handle_response_format
@mylogin_required
def task_time_slot_delete(request, time_slot_id, response_format='html'):
    """Task time slot delete"""

    task_time_slot = get_object_or_404(TaskTimeSlot, pk=time_slot_id)
    task = task_time_slot.task

    if not request.user.profile.has_permission(task_time_slot, mode='w') \
            and not request.user.profile.has_permission(task, mode='w'):
        return user_denied(request, message="You don't have access to this Task Time Slot")

    if request.POST:
        if 'delete' in request.POST:
            if 'trash' in request.POST:
                task_time_slot.trash = True
                task_time_slot.save()
            else:
                task_time_slot.delete()
            return HttpResponseRedirect(reverse('task-detail', args=[task.id]))
        elif 'cancel' in request.POST:
            return HttpResponseRedirect(reverse('task-detail', args=[task.id]))

    context = _get_default_context(request)
    context.update({'task_time_slot': task_time_slot,
                    'task': task})

    return render_to_response('projects/task_time_delete', context,
                              context_instance=RequestContext(request), response_format=response_format)

#
# Task Statuses
#


@handle_response_format
@mylogin_required
def task_status_add(request, response_format='html'):
    """TaskStatus add"""

    if not request.user.profile.is_admin('anaf.projects'):
        return user_denied(request, message="You don't have administrator access to the Projects module")

    if request.POST:
        if 'cancel' not in request.POST:
            status = TaskStatus()
            form = TaskStatusForm(
                request.user.profile, request.POST, instance=status)
            if form.is_valid():
                status = form.save()
                status.set_user_from_request(request)
                return HttpResponseRedirect(reverse('projects_index_by_status', args=[status.id]))
        else:
            return HttpResponseRedirect(reverse('projects_settings_view'))
    else:
        form = TaskStatusForm(request.user.profile)

    context = _get_default_context(request)
    context.update({'form': form})

    return render_to_response('projects/status_add', context,
                              context_instance=RequestContext(request), response_format=response_format)


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
            return HttpResponseRedirect(reverse('projects_index'))
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

#
# Gantt Chart
#


@mylogin_required
def gantt_view(request, project_id, response_format='html'):
    projects = Project.objects.filter(trash=False)
    project = projects.filter(pk=project_id)[0]
    if not project:
        raise Http404
    ganttData = []

    # generate json
    milestones = Milestone.objects.filter(project=project).filter(trash=False)
    for milestone in milestones:
        tasks = Task.objects.filter(milestone=milestone).filter(
            start_date__isnull=False).filter(end_date__isnull=False).filter(trash=False)
        series = []
        for task in tasks:
            tlabel = (
                task.name[:30] + '..') if len(task.name) > 30 else task.name
            tn = '<a href="{0!s}" class="popup-link">{1!s}</a>'.format(
                reverse('task-detail', args=[task.id]), tlabel)
            series.append({'id': task.id,
                           'name': tn,
                           'label': tlabel,
                           'start': task.start_date.date().isoformat(),
                           'end': task.end_date.date().isoformat()})
        mlabel = (
            milestone.name[:30] + '..') if len(milestone.name) > 30 else milestone.name
        mn = '<a href="{0!s}" class="popup-link projects-milestone">{1!s}</a>'.format(
            reverse('milestone-detail', args=[milestone.id]), mlabel)
        a = {'id': milestone.id, 'name': mn, 'label': mlabel}
        if series:
            a['series'] = series
        else:
            a['series'] = []
        if milestone.start_date and milestone.end_date:
            a['start'] = milestone.start_date.date().isoformat()
            a['end'] = milestone.end_date.date().isoformat()
            a['color'] = '#E3F3D9'
        if series or (milestone.start_date and milestone.end_date):
            ganttData.append(a)
    unclassified = Task.objects.filter(project=project).filter(milestone__isnull=True).filter(
        start_date__isnull=False).filter(end_date__isnull=False).filter(trash=False)
    series = []
    for task in unclassified:
        tlabel = (task.name[:30] + '..') if len(task.name) > 30 else task.name
        tn = '<a href="{0!s}" class="popup-link">{1!s}</a>'.format(
            reverse('task-detail', args=[task.id]), tlabel)
        series.append({'id': task.id,
                       'name': tn,
                       'label': tlabel,
                       'start': task.start_date.date().isoformat(),
                       'end': task.end_date.date().isoformat()})
    if series:
        ganttData.append(
            {'id': 0, 'name': _('Unclassified Tasks'), 'series': series})
    if ganttData:
        jdata = json.dumps(ganttData)
    else:
        jdata = None

    return render_to_response('projects/gantt_view',
                              {'jdata': jdata,
                               'project': project,
                               'projects': projects},
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

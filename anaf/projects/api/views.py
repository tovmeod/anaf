import json
from datetime import datetime

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.utils.translation import ugettext as _
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from rest_framework.viewsets import GenericViewSet

from anaf.core.models import Object, UpdateRecord
from anaf.projects.api.serializers import TaskTimeSlotSerializer
from anaf.projects.forms import FilterForm, MassActionForm, TaskRecordForm, TaskForm, MilestoneForm, ProjectForm, \
    TaskTimeSlotForm
from anaf.projects.models import Project, TaskStatus, Milestone, Task, TaskTimeSlot
from anaf.projects.api.serializers import ProjectSerializer, TaskStatusSerializer, MilestoneSerializer, TaskSerializer
from anaf.projects.views import _get_default_context, _get_filter_query
from anaf.core.ajax.converter import preprocess_context
from anaf import API_RENDERERS


def noapi(viewfunc):
    """
    Used to mark a method on a ViewSet that it only handles the specified accepted formats.
    """
    def decorator(self, request, *args, **kwargs):
        if request.accepted_renderer.format not in self.accepted_formats:
            # This view only handles some formats (html and ajax),
            # so if user requested json for example we return Not Acceptable
            return Response(status=406)
        return viewfunc(self, request, *args, **kwargs)
    return decorator


def apifirst(viewfunc):
    """
    Used to mark a method on a ViewSet to prioritize api formats.
    So if format is not one of the accepted formats use the parent method to process request
    """
    def decorator(self, request, *args, **kwargs):
        if request.accepted_renderer.format in self.accepted_formats:
            return viewfunc(self, request, *args, **kwargs)
        parent_viewfunc = getattr(super(self.__class__, self), viewfunc.__name__)
        return parent_viewfunc(request, *args, **kwargs)
    return decorator


class AnafViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                  mixins.ListModelMixin, GenericViewSet):
    """Base Viewset
    This doesn't have list because for some models it doesn't make sense list"""
    accepted_formats = ('html', 'ajax')

    def retrieve(self, request, *args, **kwargs):
        if request.method != 'GET':
            raise MethodNotAllowed(request.method)
        return super(AnafViewSet, self).retrieve(request, *args, **kwargs)


def process_mass_form(f):
    """Pre-process request to handle mass action form for Tasks and Milestones"""

    def wrap(view, request, *args, **kwargs):
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

        return f(view, request, *args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__

    return wrap


class ProjectView(AnafViewSet):
    """
    API endpoint that allows projects to be viewed or edited.
    """
    queryset = Project.objects.all().order_by('-date_created')
    serializer_class = ProjectSerializer
    template_name = 'projects/index.html'

    @list_route(methods=('GET', 'POST'))
    @noapi
    def new(self, request, *args, **kwargs):
        """New Project page"""
        if request.POST:
            form = ProjectForm(request.user.profile, None, request.POST)
            if form.is_valid():
                project = form.save()
                project.set_user(request.user.profile)
                return HttpResponseRedirect(reverse('project-detail', args=[project.id]))
        else:
            form = ProjectForm(request.user.profile, None)

        context = _get_default_context(request)
        context.update({'form': form})
        return Response(context, template_name='projects/project_add.html')

    @noapi
    def new_to_project(self, request, project_id=None, *args, **kwargs):
        """New sub-Project to preselected project"""

        if request.accepted_renderer.format not in self.accepted_formats:
            return super(ProjectView, self).create(request, *args, **kwargs)

        parent_project = None
        if project_id:
            parent_project = get_object_or_404(Project, pk=project_id)
            if not request.user.profile.has_permission(parent_project, mode='w'):
                parent_project = None

        if request.POST:
            form = ProjectForm(request.user.profile, project_id, request.POST)
            if form.is_valid():
                subproject = form.save()
                subproject.set_user(request.user.profile)
                return HttpResponseRedirect(reverse('project-detail', args=[subproject.id]))
        else:
            form = ProjectForm(request.user.profile, project_id)

        context = _get_default_context(request)
        context.update({'form': form, 'project': parent_project})

        return Response(context, template_name='projects/project_add_typed.html')

    @process_mass_form
    @apifirst
    def retrieve(self, request, *args, **kwargs):
        """Single Project view page"""
        if request.accepted_renderer.format not in self.accepted_formats:
            # This view only handles some formats (html and ajax),
            # so if user requested json for example we just use parent to render the response
            return super(ProjectView, self).retrieve(request, *args, **kwargs)
        project = self.get_object()
        context = _get_default_context(request)

        if request.POST:
            record = UpdateRecord()
            record.record_type = 'manual'
            form = TaskRecordForm(request.user.profile, request.POST, instance=record)
            if form.is_valid():
                record = form.save()
                record.set_user_from_request(request)
                record.save()
                record.about.add(project)
                project.set_last_updated()
                return HttpResponseRedirect(reverse('project-detail', args=[project.id]))
        else:
            form = TaskRecordForm(request.user.profile)

        task_query = Q(parent__isnull=True, project=project)
        if request.GET:
            if 'status' in request.GET and request.GET['status']:
                task_query = task_query & _get_filter_query(request.GET)
            else:
                task_query = task_query & Q(status__hidden=False) & _get_filter_query(request.GET)
        else:
            task_query &= Q(status__hidden=False)
        tasks = Object.filter_by_request(request, Task.objects.filter(task_query))
        tasks_progress = float(0)

        tasks_progress_query = Object.filter_by_request(request,
                                                        Task.objects.filter(Q(parent__isnull=True, project=project)))
        if tasks_progress_query:
            for task in tasks_progress_query:
                if not task.status.active:
                    tasks_progress += 1
            tasks_progress = (tasks_progress / len(tasks_progress_query)) * 100
            tasks_progress = round(tasks_progress, ndigits=1)

        filters = FilterForm(request.user.profile, 'project', request.GET)
        milestones = Object.filter_by_request(request,
                                              Milestone.objects.filter(project=project).filter(status__hidden=False))
        subprojects = Project.objects.filter(parent=project)  # TODO: use Project.objects.child_set
        context.update({'project': project,
                        'milestones': milestones,
                        'tasks': tasks,
                        'tasks_progress': tasks_progress,
                        'record_form': form,
                        'subprojects': subprojects,
                        'filters': filters})

        if 'massform' in context and 'project' in context['massform'].fields:
            del context['massform'].fields['project']

        return Response(context, template_name='projects/project_view.html')

    @detail_route()
    @noapi
    def gantt(self, request, *args, **kwargs):
        """Project gantt view"""
        project = self.get_object()
        gantt_data = []

        # generate json
        milestones = Milestone.objects.filter(project=project).filter(trash=False)
        for milestone in milestones:
            tasks = Task.objects.filter(milestone=milestone).filter(
                start_date__isnull=False).filter(end_date__isnull=False).filter(trash=False)
            series = []
            for task in tasks:
                tlabel = (task.name[:30] + '..') if len(task.name) > 30 else task.name
                tn = '<a href="{0!s}" class="popup-link">{1!s}</a>'.format(reverse('task-detail', args=[task.id]),
                                                                           tlabel)
                series.append({'id': task.id, 'name': tn, 'label': tlabel, 'start': task.start_date.date().isoformat(),
                               'end': task.end_date.date().isoformat()})
            mlabel = (milestone.name[:30] + '..') if len(milestone.name) > 30 else milestone.name
            mn = '<a href="{0!s}" class="popup-link projects-milestone">{1!s}</a>'.format(reverse('milestone-detail',
                                                                                                  args=[milestone.id]),
                                                                                          mlabel)
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
                gantt_data.append(a)
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
            gantt_data.append({'id': 0, 'name': _('Unclassified Tasks'), 'series': series})
        if gantt_data:
            jdata = json.dumps(gantt_data)
        else:
            jdata = None

        context = RequestContext(request)
        context.update({'jdata': jdata, 'project': project})
        return Response(context, template_name='projects/gantt_view.html')

    @detail_route(methods=('GET', 'POST'))
    @noapi
    def edit(self, request, *args, **kwargs):
        """Project edit page"""
        project = self.get_object()
        context = _get_default_context(request)

        if request.POST:
            form = ProjectForm(request.user.profile, None, request.POST, instance=project)
            if form.is_valid():
                project = form.save()
                return HttpResponseRedirect(reverse('project-detail', args=[project.id]))
        else:
            form = ProjectForm(request.user.profile, None, instance=project)

        context.update({'form': form, 'project': project})
        return Response(context, template_name='projects/project_edit.html')

    @detail_route(methods=('GET', 'POST'))
    @noapi
    def delete(self, request, *args, **kwargs):
        """Project delete"""
        project = self.get_object()

        if request.POST:
            if 'trash' in request.POST:
                project.trash = True
                project.save(update_fields=('trash',))
            else:
                project.delete()
            return HttpResponseRedirect(reverse('project-list', kwargs={'format': kwargs.get('format')}))

        context = _get_default_context(request)
        context.update({'project': project})
        return Response(context, template_name='projects/project_delete.html')

    @apifirst
    def list(self, request, *args, **kwargs):
        query = Q(parent__isnull=True)
        if request.GET:
            if 'status' in request.GET and request.GET['status']:
                query = query & _get_filter_query(request.GET)
            else:
                query = query & Q(status__hidden=False) & _get_filter_query(request.GET)
        else:
            query &= Q(status__hidden=False)

        milestones = Object.filter_by_request(request, Milestone.objects.filter(status__hidden=False))
        tasks = Object.filter_by_request(request, Task.objects.filter(query))
        filters = FilterForm(request.user.profile, '', request.GET)
        context = _get_default_context(request)
        context.update({'milestones': milestones, 'tasks': tasks, 'filters': filters})
        context = preprocess_context(context)
        return Response(context, template_name='projects/index.html')


class TaskStatusView(viewsets.ModelViewSet):
    """
    API endpoint that allows Task Status to be viewed or edited.
    """
    queryset = TaskStatus.objects.all()
    serializer_class = TaskStatusSerializer

    renderer_classes = API_RENDERERS


class MilestoneView(AnafViewSet):
    """
    API endpoint that allows Milestones to be viewed or edited.
    """
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer
    template_name = 'projects/milestone_add.html'

    def list(self, request, *args, **kwargs):
        if request.accepted_renderer.format in self.accepted_formats:
            raise Http404
        else:
            return super(MilestoneView, self).list(request, *args, **kwargs)

    @process_mass_form
    @apifirst
    def retrieve(self, request, *args, **kwargs):
        """Milestone view page"""
        milestone = self.get_object()
        tasks_query = Q(milestone=milestone, parent__isnull=True)
        if request.GET:
            if 'status' in request.GET and request.GET['status']:
                query = tasks_query & _get_filter_query(request.GET)
            else:
                query = tasks_query & Q(status__hidden=False) & _get_filter_query(request.GET)
            tasks = Object.filter_by_request(request, Task.objects.filter(query))
        else:
            tasks = Object.filter_by_request(request, Task.objects.filter(tasks_query & Q(status__hidden=False)))

        filters = FilterForm(request.user.profile, 'milestone', request.GET)

        tasks_progress = float(0)
        tasks_progress_query = Object.filter_by_request(request, Task.objects.filter(Q(parent__isnull=True,
                                                                                       milestone=milestone)))
        if tasks_progress_query:
            for task in tasks_progress_query:
                if not task.status.active:
                    tasks_progress += 1
            tasks_progress = (tasks_progress / len(tasks_progress_query)) * 100
            tasks_progress = round(tasks_progress, ndigits=1)

        context = _get_default_context(request)
        context.update({'milestone': milestone,
                        'tasks': tasks,
                        'tasks_progress': tasks_progress,
                        'filters': filters})
        return Response(context, template_name='projects/milestone_view.html')

    @detail_route(methods=('GET', 'POST'))
    @noapi
    def edit(self, request, *args, **kwargs):
        """Milestone edit page"""
        milestone = self.get_object()
        context = _get_default_context(request)

        if request.POST:
            form = MilestoneForm(request.user.profile, None, request.POST, instance=milestone)
            if form.is_valid():
                task = form.save()
                return HttpResponseRedirect(reverse('milestone-detail', args=[task.id]))
        else:
            form = MilestoneForm(request.user.profile, None, instance=milestone)

        context.update({'form': form, 'milestone': milestone})
        return Response(context, template_name='projects/milestone_edit.html')

    @noapi
    def set_status(self, request, status_id, *args, **kwargs):
        """Milestone quick set: Status"""
        # TODO: yes, it is wrong and ugly to change the task status with a GET request :(
        # buut until I have time to change the frontend this is what the frontend requests and expects to happen
        milestone = self.get_object()
        if not milestone.has_perm_write(request.user.profile):
            self.permission_denied(request, message=_("You don't have permission to edit this Milestone"))

        status = get_object_or_404(TaskStatus, pk=status_id)
        if not status.has_perm_read(request.user.profile):
            self.permission_denied(request, message=_("You don't have access to this Milestone Status"))

        if not milestone.status == status:
            milestone.status = status
            milestone.save(update_fields=('status',))

        return self.retrieve(request, *args, **kwargs)

    @detail_route(methods=('GET', 'POST'))
    @noapi
    def delete(self, request, *args, **kwargs):
        """Milestone delete"""
        milestone = self.get_object()

        if request.POST:
            if 'trash' in request.POST:
                milestone.trash = True
                milestone.save(update_fields=('trash',))
            else:
                milestone.delete()
            return HttpResponseRedirect(reverse('project-list'))

        task_query = Q(milestone=milestone, parent__isnull=True)
        if request.GET:
            task_query = task_query & _get_filter_query(request.GET)
        context = _get_default_context(request)
        tasks = Object.filter_by_request(request, Task.objects.filter(task_query))
        context.update({'milestone': milestone, 'tasks': tasks})
        return Response(context, template_name='projects/milestone_delete.html')

    @list_route(methods=('GET', 'POST'))
    @noapi
    def new(self, request, *args, **kwargs):
        if request.POST:
            milestone = Milestone()
            form = MilestoneForm(request.user.profile, None, request.POST, instance=milestone)
            if form.is_valid():
                milestone = form.save()
                milestone.set_user(request.user.profile)
                return HttpResponseRedirect(reverse('milestone-detail', args=[milestone.id]))
        else:
            form = MilestoneForm(request.user.profile, None)

        context = _get_default_context(request)
        context.update({'form': form})
        return Response(context, template_name='projects/milestone_add.html')

    @noapi
    def new_to_project(self, request, project_id=None, *args, **kwargs):
        """New milestone to preselected project"""
        project = None
        if project_id:
            project = get_object_or_404(Project, pk=project_id)
            if not project.has_perm_write(request.user.profile):
                project = None

        if request.POST:
            form = MilestoneForm(request.user.profile, project_id, request.POST)
            if form.is_valid():
                milestone = form.save()
                milestone.set_user(request.user.profile)
                return HttpResponseRedirect(reverse('milestone-detail', args=[milestone.id]))
        else:
            form = MilestoneForm(request.user.profile, project_id)

        context = _get_default_context(request)
        context.update({'form': form, 'project': project})

        return Response(context, template_name='projects/milestone_add_typed.html')


class TaskView(AnafViewSet):
    """
    API endpoint that allows Tasks to be viewed or edited.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    template_name = 'projects/index_owned.html'

    def get_queryset(self):
        query = Q(parent__isnull=True)
        if 'status' in self.request.GET and self.request.GET['status']:
            query = query & _get_filter_query(self.request.GET)
        else:
            query = query & Q(status__hidden=False) & _get_filter_query(self.request.GET)

        return Object.filter_by_request(self.request, Task.objects.filter(query))

    def _list(self, request, queryset, *args, **kwargs):
        """This is an almost copy from the method from the mixin, but it gets the queryset as an argument"""
        # queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @apifirst
    def list(self, request, *args, **kwargs):
        """Basically all tasks current user can read"""
        tasks = self.get_queryset()

        filters = FilterForm(request.user.profile, 'assigned', request.GET)
        time_slots = Object.filter_by_request(request, TaskTimeSlot.objects.filter(time_from__isnull=False,
                                                                                   time_to__isnull=True))

        context = _get_default_context(request)
        context.update({'tasks': tasks, 'filters': filters, 'time_slots': time_slots})

        context = preprocess_context(context)
        return Response(context, template_name='projects/index_owned.html')

    @list_route(methods=('GET', 'POST'))
    @noapi
    def new(self, request, *args, **kwargs):
        """New Task page"""
        if request.POST:
            form = TaskForm(request.user.profile, None, None, None, request.POST)
            if form.is_valid():
                task = form.save()
                task.set_user(request.user.profile)
                return HttpResponseRedirect(reverse('task-detail', args=[task.id]))
        else:
            form = TaskForm(request.user.profile, None, None, None)

        context = _get_default_context(request)
        context.update({'form': form})

        return Response(context, template_name='projects/task_add.html')

    @detail_route(methods=('GET', 'POST'))
    @noapi
    def new_subtask(self, request, *args, **kwargs):
        """New SubTask page"""
        task = self.get_object()
        parent = task

        if request.POST:
            form = TaskForm(request.user.profile, parent, None, None, request.POST)
            if form.is_valid():
                subtask = form.save()
                subtask.set_user(request.user.profile)
                return HttpResponseRedirect(reverse('task-detail', args=[subtask.id]))
        else:
            form = TaskForm(request.user.profile, parent, None, None)

        context = _get_default_context(request)
        context.update({'form': form, 'task': parent})

        return Response(context, template_name='projects/task_add_subtask.html')

    @noapi
    def new_to_milestone(self, request, milestone_id=None, *args, **kwargs):
        """New Task to preselected milestone"""
        milestone = None
        if milestone_id:
            milestone = get_object_or_404(Milestone, pk=milestone_id)
            if not milestone.has_perm_write(request.user.profile):
                milestone = None

        if milestone is not None:
            project = milestone.project
            project_id = milestone.project_id
        else:
            project, project_id = None, None

        if request.POST:
            form = TaskForm(request.user.profile, None, project_id, milestone_id, request.POST)
            if form.is_valid():
                task = form.save()
                task.set_user(request.user.profile)
                return HttpResponseRedirect(reverse('task-detail', args=[task.id]))
        else:
            form = TaskForm(request.user.profile, None, project_id, milestone_id)

        context = _get_default_context(request)
        context.update({'form': form, 'project': project, 'milestone': milestone})

        return Response(context, template_name='projects/task_add_to_milestone.html')

    @noapi
    def new_to_project(self, request, project_id=None, *args, **kwargs):
        """New Task to preselected project"""
        project = None
        if project_id:
            project = get_object_or_404(Project, pk=project_id)
            if not request.user.profile.has_permission(project, mode='w'):
                project = None

        if request.POST:
            task = Task()
            form = TaskForm(request.user.profile, None, project_id, None, request.POST, instance=task)
            if form.is_valid():
                task = form.save()
                task.set_user(request.user.profile)
                return HttpResponseRedirect(reverse('task-detail', args=[task.id]))
        else:
            form = TaskForm(request.user.profile, None, project_id, None)

        context = _get_default_context(request)
        context.update({'form': form, 'project': project})

        return Response(context, template_name='projects/task_add_typed.html')

    @list_route(methods=('GET', 'POST'))
    @process_mass_form
    def owned(self, request, *args, **kwargs):
        """Tasks owned by current user"""
        tasks = self.get_queryset().filter(Q(caller__related_user=self.request.user.profile))

        if request.accepted_renderer.format not in self.accepted_formats:
            return self._list(request, tasks, *args, **kwargs)

        filters = FilterForm(request.user.profile, 'status', request.GET)
        time_slots = Object.filter_by_request(request, TaskTimeSlot.objects.filter(time_from__isnull=False,
                                                                                   time_to__isnull=True))

        context = _get_default_context(request)
        context.update({'sidebar_link': 'owned', 'tasks': tasks, 'filters': filters, 'time_slots': time_slots})

        context = preprocess_context(context)
        return Response(context, template_name='projects/index_owned.html')

    @list_route(methods=('GET', 'POST'))
    @process_mass_form
    def assigned(self, request, *args, **kwargs):
        """Tasks assigned to current user"""
        tasks = self.get_queryset().filter(Q(assigned=request.user.profile))
        if request.accepted_renderer.format not in self.accepted_formats:
            return self._list(request, tasks, *args, **kwargs)

        filters = FilterForm(request.user.profile, 'assigned', request.GET)
        time_slots = Object.filter_by_request(request, TaskTimeSlot.objects.filter(time_from__isnull=False,
                                                                                   time_to__isnull=True))

        context = _get_default_context(request)
        context.update({'sidebar_link': 'assigned', 'tasks': tasks, 'filters': filters, 'time_slots': time_slots})

        context = preprocess_context(context)
        return Response(context, template_name='projects/index_owned.html')

    @list_route(methods=('GET', 'POST'))
    @process_mass_form
    def in_progress(self, request, *args, **kwargs):
        """A page with a list of tasks in progress"""
        tasks = self.get_queryset().filter(Q(tasktimeslot__time_from__isnull=False, tasktimeslot__time_to__isnull=True))
        if request.accepted_renderer.format not in self.accepted_formats:
            return self._list(request, tasks, *args, **kwargs)

        filters = FilterForm(request.user.profile, 'status', request.GET)
        time_slots = Object.filter_by_request(request, TaskTimeSlot.objects.filter(time_from__isnull=False,
                                                                                   time_to__isnull=True))

        context = _get_default_context(request)
        context.update({'sidebar_link': 'in_progress', 'tasks': tasks, 'filters': filters, 'time_slots': time_slots})

        context = preprocess_context(context)
        return Response(context, template_name='projects/index_owned.html')

    @apifirst
    def retrieve(self, request, *args, **kwargs):
        """Single task view page"""
        task = self.get_object()
        context = _get_default_context(request)

        if task.has_perm_write(request.user.profile):
            form = TaskRecordForm(request.user.profile)
        else:
            form = None

        subtasks = Object.filter_by_request(request, Task.objects.filter(parent=task))
        time_slots = Object.filter_by_request(request, TaskTimeSlot.objects.filter(task=task))

        context.update({'task': task, 'subtasks': subtasks, 'record_form': form, 'time_slots': time_slots})

        return Response(context, template_name='projects/task_view.html')

    @detail_route(methods=('GET', 'POST'))
    @noapi
    def edit(self, request, *args, **kwargs):
        """Task edit page"""
        task = self.get_object()
        if request.POST:
            form = TaskForm(request.user.profile, None, None, None, request.POST, instance=task)
            if form.is_valid():
                task = form.save()
                return HttpResponseRedirect(reverse('task-detail', args=[task.id]))
        else:
            form = TaskForm(request.user.profile, None, None, None, instance=task)

        context = _get_default_context(request)
        context.update({'form': form, 'task': task})
        return Response(context, template_name='projects/task_edit.html')

    @detail_route(methods=('GET', 'POST'))
    @noapi
    def delete(self, request, *args, **kwargs):
        """Task delete"""
        task = self.get_object()
        if request.POST:
            if 'trash' in request.POST:
                task.trash = True
                task.save()
            else:
                task.delete()
            return HttpResponseRedirect(reverse('project-list'))

        subtasks = Object.filter_by_request(request, Task.objects.filter(parent=task))
        time_slots = Object.filter_by_request(request, TaskTimeSlot.objects.filter(task=task))

        context = _get_default_context(request)
        context.update({'task': task, 'subtasks': subtasks, 'time_slots': time_slots})
        return Response(context, template_name='projects/task_delete.html')

    @detail_route(methods=('POST',))
    def start(self, request, *args, **kwargs):
        """Task start"""
        task = self.get_object()
        if not task.is_being_done_by(request.user.profile):
            task_time_slot = TaskTimeSlot(task=task, time_from=datetime.now(), user=request.user.profile)
            task_time_slot.save()
            task_time_slot.set_user(request.user.profile)

        return HttpResponseRedirect(reverse('task-detail', args=[task.id]))

    @noapi
    def set_status(self, request, status_id, *args, **kwargs):
        """Task quick set: Status"""
        # TODO: yes, it is wrong and ugly to change the task status with a GET request :(
        # buut until I have time to change the frontend this is what the frontend requests and expects to happen
        task = self.get_object()
        if not task.has_perm_write(request.user.profile):
            self.permission_denied(request, message=_("You don't have permission to edit this Task"))

        status = get_object_or_404(TaskStatus, pk=status_id)
        if not status.has_perm_read(request.user.profile):
            self.permission_denied(request, message=_("You don't have access to this Task Status"))

        if not task.status == status:
            task.status = status
            task.save(update_fields=('status',))

        return self.retrieve(request, *args, **kwargs)


class TaskTimeSlotView(AnafViewSet):
    """
    API endpoint that allows TaskTimeSlots to be viewed or edited.
    """
    queryset = TaskTimeSlot.objects.all()
    serializer_class = TaskTimeSlotSerializer

    template_name = 'projects/task_time_view.html'

    def list(self, request, *args, **kwargs):
        if request.accepted_renderer.format in self.accepted_formats:
            raise Http404
        else:
            return super(TaskTimeSlotView, self).list(request, *args, **kwargs)

    @apifirst
    def retrieve(self, request, *args, **kwargs):
        """Task time slot view page"""
        slot = self.get_object()
        context = _get_default_context(request)
        context.update({'task_time_slot': slot})
        return Response(context, template_name='projects/task_time_view.html')

    @detail_route(methods=('POST',))
    def stop(self, request, *args, **kwargs):
        """Task stop"""
        slot = self.get_object()
        slot.time_to = datetime.now()
        details = request.POST.get('details')
        if details is not None:
            slot.details = details
        slot.save()

        return HttpResponseRedirect(reverse('task-detail', args=[slot.task_id]))

    @detail_route(methods=('GET', 'POST'))
    @noapi
    def edit(self, request, *args, **kwargs):
        """Task edit page"""
        slot = self.get_object()
        if request.POST:
            form = TaskTimeSlotForm(request.user.profile, None, request.POST, instance=slot)
            if form.is_valid():
                slot = form.save()
                return HttpResponseRedirect(reverse('task-detail', args=[slot.task.id]))
        else:
            form = TaskTimeSlotForm(request.user.profile, None, instance=slot)

        context = _get_default_context(request)
        context.update({'form': form, 'task_time_slot': slot})
        return Response(context, template_name='projects/task_time_edit.html')

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route

from anaf.core.models import Object
from anaf.projects.api.serializers import TaskTimeSlotSerializer
from anaf.projects.forms import FilterForm, MassActionForm, TaskRecordForm, TaskForm, MilestoneForm
from anaf.projects.models import Project, TaskStatus, Milestone, Task, TaskTimeSlot
from anaf.projects.api.serializers import ProjectSerializer, TaskStatusSerializer, MilestoneSerializer, TaskSerializer
from anaf.projects.views import _get_default_context, _get_filter_query
from anaf.core.ajax.converter import preprocess_context
from anaf import API_RENDERERS


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


class ProjectView(viewsets.ModelViewSet):
    """
    API endpoint that allows projects to be viewed or edited.
    """
    queryset = Project.objects.all().order_by('-date_created')
    serializer_class = ProjectSerializer
    template_name = 'projects/index.html'
    accepted_formats = ('html', 'ajax')

    def list(self, request, *args, **kwargs):
        if request.accepted_renderer.format not in self.accepted_formats:
            return super(ProjectView, self).list(request, *args, **kwargs)
        query = Q(parent__isnull=True)
        if request.GET:
            if 'status' in request.GET and request.GET['status']:
                query = query & _get_filter_query(request.GET)
            else:
                query = query & Q(status__hidden=False) & _get_filter_query(request.GET)
        else:
            query = query & Q(status__hidden=False)

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


class MilestoneView(viewsets.ModelViewSet):
    """
    API endpoint that allows Milestones to be viewed or edited.
    """
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer
    accepted_formats = ('html', 'ajax')

    @list_route(methods=('GET', 'POST'))
    def new(self, request, *args, **kwargs):
        if request.accepted_renderer.format not in self.accepted_formats:
            return super(MilestoneView, self).create(request, *args, **kwargs)

        if request.POST:
            milestone = Milestone()
            form = MilestoneForm(request.user.profile, None, request.POST, instance=milestone)
            if form.is_valid():
                milestone = form.save()
                milestone.set_user_from_request(request)
                return HttpResponseRedirect(reverse('projects_milestone_view', args=[milestone.id]))
        else:
            form = MilestoneForm(request.user.profile, None)

        context = _get_default_context(request)
        context.update({'form': form})
        return Response(context, template_name='projects/milestone_add.html')


class TaskView(viewsets.ModelViewSet):
    """
    API endpoint that allows Tasks to be viewed or edited.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    template_name = 'projects/index_owned.html'
    accepted_formats = ('html', 'ajax')

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

    def list(self, request, *args, **kwargs):
        """Basically all tasks current user can read"""
        tasks = self.get_queryset()

        if request.accepted_renderer.format not in self.accepted_formats:
            return self._list(request, tasks, *args, **kwargs)

        filters = FilterForm(request.user.profile, 'assigned', request.GET)
        time_slots = Object.filter_by_request(request, TaskTimeSlot.objects.filter(time_from__isnull=False,
                                                                                   time_to__isnull=True))

        context = _get_default_context(request)
        context.update({'tasks': tasks, 'filters': filters, 'time_slots': time_slots})

        context = preprocess_context(context)
        return Response(context, template_name='projects/index_owned.html')

    @list_route(methods=('GET', 'POST'))
    def new(self, request, *args, **kwargs):
        if request.accepted_renderer.format not in self.accepted_formats:
            return super(TaskView, self).create(request, *args, **kwargs)

        if request.POST:
            task = Task()
            form = TaskForm(request.user.profile, None, None, None, request.POST, instance=task)
            if form.is_valid():
                task = form.save()
                task.set_user_from_request(request)
                return HttpResponseRedirect(reverse('task-detail', args=[task.id]))
        else:
            form = TaskForm(request.user.profile, None, None, None)

        context = _get_default_context(request)
        context.update({'form': form})

        return Response(context, template_name='projects/task_add.html')

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

    @list_route()
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

    @list_route()
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

    def retrieve(self, request, *args, **kwargs):
        """Single task view page"""
        task = self.get_object()
        has_permission = request.user.profile.has_permission(task)
        message = _("You don't have permission to view this Task")
        if request.accepted_renderer.format not in self.accepted_formats:
            # This view only handles some formats (html and ajax),
            # so if user requested json for example we just use the serializer to render the response
            if not has_permission:
                raise PermissionDenied(detail=message)
            serializer = self.get_serializer(task)
            return Response(serializer.data)

        context = _get_default_context(request)
        if not has_permission:
            context.update({'message': message})
            return Response(context, template_name='core/user_denied.html', status=403)

        if request.user.profile.has_permission(task, mode='x'):
            form = TaskRecordForm(request.user.profile)
        else:
            form = None

        subtasks = Object.filter_by_request(request, Task.objects.filter(parent=task))
        time_slots = Object.filter_by_request(request, TaskTimeSlot.objects.filter(task=task))

        context.update({'task': task, 'subtasks': subtasks, 'record_form': form, 'time_slots': time_slots})

        if 'massform' in context and 'project' in context['massform'].fields:
            del context['massform'].fields['project']

        return Response(context, template_name='projects/task_view.html')

    @detail_route(methods=('GET', 'POST'))
    def edit(self, request, *args, **kwargs):
        """Task edit page"""

        task = self.get_object()
        has_permission = request.user.profile.has_permission(task, mode='w')
        message = _("You don't have permission to edit this Task")
        if request.accepted_renderer.format not in self.accepted_formats:
            # This view only handles some formats (html and ajax),
            # so if user requested json for example we just use the serializer to render the response
            if not has_permission:
                raise PermissionDenied(detail=message)
            serializer = self.get_serializer(task)
            return Response(serializer.data)

        context = _get_default_context(request)
        if not has_permission:
            context.update({'message': message})
            return Response(context, template_name='core/user_denied.html', status=403)

        if request.POST:
            form = TaskForm(request.user.profile, None, None, None, request.POST, instance=task)
            if form.is_valid():
                task = form.save()
                return HttpResponseRedirect(reverse('task-detail', args=[task.id]))
        else:
            form = TaskForm(request.user.profile, None, None, None, instance=task)

        context.update({'form': form, 'task': task})
        return Response(context, template_name='projects/task_edit.html')

    @detail_route(methods=('GET', 'POST'))
    def delete(self, request, *args, **kwargs):
        """Task delete"""

        task = self.get_object()
        has_permission = request.user.profile.has_permission(task, mode='w')
        message = _("You don't have permission to delete this Task")
        if request.accepted_renderer.format not in self.accepted_formats:
            # This view only handles some formats (html and ajax),
            # so if user requested json for example we just use the serializer to render the response
            if not has_permission:
                raise PermissionDenied(detail=message)
            serializer = self.get_serializer(task)
            return Response(serializer.data)

        context = _get_default_context(request)
        if not has_permission:
            context.update({'message': message})
            return Response(context, template_name='core/user_denied.html', status=403)

        if request.POST:
            if 'trash' in request.POST:
                task.trash = True
                task.save()
            else:
                task.delete()
            return HttpResponseRedirect(reverse('projects_index'))

        subtasks = Object.filter_by_request(request, Task.objects.filter(parent=task))
        time_slots = Object.filter_by_request(request, TaskTimeSlot.objects.filter(task=task))

        context.update({'task': task, 'subtasks': subtasks, 'time_slots': time_slots})
        return Response(context, template_name='projects/task_delete.html')

    def set_status(self, request, status_id, *args, **kwargs):
        """Task quick set: Status"""
        # TODO: yes, it is wrong and ugly to change the task status with a GET request :(
        # buut until I have time to change the frontend this is what the frontend requests and expects to happen

        if request.accepted_renderer.format not in self.accepted_formats:
            # discourage bad use on api
            return Response(status=401)
        task = self.get_object()
        has_permission = request.user.profile.has_permission(task, mode='x')
        context = _get_default_context(request)
        if not has_permission:
            message = _("You don't have permission to edit this Task")
            context.update({'message': message})
            return Response(context, template_name='core/user_denied.html', status=403)

        # status_id = kwargs['status_id']
        status = get_object_or_404(TaskStatus, pk=status_id)
        if not request.user.profile.has_permission(status):
            message = _("You don't have access to this Task Status")
            context.update({'message': message})
            return Response(context, template_name='core/user_denied.html', status=403)

        if not task.status == status:
            task.status = status
            task.save()

        return self.retrieve(request, *args, **kwargs)


class TaskTimeSlotView(viewsets.ModelViewSet):
    """
    API endpoint that allows TaskTimeSlots to be viewed or edited.
    """
    queryset = TaskTimeSlot.objects.all()
    serializer_class = TaskTimeSlotSerializer

    renderer_classes = API_RENDERERS

from django.db.models import Q
from rest_framework import viewsets
from rest_framework.response import Response

from anaf.core.models import Object
from anaf.projects.api.serializers import TaskTimeSlotSerializer
from anaf.projects.forms import FilterForm
from anaf.projects.models import Project, TaskStatus, Milestone, Task, TaskTimeSlot
from anaf.projects.api.serializers import ProjectSerializer, TaskStatusSerializer, MilestoneSerializer, TaskSerializer
from anaf.projects.views import _get_default_context, _get_filter_query
from anaf.core.ajax.converter import preprocess_context


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
        context.update({'milestones': milestones,
                        'tasks': tasks,
                        'filters': filters})
        context = preprocess_context(context)
        return Response(context, template_name='projects/index.html')


class TaskStatusView(viewsets.ModelViewSet):
    """
    API endpoint that allows Task Status to be viewed or edited.
    """
    queryset = TaskStatus.objects.all()
    serializer_class = TaskStatusSerializer


class MilestoneView(viewsets.ModelViewSet):
    """
    API endpoint that allows Milestones to be viewed or edited.
    """
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer


class TaskView(viewsets.ModelViewSet):

    """API endpoint that allows Tasks to be viewed or edited."""
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskTimeSlotView(viewsets.ModelViewSet):
    """
    API endpoint that allows TaskTimeSlots to be viewed or edited.
    """
    queryset = TaskTimeSlot.objects.all()
    serializer_class = TaskTimeSlotSerializer

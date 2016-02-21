from rest_framework import viewsets

from anaf.projects.api.serializers import TaskTimeSlotSerializer
from anaf.projects.models import Project, TaskStatus, Milestone, Task, TaskTimeSlot
from serializers import ProjectSerializer, TaskStatusSerializer, MilestoneSerializer, TaskSerializer


class ProjectView(viewsets.ModelViewSet):
    """
    API endpoint that allows projects to be viewed or edited.
    """
    queryset = Project.objects.all().order_by('-date_created')
    serializer_class = ProjectSerializer


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

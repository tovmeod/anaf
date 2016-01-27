from rest_framework import viewsets
from anaf.projects.models import Project, TaskStatus
from serializers import ProjectSerializer, TaskStatusSerializer


class ProjectView(viewsets.ModelViewSet):
    """
    API endpoint that allows projects to be viewed or edited.
    """
    queryset = Project.objects.all().order_by('-date_created')
    serializer_class = ProjectSerializer


class TaskStatusView(viewsets.ModelViewSet):
    """
    API endpoint that allows projects to be viewed or edited.
    """
    queryset = TaskStatus.objects.all()
    serializer_class = TaskStatusSerializer

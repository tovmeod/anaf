from rest_framework import viewsets

from anaf.core.rendering import API_RENDERERS
from anaf.core.models import User as Profile, AccessEntity, Group, Perspective, Object, Module
import serializers
from anaf.viewsets import AnafViewSet


class CoreBaseViewSet(AnafViewSet):
    module = 'anaf.core'


class ProfileView(CoreBaseViewSet):
    """
    API endpoint that allows user profiles to be viewed or edited.
    """
    queryset = Profile.objects.all()
    serializer_class = serializers.ProfileSerializer

    renderer_classes = API_RENDERERS


class GroupView(CoreBaseViewSet):
    """
    API endpoint that allows Groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer

    renderer_classes = API_RENDERERS


class PerspectiveView(CoreBaseViewSet):
    """
    API endpoint that allows Groups to be viewed or edited.
    """
    queryset = Perspective.objects.all()
    serializer_class = serializers.PerspectiveSerializer

    renderer_classes = API_RENDERERS


class AccessEntityView(CoreBaseViewSet):
    """
    API endpoint that allows Access Entities to be viewed or edited.
    """
    queryset = AccessEntity.objects.all()
    serializer_class = serializers.AccessEntitySerializer

    renderer_classes = API_RENDERERS


class ObjectView(viewsets.ModelViewSet):
    """
    API endpoint that allows anaf Objects to be viewed or edited.
    """
    queryset = Object.objects.all()
    serializer_class = serializers.ObjectSerializer


class ModuleView(viewsets.ModelViewSet):
    """
    API endpoint that allows anaf Modules to be viewed or edited.
    """
    queryset = Module.objects.all()
    serializer_class = serializers.ModuleSerializer

from rest_framework import viewsets, views
from rest_framework import serializers
from anaf.core.models import User as Profile, AccessEntity, Group, Perspective
from anaf.identities.models import Contact, ContactType, ContactValue
from anaf.projects.models import Project


class PerspectiveSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Perspective


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    perspective = PerspectiveSerializer(source='get_perspective')

    class Meta:
        model = Group


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    default_group = GroupSerializer()
    perspective = PerspectiveSerializer(source='get_perspective')

    class Meta:
        model = Profile
        # fields = ('name', 'user', 'default_group', 'other_groups', 'disabled', 'last_access', 'last_updated')


class ContactTypeSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = ContactType


class ContactValueSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ContactValue


class ContactSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    contact_type = ContactTypeSerializer()
    contactvalue_set = ContactValueSerializer(many=True)

    class Meta:
        model = Contact


class AccessEntitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AccessEntity


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    creator = ProfileSerializer()
    client = ContactSerializer()
    manager = ContactSerializer()

    class Meta:
        model = Project
        # depth = 3
        # fields = ('name', 'parent', 'manager', 'client', 'details', 'last_updated', 'details')
        # creator = ProfileSerializer()


class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows projects to be viewed or edited.
    """
    queryset = Project.objects.all().order_by('-date_created')
    serializer_class = ProjectSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows user profiles to be viewed or edited.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class ContactViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows contacts to be viewed or edited.
    """
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer


class ContactTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows contacts to be viewed or edited.
    """
    queryset = ContactType.objects.all()
    serializer_class = ContactTypeSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class PerspectiveViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Groups to be viewed or edited.
    """
    queryset = Perspective.objects.all()
    serializer_class = PerspectiveSerializer

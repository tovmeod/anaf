from anaf.projects.models import Project
from rest_framework import serializers
from anaf.identities.api.serializers import ContactSerializer
from anaf.core.api.serializers import ProfileSerializer


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    creator = ProfileSerializer()
    client = ContactSerializer()
    manager = ContactSerializer()

    class Meta:
        model = Project

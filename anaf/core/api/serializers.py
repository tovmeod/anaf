from rest_framework import serializers
from anaf.core.models import User as Profile, AccessEntity, Group, Perspective, Object, Module


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


class ObjectSerializer(serializers.HyperlinkedModelSerializer):
    # id = serializers.ReadOnlyField()

    class Meta:
        model = Object


class ModuleSerializer(serializers.HyperlinkedModelSerializer):
    # id = serializers.ReadOnlyField()

    class Meta:
        model = Module


class AccessEntitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AccessEntity

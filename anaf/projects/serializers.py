from anaf.projects.models import Project, TaskStatus, Milestone, Task, TaskTimeSlot
from rest_framework import serializers

common_exclude = ('full_access', 'nuvius_resource', 'object_name', 'read_access')


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        exclude = common_exclude


class TaskStatusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TaskStatus
        exclude = common_exclude


class MilestoneSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Milestone
        exclude = common_exclude


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Task
        exclude = common_exclude


class TaskTimeSlotSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TaskTimeSlot
        exclude = common_exclude

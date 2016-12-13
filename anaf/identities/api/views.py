from rest_framework import viewsets

from anaf import API_RENDERERS
from anaf.identities import models
from anaf.identities.api import serializers
from anaf.viewsets import AnafViewSet


class IdentitiesBaseViewSet(AnafViewSet):
    module = 'anaf.identities'


class ContactField(IdentitiesBaseViewSet):
    """
    API endpoint that allows Contact Fields to be viewed or edited.
    """
    queryset = models.ContactField.objects.all()
    serializer_class = serializers.ContactField

    renderer_classes = API_RENDERERS


class ContactType(IdentitiesBaseViewSet):
    """
    API endpoint that allows contact types to be viewed or edited.
    """
    queryset = models.ContactType.objects.all()
    serializer_class = serializers.ContactType

    renderer_classes = API_RENDERERS


class Contact(IdentitiesBaseViewSet):
    """
    API endpoint that allows contacts to be viewed or edited.
    """
    queryset = models.Contact.objects.all()
    serializer_class = serializers.Contact

    renderer_classes = API_RENDERERS


class ContactValue(IdentitiesBaseViewSet):
    """
    API endpoint that allows contact values to be viewed or edited.
    """
    queryset = models.ContactValue.objects.all()
    serializer_class = serializers.ContactValue

    renderer_classes = API_RENDERERS

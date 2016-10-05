from rest_framework import viewsets
from anaf.identities import models
from anaf.identities.api import serializers


class ContactField(viewsets.ModelViewSet):
    """
    API endpoint that allows Contact Fields to be viewed or edited.
    """
    queryset = models.ContactField.objects.all()
    serializer_class = serializers.ContactField


class ContactType(viewsets.ModelViewSet):
    """
    API endpoint that allows contact types to be viewed or edited.
    """
    queryset = models.ContactType.objects.all()
    serializer_class = serializers.ContactType


class Contact(viewsets.ModelViewSet):
    """
    API endpoint that allows contacts to be viewed or edited.
    """
    queryset = models.Contact.objects.all()
    serializer_class = serializers.Contact


class ContactValue(viewsets.ModelViewSet):
    """
    API endpoint that allows contact values to be viewed or edited.
    """
    queryset = models.ContactValue.objects.all()
    serializer_class = serializers.ContactValue

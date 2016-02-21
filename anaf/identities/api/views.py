from rest_framework import viewsets
from anaf.identities.models import Contact, ContactType, ContactField
from anaf.identities.api import serializers


class ContactFieldView(viewsets.ModelViewSet):
    """
    API endpoint that allows Contact Fields to be viewed or edited.
    """
    queryset = ContactField.objects.all()
    serializer_class = serializers.ContactFieldSerializer


class ContactView(viewsets.ModelViewSet):
    """
    API endpoint that allows contacts to be viewed or edited.
    """
    queryset = Contact.objects.all()
    serializer_class = serializers.ContactSerializer


class ContactTypeView(viewsets.ModelViewSet):
    """
    API endpoint that allows contact types to be viewed or edited.
    """
    queryset = ContactType.objects.all()
    serializer_class = serializers.ContactTypeSerializer

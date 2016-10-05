from rest_framework import serializers
from anaf.identities import models


class ContactField(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = models.ContactField


class ContactType(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = models.ContactType


class ContactValue(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ContactValue


class Contact(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    contact_type = ContactType()
    contactvalue_set = ContactValue(many=True)

    class Meta:
        model = models.Contact

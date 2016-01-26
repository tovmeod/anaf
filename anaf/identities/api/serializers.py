from rest_framework import serializers
from anaf.identities.models import Contact, ContactType, ContactValue, ContactField


class ContactFieldSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = ContactField


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


from django.template import RequestContext
from rest_framework.decorators import list_route
from rest_framework.response import Response

from anaf.core.decorators import apifirst
from anaf.core.models import Object
from anaf.core.rendering import API_RENDERERS, NOAPI_RENDERERS
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

    @list_route(methods=('GET',), renderer_classes=NOAPI_RENDERERS)
    def add(self, request, type_id=None, *args, **kwargs):
        """Contact add"""

        types = Object.filter_by_request(request, models.ContactType.objects.order_by('name'))

        context = RequestContext(request)
        context.update({'types': types})
        # return render_to_response('identities/contact_add', {'types': types},
        #                           context_instance=RequestContext(request), response_format=response_format)

        return Response({'types': types}, template_name='identities/contact_add.html')

    @apifirst
    def retrieve(self, request, *args, **kwargs):
        """Contact view"""
        contact = self.get_object()
        serializer = self.get_serializer(contact)
        return Response(serializer.data)


class ContactValue(IdentitiesBaseViewSet):
    """
    API endpoint that allows contact values to be viewed or edited.
    """
    queryset = models.ContactValue.objects.all()
    serializer_class = serializers.ContactValue

    renderer_classes = API_RENDERERS

from rest_framework import viewsets
from rest_framework.exceptions import MethodNotAllowed


class AnafViewSet(viewsets.ModelViewSet):
    """Base Viewset"""
    accepted_formats = ('html', 'ajax')

    def retrieve(self, request, *args, **kwargs):
        if request.method != 'GET':
            raise MethodNotAllowed(request.method)
        return super(AnafViewSet, self).retrieve(request, *args, **kwargs)
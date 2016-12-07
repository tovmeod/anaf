import warnings
from rest_framework.permissions import BasePermission
from anaf.core.models import Object as AnafObject


class ObjectPermissions(BasePermission):
    """Implementation of object level permissions
    Anonymous users are not allowed
    The system may stores two kinds of permissions for each user/object combination read and/or write
    Each object is asked if the current user can read or write,
    the permission is checked only for this one object and not for parent objects, for example:
    it would make sense to say that a user can read a task that belongs to a project which the user has read permission
    but this would be too intensive, I've decided instead to copy permissions when an Object is created"""

    def has_permission(self, request, view):
        """
        Allows access only to authenticated users.
        """
        return request.user and request.user.is_authenticated()

    def has_object_permission(self, request, view, obj):
        """

        :type obj: Object
        """
        if request.user.is_staff:  # staff can read and write to all objects
            return True
        if not isinstance(obj, AnafObject):
            warnings.warn('Can not determine permissions for object: {} type {} id: {}'.format(obj, type(obj), obj.id),
                          stacklevel=2)
            return True
        # Determine if user is trying to read or write
        # Assume the worst, that user is trying to write unless some specific conditions
        can_write = obj.has_perm_write(request.user.profile)
        if request.method in ('GET', 'OPTIONS', 'HEAD'):
            # anything else it is assumed the user is trying to write (POST, PUT, PATCH, DELETE)
            return can_write or obj.has_perm_read(request.user.profile)
        return can_write

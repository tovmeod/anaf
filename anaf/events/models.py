"""
Events module objects.

Depends on: anaf.core, anaf.identities
"""

from django.db import models
from django.core.urlresolvers import reverse
from anaf.identities.models import Contact
from anaf.core.models import Object, Location


class Event(Object):

    """ Single Event """
    name = models.CharField(max_length=255)
    location = models.ForeignKey(
        Location, blank=True, null=True, on_delete=models.SET_NULL)
    details = models.TextField(max_length=255, null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField()

    class Meta:

        """Event"""
        ordering = ['-end']

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        """Returns absolute URL of the object"""
        return reverse('events_event_view', args=[self.id])


class Invitation(models.Model):

    """ Invitation to an Event """
    contact = models.ForeignKey(Contact)
    event = models.ForeignKey(Event)
    status = models.CharField(max_length=255, choices=(('attending', 'Attending'),
                                                       ('pending', 'Pending'),
                                                       ('not-attending', 'Not Attending')))

    def __unicode__(self):
        return 'Invitation to {}'.format(self.contact)

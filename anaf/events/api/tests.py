import json
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User as DjangoUser
from anaf.core.models import Group, Perspective, ModuleSetting
from anaf.events.models import Event
from datetime import datetime


class EventsViewsTest(TestCase):
    """Events functional tests for api"""
    username = "api_test"
    password = "api_password"
    authentication_headers = {"CONTENT_TYPE": "application/json",
                              "HTTP_AUTHORIZATION": "Basic YXBpX3Rlc3Q6YXBpX3Bhc3N3b3Jk"}
    content_type = 'application/json'

    def setUp(self):
        self.group, created = Group.objects.get_or_create(name='test')
        self.user, created = DjangoUser.objects.get_or_create(username=self.username, is_staff=True)
        self.user.set_password(self.password)
        self.user.save()

        perspective, created = Perspective.objects.get_or_create(name='default')
        perspective.set_default_user()
        perspective.save()

        ModuleSetting.set('default_perspective', perspective.id)

        self.event = Event(name='TestStatus', end=datetime.now())
        self.event.set_default_user()
        self.event.save()

    def test_unauthenticated_access(self):
        """Test index page at /api/calendar/events"""
        response = self.client.get('/api/calendar/events')
        # Redirects as unauthenticated
        self.assertEquals(response.status_code, 401)

    def test_get_events_list(self):
        """ Test index page api/infrastructure/types """
        response = self.client.get(
            path=reverse('api_events'), **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

    def test_get_field(self):
        response = self.client.get(path=reverse(
            'api_events', kwargs={'object_ptr': self.event.id}), **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

    def test_update_field(self):
        updates = {"name": "Api_name", "details": "Api details",
                   "start": "2011-03-01 01:12:09", "end": "2011-03-09 13:05:09"}
        response = self.client.put(path=reverse('api_events', kwargs={'object_ptr': self.event.id}),
                                   content_type=self.content_type, data=json.dumps(updates),
                                   **self.authentication_headers)
        self.assertEquals(response.status_code, 200)
        # TODO: update this to parse the dates properly.

        data = json.loads(response.content)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(data['name'], updates['name'])
        self.assertEquals(data['details'], updates['details'])
        self.assertEquals(data['start'].replace("T", " "), updates['start'])
        self.assertEquals(data['end'].replace("T", " "), updates['end'])

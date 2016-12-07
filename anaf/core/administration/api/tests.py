"""
Core: test api
"""
import json
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User as DjangoUser
from anaf.core.models import Group, ModuleSetting, Perspective


class CoreAPITest(TestCase):
    """Core api tests"""

    username = "api_test"
    password = "api_password"
    authentication_headers = {"CONTENT_TYPE": "application/json",
                              "HTTP_AUTHORIZATION": "Basic YXBpX3Rlc3Q6YXBpX3Bhc3N3b3Jk"}
    content_type = 'application/json'

    def setUp(self):
        self.group = Group.objects.get_or_create(name='test')[0]
        duser = DjangoUser.objects.get_or_create(username=self.username, is_staff=True)[0]
        duser.set_password(self.password)
        duser.save()
        self.user = duser
        perspective = Perspective.objects.get_or_create(name='default')[0]
        perspective.set_default_user()
        perspective.save()
        ModuleSetting.set('default_perspective', perspective.id)

        self.perspective = Perspective(name='test')
        self.perspective.set_default_user()
        self.perspective.save()

        self.group = Group(name='test')
        self.group.save()

    def test_unauthenticated_access(self):
        """Test index page at /admin/api/users"""
        response = self.client.get('/admin/api/users')
        # Redirects as unauthenticated
        self.assertEquals(response.status_code, 404)

    def test_get_ticket_groups_list(self):
        """ Test index page api /admin/api/groups """
        response = self.client.get(
            path=reverse('api_admin_groups'), **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

    def test_get_group(self):
        response = self.client.get(path=reverse('api_admin_groups', kwargs={
            'accessentity_ptr': self.group.id}), **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

    def test_update_group(self):
        updates = {'name': 'Api group name', 'details': '<p>api details</p>', 'perspective': self.perspective.id}
        response = self.client.put(path=reverse('api_admin_groups', kwargs={'accessentity_ptr': self.group.id}),
                                   content_type=self.content_type, data=json.dumps(updates),
                                   **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEquals(data['name'], updates['name'])
        self.assertEquals(data['details'], updates['details'])
        self.assertEquals(data['perspective']['id'], updates['perspective'])

    def test_get_ticket_users_list(self):
        """ Test index page api /admin/api/users """
        response = self.client.get(
            path=reverse('api_admin_users'), **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

    def test_get_user(self):
        response = self.client.get(path=reverse('api_admin_users', kwargs={
            'accessentity_ptr': self.user.profile.id}), **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

    def test_update_user(self):
        updates = {'name': 'Api user name', 'default_group': self.group.id, 'disabled': False,
                   'perspective': self.perspective.id}
        response = self.client.put(path=reverse('api_admin_users', kwargs={'accessentity_ptr': self.user.id}),
                                   content_type=self.content_type, data=json.dumps(updates),
                                   **self.authentication_headers)
        self.assertEquals(response.status_code, 405)

        # data = json.loads(response.content)
        # self.assertEquals(data['name'], updates['name'])
        # self.assertEquals(data['disabled'], updates['disabled'])
        # self.assertEquals(data['default_group']['id'], updates['default_group'])
        # self.assertEquals(data['perspective']['id'], updates['perspective'])

    def test_delete_self(self):
        response = self.client.delete(path=reverse('api_admin_users', kwargs={
            'accessentity_ptr': self.user.profile.id}), **self.authentication_headers)
        self.assertEquals(response.status_code, 401)

    def test_get_ticket_modules_list(self):
        """ Test index page api /admin/api/modules """
        response = self.client.get(
            path=reverse('api_admin_modules'), **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

    def test_get_ticket_perspectives_list(self):
        """ Test index page api /admin/api/perspectives """
        response = self.client.get(
            path=reverse('api_admin_perspectives'), **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

    def test_get_perspective(self):
        response = self.client.get(path=reverse('api_admin_perspectives', kwargs={
            'object_ptr': self.perspective.id}), **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

    def test_update_perspective(self):
        updates = {'name': 'Api perspective', 'details': 'Api details'}
        response = self.client.put(path=reverse('api_admin_perspectives', kwargs={'object_ptr': self.perspective.id}),
                                   content_type=self.content_type, data=json.dumps(updates),
                                   **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEquals(data['name'], updates['name'])
        self.assertEquals(data['details'], updates['details'])

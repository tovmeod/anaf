"""
API Project Management: test suites
"""
from time import sleep
import json
from datetime import datetime
from django.test import TestCase
from anaf.test import TestCase as TreeTestCase
from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User as DjangoUser
from freezegun import freeze_time

from anaf.identities.models import Contact, ContactType
from anaf.core.models import User, Group, Perspective, ModuleSetting
from anaf.projects.models import Project, Milestone, Task, TaskStatus, TaskTimeSlot


class ProjectsAPITest(TreeTestCase):
    """Projects functional tests for api"""
    username = "api_test"
    password = "api_password"
    authentication_headers = {"CONTENT_TYPE": "application/json",
                              "HTTP_AUTHORIZATION": "Basic YXBpX3Rlc3Q6YXBpX3Bhc3N3b3Jk"}
    content_type = 'application/json'

    def setUp(self):
        # Create objects
        self.group, created = Group.objects.get_or_create(name='api_test_group')
        with freeze_time(datetime(year=2015, month=10, day=8, hour=7, minute=20)):
            DjangoUser.objects.get_or_create(username='api_test_first_user')
        with freeze_time(datetime(year=2015, month=11, day=9, hour=8, minute=21)):
            self.user, created = DjangoUser.objects.get_or_create(username=self.username)
        with freeze_time(datetime(year=2015, month=12, day=10, hour=9, minute=22)):
            DjangoUser.objects.get_or_create(username='api_test_third_user')
        self.user.set_password(self.password)
        self.user.save()
        self.profile = self.user.profile

        perspective, created = Perspective.objects.get_or_create(name='default')
        perspective.set_default_user()
        perspective.save()

        ModuleSetting.set('default_perspective', perspective.id)

        self.contact_type = ContactType(name='api_test_contacttype')
        self.contact_type.set_default_user()
        self.contact_type.save()

        self.contact = Contact(name='api_test_contact', contact_type=self.contact_type)
        self.contact.set_default_user()
        self.contact.save()

        with freeze_time(datetime(year=2015, month=11, day=9, hour=8, minute=21)):
            self.project = Project(name='api_test_project', manager=self.contact, client=self.contact)

        self.project.set_default_user()
        with freeze_time(datetime(year=2015, month=11, day=9, hour=8, minute=26)):
            self.project.save()

        self.status = TaskStatus(name='api_test_taskstatus')
        self.status.set_default_user()
        self.status.save()

        self.milestone = Milestone(name='api_test_milestone', project=self.project, status=self.status)
        self.milestone.set_default_user()
        self.milestone.save()

        self.task = Task(name='api_test_task', project=self.project, status=self.status, priority=3)
        self.task.set_default_user()
        self.task.save()

        self.time_slot = TaskTimeSlot(
            task=self.task, details='api_test_tasktimeslot', time_from=datetime.now(), user=self.user.profile)
        self.time_slot.set_default_user()
        self.time_slot.save()

        self.parent = Project(name='api_test_project_parent')
        self.parent.set_default_user()
        self.parent.save()

        self.parent_task = Task(name='api_test', project=self.project, status=self.status, priority=3)
        self.parent_task.set_default_user()
        self.parent_task.save()

    def test_unauthenticated_access(self):
        """Test index page at /projects"""
        response = self.client.get('/api/projects/projects')
        # Redirects as unauthenticated
        self.assertEquals(response.status_code, 401)

    # Get info about projects, milestones, status, tasks, tasktimes.

    def test_get_project_list(self):
        """ Test index page api/projects """
        response = self.client.get(path=reverse('api_projects'), **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

    def test_get_status_list(self):
        """ Test index page api/status """
        response = self.client.get(
            path=reverse('api_projects_status'), **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

    def test_get_milestones_list(self):
        """ Test index page api/milestones """
        response = self.client.get(
            path=reverse('api_projects_milestones'), **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

    def test_get_task_list(self):
        """ Test index page api/tasks """
        response = self.client.get(
            path=reverse('api_projects_tasks'), **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

    def test_get_tasktimes_list(self):
        """ Test index page api/tasktimes """
        response = self.client.get(
            path=reverse('api_projects_tasktimes'), **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

    def test_get_project(self):
        response = self.client.get(reverse(
            'api_projects', kwargs={'object_ptr': self.project.id}), **self.authentication_headers)
        response2 = self.client.get(reverse(
            'project-detail', kwargs={'pk': self.project.id}), **self.authentication_headers)
        print(json.loads(response.content))
        print(json.loads(response2.content))
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.content)
        expected = {
            u'last_updated': u'2015-11-09T08:26:00', u'name': u'api_test_project', u'parent': None,
            u'creator': {
                u'name': u'api_test',
                u'default_group': {
                    u'perspective': {
                        u'details': u'', u'modules': [], u'id': 1, u'name': u'default',
                        u'resource_uri': u'/api/core/perspective/1'
                    },
                    u'name': u'api_test_group', u'parent': None, u'details': None, u'id': 1,
                    u'resource_uri': u'/api/core/group/1'
                },
                u'disabled': False, u'other_groups': [], u'perspective': {
                    u'details': u'', u'modules': [], u'id': 1, u'name': u'default',
                    u'resource_uri': u'/api/core/perspective/1'
                },
                u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
            },
            u'nuvius_resource': None, u'manager': {
                u'name': u'api_test_contact', u'parent': None, u'contact_type': {
                    u'fields': [], u'details': None, u'id': 2, u'name': u'api_test_contacttype',
                    u'resource_uri': u'/api/identities/type/2'
                }, u'contactvalue_set': [], u'related_user': None, u'id': 3,
                u'resource_uri': u'/api/identities/contact/3'
            },
            u'client': {
                u'name': u'api_test_contact', u'parent': None,
                u'contact_type': {
                    u'fields': [], u'details': None, u'id': 2, u'name': u'api_test_contacttype',
                    u'resource_uri': u'/api/identities/type/2'}, u'contactvalue_set': [], u'related_user': None,
                u'id': 3, u'resource_uri': u'/api/identities/contact/3'
            },
            u'details': None,
            u'date_created': u'2015-11-09T08:21:00', u'trash': False, u'id': self.project.id,
            u'resource_uri': u'/api/projects/project/%s' % self.project.id
        }

        self.assertEquals(data['id'], self.project.id)
        self.assertEquals(data['name'], self.project.name)
        self.assertEquals(data['details'], self.project.details)
        self.assertDictEqual(data, expected)

        self.cmpDataApi(response.content, response2.content)

    def test_get_status(self):
        response = self.client.get(reverse('api_projects_status', kwargs={
                                   'object_ptr': self.status.id}), **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEquals(data['id'], self.status.id)
        self.assertEquals(data['name'], self.status.name)

    def test_get_milestone(self):
        response = self.client.get(reverse('api_projects_milestones', kwargs={
                                   'object_ptr': self.milestone.id}), **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEquals(data['id'], self.milestone.id)
        self.assertEquals(data['name'], self.milestone.name)
        self.assertEquals(data['project']['id'], self.milestone.project.id)
        self.assertEquals(data['status']['id'], self.milestone.status.id)

    def test_get_task(self):
        response = self.client.get(reverse('api_projects_tasks', kwargs={
                                   'object_ptr': self.task.id}), **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEquals(data['id'], self.task.id)
        self.assertEquals(data['name'], self.task.name)
        self.assertEquals(data['priority'], self.task.priority)
        self.assertEquals(data['project']['id'], self.task.project.id)
        self.assertEquals(data['status']['id'], self.task.status.id)

    def test_get_timeslot(self):
        response = self.client.get(reverse('api_projects_tasktimes', kwargs={
                                   'object_ptr': self.time_slot.id}), **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEquals(data['id'], self.time_slot.id)
        self.assertEquals(data['task']['id'], self.time_slot.task.id)

    # Common test

    def test_common_project(self):

        # create new project
        new_project = {'name': 'api test',
                       'details': '<p>test details</p>'}
        response = self.client.post(reverse('api_projects'), data=json.dumps(new_project),
                                    content_type=self.content_type, **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

        # check data in response
        data = json.loads(response.content)
        self.assertEquals(data['name'], new_project['name'])
        self.assertEquals(data['details'], new_project['details'])
        project_id = data['id']

        # get info about new project
        response = self.client.get(path=reverse(
            'api_projects', kwargs={'object_ptr': project_id}), **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

        # get statuses list
        response = self.client.get(
            path=reverse('api_projects_status'), **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

        statuses = json.loads(response.content)
        fstatus = statuses[0]['id']

        # create new task status
        new_status = {'name': 'Open api test',
                      'active': True,
                      'hidden': False,
                      'details': '<p>test details</p>'}
        response = self.client.post(reverse('api_projects_status'), data=json.dumps(new_status),
                                    content_type=self.content_type, **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEquals(data['name'], new_status['name'])
        self.assertEquals(data['active'], new_status['active'])
        self.assertEquals(data['hidden'], new_status['hidden'])
        self.assertEquals(data['details'], new_status['details'])
        sstatus = data['id']

        # create new milestone
        new_milestone = {'name': 'api test milestone',
                         'status': fstatus,
                         'project': project_id,
                         'start_date': '2011-06-09 12:00:00',
                         'details': '<p>test details</p>'}
        response = self.client.post(reverse('api_projects_milestones'), data=json.dumps(new_milestone),
                                    content_type=self.content_type, **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEquals(data['name'], new_milestone['name'])
        self.assertEquals(data['status']['id'], new_milestone['status'])
        self.assertEquals(data['project']['id'], new_milestone['project'])
        self.assertEquals(data['details'], new_milestone['details'])
        milestone_id = data['id']

        #  create new task
        new_task = {'name': 'api test task',
                    'status': sstatus,
                    'project': project_id,
                    'milestone': milestone_id,
                    'priority': 5,
                    'start_date': '2011-06-02 12:00:00',
                    'estimated_time': 5000,
                    'details': '<p>test details</p>'
                    }
        response = self.client.post(reverse('api_projects_tasks'), data=json.dumps(new_task),
                                    content_type=self.content_type, **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEquals(data['name'], new_task['name'])
        self.assertEquals(data['priority'], new_task['priority'])
        self.assertEquals(data['status']['id'], new_task['status'])
        self.assertEquals(data['project']['id'], new_task['project'])
        self.assertEquals(data['milestone']['id'], new_task['milestone'])
        self.assertEquals(data['estimated_time'], new_task['estimated_time'])
        self.assertEquals(data['details'], new_task['details'])
        task_id = data['id']

        # create new subtask
        new_sub_task = {'name': 'api test task',
                        'status': sstatus,
                        'parent': task_id,
                        'project': project_id,
                        'priority': 5,
                        'start_date': '2011-06-02 13:00:00',
                        'estimated_time': 2500,
                        'details': '<p>test details</p>'
                        }

        response = self.client.post(reverse('api_projects_tasks'), data=json.dumps(new_sub_task),
                                    content_type=self.content_type, **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEquals(data['name'], new_sub_task['name'])
        self.assertEquals(data['priority'], new_sub_task['priority'])
        self.assertEquals(data['status']['id'], new_sub_task['status'])
        self.assertEquals(data['parent']['id'], new_sub_task['parent'])
        self.assertEquals(data['project']['id'], new_sub_task['project'])
        self.assertEquals(
            data['estimated_time'], new_sub_task['estimated_time'])
        self.assertEquals(data['details'], new_sub_task['details'])
        sub_task_id = data['id']

        # create task time
        new_tasktime = {'task': task_id,
                        'minutes': 400,
                        'details': '<p>test details</p>'
                        }

        response = self.client.post(reverse('api_projects_tasktimes'), data=json.dumps(new_tasktime),
                                    content_type=self.content_type, **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEquals(data['task']['id'], new_tasktime['task'])
        self.assertEquals(data['details'], new_tasktime['details'])
        tasktime_id = data['id']

        # start task time
        response = self.client.get(path=reverse('api_projects_tasktime_start', kwargs={
                                   'task_id': sub_task_id}), **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.content)
        slot_id = data['id']

        sleep(60)

        # stop task time
        response = self.client.post(reverse('api_projects_tasktime_stop', kwargs={'slot_id': slot_id}), data=json.dumps({'details': '<p>test details</p>'}),
                                    content_type=self.content_type, **self.authentication_headers)
        self.assertEquals(response.status_code, 200)

        # delete task time
        response = self.client.delete(reverse('api_projects_tasktimes', kwargs={
                                      'object_ptr': tasktime_id}), **self.authentication_headers)
        self.assertEquals(response.status_code, 204)

        # delete task
        response = self.client.delete(reverse(
            'api_projects_tasks', kwargs={'object_ptr': task_id}), **self.authentication_headers)
        self.assertEquals(response.status_code, 204)

        # check subtask
        response = self.client.get(path=reverse('api_projects_tasks', kwargs={
                                   'object_ptr': sub_task_id}), **self.authentication_headers)
        self.assertEquals(response.status_code, 404)

        # delete milestone
        response = self.client.delete(reverse('api_projects_milestones', kwargs={
                                      'object_ptr': milestone_id}), **self.authentication_headers)
        self.assertEquals(response.status_code, 204)

        # delete status
        response = self.client.delete(reverse(
            'api_projects_status', kwargs={'object_ptr': sstatus}), **self.authentication_headers)
        self.assertEquals(response.status_code, 204)

        # delete project
        response = self.client.delete(reverse(
            'api_projects', kwargs={'object_ptr': project_id}), **self.authentication_headers)
        self.assertEquals(response.status_code, 204)

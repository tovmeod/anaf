from time import sleep
import json
from datetime import datetime
from anaf.test import AnafTestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User as DjangoUser
from freezegun import freeze_time

from anaf.identities.models import Contact, ContactType
from anaf.core.models import Group, Perspective, ModuleSetting
from anaf.projects.models import Project, Milestone, Task, TaskStatus, TaskTimeSlot


class ProjectsAPITest(AnafTestCase):
    """Projects functional tests for api"""
    username = "api_test"
    password = "api_password"
    authentication_headers = {"CONTENT_TYPE": "application/json",
                              "HTTP_AUTHORIZATION": "Basic YXBpX3Rlc3Q6YXBpX3Bhc3N3b3Jk"}
    content_type = 'application/json'

    def setUp(self):
        super(ProjectsAPITest, self).setUp()
        # Create objects

        with freeze_time(datetime(year=2015, month=10, day=8, hour=7, minute=19)):
            self.group, created = Group.objects.get_or_create(name='api_test_group')
        with freeze_time(datetime(year=2015, month=10, day=8, hour=7, minute=20)):
            DjangoUser.objects.get_or_create(username='api_test_first_user')
        with freeze_time(datetime(year=2015, month=11, day=9, hour=8, minute=21)):
            # create the test user as staff so it has permissions for everything
            #  instead of creating permissions for each thing here
            self.user, created = DjangoUser.objects.get_or_create(username=self.username, is_staff=True)
        with freeze_time(datetime(year=2015, month=12, day=10, hour=9, minute=22)):
            DjangoUser.objects.get_or_create(username='api_test_third_user')
        self.user.set_password(self.password)
        self.user.save()
        self.profile = self.user.profile

        with freeze_time(datetime(year=2015, month=12, day=10, hour=9, minute=23)):
            self.perspective, created = Perspective.objects.get_or_create(name='default')
        self.perspective.set_default_user()
        with freeze_time(datetime(year=2015, month=12, day=10, hour=9, minute=24)):
            self.perspective.save()

        ModuleSetting.set('default_perspective', self.perspective.id)

        self.contact_type2 = ContactType(name='api_test_contacttype2')
        self.contact_type2.set_default_user()
        self.contact_type2.save()

        with freeze_time(datetime(year=2016, month=10, day=27, hour=16, minute=28)):
            self.contact_type = ContactType(name='api_test_contacttype')
        self.contact_type.set_default_user()
        with freeze_time(datetime(year=2016, month=10, day=27, hour=16, minute=29)):
            self.contact_type.save()

        with freeze_time(datetime(year=2016, month=10, day=27, hour=16, minute=30)):
            self.contact = Contact(name='api_test_contact', contact_type=self.contact_type)
        self.contact.set_default_user()
        with freeze_time(datetime(year=2016, month=10, day=27, hour=16, minute=31)):
            self.contact.save()

        with freeze_time(datetime(year=2015, month=11, day=9, hour=8, minute=21)):
            self.project = Project(name='api_test_project', manager=self.contact, client=self.contact)

        self.project.set_default_user()
        with freeze_time(datetime(year=2015, month=11, day=9, hour=8, minute=26)):
            self.project.save()

        with freeze_time(datetime(year=2016, month=1, day=27, hour=17, minute=29)):
            self.taskstatus = TaskStatus(name='api_test_taskstatus')
        self.taskstatus.set_default_user()
        with freeze_time(datetime(year=2016, month=1, day=27, hour=17, minute=30)):
            self.taskstatus.save()

        with freeze_time(datetime(year=2016, month=1, day=28, hour=1, minute=9)):
            self.milestone = Milestone(name='api_test_milestone', project=self.project, status=self.taskstatus)
        self.milestone.set_default_user()
        with freeze_time(datetime(year=2016, month=1, day=28, hour=1, minute=10)):
            self.milestone.save()

        with freeze_time(datetime(year=2016, month=1, day=28, hour=3, minute=6)):
            self.task = Task(name='api_test_task', project=self.project, status=self.taskstatus, priority=3)
        self.task.set_default_user()
        with freeze_time(datetime(year=2016, month=1, day=28, hour=3, minute=9)):
            self.task.save()

        with freeze_time(datetime(year=2016, month=1, day=29, hour=13, minute=51)):
            self.time_slot = TaskTimeSlot(task=self.task, details='api_test_tasktimeslot',
                                          time_from=datetime(year=2016, month=1, day=29, hour=13, minute=52),
                                          user=self.user.profile)
        self.time_slot.set_default_user()
        with freeze_time(datetime(year=2016, month=1, day=29, hour=13, minute=53)):
            self.time_slot.save()

        with freeze_time(datetime(year=2016, month=1, day=25, hour=19, minute=58)):
            self.parent_project = Project(name='api_test_project_parent')
        self.parent_project.set_default_user()
        with freeze_time(datetime(year=2016, month=1, day=25, hour=21, minute=59)):
            self.parent_project.save()

        with freeze_time(datetime(year=2016, month=1, day=28, hour=3, minute=7)):
            self.parent_task = Task(name='api_test_parent_task', project=self.project,
                                    status=self.taskstatus, priority=3)
        self.parent_task.set_default_user()
        with freeze_time(datetime(year=2016, month=1, day=28, hour=3, minute=8)):
            self.parent_task.save()

    def test_unauthenticated_access_project(self):
        """Test index page at /projects"""
        oldresponse = self.client.get(reverse('api_projects'))
        # Redirects as unauthenticated
        self.assertEquals(oldresponse.status_code, 401)
        newresponse = self.client.get(reverse('project-list'))
        self.assertEquals(newresponse.status_code, 401)

    def test_unauthenticated_access_taskstatus(self):
        self.assertEquals(self.client.get(reverse('taskstatus-list')).status_code, 401)

    def test_unauthenticated_access_milestone(self):
        self.assertEquals(self.client.get(reverse('milestone-list')).status_code, 401)

    # Get info about projects, milestones, status, tasks, tasktimes.

    def assert_not_acceptable_format(self, name, **kwargs):
        """Assert that the url exist but won't accept API format"""
        kwargs.update({'format': 'json'})
        response = self.client.get(reverse(name, kwargs=kwargs), **self.authentication_headers)
        self.assertEqual(response.status_code, 406)

    def test_project_new(self):
        """Test the project-new endpoint, an API call should return 406 Not Acceptable"""
        self.assert_not_acceptable_format('project-new')

    def test_project_new_to_project(self):
        self.assert_not_acceptable_format('project-new-to-project', project_id=self.project.id)

    def test_project_gantt(self):
        self.assert_not_acceptable_format('project-gantt', pk=self.project.id)

    def test_project_edit(self):
        self.assert_not_acceptable_format('project-edit', pk=self.project.id)

    def test_project_delete(self):
        self.assert_not_acceptable_format('project-delete', pk=self.project.id)

    def test_milestone_edit(self):
        self.assert_not_acceptable_format('milestone-edit', pk=self.milestone.id)

    def test_milestone_set_status(self):
        self.assert_not_acceptable_format('milestone-set-status', pk=self.milestone.id, status_id=self.taskstatus.id)

    def test_milestone_delete(self):
        self.assert_not_acceptable_format('milestone-delete', pk=self.milestone.id)

    def test_milestone_new(self):
        self.assert_not_acceptable_format('milestone-new')

    def test_milestone_new_to_project(self):
        self.assert_not_acceptable_format('milestone-new-to-project', project_id=self.project.id)

    def test_task_new(self):
        self.assert_not_acceptable_format('task-new')

    def test_task_new_subtask(self):
        self.assert_not_acceptable_format('task-new-subtask', pk=self.task.id)

    def test_task_new_to_milestone(self):
        self.assert_not_acceptable_format('task-new-to-milestone', milestone_id=self.milestone.id)

    def test_task_new_to_project(self):
        self.assert_not_acceptable_format('task-new-to-project', project_id=self.project.id)

    def test_task_edit(self):
        self.assert_not_acceptable_format('task-edit', pk=self.task.id)

    def test_task_delete(self):
        self.assert_not_acceptable_format('task-delete', pk=self.task.id)

    def test_task_set_status(self):
        self.assert_not_acceptable_format('task-set-status', pk=self.task.id, status_id=self.taskstatus.id)

    def test_tasktimeslot_edit(self):
        self.assert_not_acceptable_format('tasktimeslot-edit', pk=self.time_slot.id)

    def test_get_project_list(self):
        """ Test index page api/projects """
        response = self.client.get(reverse('project-list', kwargs={'format': 'json'}), **self.authentication_headers)
        self.assertEquals(response.status_code, 200)
        expected = [
            {
                u'client': u'http://testserver/contacts/contact/%s.json' % self.contact.id, u'comments': [],
                u'creator': u'http://testserver/accounts/user/%s.json' % self.user.profile.id,
                u'date_created': u'2015-11-09T08:21:00', u'details': None, u'dislikes': [],
                u'last_updated': u'2015-11-09T08:26:00', u'likes': [], u'links':[],
                u'manager': u'http://testserver/contacts/contact/%s.json' % self.contact.id,
                u'name': u'api_test_project', u'object_type': u'anaf.projects.models.Project', u'parent': None,
                u'subscribers': [], u'tags': [], u'trash': False,
                u'url': u'http://testserver/projects/project/%s.json' % self.project.id
            },
            {
                u'client': None, u'comments': [],
                u'creator': u'http://testserver/accounts/user/%s.json' % self.user.profile.id,
                u'date_created': u'2016-01-25T19:58:00', u'details': None, u'dislikes': [],
                u'last_updated': u'2016-01-25T21:59:00', u'likes': [], u'links':[],
                u'manager': None,
                u'name': u'api_test_project_parent', u'object_type': u'anaf.projects.models.Project', u'parent': None,
                u'subscribers': [], u'tags': [], u'trash': False,
                u'url': u'http://testserver/projects/project/%s.json' % self.parent_project.id
            }
        ]
        data = json.loads(response.content)
        expected.sort(key=lambda x: x['name'])
        data.sort(key=lambda x: x['name'])

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0], expected[0])
        self.assertEqual(data[1], expected[1])

    def test_get_status_list(self):
        """ Test index page api/status
        test for TaskStatus model list
         """
        response = self.client.get(reverse('taskstatus-list', kwargs={'format': 'json'}),
                                      **self.authentication_headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        expected = [{
            u'active': False,
            u'comments': [],
            u'creator': u'http://testserver/accounts/user/%s.json' % self.user.profile.id,
            u'date_created': u'2016-01-27T17:29:00',
            u'details': None,
            u'dislikes': [],
            u'hidden': False,
            u'last_updated': u'2016-01-27T17:30:00',
            u'likes': [],
            u'links': [],
            u'name': u'api_test_taskstatus',
            u'object_type': u'anaf.projects.models.TaskStatus',
            u'subscribers': [],
            u'tags': [],
            u'trash': False,
            u'url': u'http://testserver/projects/taskstatus/%s.json' % self.taskstatus.id
        }]

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0], expected[0])

    def test_get_milestones_list(self):
        """ Test index page api/milestones """
        response = self.client.get(reverse('milestone-list', kwargs={'format': 'json'}),
                                      **self.authentication_headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        expected = [{
            u'comments': [],
            u'creator': u'http://testserver/accounts/user/%s.json' % self.user.profile.id,
            u'date_created': u'2016-01-28T01:09:00',
            u'details': None,
            u'dislikes': [],
            u'end_date': None,
            u'last_updated': u'2016-01-28T01:10:00',
            u'likes': [],
            u'links': [],
            u'name': u'api_test_milestone',
            u'object_type': u'anaf.projects.models.Milestone',
            u'project': u'http://testserver/projects/project/%s.json' % self.project.id,
            u'start_date': None,
            u'status': u'http://testserver/projects/taskstatus/%s.json' % self.taskstatus.id,
            u'subscribers': [],
            u'tags': [],
            u'trash': False,
            u'url': u'http://testserver/projects/milestone/%s.json' % self.milestone.id
        }]

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0], expected[0])

    def test_get_task_list(self):
        """ Test index page api/tasks """
        response = self.client.get(reverse('task-list', kwargs={'format': 'json'}), **self.authentication_headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        expected = [{
            u'assigned': [],
            u'caller': None,
            u'comments': [],
            u'creator': u'http://testserver/accounts/user/%s.json' % self.user.profile.id,
            u'date_created': u'2016-01-28T03:07:00',
            u'depends': None,
            u'details': None,
            u'dislikes': [],
            u'end_date': None,
            u'estimated_time': None,
            u'last_updated': u'2016-01-28T03:08:00',
            u'likes': [],
            u'links': [],
            u'milestone': None,
            u'name': u'api_test_parent_task',
            u'object_type': u'anaf.projects.models.Task',
            u'parent': None,
            u'priority': 3,
            u'project': u'http://testserver/projects/project/%s.json' % self.project.id,
            u'start_date': None,
            u'status': u'http://testserver/projects/taskstatus/%s.json' % self.taskstatus.id,
            u'subscribers': [],
            u'tags': [],
            u'trash': False,
            u'url': u'http://testserver/projects/task/%s.json' % self.parent_task.id,
        }, {
            u'assigned': [],
            u'caller': None,
            u'comments': [],
            u'creator': u'http://testserver/accounts/user/%s.json' % self.user.profile.id,
            u'date_created': u'2016-01-28T03:06:00',
            u'depends': None,
            u'details': None,
            u'dislikes': [],
            u'end_date': None,
            u'estimated_time': None,
            u'last_updated': u'2016-01-28T03:09:00',
            u'likes': [],
            u'links': [],
            u'milestone': None,
            u'name': u'api_test_task',
            u'object_type': u'anaf.projects.models.Task',
            u'parent': None,
            u'priority': 3,
            u'project': u'http://testserver/projects/project/%s.json' % self.project.id,
            u'start_date': None,
            u'status': u'http://testserver/projects/taskstatus/%s.json' % self.taskstatus.id,
            u'subscribers': [],
            u'tags': [],
            u'trash': False,
            u'url': u'http://testserver/projects/task/%s.json' % self.task.id,
        }]
        self.assertEqual(len(data), 2)
        data.sort(key=lambda x: x['name'])
        expected.sort(key=lambda x: x['name'])
        self.assertEqual(data[0], expected[0])
        self.assertEqual(data[1], expected[1])

    def test_get_task_owned(self):
        contact = Contact(name='api_test user contact', contact_type=self.contact_type, related_user=self.profile)
        contact.save()

        with freeze_time(datetime(year=2016, month=10, day=27, hour=15, minute=53)):
            task = Task(name='api_test_task', project=self.project, status=self.taskstatus, priority=3, caller=contact)
        task.set_default_user()
        with freeze_time(datetime(year=2016, month=10, day=27, hour=15, minute=54)):
            task.save()

        response = self.client.get(reverse('task-owned', kwargs={'format': 'json'}), **self.authentication_headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        expected = [{
            u'last_updated': u'2016-10-27T15:54:00',
            u'links': [],
            u'creator': u'http://testserver/accounts/user/%s.json' % self.profile.id,
            u'estimated_time': None,
            u'object_type': u'anaf.projects.models.Task',
            u'assigned': [],
            u'depends': None,
            u'comments': [],
            u'parent': None,
            u'priority': 3,
            u'details': None, u'trash': False, u'start_date': None,
            u'status': u'http://testserver/projects/taskstatus/%s.json' % self.taskstatus.id,
            u'end_date': None, u'tags': [], u'dislikes': [], u'subscribers': [], u'milestone': None,
            u'name': u'api_test_task',
            u'url': u'http://testserver/projects/task/%s.json' % task.id,
            u'caller': u'http://testserver/contacts/contact/%s.json' % contact.id,
            u'project': u'http://testserver/projects/project/%s.json' % self.project.id,
            u'date_created': u'2016-10-27T15:53:00', u'likes': []
        }]
        self.assertEqual(len(data), 1)
        self.maxDiff = None
        self.assertEqual(data[0], expected[0])
    # def test_get_task_owned(self):
    # def test_get_task_assigned(self):
    # def test_get_task_in_progress(self):

    def test_get_tasktimes_list(self):
        """ Test index page api/tasktimes """
        response = self.client.get(reverse('tasktimeslot-list', kwargs={'format': 'json'}),
                                   **self.authentication_headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        expected = [{
            u'comments': [],
            u'creator': u'http://testserver/accounts/user/%s.json' % self.profile.id,
            u'date_created': u'2016-01-29T13:51:00',
            u'details': u'api_test_tasktimeslot',
            u'dislikes': [],
            u'last_updated': u'2016-01-29T13:53:00',
            u'likes': [],
            u'links': [],
            u'object_type': u'anaf.projects.models.TaskTimeSlot',
            u'subscribers': [],
            u'tags': [],
            u'task': u'http://testserver/projects/task/%s.json' % self.task.id,
            u'time_from': u'2016-01-29T13:52:00',
            u'time_to': None,
            u'timezone': 0,
            u'trash': False,
            u'url': u'http://testserver/projects/tasktimeslot/%s.json' % self.time_slot.id,
            u'user': u'http://testserver/accounts/user/%s.json' % self.user.profile.id,
        }]

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0], expected[0])

    def test_get_project(self):
        response = self.client.get(reverse(
                'project-detail', kwargs={'pk': self.project.id, 'format': 'json'}), **self.authentication_headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        expected = {
            u'dislikes': [],
            u'last_updated': u'2015-11-09T08:26:00',
            u'name': u'api_test_project',
            u'object_type': u'anaf.projects.models.Project',
            u'parent': None,
            u'creator': u'http://testserver/accounts/user/%s.json' % self.profile.id,
            u'likes': [],
            u'links': [],
            u'manager': u'http://testserver/contacts/contact/%s.json' % self.contact.id,
            u'client': u'http://testserver/contacts/contact/%s.json' % self.contact.id,
            u'comments': [],
            u'details': None,
            u'date_created': u'2015-11-09T08:21:00',
            u'subscribers': [],
            u'tags': [],
            u'trash': False,
            u'url': u'http://testserver/projects/project/%s.json' % self.project.id
        }
        self.assertDictEqual(data, expected)

    def test_get_status(self):
        response = self.client.get(reverse('taskstatus-detail', kwargs={'pk': self.taskstatus.id, 'format': 'json'}),
                                   **self.authentication_headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        expected = {
            u'active': False,
            u'comments': [],
            u'creator': u'http://testserver/accounts/user/%s.json' % self.profile.id,
            u'date_created': u'2016-01-27T17:29:00',
            u'details': None,
            u'dislikes': [],
            u'hidden': False,
            u'last_updated': u'2016-01-27T17:30:00',
            u'likes': [],
            u'links': [],
            u'name': u'api_test_taskstatus',
            u'object_type': u'anaf.projects.models.TaskStatus',
            u'subscribers': [],
            u'tags': [],
            u'trash': False,
            u'url': u'http://testserver/projects/taskstatus/%s.json' % self.taskstatus.id
        }

        self.assertDictEqual(data, expected)

    def test_get_milestone(self):
        response = self.client.get(reverse('milestone-detail', kwargs={'pk': self.milestone.id, 'format': 'json'}),
                                   **self.authentication_headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        expected = {
            u'comments': [],
            u'creator': u'http://testserver/accounts/user/%s.json' % self.user.profile.id,
            u'date_created': u'2016-01-28T01:09:00',
            u'details': None,
            u'dislikes': [],
            u'end_date': None,
            u'last_updated': u'2016-01-28T01:10:00',
            u'likes': [],
            u'links': [],
            u'name': u'api_test_milestone',
            u'object_type': u'anaf.projects.models.Milestone',
            u'project': u'http://testserver/projects/project/%s.json' % self.project.id,
            u'start_date': None,
            u'status': u'http://testserver/projects/taskstatus/%s.json' % self.taskstatus.id,
            u'subscribers': [],
            u'tags': [],
            u'trash': False,
            u'url': u'http://testserver/projects/milestone/%s.json' % self.milestone.id
        }

        self.assertDictEqual(data, expected)

    def test_get_task(self):
        response = self.client.get(reverse('task-detail', kwargs={'pk': self.task.id, 'format': 'json'}),
                                   **self.authentication_headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.maxDiff = None
        expected = {
            u'assigned': [],
            u'caller': None,
            u'comments': [],
            u'creator': u'http://testserver/accounts/user/%s.json' % self.user.profile.id,
            u'date_created': u'2016-01-28T03:06:00',
            u'depends': None,
            u'details': None,
            u'dislikes': [],
            u'end_date': None,
            u'estimated_time': None,
            u'last_updated': u'2016-01-28T03:09:00',
            u'likes': [],
            u'links': [],
            u'milestone': None,
            u'name': u'api_test_task',
            u'object_type': u'anaf.projects.models.Task',
            u'parent': None,
            u'priority': 3,
            u'project': u'http://testserver/projects/project/%s.json' % self.project.id,
            u'start_date': None,
            u'status': u'http://testserver/projects/taskstatus/%s.json' % self.taskstatus.id,
            u'subscribers': [],
            u'tags': [],
            u'trash': False,
            u'url': u'http://testserver/projects/task/%s.json' % self.task.id,
        }

        self.assertDictEqual(data, expected)

    def test_get_timeslot(self):
        response = self.client.get(reverse('tasktimeslot-detail', kwargs={'pk': self.time_slot.id, 'format': 'json'}),
                                   **self.authentication_headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        expected = {
            u'comments': [],
            u'creator': u'http://testserver/accounts/user/%s.json' % self.profile.id,
            u'date_created': u'2016-01-29T13:51:00',
            u'details': u'api_test_tasktimeslot',
            u'dislikes': [],
            u'last_updated': u'2016-01-29T13:53:00',
            u'likes': [],
            u'links': [],
            u'object_type': u'anaf.projects.models.TaskTimeSlot',
            u'subscribers': [],
            u'tags': [],
            u'task': u'http://testserver/projects/task/%s.json' % self.task.id,
            u'time_from': u'2016-01-29T13:52:00',
            u'time_to': None,
            u'timezone': 0,
            u'trash': False,
            u'url': u'http://testserver/projects/tasktimeslot/%s.json' % self.time_slot.id,
            u'user': u'http://testserver/accounts/user/%s.json' % self.user.profile.id,
        }

        self.assertDictEqual(data, expected)

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

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
            self.user, created = DjangoUser.objects.get_or_create(username=self.username)
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

    def test_get_project_list(self):
        """ Test index page api/projects """
        oldresponse = self.client.get(path=reverse('api_projects'), **self.authentication_headers)
        newresponse = self.client.get(reverse('project-list', kwargs={'format': 'json'}), **self.authentication_headers)
        self.assertEquals(oldresponse.status_code, 200)
        self.assertEquals(newresponse.status_code, 200)

        data = json.loads(oldresponse.content)

        expected = [{u'last_updated': u'2015-11-09T08:26:00', u'name': u'api_test_project', u'parent': None,
                     u'creator': {
                         u'name': u'api_test', u'default_group': {
                             u'perspective': {
                                 u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                                 u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                             },
                             u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                             u'resource_uri': u'/api/core/group/%s' % self.group.id
                         },
                         u'disabled': False, u'other_groups': [],
                         u'perspective': {
                             u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                             u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                         },
                         u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                         u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
                     },
                     u'nuvius_resource': None,
                     u'manager': {
                         u'name': u'api_test_contact', u'parent': None,
                         u'contact_type': {
                             u'fields': [], u'details': None, u'id': self.contact_type.id,
                             u'name': u'api_test_contacttype',
                             u'resource_uri': u'/api/identities/type/%s' % self.contact_type.id
                         },
                         u'contactvalue_set': [], u'related_user': None, u'id': self.contact.id,
                         u'resource_uri': u'/api/identities/contact/%s' % self.contact.id
                     },
                     u'client': {
                         u'name': u'api_test_contact', u'parent': None,
                         u'contact_type': {
                             u'fields': [], u'details': None, u'id': self.contact_type.id,
                             u'name': u'api_test_contacttype',
                             u'resource_uri': u'/api/identities/type/%s' % self.contact_type.id
                         },
                         u'contactvalue_set': [], u'related_user': None,
                         u'id': self.contact.id, u'resource_uri': u'/api/identities/contact/%s' % self.contact.id
                     },
                     u'details': None, u'date_created': u'2015-11-09T08:21:00', u'trash': False,
                     u'id': self.project.id, u'resource_uri': u'/api/projects/project/%s' % self.project.id
                     },
                    {u'last_updated': u'2016-01-25T21:59:00', u'name': u'api_test_project_parent', u'parent': None,
                     u'creator': {
                         u'name': u'api_test',
                         u'default_group': {
                             u'perspective': {
                                 u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                                 u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                             },
                             u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                             u'resource_uri': u'/api/core/group/%s' % self.group.id
                         },
                         u'disabled': False, u'other_groups': [],
                         u'perspective': {
                             u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                             u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                         },
                         u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                         u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
                     },
                     u'nuvius_resource': None, u'manager': None,
                     u'client': None, u'details': None, u'date_created': u'2016-01-25T19:58:00', u'trash': False,
                     u'id': self.parent_project.id,
                     u'resource_uri': u'/api/projects/project/%s' % self.parent_project.id
                     }]

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0], expected[0])
        self.assertEqual(data[1], expected[1])
        self.cmpDataApi(oldresponse.content, newresponse.content)

    def test_get_status_list(self):
        """ Test index page api/status
        test for TaskStatus model list
         """
        oldresponse = self.client.get(path=reverse('api_projects_status'), **self.authentication_headers)
        newresponse = self.client.get(reverse('taskstatus-list', kwargs={'format': 'json'}),
                                      **self.authentication_headers)
        self.assertEquals(oldresponse.status_code, 200)
        self.assertEquals(newresponse.status_code, 200)
        data = json.loads(oldresponse.content)
        expected = [{
            u'last_updated': u'2016-01-27T17:30:00', u'name': u'api_test_taskstatus',
            u'creator': {
                u'name': u'api_test',
                u'default_group': {
                    u'perspective': {
                        u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                        u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                    },
                    u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                    u'resource_uri': u'/api/core/group/%s' % self.group.id
                },
                u'disabled': False, u'other_groups': [],
                u'perspective': {
                    u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                    u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                },
                u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
            }, u'nuvius_resource': None, u'details': None, u'active': False,
            u'date_created': u'2016-01-27T17:29:00', u'hidden': False, u'trash': False, u'id': self.taskstatus.id,
            u'resource_uri': u'/api/projects/status/%s' % self.taskstatus.id
        }]

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0], expected[0])
        self.cmpDataApi(oldresponse.content, newresponse.content)

    def test_get_milestones_list(self):
        """ Test index page api/milestones """
        oldresponse = self.client.get(path=reverse('api_projects_milestones'), **self.authentication_headers)
        newresponse = self.client.get(reverse('milestone-list', kwargs={'format': 'json'}),
                                      **self.authentication_headers)
        self.assertEquals(oldresponse.status_code, 200)
        self.assertEquals(newresponse.status_code, 200)
        data = json.loads(oldresponse.content)
        expected = [{u'status': {
            u'last_updated': u'2016-01-27T17:30:00', u'name': u'api_test_taskstatus',
            u'creator': {
                u'name': u'api_test',
                u'default_group': {
                    u'perspective': {
                        u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                        u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                    },
                    u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                    u'resource_uri': u'/api/core/group/%s' % self.group.id
                },
                u'disabled': False, u'other_groups': [],
                u'perspective': {
                    u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                    u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                },
                u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
            },
            u'nuvius_resource': None,  u'details': None, u'active': False, u'date_created': u'2016-01-27T17:29:00',
            u'hidden': False, u'trash': False, u'id': self.taskstatus.id,
            u'resource_uri': u'/api/projects/status/%s' % self.taskstatus.id
        },
            u'last_updated': u'2016-01-28T01:10:00', u'name': u'api_test_milestone', u'end_date': None,
            u'creator': {
                u'name': u'api_test', u'default_group': {
                    u'perspective': {
                        u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                        u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                    },
                    u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                    u'resource_uri': u'/api/core/group/%s' % self.group.id
                },
                u'disabled': False, u'other_groups': [],
                u'perspective': {
                    u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                    u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                },
                u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
            },
            u'nuvius_resource': None, u'start_date': None,
            u'project': {
                u'last_updated': u'2015-11-09T08:26:00', u'name': u'api_test_project', u'parent': None,
                u'creator': {
                    u'name': u'api_test', u'default_group': {
                        u'perspective': {
                            u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                            u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                        },
                        u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                        u'resource_uri': u'/api/core/group/%s' % self.group.id
                    },
                    u'disabled': False, u'other_groups': [],
                    u'perspective': {
                        u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                        u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                    },
                    u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                    u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
                },
                u'nuvius_resource': None,
                u'manager': {
                    u'name': u'api_test_contact', u'parent': None,
                    u'contact_type': {
                        u'fields': [], u'details': None, u'id': self.contact_type.id,  u'name': u'api_test_contacttype',
                        u'resource_uri': u'/api/identities/type/%s' % self.contact_type.id
                    },
                    u'contactvalue_set': [], u'related_user': None, u'id': self.contact.id,
                    u'resource_uri': u'/api/identities/contact/%s' % self.contact.id
                },
                u'client': {
                    u'name': u'api_test_contact', u'parent': None,
                    u'contact_type': {
                        u'fields': [], u'details': None, u'id': self.contact_type.id, u'name': u'api_test_contacttype',
                        u'resource_uri': u'/api/identities/type/%s' % self.contact_type.id
                    },
                    u'contactvalue_set': [], u'related_user': None, u'id': self.contact.id,
                    u'resource_uri': u'/api/identities/contact/%s' % self.contact.id
                },
                u'details': None, u'date_created': u'2015-11-09T08:21:00', u'trash': False, u'id': self.project.id,
                u'resource_uri': u'/api/projects/project/%s' % self.project.id
            }, u'details': None, u'date_created': u'2016-01-28T01:09:00', u'trash': False, u'id': self.milestone.id,
            u'resource_uri': u'/api/projects/milestone/%s' % self.milestone.id
        }]

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0], expected[0])
        self.cmpDataApi(oldresponse.content, newresponse.content)

    def test_get_task_list(self):
        """ Test index page api/tasks """
        oldresponse = self.client.get(path=reverse('api_projects_tasks'), **self.authentication_headers)
        newresponse = self.client.get(reverse('task-list', kwargs={'format': 'json'}), **self.authentication_headers)
        self.assertEquals(oldresponse.status_code, 200)
        self.assertEquals(newresponse.status_code, 200)
        data = json.loads(oldresponse.content)
        expected = [{
            u'last_updated': u'2016-01-28T03:08:00', u'end_date': None, u'name': u'api_test_parent_task',
            u'parent': None, u'estimated_time': None, u'caller': None, u'nuvius_resource': None, u'start_date': None,
            u'priority': 3, u'depends': None, u'details': None, u'milestone': None,
            u'date_created': u'2016-01-28T03:07:00', u'trash': False, u'id': self.parent_task.id,
            u'resource_uri': u'/api/projects/task/%s' % self.parent_task.id,
            u'status': {
                u'last_updated': u'2016-01-27T17:30:00', u'name': u'api_test_taskstatus',
                u'creator': {
                     u'name': u'api_test',
                     u'default_group': {
                         u'perspective': {
                             u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                             u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                         },
                         u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                         u'resource_uri': u'/api/core/group/%s' % self.group.id
                     },
                     u'disabled': False, u'other_groups': [],
                     u'perspective': {
                         u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                         u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                     },
                     u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                     u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
                 },
                 u'nuvius_resource': None, u'details': None, u'active': False, u'date_created': u'2016-01-27T17:29:00',
                 u'hidden': False, u'trash': False, u'id': self.taskstatus.id,
                 u'resource_uri': u'/api/projects/status/%s' % self.taskstatus.id
            },
            u'project': {
                u'last_updated': u'2015-11-09T08:26:00', u'name': u'api_test_project', u'parent': None,
                u'creator': {
                    u'name': u'api_test',
                    u'default_group': {
                        u'perspective': {
                            u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                            u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                        },
                        u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                        u'resource_uri': u'/api/core/group/%s' % self.group.id
                    },
                    u'disabled': False, u'other_groups': [],
                    u'perspective': {
                        u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                        u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                    },
                    u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                    u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
                },
                u'nuvius_resource': None, u'manager': {
                    u'name': u'api_test_contact', u'parent': None, u'contact_type': {
                        u'fields': [], u'details': None, u'id': self.contact_type.id, u'name': u'api_test_contacttype',
                        u'resource_uri': u'/api/identities/type/%s' % self.contact_type.id
                    },
                    u'contactvalue_set': [], u'related_user': None, u'id': self.contact.id,
                    u'resource_uri': u'/api/identities/contact/%s' % self.contact.id
                },
                u'client': {u'name': u'api_test_contact', u'parent': None,
                            u'contact_type': {
                                u'fields': [], u'details': None, u'id': self.contact_type.id,
                                u'name': u'api_test_contacttype',
                                u'resource_uri': u'/api/identities/type/%s' % self.contact_type.id
                            },
                            u'contactvalue_set': [], u'related_user': None, u'id': self.contact.id,
                            u'resource_uri': u'/api/identities/contact/%s' % self.contact.id
                            },
                u'details': None, u'date_created': u'2015-11-09T08:21:00', u'trash': False, u'id': self.project.id,
                u'resource_uri': u'/api/projects/project/%s' % self.project.id
            },
            u'creator': {
                u'name': u'api_test', u'default_group': {
                    u'perspective': {
                        u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                        u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                    },
                    u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                    u'resource_uri': u'/api/core/group/%s' % self.group.id
                },
                u'disabled': False, u'other_groups': [], u'perspective': {
                    u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                    u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                },
                u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
            },
        }, {
            u'estimated_time': None, u'caller': None, u'nuvius_resource': None, u'start_date': None, u'priority': 3,
            u'depends': None, u'details': None, u'milestone': None, u'date_created': u'2016-01-28T03:06:00',
            u'trash': False, u'id': self.task.id, u'resource_uri': u'/api/projects/task/%s' % self.task.id,
            u'last_updated': u'2016-01-28T03:09:00', u'end_date': None, u'name': u'api_test_task', u'parent': None,
            u'status': {
                u'last_updated': u'2016-01-27T17:30:00', u'name': u'api_test_taskstatus',
                u'creator': {
                    u'name': u'api_test', u'default_group': {
                        u'perspective': {
                            u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                            u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                        },
                        u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                        u'resource_uri': u'/api/core/group/%s' % self.group.id
                    },
                    u'disabled': False, u'other_groups': [], u'perspective': {
                        u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                        u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                    },
                    u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                    u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
                },
                u'nuvius_resource': None, u'details': None, u'active': False, u'date_created': u'2016-01-27T17:29:00',
                u'hidden': False, u'trash': False, u'id': self.taskstatus.id,
                u'resource_uri': u'/api/projects/status/%s' % self.taskstatus.id
            },
            u'project': {
                u'last_updated': u'2015-11-09T08:26:00', u'name': u'api_test_project', u'parent': None,
                u'creator': {
                    u'name': u'api_test', u'default_group': {
                        u'perspective': {
                            u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                            u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                        },
                        u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                        u'resource_uri': u'/api/core/group/%s' % self.group.id
                    },
                    u'disabled': False, u'other_groups': [], u'perspective': {
                        u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                        u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                    },
                    u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                    u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
                },
                u'nuvius_resource': None,
                u'manager': {
                    u'name': u'api_test_contact', u'parent': None,
                    u'contact_type': {
                        u'fields': [], u'details': None, u'id': self.contact_type.id, u'name': u'api_test_contacttype',
                        u'resource_uri': u'/api/identities/type/%s' % self.contact_type.id
                    },
                    u'contactvalue_set': [], u'related_user': None, u'id': self.contact.id,
                    u'resource_uri': u'/api/identities/contact/%s' % self.contact.id
                },
                u'client': {
                    u'name': u'api_test_contact', u'parent': None,
                    u'contact_type': {
                        u'fields': [], u'details': None, u'id': self.contact_type.id, u'name': u'api_test_contacttype',
                        u'resource_uri': u'/api/identities/type/%s' % self.contact_type.id
                    },
                    u'contactvalue_set': [], u'related_user': None, u'id': self.contact.id,
                    u'resource_uri': u'/api/identities/contact/%s' % self.contact.id
                },
                u'details': None, u'date_created': u'2015-11-09T08:21:00', u'trash': False, u'id': self.project.id,
                u'resource_uri': u'/api/projects/project/%s' % self.project.id
            },
            u'creator': {
                u'name': u'api_test', u'default_group': {
                    u'perspective': {
                        u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                        u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                    },
                    u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                    u'resource_uri': u'/api/core/group/%s' % self.group.id
                },
                u'disabled': False, u'other_groups': [], u'perspective': {
                    u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                    u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                },
                u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
            },
        }]
        self.assertEqual(len(data), 2)
        data.sort(key=lambda x: x['id'])
        expected.sort(key=lambda x: x['id'])
        self.assertEqual(data[0], expected[0])
        self.assertEqual(data[1], expected[1])
        self.cmpDataApi(oldresponse.content, newresponse.content)

    def test_get_task_owned(self):
        contact = Contact(name='api_test user contact', contact_type=self.contact_type, related_user=self.profile)
        # self.contact.set_default_user()
        contact.save()

        with freeze_time(datetime(year=2016, month=10, day=27, hour=15, minute=53)):
            task = Task(name='api_test_task', project=self.project, status=self.taskstatus, priority=3, caller=contact)
        task.set_default_user()
        with freeze_time(datetime(year=2016, month=10, day=27, hour=15, minute=54)):
            task.save()

        response = self.client.get(reverse('task-owned', kwargs={'format': 'json'}), **self.authentication_headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        expected = [{u'last_updated': u'2016-10-27T15:54:00', u'links': [],
                     u'creator': {
                         u'last_updated': u'2015-11-09T08:21:00', u'name': u'api_test',
                         u'url': u'http://testserver/accounts/user/%s.json' % self.profile.id,
                         u'default_group': {
                             u'last_updated': u'2015-10-08T07:19:00', u'name': u'api_test_group',
                             u'parent': None, u'url': u'http://testserver/accounts/group/%s.json' % self.group.id,
                             u'details': None, u'id': self.group.id,
                             u'perspective': {
                                 u'likes': [], u'last_updated': u'2015-12-10T09:24:00', u'name': u'default',
                                 u'links': [],
                                 u'creator': u'http://testserver/accounts/user/%s.json' % self.profile.id,
                                 u'url': u'http://testserver/accounts/perspective/%s.json' % self.perspective.id,
                                 u'dislikes': [], u'object_type': u'anaf.core.models.Perspective',
                                 u'nuvius_resource': None, u'modules': [], u'read_access': [],
                                 u'object_name': u'default', u'full_access': [], u'details': u'', u'subscribers': [],
                                 u'date_created': u'2015-12-10T09:23:00', u'trash': False, u'id': self.perspective.id,
                                 u'tags': [], u'comments': []}},
                         u'disabled': False, u'other_groups': [],
                         u'perspective': {
                             u'likes': [], u'last_updated': u'2015-12-10T09:24:00', u'name': u'default',
                             u'links': [],
                             u'creator': u'http://testserver/accounts/user/%s.json' % self.profile.id,
                             u'url': u'http://testserver/accounts/perspective/%s.json' % self.perspective.id,
                             u'dislikes': [], u'object_type': u'anaf.core.models.Perspective', u'nuvius_resource': None,
                             u'modules': [], u'read_access': [], u'object_name': u'default',
                             u'full_access': [], u'details': u'', u'subscribers': [],
                             u'date_created': u'2015-12-10T09:23:00', u'trash': False, u'id': self.perspective.id,
                             u'tags': [], u'comments': []},
                         u'last_access': u'2015-11-09T08:21:00', u'id': self.profile.id,
                         u'user': u'http://testserver/accounts/user/%s.json' % self.user.id},
                     u'estimated_time': None, u'object_type': u'anaf.projects.models.Task', u'nuvius_resource': None,
                     u'assigned': [], u'depends': None, u'comments': [], u'id': task.id, u'parent': None,
                     u'read_access': [], u'priority': 3, u'object_name': u'api_test_task', u'full_access': [],
                     u'details': None, u'trash': False, u'start_date': None,
                     u'status': {
                         u'likes': [], u'last_updated': u'2016-01-27T17:30:00', u'name': u'api_test_taskstatus',
                         u'links': [],
                         u'creator': {
                             u'last_updated': u'2015-11-09T08:21:00', u'name': u'api_test',
                             u'url': u'http://testserver/accounts/user/%s.json' % self.profile.id,
                             u'default_group': {
                                 u'last_updated': u'2015-10-08T07:19:00', u'name': u'api_test_group',
                                 u'parent': None, u'url': u'http://testserver/accounts/group/%s.json' % self.group.id,
                                 u'details': None, u'id': self.group.id,
                                 u'perspective': {
                                     u'likes': [], u'last_updated': u'2015-12-10T09:24:00', u'name': u'default',
                                     u'links': [],
                                     u'creator': u'http://testserver/accounts/user/%s.json' % self.profile.id,
                                     u'url': u'http://testserver/accounts/perspective/%s.json' % self.perspective.id,
                                     u'dislikes': [], u'object_type': u'anaf.core.models.Perspective',
                                     u'nuvius_resource': None, u'modules': [], u'read_access': [],
                                     u'object_name': u'default', u'full_access': [], u'details': u'',
                                     u'subscribers': [], u'date_created': u'2015-12-10T09:23:00', u'trash': False,
                                     u'id': self.perspective.id,
                                     u'tags': [], u'comments': []}},
                             u'disabled': False, u'other_groups': [],
                             u'perspective': {
                                 u'likes': [], u'last_updated': u'2015-12-10T09:24:00', u'name': u'default',
                                 u'links': [],
                                 u'creator': u'http://testserver/accounts/user/%s.json' % self.profile.id,
                                 u'url': u'http://testserver/accounts/perspective/%s.json' % self.perspective.id,
                                 u'dislikes': [], u'object_type': u'anaf.core.models.Perspective',
                                 u'nuvius_resource': None, u'modules': [], u'read_access': [],
                                 u'object_name': u'default', u'full_access': [], u'details': u'', u'subscribers': [],
                                 u'date_created': u'2015-12-10T09:23:00', u'trash': False, u'id': self.perspective.id,
                                 u'tags': [], u'comments': []},
                             u'last_access': u'2015-11-09T08:21:00', u'id': self.profile.id,
                             u'user': u'http://testserver/accounts/user/%s.json' % self.user.id},
                         u'url': u'http://testserver/projects/taskstatus/%s.json' % self.taskstatus.id, u'dislikes': [],
                         u'object_type': u'anaf.projects.models.TaskStatus', u'nuvius_resource': None,
                         u'read_access': [], u'object_name': u'api_test_taskstatus', u'full_access': [],
                         u'details': None, u'subscribers': [], u'active': False,
                         u'date_created': u'2016-01-27T17:29:00', u'hidden': False, u'trash': False,
                         u'id': self.taskstatus.id, u'tags': [], u'comments': []},
                     u'end_date': None, u'tags': [], u'dislikes': [], u'subscribers': [], u'milestone': None,
                     u'name': u'api_test_task', u'url': u'http://testserver/projects/task/%s.json' % task.id,
                     u'caller': u'http://testserver/contacts/contact/%s.json' % contact.id,
                     u'project': {
                         u'last_updated': u'2015-11-09T08:26:00', u'links': [],
                         u'creator': {
                             u'last_updated': u'2015-11-09T08:21:00', u'name': u'api_test',
                             u'url': u'http://testserver/accounts/user/%s.json' % self.profile.id,
                             u'default_group': {
                                 u'last_updated': u'2015-10-08T07:19:00', u'name': u'api_test_group',
                                 u'parent': None, u'url': u'http://testserver/accounts/group/%s.json' % self.group.id,
                                 u'details': None, u'id': self.group.id,
                                 u'perspective': {
                                     u'likes': [], u'last_updated': u'2015-12-10T09:24:00', u'name': u'default',
                                     u'links': [], u'creator': u'http://testserver/accounts/user/%s.json' % self.profile.id,
                                     u'url': u'http://testserver/accounts/perspective/%s.json' % self.perspective.id, u'dislikes': [],
                                     u'object_type': u'anaf.core.models.Perspective', u'nuvius_resource': None,
                                     u'modules': [], u'read_access': [], u'object_name': u'default', u'full_access': [],
                                     u'details': u'', u'subscribers': [],
                                     u'date_created': u'2015-12-10T09:23:00', u'trash': False,
                                     u'id': self.perspective.id, u'tags': [], u'comments': []}},
                             u'disabled': False, u'other_groups': [],
                             u'perspective': {
                                 u'likes': [], u'last_updated': u'2015-12-10T09:24:00', u'name': u'default',
                                 u'links': [], u'creator': u'http://testserver/accounts/user/%s.json' % self.profile.id,
                                 u'url': u'http://testserver/accounts/perspective/%s.json' % self.perspective.id,
                                 u'dislikes': [], u'object_type': u'anaf.core.models.Perspective',
                                 u'nuvius_resource': None, u'modules': [], u'read_access': [],
                                 u'object_name': u'default', u'full_access': [], u'details': u'', u'subscribers': [],
                                 u'date_created': u'2015-12-10T09:23:00', u'trash': False, u'id': self.perspective.id,
                                 u'tags': [], u'comments': []},
                             u'last_access': u'2015-11-09T08:21:00', u'id': self.user.id,
                             u'user': u'http://testserver/accounts/user/%s.json' % self.user.id},
                         u'object_type': u'anaf.projects.models.Project', u'nuvius_resource': None,
                         u'manager': {
                             u'last_updated': u'2016-10-27T16:31:00', u'links': [],
                             u'creator': u'http://testserver/accounts/user/%s.json' % self.profile.id,
                             u'object_type': u'anaf.identities.models.Contact', u'dislikes': [], u'comments': [],
                             u'id': self.contact.id, u'read_access': [], u'object_name': u'api_test_contact',
                             u'full_access': [], u'trash': False, u'parent': None, u'tags': [],
                             u'nuvius_resource': None, u'contactvalue_set': [], u'subscribers': [],
                             u'date_created': u'2016-10-27T16:30:00', u'name': u'api_test_contact',
                             u'contact_type': {
                                 u'likes': [], u'last_updated': u'2016-10-27T16:29:00',
                                 u'name': u'api_test_contacttype', u'links': [],
                                 u'creator': u'http://testserver/accounts/user/%s.json' % self.profile.id,
                                 u'url': u'http://testserver/contacts/contacttype/%s.json' % self.contact_type.id,
                                 u'dislikes': [], u'object_type': u'anaf.identities.models.ContactType',
                                 u'nuvius_resource': None, u'read_access': [], u'slug': u'api_test_contacttype',
                                 u'object_name': u'api_test_contacttype', u'full_access': [], u'details': None,
                                 u'subscribers': [], u'fields': [], u'date_created': u'2016-10-27T16:28:00',
                                 u'trash': False, u'id': self.contact_type.id, u'tags': [], u'comments': []},
                             u'url': u'http://testserver/contacts/contact/%s.json' % self.contact.id,
                             u'related_user': None, u'likes': []},
                         u'likes': [], u'id': self.project.id, u'comments': [], u'read_access': [],
                         u'object_name': u'api_test_project', u'full_access': [], u'details': None, u'trash': False,
                         u'parent': None, u'tags': [], u'dislikes': [], u'subscribers': [],
                         u'name': u'api_test_project',
                         u'url': u'http://testserver/projects/project/%s.json' % self.project.id,
                         u'client': {
                             u'last_updated': u'2016-10-27T16:31:00', u'links': [],
                             u'creator': u'http://testserver/accounts/user/%s.json' % self.profile.id,
                             u'object_type': u'anaf.identities.models.Contact', u'dislikes': [], u'comments': [],
                             u'id': self.contact.id, u'read_access': [], u'object_name': u'api_test_contact',
                             u'full_access': [], u'trash': False, u'parent': None, u'tags': [],
                             u'nuvius_resource': None, u'contactvalue_set': [], u'subscribers': [],
                             u'date_created': u'2016-10-27T16:30:00', u'name': u'api_test_contact',
                             u'contact_type': {
                                 u'likes': [], u'last_updated': u'2016-10-27T16:29:00',
                                 u'name': u'api_test_contacttype', u'links': [],
                                 u'creator': u'http://testserver/accounts/user/%s.json' % self.profile.id,
                                 u'url': u'http://testserver/contacts/contacttype/%s.json' % self.contact_type.id,
                                 u'dislikes': [], u'object_type': u'anaf.identities.models.ContactType',
                                 u'nuvius_resource': None, u'read_access': [], u'slug': u'api_test_contacttype',
                                 u'object_name': u'api_test_contacttype', u'full_access': [], u'details': None,
                                 u'subscribers': [], u'fields': [], u'date_created': u'2016-10-27T16:28:00',
                                 u'trash': False, u'id': self.contact_type.id, u'tags': [], u'comments': []},
                             u'url': u'http://testserver/contacts/contact/%s.json' % self.contact.id,
                             u'related_user': None, u'likes': []},
                         u'date_created': u'2015-11-09T08:21:00'},
                     u'date_created': u'2016-10-27T15:53:00', u'likes': []}]
        self.assertEqual(len(data), 1)
        self.maxDiff = None
        # data.sort(key=lambda x: x['id'])
        # expected.sort(key=lambda x: x['id'])
        self.assertEqual(data[0], expected[0])
    # def test_get_task_owned(self):
    # def test_get_task_assigned(self):
    # def test_get_task_in_progress(self):

    def test_get_tasktimes_list(self):
        """ Test index page api/tasktimes """
        oldresponse = self.client.get(path=reverse('api_projects_tasktimes'), **self.authentication_headers)
        newresponse = self.client.get(reverse('tasktimeslot-list', kwargs={'format': 'json'}),
                                      **self.authentication_headers)
        self.assertEquals(oldresponse.status_code, 200)
        self.assertEquals(newresponse.status_code, 200)
        data = json.loads(oldresponse.content)

        expected = [{
            u'task': {
                u'last_updated': u'2016-01-28T03:09:00', u'end_date': None, u'name': u'api_test_task', u'parent': None,
                u'estimated_time': None, u'caller': None, u'nuvius_resource': None, u'start_date': None, u'priority': 3,
                u'depends': None, u'details': None, u'milestone': None, u'date_created': u'2016-01-28T03:06:00',
                u'trash': False, u'id': self.task.id, u'resource_uri': u'/api/projects/task/%s' % self.task.id,
                u'status': {
                    u'nuvius_resource': None, u'details': None, u'active': False,
                    u'date_created': u'2016-01-27T17:29:00', u'hidden': False, u'trash': False,
                    u'id': self.taskstatus.id, u'resource_uri': u'/api/projects/status/%s' % self.taskstatus.id,
                    u'last_updated': u'2016-01-27T17:30:00', u'name': u'api_test_taskstatus',
                    u'creator': {
                        u'name': u'api_test', u'default_group': {
                            u'perspective': {
                                u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                                u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                            },
                            u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                            u'resource_uri': u'/api/core/group/%s' % self.group.id
                        },
                        u'disabled': False, u'other_groups': [],
                        u'perspective': {
                            u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                            u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                        },
                        u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                        u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
                    },
                },
                u'project': {
                    u'last_updated': u'2015-11-09T08:26:00', u'name': u'api_test_project', u'parent': None,
                    u'creator': {
                        u'name': u'api_test', u'default_group': {
                            u'perspective': {
                                u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                                u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                            },
                            u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                            u'resource_uri': u'/api/core/group/%s' % self.group.id
                        },
                        u'disabled': False, u'other_groups': [],
                        u'perspective': {
                            u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                            u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                        },
                        u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                        u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
                    },
                    u'nuvius_resource': None, u'manager': {
                        u'name': u'api_test_contact', u'parent': None,
                        u'contact_type': {
                            u'fields': [], u'details': None, u'id': self.contact_type.id, u'name':
                                u'api_test_contacttype',
                            u'resource_uri': u'/api/identities/type/%s' % self.contact_type.id
                        },
                        u'contactvalue_set': [], u'related_user': None, u'id': self.contact.id,
                        u'resource_uri': u'/api/identities/contact/%s' % self.contact.id
                    },
                    u'client': {
                        u'name': u'api_test_contact', u'parent': None, u'contact_type': {
                            u'fields': [], u'details': None, u'id': self.contact_type.id,
                            u'name': u'api_test_contacttype',
                            u'resource_uri': u'/api/identities/type/%s' % self.contact_type.id
                        },
                        u'contactvalue_set': [], u'related_user': None, u'id': self.contact.id,
                        u'resource_uri': u'/api/identities/contact/%s' % self.contact.id
                    },
                    u'details': None, u'date_created': u'2015-11-09T08:21:00', u'trash': False, u'id': self.project.id,
                    u'resource_uri': u'/api/projects/project/%s' % self.project.id
                },
                u'creator': {
                    u'name': u'api_test', u'default_group': {
                        u'perspective': {
                            u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                            u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                        },
                        u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                        u'resource_uri': u'/api/core/group/%s' % self.group.id
                    },
                    u'disabled': False, u'other_groups': [], u'perspective': {
                        u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                        u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                    },
                    u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                    u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
                },
            },
            u'last_updated': u'2016-01-29T13:53:00', u'creator': {
                u'name': u'api_test', u'default_group': {
                    u'perspective': {
                        u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                        u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                    },
                    u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                    u'resource_uri': u'/api/core/group/%s' % self.group.id
                },
                u'disabled': False, u'other_groups': [], u'perspective': {
                    u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                    u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                },
                u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
            },
            u'user': {
                u'name': u'api_test', u'default_group': {
                    u'perspective': {
                        u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                        u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                    },
                    u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                    u'resource_uri': u'/api/core/group/%s' % self.group.id
                },
                u'disabled': False, u'other_groups': [], u'perspective': {
                    u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                    u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                },
                u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
            },
            u'time_from': u'2016-01-29T13:52:00', u'nuvius_resource': None, u'details': u'api_test_tasktimeslot',
            u'timezone': 0, u'date_created': u'2016-01-29T13:51:00', u'time_to': None, u'trash': False,
            u'id': self.time_slot.id, u'resource_uri': u'/api/projects/task/time/%s' % self.time_slot.id
        }]

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0], expected[0])
        self.cmpDataApi(oldresponse.content, newresponse.content)

    def test_get_project(self):
        oldresponse = self.client.get(reverse(
            'api_projects', kwargs={'object_ptr': self.project.id}), **self.authentication_headers)
        newresponse = self.client.get(reverse(
                'project-detail', kwargs={'pk': self.project.id, 'format': 'json'}), **self.authentication_headers)
        self.assertEquals(oldresponse.status_code, 200)
        self.assertEquals(newresponse.status_code, 200)

        data = json.loads(oldresponse.content)
        expected = {
            u'last_updated': u'2015-11-09T08:26:00', u'name': u'api_test_project', u'parent': None,
            u'creator': {
                u'name': u'api_test',
                u'default_group': {
                    u'perspective': {
                        u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                        u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                    },
                    u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                    u'resource_uri': u'/api/core/group/%s' % self.group.id
                },
                u'disabled': False, u'other_groups': [], u'perspective': {
                    u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                    u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                },
                u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
            },
            u'nuvius_resource': None,
            u'manager': {
                u'name': u'api_test_contact', u'parent': None,
                u'contact_type': {
                    u'fields': [], u'details': None, u'id': self.contact_type.id, u'name': u'api_test_contacttype',
                    u'resource_uri': u'/api/identities/type/%s' % self.contact_type.id
                },
                u'contactvalue_set': [], u'related_user': None, u'id': self.contact.id,
                u'resource_uri': u'/api/identities/contact/%s' % self.contact.id
            },
            u'client': {
                u'name': u'api_test_contact', u'parent': None,
                u'contact_type': {
                    u'fields': [], u'details': None, u'id': self.contact_type.id, u'name': u'api_test_contacttype',
                    u'resource_uri': u'/api/identities/type/%s' % self.contact_type.id},
                u'contactvalue_set': [], u'related_user': None,
                u'id': self.contact.id, u'resource_uri': u'/api/identities/contact/%s' % self.contact.id
            },
            u'details': None,
            u'date_created': u'2015-11-09T08:21:00', u'trash': False, u'id': self.project.id,
            u'resource_uri': u'/api/projects/project/%s' % self.project.id
        }

        self.assertEquals(data['id'], self.project.id)
        self.assertDictEqual(data, expected)

        self.cmpDataApi(oldresponse.content, newresponse.content)

    def test_get_status(self):
        oldresponse = self.client.get(reverse('api_projects_status',
                                              kwargs={'object_ptr': self.taskstatus.id}), **self.authentication_headers)
        newresponse = self.client.get(reverse('taskstatus-detail', kwargs={'pk': self.taskstatus.id, 'format': 'json'}),
                                      **self.authentication_headers)
        self.assertEquals(oldresponse.status_code, 200)
        self.assertEquals(newresponse.status_code, 200)

        data = json.loads(oldresponse.content)
        expected = {
            u'last_updated': u'2016-01-27T17:30:00', u'name': u'api_test_taskstatus',
            u'creator': {
                u'name': u'api_test', u'default_group': {
                    u'perspective': {
                        u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                        u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                    },
                    u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                    u'resource_uri': u'/api/core/group/%s' % self.group.id
                },
                u'disabled': False, u'other_groups': [],
                u'perspective': {
                    u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                    u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id},
                u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
            },
            u'nuvius_resource': None, u'details': None,
            u'active': False, u'date_created': u'2016-01-27T17:29:00', u'hidden': False, u'trash': False,
            u'id': self.taskstatus.id, u'resource_uri': u'/api/projects/status/%s' % self.taskstatus.id
        }

        self.assertEquals(data['id'], self.taskstatus.id)
        self.assertDictEqual(data, expected)
        self.cmpDataApi(oldresponse.content, newresponse.content)

    def test_get_milestone(self):
        oldresponse = self.client.get(reverse('api_projects_milestones', kwargs={
                                   'object_ptr': self.milestone.id}), **self.authentication_headers)
        newresponse = self.client.get(reverse('milestone-detail',
                                              kwargs={'pk': self.milestone.id, 'format': 'json'}),
                                      **self.authentication_headers)
        self.assertEquals(oldresponse.status_code, 200)
        self.assertEquals(newresponse.status_code, 200)
        data = json.loads(oldresponse.content)
        expected = {
            u'status': {
                u'last_updated': u'2016-01-27T17:30:00', u'name': u'api_test_taskstatus',
                u'creator': {
                    u'name': u'api_test', u'default_group': {
                        u'perspective': {
                            u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                            u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                        },
                        u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                        u'resource_uri': u'/api/core/group/%s' % self.group.id
                    },
                    u'disabled': False, u'other_groups': [],
                    u'perspective': {
                        u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                        u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                    },
                    u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                    u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
                },
                u'nuvius_resource': None, u'details': None, u'active': False, u'date_created': u'2016-01-27T17:29:00',
                u'hidden': False, u'trash': False, u'id': self.taskstatus.id,
                u'resource_uri': u'/api/projects/status/%s' % self.taskstatus.id
            },
            u'last_updated': u'2016-01-28T01:10:00', u'name': u'api_test_milestone', u'end_date': None,
            u'creator': {
                u'name': u'api_test', u'default_group': {
                    u'perspective': {
                        u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                        u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                    },
                    u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                    u'resource_uri': u'/api/core/group/%s' % self.group.id
                },
                u'disabled': False, u'other_groups': [], u'perspective': {
                    u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                    u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                },
                u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
            },
            u'nuvius_resource': None, u'start_date': None, u'project': {
                u'last_updated': u'2015-11-09T08:26:00', u'name': u'api_test_project', u'parent': None,
                u'creator': {
                    u'name': u'api_test', u'default_group': {
                        u'perspective': {
                            u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                            u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                        },
                        u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                        u'resource_uri': u'/api/core/group/%s' % self.group.id
                    },
                    u'disabled': False, u'other_groups': [],
                    u'perspective': {
                        u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                        u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                    },
                    u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                    u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
                },
                u'nuvius_resource': None, u'manager': {
                    u'name': u'api_test_contact', u'parent': None, u'contact_type': {
                        u'fields': [], u'details': None, u'id': self.contact_type.id, u'name': u'api_test_contacttype',
                        u'resource_uri': u'/api/identities/type/%s' % self.contact_type.id
                    },
                    u'contactvalue_set': [], u'related_user': None, u'id': self.contact.id,
                    u'resource_uri': u'/api/identities/contact/%s' % self.contact.id
                },
                u'client': {
                    u'name': u'api_test_contact', u'parent': None, u'contact_type': {
                        u'fields': [], u'details': None, u'id': self.contact_type.id, u'name': u'api_test_contacttype',
                        u'resource_uri': u'/api/identities/type/%s' % self.contact_type.id
                    },
                    u'contactvalue_set': [], u'related_user': None, u'id': self.contact.id,
                    u'resource_uri': u'/api/identities/contact/%s' % self.contact.id
                },
                u'details': None, u'date_created': u'2015-11-09T08:21:00', u'trash': False, u'id': self.project.id,
                u'resource_uri': u'/api/projects/project/%s' % self.project.id
            },
            u'details': None, u'date_created': u'2016-01-28T01:09:00', u'trash': False, u'id': self.milestone.id,
            u'resource_uri': u'/api/projects/milestone/%s' % self.milestone.id
        }

        self.assertEquals(data['id'], self.milestone.id)
        self.assertDictEqual(data, expected)
        self.cmpDataApi(oldresponse.content, newresponse.content)

    def test_get_task(self):
        oldresponse = self.client.get(reverse('api_projects_tasks',
                                              kwargs={'object_ptr': self.task.id}), **self.authentication_headers)
        newresponse = self.client.get(reverse('task-detail', kwargs={'pk': self.task.id, 'format': 'json'}),
                                      **self.authentication_headers)
        self.assertEquals(oldresponse.status_code, 200)
        self.assertEquals(newresponse.status_code, 200)
        data = json.loads(oldresponse.content)
        expected = {
            u'status': {
                u'last_updated': u'2016-01-27T17:30:00', u'name': u'api_test_taskstatus',
                u'creator': {
                    u'name': u'api_test', u'default_group': {
                        u'perspective': {
                            u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                            u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                        },
                        u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                        u'resource_uri': u'/api/core/group/%s' % self.group.id
                    },
                    u'disabled': False, u'other_groups': [],
                    u'perspective': {
                        u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                        u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                    },
                    u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                    u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
                },
                u'nuvius_resource': None, u'details': None, u'active': False, u'date_created': u'2016-01-27T17:29:00',
                u'hidden': False, u'trash': False, u'id': self.taskstatus.id,
                u'resource_uri': u'/api/projects/status/%s' % self.taskstatus.id
            },
            u'project': {
                u'last_updated': u'2015-11-09T08:26:00', u'name': u'api_test_project', u'parent': None,
                u'creator': {
                    u'name': u'api_test', u'default_group': {
                        u'perspective': {
                            u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                            u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                        },
                        u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                        u'resource_uri': u'/api/core/group/%s' % self.group.id
                    },
                    u'disabled': False, u'other_groups': [], u'perspective': {
                        u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                        u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                    },
                    u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                    u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
                },
                u'nuvius_resource': None, u'manager': {
                    u'name': u'api_test_contact', u'parent': None, u'contact_type': {
                        u'fields': [], u'details': None, u'id': self.contact_type.id, u'name': u'api_test_contacttype',
                        u'resource_uri': u'/api/identities/type/%s' % self.contact_type.id
                    },
                    u'contactvalue_set': [], u'related_user': None, u'id': self.contact.id,
                    u'resource_uri': u'/api/identities/contact/%s' % self.contact.id
                },
                u'client': {
                    u'name': u'api_test_contact', u'parent': None, u'contact_type': {
                        u'fields': [], u'details': None, u'id': self.contact_type.id, u'name': u'api_test_contacttype',
                        u'resource_uri': u'/api/identities/type/%s' % self.contact_type.id
                    },
                    u'contactvalue_set': [], u'related_user': None, u'id': self.contact.id,
                    u'resource_uri': u'/api/identities/contact/%s' % self.contact.id
                },
                u'details': None, u'date_created': u'2015-11-09T08:21:00', u'trash': False, u'id': self.project.id,
                u'resource_uri': u'/api/projects/project/%s' % self.project.id
            },
            u'last_updated': u'2016-01-28T03:09:00', u'end_date': None, u'name': u'api_test_task',
            u'parent': None, u'creator': {
                u'name': u'api_test', u'default_group': {
                    u'perspective': {
                        u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                        u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                    },
                    u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                    u'resource_uri': u'/api/core/group/%s' % self.group.id
                },
                u'disabled': False, u'other_groups': [], u'perspective': {
                    u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                    u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                },
                u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
            },
            u'estimated_time': None, u'caller': None, u'nuvius_resource': None, u'start_date': None, u'priority': 3,
            u'depends': None, u'details': None, u'milestone': None, u'date_created': u'2016-01-28T03:06:00',
            u'trash': False, u'id': self.task.id, u'resource_uri': u'/api/projects/task/%s' % self.task.id
        }

        self.assertEquals(data['id'], self.task.id)
        self.assertDictEqual(data, expected)
        self.cmpDataApi(oldresponse.content, newresponse.content)

    def test_get_timeslot(self):
        oldresponse = self.client.get(reverse('api_projects_tasktimes',
                                              kwargs={'object_ptr': self.time_slot.id}), **self.authentication_headers)
        newresponse = self.client.get(reverse('tasktimeslot-detail', kwargs={'pk': self.time_slot.id,
                                                                             'format': 'json'}),
                                      **self.authentication_headers)

        self.assertEquals(oldresponse.status_code, 200)
        self.assertEquals(newresponse.status_code, 200)
        data = json.loads(oldresponse.content)
        expected = {
            u'task': {
                u'status': {
                    u'last_updated': u'2016-01-27T17:30:00', u'name': u'api_test_taskstatus',
                    u'creator': {
                        u'name': u'api_test', u'default_group': {
                            u'perspective': {
                                u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                                u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                            },
                            u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                            u'resource_uri': u'/api/core/group/%s' % self.group.id
                        },
                        u'disabled': False, u'other_groups': [], u'perspective': {
                            u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                            u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                        },
                        u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                        u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
                    },
                    u'nuvius_resource': None, u'details': None, u'active': False,
                    u'date_created': u'2016-01-27T17:29:00', u'hidden': False, u'trash': False,
                    u'id': self.taskstatus.id, u'resource_uri': u'/api/projects/status/%s' % self.taskstatus.id
                },
                u'project': {
                    u'last_updated': u'2015-11-09T08:26:00', u'name': u'api_test_project', u'parent': None,
                    u'creator': {
                        u'name': u'api_test', u'default_group': {
                            u'perspective': {
                                u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                                u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                            },
                            u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                            u'resource_uri': u'/api/core/group/%s' % self.group.id
                        },
                        u'disabled': False, u'other_groups': [], u'perspective': {
                            u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                            u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                        },
                        u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                        u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
                    },
                    u'nuvius_resource': None, u'manager': {
                        u'name': u'api_test_contact', u'parent': None, u'contact_type': {
                            u'fields': [], u'details': None, u'id': self.contact_type.id,
                            u'name': u'api_test_contacttype',
                            u'resource_uri': u'/api/identities/type/%s' % self.contact_type.id
                        },
                        u'contactvalue_set': [], u'related_user': None, u'id': self.contact.id,
                        u'resource_uri': u'/api/identities/contact/%s' % self.contact.id
                    },
                    u'client': {
                        u'name': u'api_test_contact', u'parent': None, u'contact_type': {
                            u'fields': [], u'details': None, u'id': self.contact_type.id,
                            u'name': u'api_test_contacttype',
                            u'resource_uri': u'/api/identities/type/%s' % self.contact_type.id
                        },
                        u'contactvalue_set': [], u'related_user': None, u'id': self.contact.id,
                        u'resource_uri': u'/api/identities/contact/%s' % self.contact.id
                    },
                    u'details': None, u'date_created': u'2015-11-09T08:21:00', u'trash': False, u'id': self.project.id,
                    u'resource_uri': u'/api/projects/project/%s' % self.project.id
                },
                u'last_updated': u'2016-01-28T03:09:00', u'end_date': None, u'name': u'api_test_task', u'parent': None,
                u'creator': {
                    u'name': u'api_test', u'default_group': {
                        u'perspective': {
                            u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                            u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                        },
                        u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                        u'resource_uri': u'/api/core/group/%s' % self.group.id
                    },
                    u'disabled': False, u'other_groups': [], u'perspective': {
                        u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                        u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                    },
                    u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                    u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
                },
                u'estimated_time': None, u'caller': None, u'nuvius_resource': None, u'start_date': None, u'priority': 3,
                u'depends': None, u'details': None, u'milestone': None, u'date_created': u'2016-01-28T03:06:00',
                u'trash': False, u'id': self.task.id, u'resource_uri': u'/api/projects/task/%s' % self.task.id
            },
            u'last_updated': u'2016-01-29T13:53:00', u'creator': {
                u'name': u'api_test', u'default_group': {
                    u'perspective': {
                        u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                        u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                    },
                    u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                    u'resource_uri': u'/api/core/group/%s' % self.group.id
                },
                u'disabled': False, u'other_groups': [], u'perspective': {
                    u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                    u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                },
                u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
            },
            u'user': {
                u'name': u'api_test', u'default_group': {
                    u'perspective': {
                        u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                        u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                    },
                    u'name': u'api_test_group', u'parent': None, u'details': None, u'id': self.group.id,
                    u'resource_uri': u'/api/core/group/%s' % self.group.id
                },
                u'disabled': False, u'other_groups': [], u'perspective': {
                    u'details': u'', u'modules': [], u'id': self.perspective.id, u'name': u'default',
                    u'resource_uri': u'/api/core/perspective/%s' % self.perspective.id
                },
                u'last_access': u'2015-11-09T08:21:00', u'id': self.user.profile.id,
                u'resource_uri': u'/api/core/user/%s' % self.user.profile.id
            },
            u'time_from': u'2016-01-29T13:52:00', u'nuvius_resource': None, u'details': u'api_test_tasktimeslot',
            u'timezone': 0, u'date_created': u'2016-01-29T13:51:00', u'time_to': None, u'trash': False,
            u'id': self.time_slot.id, u'resource_uri': u'/api/projects/task/time/%s' % self.time_slot.id
        }

        self.assertEquals(data['id'], self.time_slot.id)
        self.assertDictEqual(data, expected)
        self.cmpDataApi(oldresponse.content, newresponse.content)

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

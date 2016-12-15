from __future__ import unicode_literals
import json
import urllib
from datetime import datetime, timedelta

from freezegun import freeze_time
from django.utils import six
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User as DjangoUser
from anaf.core.models import Group, Perspective, ModuleSetting
from forms import FilterForm, ProjectForm
from models import Project, Milestone, Task, TaskStatus, TaskTimeSlot
from anaf.identities.models import Contact, ContactType
from anaf.test import AnafTestCase, form_to_dict


class ProjectsModelsTest(AnafTestCase):
    """ Documents models tests"""
    def setUp(self):
        self.taskstatus = TaskStatus(name='test')
        self.taskstatus.save()

        self.project = Project(name='test')
        self.project.save()
        self.project2 = Project(name='project 2')
        self.project2.save()

        self.milestone = Milestone(name='milestone name', project=self.project, status=self.taskstatus)
        self.milestone.save()
        self.milestone2 = Milestone(name='milestone 2', project=self.project2, status=self.taskstatus)
        self.milestone2.save()

        self.task = Task(name='test', project=self.project, milestone=self.milestone, status=self.taskstatus)
        self.task.save()

    def test_task_priority_human(self):
        """Default priority should be 3, text representation should be 'Normal'
        """
        self.assertEqual(self.task.priority, 3)
        self.assertEqual(self.task.priority_human(), 'Normal')

    def test_get_estimated_time_default(self):
        """Default estimated time is None, string representation is empty string """
        self.assertIsNone(self.task.estimated_time)
        self.assertEqual(self.task.get_estimated_time(), '')

    def test_get_estimated_time_one_min(self):
        self.task.estimated_time = 1
        self.assertEqual(self.task.get_estimated_time(), ' 1 minutes')

    def test_get_estimated_time_zero_min(self):
        self.task.estimated_time = 0
        self.assertEqual(self.task.get_estimated_time(), 'Less than 1 minute')

    def test_get_estimated_time_60_min(self):
        self.task.estimated_time = 60
        self.assertEqual(self.task.get_estimated_time(), ' 1 hours ')

    def test_get_estimated_time_61_min(self):
        self.task.estimated_time = 61
        self.assertEqual(self.task.get_estimated_time(), ' 1 hours  1 minutes')

    def test_model_task_get_absolute_url(self):
        self.task.get_absolute_url()

    def test_save_milestone_proj_diff_proj(self):
        """If a new task being saved has a self.milestone.project!=self.project
        then task is saved using the milestone project
        """
        newtask = Task(name='new task', project=self.project2, status=self.taskstatus, milestone=self.milestone)
        newtask.save()
        self.assertEqual(newtask.project_id, self.project.id)

    def test_save_inherits(self):
        """Subtask inherits project and milestone from parent task"""
        newtask = Task(name='new task', parent=self.task, project=self.project2, status=self.taskstatus,
                       milestone=self.milestone2)
        newtask.save()
        self.assertEqual(newtask.project_id, self.project.id)
        self.assertEqual(newtask.milestone_id, self.milestone.id)

    def test_save_changed_project(self):
        self.task.project = self.project2
        self.task.save()
        self.assertIsNone(self.task.milestone_id)

    def test_save_changed_milestone(self):
        """changing to a milestone that belongs to another project also change the task.project"""
        self.task.milestone = self.milestone2
        self.task.save()
        self.assertEqual(self.task.project_id, self.project2.id)

    def test_save_status_hidden(self):
        """Changing a task.status to a hidden will also change the subtasks, and also closes timeslots"""
        slot = self.add_time_slot()
        self.assertTrue(slot.is_open())
        status2 = TaskStatus(name='status2', hidden=True)
        status2.save()
        subtask1 = Task(name='sb1', parent=self.task, status=self.taskstatus)
        subtask1.save()
        subtask2 = Task(name='sb2', parent=self.task, status=self.taskstatus)
        subtask2.save()
        self.task.status = status2
        self.task.save()
        subtask1, subtask2 = Task.objects.get(id=subtask1.id), Task.objects.get(id=subtask2.id)
        self.assertEqual(subtask1.status_id, status2.id)
        self.assertEqual(subtask2.status_id, status2.id)
        slot = TaskTimeSlot.objects.get(id=slot.id)
        self.assertFalse(slot.is_open())

    def test_get_absolute_url(self):
        """Test if get_absolute_url works without raising any exception"""
        self.project.get_absolute_url()

    def add_time_slot(self, total_time=None):
        duser, created = DjangoUser.objects.get_or_create(username='testuser')
        time_from = datetime(year=2015, month=8, day=3)
        if total_time is not None:
            time_to = time_from + total_time
        else:
            time_to = None
        timeslot = TaskTimeSlot(task=self.task, user=duser.profile, time_from=time_from, time_to=time_to)
        timeslot.save()
        return timeslot

    def test_get_total_time_default(self):
        self.assertEqual(self.task.get_total_time(), timedelta())

    def test_get_total_time_with_timeslots1(self):
        total_time = timedelta(hours=3)
        self.add_time_slot(total_time)
        self.assertEqual(self.task.get_total_time(), total_time)

    def test_get_total_time_tuple_default(self):
        self.assertIsNone(self.task.get_total_time_tuple())

    def test_get_total_time_tuple(self):
        total_time = timedelta(hours=3)
        self.add_time_slot(total_time)
        h, m, s = self.task.get_total_time_tuple()
        self.assertEqual((h, m, s), (3, 0, 0))

    def test_get_total_time_string_default(self):
        self.assertEqual(self.task.get_total_time_string(), '0 minutes')

    def test_get_total_time_string_one_min(self):
        total_time = timedelta(minutes=1)
        self.add_time_slot(total_time)
        self.assertEqual(self.task.get_total_time_string(), ' 1 minutes')

    def test_get_total_time_string_zero_min(self):
        total_time = timedelta(minutes=0)
        self.add_time_slot(total_time)
        self.assertEqual(self.task.get_total_time_string(), '0 minutes')

    def test_get_total_time_string_30_secs(self):
        total_time = timedelta(seconds=30)
        self.add_time_slot(total_time)
        self.assertEqual(self.task.get_total_time_string(), 'Less than 1 minute')

    def test_get_total_time_string_60_min(self):
        total_time = timedelta(minutes=60)
        self.add_time_slot(total_time)
        self.assertEqual(self.task.get_total_time_string(), ' 1 hours ')

    def test_get_total_time_string_61_min(self):
        total_time = timedelta(minutes=61)
        self.add_time_slot(total_time)
        self.assertEqual(self.task.get_total_time_string(), ' 1 hours  1 minutes')

    def test_is_being_done_by(self):
        duser, created = DjangoUser.objects.get_or_create(username='testuser')
        self.assertFalse(self.task.is_being_done_by(duser.profile))

        time_from = datetime(year=2015, month=8, day=3)
        timeslot = TaskTimeSlot(task=self.task, user=duser.profile, time_from=time_from)
        timeslot.save()
        self.task.save()

        self.assertTrue(self.task.is_being_done_by(duser.profile))

    def test_model_task_status(self):
        """Test task status"""
        obj = TaskStatus(name='test')
        obj.save()
        self.assertEquals('test', obj.name)
        self.assertNotEquals(obj.id, None)
        obj.get_absolute_url()
        obj.delete()

    def test_milestone_model(self):
        """Changing a milestone.project will also change the project for all tasks associated"""
        self.milestone.project = self.project2
        self.milestone.save()
        task = Task.objects.get(id=self.task.id)
        self.assertEqual(task.project_id, self.project2.id)
        # makes sure the method doesn't raise any exceptions
        self.milestone.get_absolute_url()



class TestModelTaskTimeSlot(AnafTestCase):
    username = "testuser"
    password = "password"

    def setUp(self):
        self.group, created = Group.objects.get_or_create(name='test_group')
        self.user, created = DjangoUser.objects.get_or_create(username=self.username)
        self.user.set_password(self.password)
        self.user.save()

        self.project = Project(name='test')
        self.project.save()

        self.taskstatus = TaskStatus(name='test')
        self.taskstatus.save()

        self.task = Task(name='test', project=self.project, status=self.taskstatus)
        self.task.save()

        self.time_from = datetime(year=2015, month=8, day=3)
        self.total_time = timedelta(minutes=61)
        self.time_to = self.time_from + self.total_time
        self.timeslot = TaskTimeSlot(task=self.task, user=self.user.profile, time_from=self.time_from,
                                     time_to=self.time_to)
        self.timeslot.save()

    def test_get_absolute_url(self):
        self.timeslot.get_absolute_url()

    def test_get_time_secs(self):
        with freeze_time(datetime(year=2015, month=8, day=4)):
            self.assertEqual(self.timeslot.get_time_secs(), 86400)

    def test_get_time(self):
        """A time slot without a time from or time to will return a delta of 0"""
        timeslot2 = TaskTimeSlot(task=self.task, user=self.user.profile, time_from=self.time_from)
        timeslot3 = TaskTimeSlot(task=self.task, user=self.user.profile, time_to=self.time_to)
        self.assertEqual(timeslot2.get_time(), timedelta(0))
        self.assertEqual(timeslot3.get_time(), timedelta(0))
        self.assertEqual(self.timeslot.get_time(), self.total_time)

    def test_get_time_tuple(self):
        h, m, s = self.timeslot.get_time_tuple()
        self.assertEqual((h, m, s), (1, 1, 0))
        timeslot2 = TaskTimeSlot(task=self.task, user=self.user.profile, time_to=self.time_to)
        self.assertIsNone(timeslot2.get_time_tuple())

    def test_get_time_string(self):
        self.assertEqual(self.timeslot.get_time_string(), ' 1 hours  1 minutes')

        total_time = timedelta(minutes=1)
        self.timeslot.time_to = self.time_from + total_time
        self.assertEqual(self.timeslot.get_time_string(), ' 1 minutes')

        # if it has a timedelta of zero it will use now-time_from
        total_time = timedelta(minutes=0)
        self.timeslot.time_to = self.time_from + total_time
        with freeze_time(datetime(year=2015, month=8, day=4)):
            self.assertEqual(self.timeslot.get_time_string(), '24 hours ')

        total_time = timedelta(seconds=30)
        self.timeslot.time_to = self.time_from + total_time
        self.assertEqual(self.timeslot.get_time_string(), 'Less than 1 minute')

        total_time = timedelta(minutes=60)
        self.timeslot.time_to = self.time_from + total_time
        self.assertEqual(self.timeslot.get_time_string(), ' 1 hours ')

        self.timeslot.time_from = None
        self.assertEqual(self.timeslot.get_time_string(), '')

        self.timeslot.time_from = self.time_from
        self.timeslot.time_to = None
        with freeze_time(datetime(year=2015, month=8, day=4)):
            self.assertEqual(self.timeslot.get_time_string(), '24 hours ')

    def test_is_open(self):
        # a time slot with both time_from and time_to means it is closed
        self.assertFalse(self.timeslot.is_open())
        self.timeslot.time_to = None
        self.assertTrue(self.timeslot.is_open())


class ProjectsViewsNotLoggedIn(AnafTestCase):
    """Test views Behaviour when user is not logged in
    Basically assert that all views are protected by login
    """

    def assert_protected(self, name, args=None):
        response = self.client.get(reverse(name, args=args))
        # old view redirects to login page
        if response.status_code == 302:
            self.assertRedirects(response, reverse('user_login'))
        else:
            # DRF based view returns 401 unauthorized
            self.assertEqual(response.status_code, 401)

    def test_index(self):
        self.assert_protected('project-list')

    def test_index_owned(self):
        self.assert_protected('task-owned')

    def test_index_assigned(self):
        self.assert_protected('task-assigned')

    def test_index_by_status(self):
        self.assert_protected('task-status', (1,))

    def test_index_in_progress(self):
        self.assert_protected('task-in-progress')

    def test_project_add(self):
        self.assert_protected('project-new')

    def test_project_add_typed(self):
        self.assert_protected('project-new-to-project', (1,))

    def test_project_view(self):
        self.assert_protected('project-detail', (1, ))

    def test_project_edit(self):
        self.assert_protected('project-edit', (1, ))

    def test_project_delete(self):
        self.assert_protected('project-delete', (1, ))

    def test_milestone_add(self):
        self.assert_protected('milestone-new')

    def test_milestone_add_typed(self):
        self.assert_protected('milestone-new-to-project', (1, ))

    def test_milestone_view(self):
        self.assert_protected('milestone-detail', (1, ))

    def test_milestone_edit(self):
        self.assert_protected('milestone-edit', (1, ))

    def test_milestone_delete(self):
        self.assert_protected('milestone-delete', (1, ))

    def test_milestone_set_status(self):
        self.assert_protected('milestone-set-status', (1, 1))

    def test_task_add(self):
        self.assert_protected('task-new')

    def test_task_add_typed(self):
        self.assert_protected('task-new-to-project', (1,))

    def test_task_add_to_milestone(self):
        self.assert_protected('task-new-to-milestone', (1,))

    def test_task_add_subtask(self):
        self.assert_protected('task-new-subtask', (1,))

    def test_task_view(self):
        self.assert_protected('task-detail', (1,))

    def test_task_edit(self):
        self.assert_protected('task-edit', (1,))

    def test_task_delete(self):
        self.assert_protected('task-delete', (1,))

    def test_task_set_status(self):
        self.assert_protected('task-set-status', (1, 1))

    def test_task_time_slot_start(self):
        self.assert_protected('task-start', (1,))

    def test_task_time_slot_stop(self):
        self.assert_protected('tasktimeslot-stop', (1,))

    def test_task_time_slot_add(self):
        self.assert_protected('tasktimeslot-new-to-task', (1,))

    def test_task_time_slot_view(self):
        self.assert_protected('tasktimeslot-detail', (1,))

    def test_task_time_slot_edit(self):
        self.assert_protected('tasktimeslot-edit', (1,))

    def test_task_time_slot_delete(self):
        self.assert_protected('tasktimeslot-delete', (1,))

    def test_task_status_add(self):
        self.assert_protected('taskstatus-new')

    def test_task_status_edit(self):
        self.assert_protected('taskstatus-edit', (1,))

    def test_task_status_delete(self):
        self.assert_protected('taskstatus-delete', (1,))

    def test_settings_view(self):
        self.assert_protected('projectssettings-view')

    def test_settings_edit(self):
        self.assert_protected('projectssettings-edit')

    def test_ajax_task_lookup(self):
        self.assert_protected('task-lookup')

    def test_gantt_view(self):
        self.assert_protected('project-gantt', (1,))


class ProjectsViewsTest(AnafTestCase):
    username = "test"
    password = "password"

    def setUp(self):
        self.group, created = Group.objects.get_or_create(name='test')
        self.user, created = DjangoUser.objects.get_or_create(username=self.username, is_staff=True)
        self.user.set_password(self.password)
        self.user.save()
        perspective, created = Perspective.objects.get_or_create(name='default')
        perspective.set_default_user()
        perspective.save()

        ModuleSetting.set('default_perspective', perspective.id)

        self.contact_type = ContactType(name='test')
        self.contact_type.set_default_user()
        self.contact_type.save()

        self.contact = Contact(name='test', contact_type=self.contact_type)
        self.contact.related_user = self.user.profile
        self.contact.set_default_user()
        self.contact.save()

        self.project = Project(name='test', manager=self.contact, client=self.contact)
        self.project.set_default_user()
        self.project.save()

        self.status = TaskStatus(name='test')
        self.status.set_default_user()
        self.status.save()

        self.status2 = TaskStatus(name='second status')
        self.status2.set_default_user()
        self.status2.save()

        self.milestone = Milestone(name='test', project=self.project, status=self.status)
        self.milestone.set_default_user()
        self.milestone.save()

        self.task = Task(name='test task', project=self.project, status=self.status, caller=self.contact)
        self.task.set_default_user()
        self.task.save()

        self.task_assigned = Task(name='Task2', project=self.project, status=self.status)
        self.task_assigned.save()
        self.task_assigned.assigned.add(self.user.profile)

        self.time_slot = TaskTimeSlot(task=self.task, details='test', time_from=datetime.now(), user=self.user.profile)
        self.time_slot.set_default_user()
        self.time_slot.save()

        self.parent = Project(name='test')
        self.parent.set_default_user()
        self.parent.save()

        self.parent_task = Task(name='task3', project=self.project, status=self.status, priority=3)
        self.parent_task.set_default_user()
        self.parent_task.save()

        self.client = Client()

        self.client.login(username=self.username, password=self.password)

    def test_index(self):
        """Test project index page with login at /projects/"""
        response = self.client.get(reverse('project-list'))
        self.assertEquals(response.status_code, 200)

    def assertQuerysetEqual(self, qs, values, transform=repr, ordered=True, msg=None):
        return super(ProjectsViewsTest, self).assertQuerysetEqual(qs, map(repr, values), transform, ordered, msg)

    def test_index_owned(self):
        """Test owned tasks page at /task/owned/"""
        response = self.client.get(reverse('task-owned'))
        self.assertEquals(response.status_code, 200)
        self.assertQuerysetEqual(response.context['tasks'], [self.task])
        self.assertEqual(type(response.context['filters']), FilterForm)
        # todo: actually test the form generated, if it has the right fields and querysets
        # self.assertEqual(str(response.context['filters']), str(filterform))

    def test_index_assigned(self):
        """Test assigned tasks page at /task/assigned/"""
        response = self.client.get(reverse('task-assigned'))
        self.assertEquals(response.status_code, 200)
        self.assertQuerysetEqual(response.context['tasks'], [self.task_assigned])
        self.assertEqual(type(response.context['filters']), FilterForm)

    # Projects
    def test_project_new(self):
        """Test index page with login at /projects/add/"""
        response = self.client.get(reverse('project-new'))
        self.assertEquals(response.status_code, 200)
        self.assertEqual(type(response.context['form']), ProjectForm)

        projects_qty = Project.objects.count()
        form_params = {'name': 'project_name', 'details': 'new project details'}
        response = self.client.post(reverse('project-new'), data=form_params)
        self.assertEquals(response.status_code, 302)
        project_id = response['Location'].split('/')[-2]
        project_id = int(project_id)  # make sure it got a number for project id
        self.assertRedirects(response, reverse('project-detail', args=[project_id]))
        self.assertEqual(Project.objects.count(), projects_qty+1)
        project = Project.objects.get(id=project_id)
        self.assertEqual(project.name, form_params['name'])
        self.assertEqual(project.details, form_params['details'])

    def test_project_new_to_project(self):
        projects_qty = Project.objects.count()
        response = self.client.get(reverse('project-new-to-project', args=[self.parent.id]))
        self.assertEquals(response.status_code, 200)
        form_data = form_to_dict(response.data['form'])
        form_data['name'] = 'new subproject'
        response = self.client.post(reverse('project-new-to-project', args=[self.parent.id]), data=form_data)
        self.assertEquals(response.status_code, 302)
        project_id = response['Location'].split('/')[-2]
        project_id = int(project_id)  # make sure it got a number for project id
        self.assertRedirects(response, reverse('project-detail', args=[project_id]))
        self.assertEqual(Project.objects.count(), projects_qty + 1)
        project = Project.objects.get(id=project_id)
        self.assertEqual(project.name, form_data['name'])
        self.assertEqual(project.parent_id, int(form_data['parent']))

    def test_project_detail(self):
        """Test index page with login at /projects/view/<project_id>"""
        response = self.client.get(reverse('project-detail', args=[self.project.id]))
        self.assertEquals(response.status_code, 200)

    def test_project_gantt(self):
        """Test gant view page for project, just makes sure it doesn't generates exceptions"""
        # todo, create more data to improve coverage of gantt view
        response = self.client.get(reverse('project-gantt', args=[self.project.id]))
        self.assertEquals(response.status_code, 200)

    def test_project_edit(self):
        """Test project edit page"""
        response = self.client.get(reverse('project-edit', args=[self.project.id]))
        self.assertEquals(response.status_code, 200)
        form_data = form_to_dict(response.data['form'])
        form_data['name'] = 'changed the project name'
        response = self.client.post(reverse('project-edit', args=[self.project.id]), data=form_data)
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse('project-detail', args=[self.project.id]))
        project = Project.objects.get(id=self.project.id)
        self.assertEqual(project.name, form_data['name'])

    def test_project_delete(self):
        """Test project delete page"""
        response = self.client.get(reverse('project-delete', args=[self.project.id]))
        self.assertEquals(response.status_code, 200)
        self.assertFalse(self.project.trash)  # makes sure object is not already in trash
        response = self.client.post(reverse('project-delete', args=[self.project.id]), data={'trash': ''})
        self.assertRedirects(response, reverse('project-list'))
        self.assertTrue(Project.objects.get(id=self.project.id).trash)
        # user should still be able to see project details even if project is in trash
        response = self.client.get(reverse('project-delete', args=[self.project.id]))
        self.assertEquals(response.status_code, 200)
        # now actually delete
        response = self.client.post(reverse('project-delete', args=[self.project.id]))
        self.assertRedirects(response, reverse('project-list'))
        response = self.client.get(reverse('project-delete', args=[self.project.id]))
        self.assertEquals(response.status_code, 404)
        with self.assertRaises(Project.DoesNotExist):
            Project.objects.get(id=self.project.id)

    # Milestones
    def test_milestone_add(self):
        """Test index page with login at /projects/milestone/new"""
        response = self.client.get(reverse('milestone-new'))
        self.assertEquals(response.status_code, 200)

    def test_milestone_new_to_project(self):
        """Test newmilestone page with login at /projects/milestone/new_to_project/<project_id>/"""
        response = self.client.get(reverse('milestone-new-to-project', args=[self.parent.id]))
        self.assertEquals(response.status_code, 200)

    def test_milestone_view_login(self):
        """Test index page with login at /projects/milestone/view/<milestone_id>"""
        response = self.client.get(reverse('milestone-detail', args=[self.milestone.id]))
        self.assertEquals(response.status_code, 200)

    def test_milestone_edit_login(self):
        """Test index page with login at /projects/milestone/edit/<milestone_id>"""
        response = self.client.get(reverse('milestone-edit', args=[self.milestone.id]))
        self.assertEquals(response.status_code, 200)

    def test_milestone_delete_login(self):
        """Test index page with login at /projects/milestone/delete/<milestone_id>"""
        response = self.client.get(reverse('milestone-delete', args=[self.milestone.id]))
        self.assertEquals(response.status_code, 200)

    def test_milestone_set_status_login(self):
        self.assertEqual(self.milestone.status_id, self.status.id)
        response = self.client.get(reverse('milestone-set-status', args=[self.milestone.id, self.status2.id]))
        self.assertEquals(response.status_code, 200)
        milestone = Milestone.objects.get(id=self.milestone.id)
        self.assertEqual(milestone.status_id, self.status2.id)

    # Tasks
    def test_task_add(self):
        """Test index page with login at /projects/task/new/"""
        response = self.client.get(reverse('task-new'))
        self.assertEquals(response.status_code, 200)

    def test_task_add_typed(self):
        """Test index page with login at /projects/task/add/<project_id>"""
        response = self.client.get(reverse('task-new-to-project', args=[self.project.id]))
        self.assertEquals(response.status_code, 200)

    def test_task_add_to_milestone(self):
        """Test new task to milestone page with login at /projects/task/new_to_milestone/<milestone_id>/"""
        response = self.client.get(reverse('task-new-to-milestone', args=[self.milestone.id]))
        self.assertEquals(response.status_code, 200)

    def test_task_add_subtask(self):
        """Test index page with login at /projects/task/add/<task_id>/"""
        response = self.client.get(reverse('task-new-subtask', args=[self.parent_task.id]))
        self.assertEquals(response.status_code, 200)

    def test_task_set_status(self):
        """Test set status page with login at /projects/task/set/<task_id>/status/<status_id>"""
        # no format specified
        response = self.client.get(reverse('task-set-status', args=[self.task.id, self.status2.id]))
        self.assertEquals(response.status_code, 200)
        # check if status was changed on DB
        self.assertEqual(Task.objects.get(id=self.task.id).status_id, self.status2.id)
        # html
        response = self.client.get(reverse('task-set-status', args=[self.task.id, self.status.id, 'html']))
        self.assertEquals(response.status_code, 200)
        # check if status was changed on DB
        self.assertEqual(Task.objects.get(id=self.task.id).status_id, self.status.id)
        # json
        response = self.client.get(reverse('task-set-status', args=[self.task.id, self.status2.id, 'json']))
        self.assertEquals(response.status_code, 406)
        # check if status was not changed on DB
        self.assertEqual(Task.objects.get(id=self.task.id).status_id, self.status.id)

    def test_task_start(self):
        # creates empty task and makes sure it creates a time slot for the task
        task = Task(name='task 2', project=self.project, status=self.status, caller=self.contact)
        task.set_default_user()
        task.save()
        self.assertFalse(task.tasktimeslot_set.all().count())
        response = self.client.post(reverse('task-start', args=(task.id, )))
        self.assertRedirects(response, reverse('task-detail', args=[task.id]))
        self.assertEqual(task.tasktimeslot_set.all().count(), 1)  # assert that only one time slot was created
        timeslot = task.tasktimeslot_set.all()[0]
        self.assertTrue(timeslot.is_open())  # assert that timeslot correctly calculates that it is open
        self.assertTrue(task.is_being_done_by(self.user.profile))

    def test_task_start2(self):
        # start a task which has already started
        self.assertTrue(self.task.is_being_done_by(self.user.profile))
        self.assertEqual(self.task.tasktimeslot_set.all().count(), 1)  # makes sure that the task has only one timeslot
        timeslot = self.task.tasktimeslot_set.all()[0]
        self.assertTrue(timeslot.is_open())

        response = self.client.post(reverse('task-start', args=(self.task.id,)))
        self.assertRedirects(response, reverse('task-detail', args=[self.task.id]))
        self.assertEqual(self.task.tasktimeslot_set.all().count(), 1)  # assert that it didn't create another timeslot

    def test_task_start_fails_on_get(self):
        # task start shouldn't allow GET requests
        task = Task(name='task 2', project=self.project, status=self.status, caller=self.contact)
        task.set_default_user()
        task.save()
        response = self.client.get(reverse('task-start', args=(task.id,)))
        self.assertEquals(response.status_code, 405)
        response = self.client.get(reverse('task-start', args=(self.task.id,)))
        self.assertEquals(response.status_code, 405)

    def test_task_stop(self):
        self.assertTrue(self.time_slot.is_open())
        self.assertIsNone(self.time_slot.time_to)
        response = self.client.post(reverse('tasktimeslot-stop', args=(self.time_slot.id,)))
        self.assertRedirects(response, reverse('task-detail', args=[self.task.id]))
        self.time_slot = TaskTimeSlot.objects.get(id=self.time_slot.id)
        self.assertFalse(self.time_slot.is_open())
        self.assertIsNotNone(self.time_slot.time_to)

        response = self.client.get(reverse('tasktimeslot-stop', args=(self.time_slot.id,)))
        self.assertEquals(response.status_code, 405)

    def test_task_view_login(self):
        """Test index page with login at /projects/task/view/<task_id>"""
        response = self.client.get(reverse('task-detail', args=[self.task.id]))
        self.assertEquals(response.status_code, 200)

    def test_task_edit_login(self):
        """Test index page with login at /projects/task/edit/<task_id>"""
        response = self.client.get(reverse('task-edit', args=[self.task.id]))
        self.assertEquals(response.status_code, 200)

    def test_task_delete_login(self):
        """Test index page with login at /projects/task/delete/<task_id>"""
        response = self.client.get(reverse('task-delete', args=[self.task.id]))
        self.assertEquals(response.status_code, 200)

    # Task Time Slots
    def test_time_slot_add(self):
        """Test index page with login at /projects/task/view/time/<task_id>add/"""
        response = self.client.get(reverse('tasktimeslot-new-to-task', args=[self.task.id]))
        self.assertEquals(response.status_code, 200)

    def test_time_slot_view_login(self):
        """Test index page with login at /projects/task/view/time/<time_slot_id>"""
        response = self.client.get(reverse('task-detail', args=[self.task.id]))
        self.assertEquals(response.status_code, 200)

    def test_time_slot_edit_login(self):
        """Test index page with login at /projects/task/edit/time/<time_slot_id>"""
        response = self.client.get(reverse('task-edit', args=[self.task.id]))
        self.assertEquals(response.status_code, 200)

    def test_time_slot_delete_login(self):
        """Test index page with login at /projects/task/delete/time/<time_slot_id>"""
        response = self.client.get(reverse('task-delete', args=[self.task.id]))
        self.assertEquals(response.status_code, 200)

    # Task Statuses
    def test_task_status_new(self):
        """Test new taskstatus page"""
        status_qty = TaskStatus.objects.count()
        response = self.client.get(reverse('taskstatus-new'))
        self.assertEquals(response.status_code, 200)
        form_data = form_to_dict(response.data['form'])
        form_data['name'] = 'new status'
        response = self.client.post(reverse('taskstatus-new'), data=form_data)
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse('projectssettings-view'))
        self.assertEqual(TaskStatus.objects.count(), status_qty + 1)
        status = TaskStatus.objects.get(name=form_data['name'])
        self.assertEqual(status.name, form_data['name'])

    def test_task_status_view_login(self):
        """Test index page with login at /projects/task/status/view/<status_id>/"""
        response = self.client.get(reverse('task-status', args=[self.status.id]))
        self.assertEquals(response.status_code, 200)

    def test_task_status_edit_login(self):
        """Test index page with login at /projects/task/status/edit/<status_id>/"""
        response = self.client.get(reverse('taskstatus-edit', args=[self.status.id]))
        self.assertEquals(response.status_code, 200)

    def test_task_status_delete_login(self):
        """Test index page with login at /projects/task/status/delete/<status_id>/"""
        response = self.client.get(reverse('taskstatus-delete', args=[self.status.id]))
        self.assertEquals(response.status_code, 200)

    # Settings

    def test_project_settings_view(self):
        """Test index page with login at /projects/settings/view/"""
        response = self.client.get(reverse('projectssettings-view'))
        self.assertEquals(response.status_code, 200)

    def test_project_settings_edit(self):
        """Test index page with login at /projects/settings/edit/"""
        response = self.client.get(reverse('projectssettings-edit'))
        self.assertEquals(response.status_code, 200)

    def _test_ajax_task_lookup(self, search_value, expected):
        url = six.moves.urllib.parse.urlparse(reverse('task-lookup', kwargs={'format': 'json'})). \
            _replace(query=urllib.urlencode({'term': search_value})).geturl()
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        data.sort(key=lambda x: x['value'])
        expected.sort(key=lambda x: x['value'])
        self.assertEqual(data, expected)

    def test_ajax_task_lookup(self):
        expected = [{u'value': self.task_assigned.id, u'label': u'Task2'},
                    {u'value': self.parent_task.id, u'label': u'task3'},
                    {u'value': self.task.id, u'label': u'test task'}]
        self._test_ajax_task_lookup('a', expected)
        self._test_ajax_task_lookup('task', expected)  # ensures search is case insensitive
        self._test_ajax_task_lookup('xpto', [])
        self._test_ajax_task_lookup('te', [{u'label': u'test task', u'value': self.task.id}])

        # asserts the endpoint won't take html
        for fmt in ('html', 'ajax'):
            response = self.client.get(reverse('task-lookup', kwargs={'format': fmt}))
            self.assertEquals(response.status_code, 406)

from time import sleep
from django.core.urlresolvers import reverse
from django.utils import six
from anaf.projects.models import Project, TaskStatus, Task, TaskTimeSlot
from anaf.test import LiveTestCase
from datetime import datetime, timedelta
from freezegun import freeze_time
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select


class ProjectTestCase(LiveTestCase):
    def setUp(self):
        super(ProjectTestCase, self).setUp()
        # self.driver.implicitly_wait(2)

        with freeze_time(datetime(year=2015, month=11, day=9, hour=8, minute=21)):
            self.project = Project(name='front_test_project 1', manager=self.contact, client=self.contact)
        with freeze_time(datetime(year=2015, month=11, day=9, hour=8, minute=26)):
            self.project.save()

        with freeze_time(datetime(year=2016, month=10, day=25, hour=12, minute=11)):
            self.project2 = Project(name='Front test Second project', manager=self.contact, client=self.contact)
        with freeze_time(datetime(year=2016, month=10, day=25, hour=12, minute=26)):
            self.project2.save()

        self.taskstatus1 = TaskStatus(name='taskstatus1')
        self.taskstatus1.save()
        self.taskstatus2 = TaskStatus(name='taskstatus 2')
        self.taskstatus2.save()
        self.taskstatus3 = TaskStatus(name='Task Status 3')
        self.taskstatus3.save()

        self.task = Task(name='Test Task', project=self.project, status=self.taskstatus1)
        self.task.save()
        self.task2 = Task(name='Second Test Task', project=self.project, status=self.taskstatus2)
        self.task2.save()
        self.task3 = Task(name='Test Task 3', project=self.project, status=self.taskstatus3)
        self.task3.save()

        self.time_from = datetime(year=2015, month=8, day=3)
        self.total_time = timedelta(minutes=61)
        self.time_to = self.time_from + self.total_time
        self.timeslot = TaskTimeSlot(task=self.task, user=self.user.profile, time_from=self.time_from,
                                     time_to=self.time_to)
        self.timeslot.save()


class ProjectBasicTests(ProjectTestCase):
    def test_project_index(self):
        self._login()
        url = six.moves.urllib.parse.urljoin(self.live_server_url, reverse('projects'))
        self.driver.get(url)
        self.assertTrue(self.driver.find_element_by_css_selector('#menu-anaf-projects.active'))

    def test_new_simple_project(self):
        """Test creating a minimal project
        """
        self._login()
        self.get('projects')
        name = 'simple_project_name'
        btn = self.driver.find_element_by_css_selector('a[href="#/projects/add"]')
        btn.click()
        self.wait_loaded_selector('.popup-block')
        self.assertTrue(self.driver.find_element_by_css_selector('.popup-block'))
        em = self.send_keys('#id_name', name)
        em.submit()
        self.wait_load()
        sleep(0.1)
        p = Project.objects.get(name=name)
        self.assertEqual(p.name, name)


class ProjectTests(ProjectTestCase):
    def setUp(self):
        super(ProjectTests, self).setUp()
        self._login()
        self.get('projects')
        self.driver.find_element_by_css_selector('a[href="#/projects/view/{}"]'.format(self.project.id)).click()
        self.wait_load()

    def test_edit_project(self):
        name = 'edited name'
        self.click_wait('a[href="#/projects/edit/{}"]'.format(self.project.id))
        em = self.send_keys('#id_name', name, clear=True)
        em.submit()
        self.wait_load()
        p = Project.objects.get(id=self.project.id)
        self.assertEqual(p.name, name)

    def test_trash_project(self):
        self.click_wait('a[href="#/projects/delete/{}"]'.format(self.project.id))
        self.assertFalse(self.project.trash)
        self.click_wait('[name="delete"]')

        p = Project.objects.get(id=self.project.id)
        self.assertTrue(p.trash)
        # after sending to trash confirm it redirects to the projects page
        self.assertEqual(six.moves.urllib.parse.urlparse(self.driver.current_url).fragment, '/projects/index')
        # after sending to the trash it won't be visible anymore
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element_by_css_selector('a[href="#/projects/view/{}"]'.format(self.project.id))

    def test_untrash_project(self):
        self.project.trash = True
        self.project.save()

        # go to trash page and check if project is there
        self.click_wait('a[href="#/trash"]')
        # untrash the project and check if it is really on the projects page
        untrashbtn = self.driver.find_element_by_css_selector('a[href="#/trash/untrash/{}"]'.format(self.project.id))
        builder = ActionChains(self.driver)
        builder.move_to_element(untrashbtn).perform()
        self.wait_until(lambda driver: untrashbtn.is_displayed())
        untrashbtn.click()
        self.wait_load()
        p = Project.objects.get(id=self.project.id)
        self.assertFalse(p.trash)
        self.get('projects')
        self.driver.find_element_by_css_selector('a[href="#/projects/view/{}"]'.format(self.project.id))

    def test_delete_project(self):
        self.driver.find_element_by_css_selector('a[href="#/projects/delete/{}"]'.format(self.project.id)).click()
        self.wait_load()
        self.driver.find_element_by_css_selector('#trash').click()
        self.driver.find_element_by_css_selector('[name="delete"]').click()
        sleep(0.1)
        self.wait_load()
        with self.assertRaises(Project.DoesNotExist):
            Project.objects.get(id=self.project.id)

    def test_task_new(self):
        """Test creating a minimal task
        """
        name = 'task name'
        self.get('projects')
        self.click_wait('a[href="#/projects/task/new/"]')
        # select project from dropdown
        em = self.driver.find_element_by_css_selector('#id_project')
        select = Select(em)
        select.select_by_index(1)

        em = self.send_keys('#id_name', name)
        em.submit()
        self.wait_load()
        sleep(0.1)
        t = Task.objects.get(name=name)
        self.assertEqual(t.name, name)
    # get owned tasks
    # get assigned tasks
    # get in progress tasks
    # view task
    # edit task
    # delete task
    # quick set task status
    # add milestone
    # new status
    # edit status

    # def test_sidebar_links(self):
    #     self._login()
    #     url = urljoin(self.live_server_url, reverse('projects'))
    #     self.driver.get(url)
    #     self.wait_until(lambda driver: not driver.find_element_by_css_selector('#loading-splash').is_displayed())
    #     loading_em = self.driver.find_element_by_css_selector('#loading-status')
    #     sidebar_links = self.driver.find_elements_by_class_name('sidebar-link')
    #     links_count = len(sidebar_links)
    #     for i in range(links_count):
    #         em = self.driver.find_elements_by_class_name('sidebar-link')[i]
    #         em.click()
    #         self.wait_until(lambda driver: not driver.find_element_by_css_selector('#loading-splash').is_displayed())
    #         print(self.driver.find_element_by_css_selector('#loading-splash').is_displayed())
    # click on sidebar links and check console

    # def test_toolbar_login_view(self):
    #     User = get_user_model()
    #     create_page('Home', 'simple.html', 'en', published=True)
    #     ex1 = Example1.objects.create(
    #         char_1='char_1', char_2='char_1', char_3='char_3', char_4='char_4',
    #         date_field=datetime.datetime.now()
    #     )
    #     try:
    #         apphook_pool.register(Example1App)
    #     except AppAlreadyRegistered:
    #         pass
    #     self.reload_urls()
    #     create_page('apphook', 'simple.html', 'en', published=True,
    #                 apphook=Example1App)
    #
    #     url = '%s/%s/?%s' % (self.live_server_url, 'apphook/detail/%s' % ex1.pk, get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON'))
    #     self.driver.get(url)
    #     username_input = self.driver.find_element_by_id("id_cms-username")
    #     username_input.send_keys(getattr(self.user, User.USERNAME_FIELD))
    #     password_input = self.driver.find_element_by_id("id_cms-password")
    #     password_input.send_keys("what")
    #     password_input.submit()
    #     self.wait_page_loaded()
    #     self.assertTrue(self.driver.find_element_by_class_name('cms-error'))
    #
    # def test_toolbar_login_cbv(self):
    #     User = get_user_model()
    #     try:
    #         apphook_pool.register(Example1App)
    #     except AppAlreadyRegistered:
    #         pass
    #     self.reload_urls()
    #     create_page('Home', 'simple.html', 'en', published=True)
    #     ex1 = Example1.objects.create(
    #         char_1='char_1', char_2='char_1', char_3='char_3', char_4='char_4',
    #         date_field=datetime.datetime.now()
    #     )
    #     create_page('apphook', 'simple.html', 'en', published=True,
    #                 apphook=Example1App)
    #     url = '%s/%s/?%s' % (self.live_server_url, 'apphook/detail/class/%s' % ex1.pk, get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON'))
    #     self.driver.get(url)
    #     username_input = self.driver.find_element_by_id("id_cms-username")
    #     username_input.send_keys(getattr(self.user, User.USERNAME_FIELD))
    #     password_input = self.driver.find_element_by_id("id_cms-password")
    #     password_input.send_keys("what")
    #     password_input.submit()
    #     self.wait_page_loaded()
    #     self.assertTrue(self.driver.find_element_by_class_name('cms-error'))
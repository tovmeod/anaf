from urlparse import urljoin
from django.core.urlresolvers import reverse

from anaf.projects.models import Project
from anaf.test import LiveTestCase
from datetime import datetime
from freezegun import freeze_time


class ProjectTests(LiveTestCase):
    def setUp(self):
        super(ProjectTests, self).setUp()
        # self.driver.implicitly_wait(2)

        with freeze_time(datetime(year=2015, month=11, day=9, hour=8, minute=21)):
            self.project = Project(name='front_test_project', manager=self.contact, client=self.contact)
        with freeze_time(datetime(year=2015, month=11, day=9, hour=8, minute=26)):
            self.project.save()

    def test_project_index(self):
        self._login()
        url = urljoin(self.live_server_url, reverse('projects'))
        self.driver.get(url)
        self.assertTrue(self.driver.find_element_by_css_selector('#menu-anaf-projects.active'))

    def test_new_simple_project(self):
        """Test creating a minimal project
        """
        name = 'simple_project_name'
        self._login()
        url = urljoin(self.live_server_url, reverse('projects'))
        self.driver.get(url)
        self.wait_not_selector('#loading-splash')
        btn = self.driver.find_element_by_css_selector('a[href="#/projects/add"]')
        btn.click()
        self.wait_loaded_selector('.popup-block')
        self.assertTrue(self.driver.find_element_by_css_selector('.popup-block'))
        em = self.send_keys('#id_name', name)
        em.submit()
        self.wait_not_selector('#loading-status')
        p = Project.objects.get(name=name)
        self.assertEqual(p.name, name)

    def test_edit_project(self):
        name = 'edited name'
        self._login()
        url = urljoin(self.live_server_url, reverse('projects'))
        self.driver.get(url)
        self.wait_not_selector('#loading-splash')
        self.driver.find_element_by_css_selector('a[href="#/projects/view/{}"]'.format(self.project.id)).click()
        self.wait_not_selector('#loading-status')
        self.driver.find_element_by_css_selector('a[href="#/projects/edit/{}"]'.format(self.project.id)).click()
        self.wait_not_selector('#loading-status')
        em = self.send_keys('#id_name', name, clear=True)
        em.submit()
        self.wait_not_selector('#loading-status')
        p = Project.objects.get(id=self.project.id)
        self.assertEqual(p.name, name)

    def test_trash_project(self):
        self._login()
        url = urljoin(self.live_server_url, reverse('projects'))
        self.driver.get(url)
        self.wait_not_selector('#loading-splash')
        self.driver.find_element_by_css_selector('a[href="#/projects/view/{}"]'.format(self.project.id)).click()
        self.wait_not_selector('#loading-status')
        self.driver.find_element_by_css_selector('a[href="#/projects/delete/{}"]'.format(self.project.id)).click()
        self.wait_not_selector('#loading-status')
        self.assertFalse(self.project.trash)
        self.driver.find_element_by_css_selector('[name="delete"]').click()
        self.wait_not_selector('#loading-status')
        p = Project.objects.get(id=self.project.id)
        self.assertTrue(p.trash)

    def test_delete_project(self):
        self._login()
        url = urljoin(self.live_server_url, reverse('projects'))
        self.driver.get(url)
        self.wait_not_selector('#loading-splash')
        self.driver.find_element_by_css_selector('a[href="#/projects/view/{}"]'.format(self.project.id)).click()
        self.wait_not_selector('#loading-status')
        self.driver.find_element_by_css_selector('a[href="#/projects/delete/{}"]'.format(self.project.id)).click()
        self.wait_not_selector('#loading-status')
        self.driver.find_element_by_css_selector('#trash').click()
        self.driver.find_element_by_css_selector('[name="delete"]').click()
        self.wait_not_selector('#loading-status')
        with self.assertRaises(Project.DoesNotExist):
            Project.objects.get(id=self.project.id)

    # send to trash, and open trash page to check it is there
    # add milestone
    # add task
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
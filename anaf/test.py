# -*- coding: utf-8 -*-
from importlib import import_module
import unittest
import json
import os
from urlparse import urlparse, urljoin
from django.test import TestCase as DjangoTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.contrib.auth.models import User as DjangoUser
from django.core.urlresolvers import reverse
from anaf.identities.models import Contact, ContactType
from anaf.core.models import Group


@unittest.skipIf(not os.environ.get('SELENIUM', ''), 'Selenium env is set to 1')
class AnafTestCase(DjangoTestCase):
    """
    Base class for tests, common functionality will be here
    """
    def cmpDataApi(self, old, new, fieldname='root'):
        """
        Compares data using the old API with data retrieved with the new
        They don't need to be equivalent, the new API may return at least the data the old API was able to and may add
        :param str or dict or list old: content retrieved using the old API
        :param str or dict or list new: content retrieved using the new DRF API
        :return bool: is it kosher?
        """
        if isinstance(old, basestring):
            old = json.loads(old)
        if isinstance(new, basestring):
            new = json.loads(new)
        if isinstance(old, dict) and isinstance(new, dict):
            for k, v in sorted(old.items()):
                if k == 'resource_uri':
                        continue
                assert k in new, 'Field {}.{} not found on new.\nold:{}\nnew:{}'.format(fieldname, k, old, new)
                assert isinstance(v, type(new[k])),\
                    'Field {}.{} exists but have different content type.\nold:{}\nnew:{}'.format(fieldname, k, v, new[k])
                if isinstance(v, dict):
                    self.cmpDataApi(v, new[k], '{}.{}'.format(fieldname, k))
                elif isinstance(v, basestring):
                    assert v == new[k], 'Field {}.{} exists but have different value.\nold:{}\nnew:{}'.format(fieldname, k,
                                                                                                              v, new[k])
                else:
                    assert v == new[k]
        elif isinstance(old, list) and isinstance(new, list):
            old.sort(key=lambda x: x['id'])
            new.sort(key=lambda x: x['id'])
            for i, v in enumerate(old):
                self.cmpDataApi(v, new[i], str(i))
        else:
            assert False, 'old and new have different types'


import datetime
import os
import time


from django.conf import settings
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.models import Permission

from django.core.cache import cache
from django.test.utils import override_settings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException

# from cms.api import create_page, create_title, add_plugin
# from cms.apphook_pool import apphook_pool
# from cms.exceptions import AppAlreadyRegistered
# from cms.models import CMSPlugin, Page, Placeholder
# from cms.test_utils.project.placeholderapp.cms_apps import Example1App
# from cms.test_utils.project.placeholderapp.models import Example1
# from cms.utils.conf import get_cms_setting


class AttributeObject(object):
    """
    mock = AttributeObject(hello='world')
    mock.hello # 'world'
    """
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return '<AttributeObject: %r>' % self.kwargs


class MyStaticFilesHandler(StaticFilesHandler):
    def serve(self, request):
        if request.path == '/static/favicon.ico':
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden()  # I'm not serving favicon during test
        return super(MyStaticFilesHandler, self).serve(request)


@unittest.skipIf(not os.environ.get('SELENIUM', ''), 'Selenium env is set to 0')
class LiveTestCase(StaticLiveServerTestCase):
    username = "fronttestuser"
    password = "password"

    static_handler = MyStaticFilesHandler
    driver = None

    @classmethod
    def setUpClass(cls):
        super(LiveTestCase, cls).setUpClass()
        cache.clear()
        if os.environ.get("TRAVIS_BUILD_NUMBER"):
            capabilities = webdriver.DesiredCapabilities.CHROME
            capabilities['version'] = '45'  # If this capability is null, an empty string, or omitted altogether, the latest version of the browser will be used automatically.  # noqa
            capabilities['platform'] = 'Windows 7'
            capabilities['name'] = 'Anaf'
            capabilities['build'] = os.environ.get("TRAVIS_BUILD_NUMBER")
            capabilities['tags'] = [os.environ.get("TRAVIS_PYTHON_VERSION"), "CI"]
            username = os.environ.get("SAUCE_USERNAME")
            access_key = os.environ.get("SAUCE_ACCESS_KEY")
            capabilities["tunnel-identifier"] = os.environ.get("TRAVIS_JOB_NUMBER")
            hub_url = "http://%s:%s@ondemand.saucelabs.com/wd/hub" % (username, access_key)
            cls.driver = webdriver.Remote(desired_capabilities=capabilities, command_executor=hub_url)
            cls.driver.implicitly_wait(30)
        else:
            # cls.driver = webdriver.Firefox()
            cls.driver = webdriver.Chrome()
            cls.driver.implicitly_wait(5)
        cls.accept_next_alert = True

    @classmethod
    def tearDownClass(cls):
        super(LiveTestCase, cls).tearDownClass()
        if cls.driver:
            cls.driver.quit()
        time.sleep(1)

    def setUp(self):
        super(LiveTestCase, self).setUp()
        self.group, created = Group.objects.get_or_create(name='test_group')
        self.user, created = DjangoUser.objects.get_or_create(username=self.username)
        self.user.set_password(self.password)
        self.user.save()

        self.contact_type = ContactType(name='front_test_contacttype')
        self.contact_type.set_default_user()
        self.contact_type.save()

        self.contact = Contact(name='front_test_contact', contact_type=self.contact_type)
        self.contact.set_default_user()
        self.contact.save()

    def tearDown(self):
        super(LiveTestCase, self).tearDown()
        time.sleep(1)
        cache.clear()

    def get(self, viewname):
        """Get the page based on the viewname and wait it to load
        """
        url = urljoin(self.live_server_url, reverse(viewname))
        self.driver.get(url)
        time.sleep(0.1)
        self.wait_load()

    def wait_load(self):
        """wait for the #loading-splash and #loading-status to not be visible anymore
        """
        self.wait_not_selector('#loading-splash')
        self.wait_not_selector('#loading-status')

    def get_log(self):
        return self.driver.get_log('browser')

    def send_keys(self, selector, value, clear=False):
        em = self.driver.find_element_by_css_selector(selector)
        if clear:
            em.clear()
        em.send_keys(value)
        return em

    def _login(self):
        url = urljoin(self.live_server_url, '/')
        self.driver.get(url)
        self.send_keys('#username', self.username)
        password_input = self.send_keys('#password', self.password)
        password_input.submit()
        self.wait_loaded_id('user-block')

    def _fastlogin(self, **credentials):
        session = import_module(settings.SESSION_ENGINE).SessionStore()
        session.save()
        request = AttributeObject(session=session, META={})
        user = authenticate(**credentials)
        login(request, user)
        session.save()

        # We need to "warm up" the webdriver as we can only set cookies on the
        # current domain
        self.driver.get(self.live_server_url)
        # While we don't care about the page fully loading, Django will freak
        # out if we 'abort' this request, so we wait patiently for it to finish
        self.wait_page_loaded()
        self.driver.add_cookie({
            'name': settings.SESSION_COOKIE_NAME,
            'value': session.session_key,
            'path': '/',
            'domain': urlparse(self.live_server_url).hostname
        })
        self.driver.get('{0}/?{1}'.format(
            self.live_server_url,
            get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON')
        ))
        self.wait_page_loaded()

    def wait_until(self, callback, timeout=10):
        """
        Helper function that blocks the execution of the tests until the
        specified callback returns a value that is not falsy. This function can
        be called, for example, after clicking a link or submitting a form.
        See the other public methods that call this function for more details.
        """
        WebDriverWait(self.driver, timeout).until(callback)

    def wait_loaded_tag(self, tag_name, timeout=10):
        """
        Helper function that blocks until the element with the given tag name
        is found on the page.
        """
        self.wait_until( lambda driver: driver.find_element_by_tag_name(tag_name), timeout)

    def wait_loaded_id(self, id, timeout=10):
        self.wait_until(lambda driver: driver.find_element_by_id(id), timeout)

    def wait_loaded_selector(self, selector, timeout=10):
        self.wait_until(lambda driver: driver.find_element_by_css_selector(selector), timeout)

    def wait_not_selector(self, selector, timeout=10):
        self.wait_until(lambda driver: not driver.find_element_by_css_selector(selector).is_displayed(), timeout)

    def wait_page_loaded(self):
        """
        Block until page has started to load.
        """
        from selenium.common.exceptions import TimeoutException

        try:
            # Wait for the next page to be loaded
            self.wait_loaded_tag('body')
        except TimeoutException:
            # IE7 occasionnally returns an error "Internet Explorer cannot
            # display the webpage" and doesn't load the next page. We just
            # ignore it.
            pass

    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True

    def is_alert_present(self):
        try:
            self.driver.switch_to_alert()
        except NoAlertPresentException:
            return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally:
            self.accept_next_alert = True

#
#
#
# @override_settings(
#     LANGUAGE_CODE='en',
#     LANGUAGES=(('en', 'English'),
#                ('it', 'Italian')),
#     CMS_LANGUAGES={
#         1: [{'code' : 'en',
#              'name': 'English',
#              'public': True},
#             {'code': 'it',
#              'name': 'Italian',
#              'public': True},
#         ],
#         'default': {
#             'public': True,
#             'hide_untranslated': False,
#         },
#     },
#     SITE_ID=1,
# )
# class PlaceholderBasicTests(FastLogin, CMSLiveTests):
#     def setUp(self):
#         self.page = create_page('Home', 'simple.html', 'en', published=True)
#         self.italian_title = create_title('it', 'Home italian', self.page)
#
#         self.placeholder = self.page.placeholders.all()[0]
#
#         add_plugin(self.placeholder, 'TextPlugin', 'en', body='test')
#
#         self.base_url = self.live_server_url
#
#         self.user = self._create_user('admin', True, True, True)
#
#         self.driver.implicitly_wait(5)
#
#         super(PlaceholderBasicTests, self).setUp()
#
#     def _login(self):
#         username = getattr(self.user, get_user_model().USERNAME_FIELD)
#         password = username
#         self._fastlogin(username=username, password=password)
#
#     def test_copy_from_language(self):
#         self._login()
#         self.driver.get('%s/it/?%s' % (self.live_server_url, get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON')))
#
#         # check if there are no plugins in italian version of the page
#
#         italian_plugins = self.page.placeholders.all()[0].get_plugins_list('it')
#         self.assertEqual(len(italian_plugins), 0)
#
#         build_button = self.driver.find_element_by_css_selector('.cms-toolbar-item-cms-mode-switcher a[href="?%s"]' % get_cms_setting('CMS_TOOLBAR_URL__BUILD'))
#         build_button.click()
#
#         submenu = self.driver.find_element_by_css_selector('.cms-dragbar .cms-submenu-settings')
#         submenu.click()
#
#         submenu_link_selector = '.cms-submenu-item a[data-rel="copy-lang"][data-language="en"]'
#         WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, submenu_link_selector)))
#         copy_from_english = self.driver.find_element_by_css_selector(submenu_link_selector)
#         copy_from_english.click()
#
#         # Done, check if the text plugin was copied and it is only one
#
#         WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.cms-draggable:nth-child(2)')))
#
#         italian_plugins = self.page.placeholders.all()[0].get_plugins_list('it')
#         self.assertEqual(len(italian_plugins), 1)
#
#         plugin_instance = italian_plugins[0].get_plugin_instance()[0]
#
#         self.assertEqual(plugin_instance.body, 'test')
#
#     def test_copy_to_from_clipboard(self):
#         self.assertEqual(CMSPlugin.objects.count(), 1)
#         self._login()
#
#         build_button = self.driver.find_element_by_css_selector('.cms-toolbar-item-cms-mode-switcher a[href="?%s"]' % get_cms_setting('CMS_TOOLBAR_URL__BUILD'))
#         build_button.click()
#
#         cms_draggable = self.driver.find_element_by_css_selector('.cms-dragarea-1 .cms-draggable')
#
#         hov = ActionChains(self.driver).move_to_element(cms_draggable)
#         hov.perform()
#
#         submenu = cms_draggable.find_element_by_css_selector('.cms-submenu-settings')
#         submenu.click()
#
#         copy = cms_draggable.find_element_by_css_selector('.cms-submenu-dropdown a[data-rel="copy"]')
#         copy.click()
#
#         menu_trigger = self.driver.find_element_by_css_selector('.cms-toolbar-left .cms-toolbar-item-navigation li:first-child')
#
#         menu_trigger.click()
#
#         self.driver.find_element_by_css_selector('.cms-clipboard-trigger a').click()
#
#         # necessary sleeps for making a "real" drag and drop, that works with the clipboard
#         time.sleep(0.3)
#
#         self.assertEqual(CMSPlugin.objects.count(), 2)
#
#         drag = ActionChains(self.driver).click_and_hold(
#             self.driver.find_element_by_css_selector('.cms-clipboard-containers .cms-draggable:nth-child(1)')
#         )
#
#         drag.perform()
#
#         time.sleep(0.1)
#
#         drag = ActionChains(self.driver).move_to_element(
#             self.driver.find_element_by_css_selector('.cms-dragarea-1')
#         )
#         drag.perform()
#
#         time.sleep(0.2)
#
#         drag = ActionChains(self.driver).move_by_offset(
#             0, 10
#         ).release()
#
#         drag.perform()
#
#         time.sleep(0.5)
#
#         self.assertEqual(CMSPlugin.objects.count(), 3)
#
#         plugins = self.page.placeholders.all()[0].get_plugins_list('en')
#
#         self.assertEqual(len(plugins), 2)
#
#
# @override_settings(
#     SITE_ID=1,
#     CMS_PERMISSION=False,
# )
# class StaticPlaceholderPermissionTests(FastLogin, CMSLiveTests):
#     def setUp(self):
#         self.page = create_page('Home', 'static.html', 'en', published=True)
#
#         self.base_url = self.live_server_url
#
#         self.user = self._create_user("testuser", is_staff=True)
#         self.user.user_permissions = Permission.objects.exclude(codename="edit_static_placeholder")
#
#         self.driver.implicitly_wait(2)
#
#         super(StaticPlaceholderPermissionTests, self).setUp()
#
#     def test_static_placeholders_permissions(self):
#         username = getattr(self.user, get_user_model().USERNAME_FIELD)
#         password = username
#         self._fastlogin(username=username, password=password)
#
#         pk = Placeholder.objects.filter(slot='logo').order_by('id')[0].pk
#         placeholder_name = 'cms-placeholder-%s' % pk
#
#         # test static placeholder permission (content of static placeholders is NOT editable)
#         self.driver.get('%s/en/?%s' % (self.live_server_url, get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON')))
#         self.assertRaises(NoSuchElementException, self.driver.find_element_by_class_name, placeholder_name)
#
#         # update userpermission
#         edit_permission = Permission.objects.get(codename="edit_static_placeholder")
#         self.user.user_permissions.add( edit_permission )
#
#         # test static placeholder permission (content of static placeholders is editable)
#         self.driver.get('%s/en/?%s' % (self.live_server_url, get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON')))
#         self.assertTrue(self.driver.find_element_by_class_name(placeholder_name))

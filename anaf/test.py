from __future__ import print_function
# -*- coding: utf-8 -*-
import base64
from importlib import import_module
import unittest
import socket
import json
import os
from time import sleep
import pytest
try:
    from sauceclient import SauceClient
    USE_SAUCE = True
except ImportError:
    USE_SAUCE = False
from django.test import TestCase as DjangoTestCase, TransactionTestCase
from django.test.testcases import LiveServerThread as DjangoLiveServerThread, _MediaFilesHandler
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.contrib.auth.models import User as DjangoUser
from django.core.urlresolvers import reverse
from anaf.identities.models import Contact, ContactType
from anaf.core.models import Group

import datetime

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
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException, ElementNotVisibleException

# from cms.api import create_page, create_title, add_plugin
# from cms.apphook_pool import apphook_pool
# from cms.exceptions import AppAlreadyRegistered
# from cms.models import CMSPlugin, Page, Placeholder
# from cms.test_utils.project.placeholderapp.cms_apps import Example1App
# from cms.test_utils.project.placeholderapp.models import Example1
# from cms.utils.conf import get_cms_setting

from django.db import connections
from django.utils import six
from django.core.exceptions import ImproperlyConfigured
from django.core.handlers.wsgi import WSGIHandler
from django.core.servers.basehttp import WSGIServer, WSGIRequestHandler
import sys
import errno


@pytest.mark.skipif(os.environ.get('SELENIUM', False), reason='Selenium env is set to 1')
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
        if isinstance(old, six.string_types):
            old = json.loads(old)
        if isinstance(new, six.string_types):
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
                elif isinstance(v, six.string_types):
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


class MyStaticFilesHandler(StaticFilesHandler):
    def serve(self, request):
        if request.path == '/static/favicon.ico':
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden()  # I'm not serving favicon during test
        return super(MyStaticFilesHandler, self).serve(request)


class WSGITestRequestHandler(WSGIRequestHandler):
    """
    Just a regular WSGIRequestHandler except it doesn't log to the standard
    output any of the requests received, so as to not clutter the output for
    the tests results, instead it saves to a given list, useful to print the logs only when a test fails
    """
    def log_message(self, *args):
        # print(args)
        self.logs.append(args)


class LiveServerThread(DjangoLiveServerThread):
    """
    Almost an copy of django's LiveServerThread, but I wanted it to use my own WSGI handler
    """
    def __init__(self, *args, **kwargs):
        self.logs = kwargs.pop('logs', None)
        super(LiveServerThread, self).__init__(*args, **kwargs)

    def run(self):
        """
        Sets up the live server and databases, and then loops over handling
        http requests.
        """
        if self.connections_override:
            # Override this thread's database connections with the ones
            # provided by the main thread.
            for alias, conn in self.connections_override.items():
                connections[alias] = conn
        try:
            # Create the handler for serving static and media files
            handler = self.static_handler(_MediaFilesHandler(WSGIHandler()))

            # Go through the list of possible ports, hoping that we can find
            # one that is free to use for the WSGI server.
            for index, port in enumerate(self.possible_ports):
                try:
                    WSGITestRequestHandler.logs = self.logs
                    self.httpd = WSGIServer(
                        (self.host, port), WSGITestRequestHandler)
                except socket.error as e:
                    if (index + 1 < len(self.possible_ports) and
                            e.errno == errno.EADDRINUSE):
                        # This port is already in use, so we go on and try with
                        # the next one in the list.
                        continue
                    else:
                        # Either none of the given ports are free or the error
                        # is something else than "Address already in use". So
                        # we let that error bubble up to the main thread.
                        raise
                else:
                    # A free port was found.
                    self.port = port
                    break

            self.httpd.set_app(handler)
            self.is_ready.set()
            self.httpd.serve_forever()
        except Exception as e:
            self.error = e
            self.is_ready.set()


class LiveServerTestCase(TransactionTestCase):
    """
    This is almost an copy from django's LiveServerTestCase, I wanted to override setUpClass
     so it can use my own LiveServerThread
    """

    static_handler = MyStaticFilesHandler

    @property
    def live_server_url(self):
        return 'http://%s:%s' % (self.server_thread.host, self.server_thread.port)

    @classmethod
    def setUpClass(cls):
        connections_override = {}
        for conn in connections.all():
            # If using in-memory sqlite databases, pass the connections to
            # the server thread.
            if (conn.vendor == 'sqlite'
                    and conn.settings_dict['NAME'] == ':memory:'):
                # Explicitly enable thread-shareability for this connection
                conn.allow_thread_sharing = True
                connections_override[conn.alias] = conn

        # Launch the live server's thread
        specified_address = os.environ.get(
            'DJANGO_LIVE_TEST_SERVER_ADDRESS', 'localhost:8081')

        # The specified ports may be of the form '8000-8010,8080,9200-9300'
        # i.e. a comma-separated list of ports or ranges of ports, so we break
        # it down into a detailed list of all possible ports.
        possible_ports = []
        try:
            host, port_ranges = specified_address.split(':')
            for port_range in port_ranges.split(','):
                # A port range can be of either form: '8000' or '8000-8010'.
                extremes = list(map(int, port_range.split('-')))
                assert len(extremes) in [1, 2]
                if len(extremes) == 1:
                    # Port range of the form '8000'
                    possible_ports.append(extremes[0])
                else:
                    # Port range of the form '8000-8010'
                    for port in range(extremes[0], extremes[1] + 1):
                        possible_ports.append(port)
        except Exception:
            msg = 'Invalid address ("%s") for live server.' % specified_address
            six.reraise(ImproperlyConfigured, ImproperlyConfigured(msg), sys.exc_info()[2])
        cls.logs = []
        cls.server_thread = LiveServerThread(host, possible_ports,
                                             cls.static_handler,
                                             connections_override=connections_override, logs=cls.logs)
        cls.server_thread.daemon = True
        cls.server_thread.start()

        # Wait for the live server to be ready
        cls.server_thread.is_ready.wait()
        if cls.server_thread.error:
            # Clean up behind ourselves, since tearDownClass won't get called in
            # case of errors.
            cls._tearDownClassInternal()
            raise cls.server_thread.error

        super(LiveServerTestCase, cls).setUpClass()

    @classmethod
    def _tearDownClassInternal(cls):
        # There may not be a 'server_thread' attribute if setUpClass() for some
        # reasons has raised an exception.
        if hasattr(cls, 'server_thread'):
            # Terminate the live server's thread
            cls.server_thread.terminate()
            cls.server_thread.join()

        # Restore sqlite connections' non-shareability
        for conn in connections.all():
            if (conn.vendor == 'sqlite'
                    and conn.settings_dict['NAME'] == ':memory:'):
                conn.allow_thread_sharing = False

    @classmethod
    def tearDownClass(cls):
        cls._tearDownClassInternal()
        super(LiveServerTestCase, cls).tearDownClass()

    def _ifailed(self):
        """Call this on tearDown, check if it was the last run test that failed
        """
        return not sys.exc_info() == (None, None, None)

    def tearDown(self):
        super(LiveServerTestCase, self).tearDown()
        if self._ifailed():
            for log in self.logs:
                print(*log)
        del self.logs[:]


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


@pytest.mark.skipif(not os.environ.get('SELENIUM', False), reason='Selenium env is set to 0')
class LiveTestCase(LiveServerTestCase):
    username = "fronttestuser"
    password = "password"

    static_handler = MyStaticFilesHandler
    driver = None

    @classmethod
    def setUpClass(cls):
        super(LiveTestCase, cls).setUpClass()
        cache.clear()

        if not USE_SAUCE:
            # cls.driver = webdriver.Firefox()
            cls.driver = webdriver.Chrome()
            cls.driver.set_window_size(1366, 768)
            cls.driver.implicitly_wait(5)
        cls.accept_next_alert = True

    @classmethod
    def tearDownClass(cls):
        super(LiveTestCase, cls).tearDownClass()
        if not USE_SAUCE and cls.driver:
            cls.driver.refresh()
            cls.driver.quit()
            sleep(1)
        cls.server_thread.terminate()
        cls.server_thread.join()

    def setUp(self):
        super(LiveTestCase, self).setUp()
        self.group, created = Group.objects.get_or_create(name='test_group')
        self.user, created = DjangoUser.objects.get_or_create(username=self.username)
        self.user.set_password(self.password)
        self.user.save()

        self.contact_type = ContactType(name='front_test_contacttype')
        self.contact_type.set_default_user()
        self.contact_type.save()

        self.contact_type2 = ContactType(name='front_test second contacttype')
        self.contact_type2.set_default_user()
        self.contact_type2.save()

        self.contact = Contact(name='front_test_contact', contact_type=self.contact_type)
        self.contact.set_default_user()
        self.contact.save()

        self.contact2 = Contact(name='front_test second contact', contact_type=self.contact_type2)
        self.contact2.set_default_user()
        self.contact2.save()

        if USE_SAUCE:
            capabilities = webdriver.DesiredCapabilities.CHROME
            capabilities['version'] = '45'  # If this capability is null, an empty string, or omitted altogether, the latest version of the browser will be used automatically.  # noqa
            capabilities['platform'] = 'Windows 7'
            capabilities['name'] = self.id()
            capabilities['build'] = os.environ.get("TRAVIS_BUILD_NUMBER")
            capabilities['tags'] = [os.environ.get("TRAVIS_PYTHON_VERSION"), "CI"]
            username = os.environ.get("SAUCE_USERNAME")
            access_key = os.environ.get("SAUCE_ACCESS_KEY")
            capabilities["tunnel-identifier"] = os.environ.get("TRAVIS_JOB_NUMBER")
            hub_url = "http://%s:%s@ondemand.saucelabs.com/wd/hub" % (username, access_key)
            self.driver = webdriver.Remote(desired_capabilities=capabilities, command_executor=hub_url)
            self.driver.implicitly_wait(30)

    def tearDown(self):
        super(LiveTestCase, self).tearDown()
        if USE_SAUCE and self.driver:
            self.driver.quit()
            self._report_pass_fail()
        sleep(1)
        cache.clear()

    def _report_pass_fail(self):
        session_id = self.driver.session_id
        job_name = self.id()
        sauce_client = SauceClient(os.environ.get("SAUCE_USERNAME"), os.environ.get("SAUCE_ACCESS_KEY"))
        status = (sys.exc_info() == (None, None, None))
        sauce_client.jobs.update_job(session_id, passed=status)
        print("SauceOnDemandSessionID=%s job-name=%s" % (session_id, job_name))

    def get(self, viewname):
        """Get the page based on the viewname and wait it to load
        """
        url = six.moves.urllib.parse.urljoin(self.live_server_url, '#'+reverse(viewname))
        self.driver.get(url)
        sleep(0.1)
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

    def click_wait(self, css_selector):
        for btn in self.driver.find_elements_by_css_selector(css_selector):
            if btn.is_displayed():
                btn.click()
                break
        else:
            # else clause is executed when the loop terminates through exhaustion of the list,
            # but not when the loop is terminated by a break
            raise ElementNotVisibleException()
        self.wait_load()

    def _login(self):
        url = six.moves.urllib.parse.urljoin(self.live_server_url, '/')
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
            'domain': six.moves.urllib.parse.urlparse(self.live_server_url).hostname
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

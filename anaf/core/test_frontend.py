from django.utils import six
from anaf.test import LiveTestCase
from selenium.common.exceptions import NoSuchElementException


class CoreTests(LiveTestCase):
    def test_login(self):
        url = six.moves.urllib.parse.urljoin(self.live_server_url, '/')
        self.driver.get(url)
        self.assertRaises(NoSuchElementException,  self.driver.find_element_by_css_selector,
                          "a[href='#/accounts/logout']")
        self._login()
        parsedurl = six.moves.urllib.parse.urlparse(self.driver.current_url)
        self.assertEqual(parsedurl.path, '/')
        self.assertTrue(self.driver.find_element_by_css_selector("a[href='#/accounts/logout']"))

    def test_blank_login_form(self):
        url = six.moves.urllib.parse.urljoin(self.live_server_url, '/')
        self.driver.get(url)
        self.assertRaises(NoSuchElementException,  self.driver.find_element_by_css_selector,
                          "a[href='#/accounts/logout']")
        password_input = self.driver.find_element_by_id('password')
        password_input.submit()
        self.wait_page_loaded()
        parsedurl = six.moves.urllib.parse.urlparse(self.driver.current_url)
        self.assertEqual(parsedurl.path, '/accounts/login')
        self.assertTrue(self.driver.find_element_by_class_name('error'))
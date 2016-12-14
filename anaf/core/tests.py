"""
Core: test suites
Middleware: test chat
"""
from __future__ import print_function
import os
import datetime
from itertools import chain
import pytest
from django.test import TestCase
from django.core.urlresolvers import reverse, resolve
from django.contrib.auth.models import User as DjangoUser
from django.core.urlresolvers import get_resolver
from django.utils import six
from anaf.identities.models import Contact
from models import User, Group, Module, Perspective, AccessEntity


def _get_url_patterns():
    """Returns list of (pattern-name, pattern) tuples"""
    resolver = get_resolver(None)
    for key, value in sorted(resolver.reverse_dict.items()):
        # sorted because xdist get's crazy if fixtures re returned in a different order
        if isinstance(key, six.string_types):
            yield key, value[0][0][1]


def _get_noargs_urls():
    for name, args in _get_url_patterns():
        if not args:
            match = (resolve(reverse(name)))
            # if match.args:
            #     print(match)
            yield reverse(name)


def _get_withargs_urls():
    skip = ('dajaxice-call-endpoint', )
    for name, args in _get_url_patterns():
        if name not in skip and args:
            args = list(args)
            for i in six.moves.range(len(args)):
                args[i] = str(args[i].lower().replace('_', ''))
                if 'id' in args[i] or 'ptr' in args[i]:
                    args[i] = i
                elif 'path' in args[i]:
                    args[i] += '/'
                elif name == 'events_event_add_to_date':
                    args[i] = i
            yield reverse(name, args=args)


@pytest.mark.skipif(os.environ.get('SELENIUM', False), reason='Selenium env is set to 1')
@pytest.mark.parametrize('url', chain(_get_noargs_urls(), _get_withargs_urls()))
@pytest.mark.django_db(transaction=True)
def test_urls_protected(url, client):
    """All URLs should redirect to the login page or 401 Unauthorized with a few exceptions"""
    response = client.get(url)
    unprotected = ('/accounts/login', '/accounts/password_reset/', '/accounts/password_reset/done/',
                   '/accounts/logo/image/ie/', '/accounts/logo/image/', '/iframe', '/accounts/denied',
                   '/accounts/setup', '/reports/chart/0/options/1')
    if url.endswith('/doc') or url in unprotected:
        assert response.status_code == 200
    elif url in ('/captcha/refresh/', '/captcha/audio/key/', '/accounts/invitation/', '/dajaxice/'):
        # captcha lib incorrectly returns 404 not found
        assert response.status_code == 404
    elif url in ('/captcha/image/key@2/', '/captcha/image/key/'):
        assert response.status_code == 410
    elif url == '/accounts/ajax/upload/0/':
        assert response.status_code == 405
    else:
        assert response.status_code in (302, 401)
        if response.status_code == 302:
            assert response.url in ('http://testserver/accounts/login',
                                    'http://testserver/m/accounts/login',
                                    'http://testserver/accounts/login/?next=/api/auth/authorize_request_token')


@pytest.fixture
def userpsw():
    username = 'test_username'
    password = 'password'
    Group.objects.get_or_create(name='test')
    duser = DjangoUser.objects.get_or_create(username=username, is_staff=True)[0]
    duser.set_password(password)
    duser.save()

    perspective = Perspective(name='test')
    perspective.set_default_user()
    perspective.save()

    return username, password


@pytest.fixture
def authentication_headers():
    username = "api_test"
    password = "api_password"
    headers = {"CONTENT_TYPE": "application/json", "HTTP_AUTHORIZATION": "Basic YXBpX3Rlc3Q6YXBpX3Bhc3N3b3Jk"}
    user = DjangoUser.objects.get_or_create(username=username, is_staff=True)[0]
    user.set_password(password)
    user.save()
    return headers


@pytest.mark.skipif(os.environ.get('SELENIUM', False), reason='Selenium env is set to 1')
@pytest.mark.parametrize('url', _get_noargs_urls())
@pytest.mark.django_db(transaction=True)
def test_no_args_urls_loggedin(url, client, userpsw, authentication_headers):
    _test_no_args_urls_loggedin(url, client, userpsw, authentication_headers)


def _test_no_args_urls_loggedin(url, client, userpsw, authentication_headers):
    """All URLs without arguments should return 200 if logged in"""
    if url.startswith('/api/'):
        # piston can only do http basic auth
        response = client.get(path=url, **authentication_headers)
    else:
        user, psw = userpsw
        client.login(username=user, password=psw)
        response = client.get(url)

    if url in ('/api/auth/get_access_token', '/api/auth/get_request_token'):
        assert response.status_code == 401
    elif url in ('/accounts/logout', '/accounts/login', '/accounts/invitation/', '/accounts/setup',
                 '/dashboard/widget/arrange/', '/api/auth/authorize_request_token'):
        assert response.status_code in (302, 400), url
    elif response.status_code == 302:
        print('%s redirects to %s' % (url, response.url))
    elif url in ('/captcha/refresh/', '/dajaxice/', '/projects/milestone/', '/projects/tasktimeslot/'):
        # captcha lib incorrectly returns 404 not found
        # milestone list and tasktimeslot list returns 404 for format=html,
        # because it is not implemented on the format because it doesn't makes sense
        assert response.status_code == 404
    elif url in ('/projects/taskstatus/', '/projects/task/lookup/'):
        assert response.status_code == 406
    else:
        assert response.status_code == 200


@pytest.mark.skipif(os.environ.get('SELENIUM', False), reason='Selenium env is set to 1')
@pytest.mark.django_db(transaction=True)
@pytest.mark.skip(reason='This takes too much time, I am afraid to timeout travis')
def test_no_args_urls_loggedin_same_session(client, userpsw, authentication_headers):
    for url in _get_noargs_urls():
        _test_no_args_urls_loggedin(url, client, userpsw, authentication_headers)


class CoreModelsTest(TestCase):
    """Core Model Tests"""
    fixtures = ['myinitial_data.json']

    def test_model_AccessEntity(self):
        obj = AccessEntity()
        obj.save()
        self.assertTrue(obj.last_updated - datetime.datetime.now() < datetime.timedelta(seconds=1))

        self.assertIsNone(obj.get_entity())
        self.assertFalse(obj.is_user())
        self.assertEqual(obj.__unicode__(), str(obj.id))
        self.assertEqual(obj.get_absolute_url(), '')

    def test_model_Group_basic(self):
        """Test Group model"""
        name = 'testgroup'
        obj = Group(name=name)
        obj.save()
        self.assertIsNone(obj.parent)
        self.assertIsNone(obj.details)
        self.assertQuerysetEqual(obj.child_set.all(), [])
        self.assertEqual(obj.get_absolute_url(), '/contacts/group/view/{}'.format(obj.id))
        self.assertEqual(obj.get_root(), obj)
        self.assertEqual(obj.get_tree_path(), [obj])
        self.assertIsNone(obj.get_contact())
        self.assertFalse(obj.has_contact())
        self.assertEqual(obj.get_fullname(), name)
        self.assertEqual(obj.get_perspective(), Perspective.objects.all()[0])
        # todo obj.set_perspective()

    def test_model_User_profile(self):
        """Test User model"""
        username = "testusername"
        password = "password"
        user = DjangoUser(username=username)
        user.set_password(password)
        user.save()
        Module.objects.get(name='anaf.core').give_perm_write(user.profile)
        self.assertEquals(user.username, username)
        self.assertIsNotNone(user.id)
        profile = user.profile
        self.assertEquals(profile.name, username)
        self.assertEquals(profile.default_group, Group.objects.all()[0])
        self.assertQuerysetEqual(profile.other_groups.all(), [])
        self.assertFalse(profile.disabled)
        self.assertTrue(profile.last_access - datetime.datetime.now() < datetime.timedelta(seconds=1))
        self.assertEqual(profile.get_absolute_url(), '/contacts/user/view/{}'.format(profile.id))
        oldpsw = profile.user.password
        self.assertNotEqual(profile.generate_new_password(), oldpsw)
        self.assertQuerysetEqual(profile.get_groups(), map(repr, [profile.default_group]))
        self.assertTrue(profile.is_admin())
        self.assertEqual(profile.get_username(), username)
        self.assertEqual(profile.get_perspective(), Perspective.objects.get(name='Default'))
        self.assertEqual(profile.get_contact(), Contact.objects.get(related_user=profile))
        self.assertTrue(profile.has_contact())

        self.assertEqual(profile.__unicode__(), username)

    def test_model_User_profile_change_default_group(self):
        username = "testusername"
        user = DjangoUser(username=username)
        user.save()
        profile = user.profile
        group = Group(name='testgroupname')
        group.save()
        profile.default_group = group
        profile.save()
        profile = User.objects.get(user=user)
        self.assertEquals(profile.default_group, group)

    def test_model_Module_basic(self):
        """Test Module model with minimum parameters"""
        name = 'test module'
        title = 'Test title'
        url = '/test_url/'
        obj = Module(name=name, title=title, url=url)
        obj.save()
        self.assertIsNotNone(obj.id)
        obj = Module.objects.get(id=obj.id)
        self.assertEquals(obj.name, name)
        self.assertEquals(obj.title, title)
        self.assertEquals(obj.url, url)
        self.assertEquals(obj.details, '')
        self.assertTrue(obj.display)
        self.assertTrue(obj.system)
        self.assertEqual(obj.get_absolute_url(), '/admin/module/view/{}'.format(obj.id))

    def test_model_Perspective_basic(self):
        """Test Perspective model with minimum parameters"""
        name = 'test'
        obj = Perspective(name=name)
        obj.save()
        self.assertIsNotNone(obj.id)
        obj = Perspective.objects.get(id=obj.id)
        self.assertEqual(obj.name, name)
        self.assertEqual(obj.details, '')
        self.assertQuerysetEqual(obj.modules.all(), [])
        # default is to have all modules available
        self.assertQuerysetEqual(obj.get_modules(), map(repr, Module.objects.all()))
        self.assertEqual(obj.get_absolute_url(), '/admin/perspective/view/{}'.format(obj.id))

    def test_model_Perspective_full(self):
        """Test Perspective model with all parameters"""
        name = 'test'
        details = 'perspective details'
        obj = Perspective(name='test', details=details)
        obj.save()
        self.assertIsNotNone(obj.id)
        obj = Perspective.objects.get(id=obj.id)
        self.assertEqual(obj.name, name)
        self.assertEqual(obj.details, details)
        module = Module.objects.all()[0]
        obj.modules.add(module)
        self.assertQuerysetEqual(obj.modules.all(), map(repr, [module]))
        self.assertQuerysetEqual(obj.get_modules(), map(repr, [module]))
        self.assertEqual(obj.get_absolute_url(), '/admin/perspective/view/{}'.format(obj.id))


class CoreViewsTestLoggedIn(TestCase):
    """Core View tests when logged in"""
    username = "test"
    password = "password"

    def setUp(self):
        self.group, created = Group.objects.get_or_create(name='test')
        duser, created = DjangoUser.objects.get_or_create(username=self.username, is_staff=True)
        duser.set_password(self.password)
        duser.save()
        self.user = duser

        self.perspective = Perspective(name='test')
        self.perspective.set_default_user()
        self.perspective.save()

        self.client.login(username=self.username, password=self.password)

    def test_user_logout(self):
        """Test logout page at /logout"""
        response = self.client.get(reverse('user_logout'))
        self.assertRedirects(response, reverse('user_login'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_user_login(self):
        """Test login page at /login"""
        response = self.client.post(reverse('user_login'), {'username': self.username, 'password': self.password})
        self.assertRedirects(response, reverse('user_denied'))

    def test_home_login(self):
        """Test home page with login at /"""
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)
        self.assertEqual(self.client.session['_auth_user_id'], self.user.pk)

    # Perspectives
    def test_index_perspectives_login(self):
        """Test page with login at /admin/perspectives/"""
        response = self.client.get(reverse('core_admin_index_perspectives'))
        self.assertEquals(response.status_code, 200)

    def test_perspective_add(self):
        """Test index page with login at /admin/perspective/add"""
        response = self.client.get(reverse('core_admin_perspective_add'))
        self.assertEquals(response.status_code, 200)

    def test_perspective_view(self):
        """Test index page with login at /admin/perspective/view/<perspective_id>"""
        response = self.client.get(reverse('core_admin_perspective_view', args=[self.perspective.id]))
        self.assertEquals(response.status_code, 200)

    def test_perspective_edit(self):
        """Test index page with login at /admin/perspective/edit/<perspective_id>"""
        response = self.client.get(reverse('core_admin_perspective_edit', args=[self.perspective.id]))
        self.assertEquals(response.status_code, 200)

    def test_perspective_delete(self):
        """Test index page with login at /admin/perspective/delete/<perspective_id>"""
        response = self.client.get(reverse('core_admin_perspective_delete', args=[self.perspective.id]))
        self.assertEquals(response.status_code, 200)

    # Modules
    def test_index_modules_login(self):
        """Test page with login at /admin/modules/"""
        response = self.client.get(reverse('core_admin_index_modules'))
        self.assertEquals(response.status_code, 200)

    # Users
    def test_index_users_login(self):
        """Test page with login at /admin/users/"""
        response = self.client.get(reverse('core_admin_index_users'))
        self.assertEquals(response.status_code, 200)

    def test_core_user_add(self):
        """Test page with login at /admin/user/add"""
        name = 'newuser'
        password = 'newuserpsw'
        data = {'name': name, 'password': password, 'password_again': password}
        response = self.client.post(path=reverse('core_admin_user_add'), data=data)
        self.assertEquals(response.status_code, 302)
        profile = User.objects.get(name=name)

        self.assertEquals(profile.name, name)
        self.assertRedirects(response, reverse('core_admin_user_view', args=[profile.id]))
        self.assertEquals(self.client.login(username=name, password=password), True)
        self.client.logout()
        response = self.client.post('/accounts/login', {'username': name, 'password': password})
        self.assertRedirects(response, '/')

    def test_core_user_delete(self):
        """Test page with login at /admin/user/delete"""
        name = 'newuser'
        password = 'newuserpsw'
        user, created = DjangoUser.objects.get_or_create(username=name)
        if created:
            user.set_password(password)
            user.save()
        response = self.client.post(path=reverse('core_admin_user_delete', args=[user.profile.id]),
                                    data={'delete': ''})
        self.assertRedirects(response, reverse('core_admin_index_users'))
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(name=name)
        with self.assertRaises(DjangoUser.DoesNotExist):
            DjangoUser.objects.get(username=name)

    def test_core_user_invite(self):
        """Test page with login at /admin/user/invite"""
        response = self.client.get(reverse('core_admin_user_invite'))
        self.assertEquals(response.status_code, 200)

    # Groups
    def test_index_groups_login(self):
        """Test page with login at /admin/groups/"""
        response = self.client.get(reverse('core_admin_index_groups'))
        self.assertEquals(response.status_code, 200)

    def test_core_group_add(self):
        """Test page with login at /admin/group/add"""
        response = self.client.get(reverse('core_admin_group_add'))
        self.assertEquals(response.status_code, 200)

    def test_core_group_view(self):
        """Test index page with login at /admin/group/view/<group_id>"""
        response = self.client.get(reverse('core_admin_group_view', args=[self.group.id]))
        self.assertEquals(response.status_code, 200)

    def test_core_group_edit(self):
        """Test index page with login at /admin/group/edit/<group_id>"""
        response = self.client.get(reverse('core_admin_group_edit', args=[self.group.id]))
        self.assertEquals(response.status_code, 200)

    def test_core_group_delete(self):
        """Test index page with login at /admin/group/delete/<group_id>"""
        response = self.client.get(reverse('core_admin_group_delete', args=[self.group.id]))
        self.assertEquals(response.status_code, 200)

    # Settings
    def test_core_settings_view(self):
        """Test index page with login at /admin/settings/view/"""
        response = self.client.get(reverse('core_settings_view'))
        self.assertEquals(response.status_code, 200)

    def test_core_settings_edit(self):
        """Test index page with login at /admin/settings/edit/"""
        response = self.client.get(reverse('core_settings_edit'))
        self.assertEquals(response.status_code, 200)


class CoreViewsTestNoLogin(TestCase):
    """Core View tests when not logged in"""
    username = "test"
    password = "password"

    def setUp(self):
        self.group, created = Group.objects.get_or_create(name='test')
        self.user, created = DjangoUser.objects.get_or_create(username=self.username)
        self.user.set_password(self.password)
        self.user.save()

        self.perspective = Perspective(name='test')
        self.perspective.set_default_user()
        self.perspective.save()

    def test_user_logout(self):
        """A logout request from an already logged out user should be harmless
        """
        response = self.client.get(reverse('user_logout'))
        self.assertRedirects(response, reverse('user_login'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_user_login(self):
        """Test login page at /login"""
        response = self.client.post(reverse('user_login'), {'username': self.username, 'password': self.password})
        self.assertRedirects(response, '/')
        self.assertEqual(self.client.session['_auth_user_id'], self.user.pk)

    def test_logo(self):
        """Just test that the logo view works"""
        response = self.client.get(reverse('core_logo_image'))
        self.assertEquals(response.status_code, 200)

    def test_home(self):
        """Test home page at /"""
        response = self.client.get('/')
        # Redirects as unauthenticated
        self.assertRedirects(response, reverse('user_login'))

    def test_index_perspectives_out(self):
        """Test page at /admin/perspectives/"""
        response = self.client.get(reverse('core_admin_index_perspectives'))
        self.assertRedirects(response, reverse('user_login'))

    def test_perspective_add_out(self):
        """Test add perspective page at /admin/perspective/add"""
        response = self.client.get(reverse('core_admin_perspective_add'))
        self.assertRedirects(response, reverse('user_login'))

    def test_perspective_view_out(self):
        """Test perspective view at /admin/perspective/view/<perspective_id>"""
        response = self.client.get(reverse('core_admin_perspective_view', args=[self.perspective.id]))
        self.assertRedirects(response, reverse('user_login'))

    def test_perspective_edit_out(self):
        """Test perspective add at /admin/perspective/edit/<perspective_id>"""
        response = self.client.get(reverse('core_admin_perspective_edit', args=[self.perspective.id]))
        self.assertRedirects(response, reverse('user_login'))

    def test_perspective_delete_out(self):
        """Test perspective delete at /admin/perspective/delete/<perspective_id>"""
        response = self.client.get(reverse('core_admin_perspective_delete', args=[self.perspective.id]))
        self.assertRedirects(response, reverse('user_login'))

    # Modules
    def test_index_modules_out(self):
        """Test index modules page at /admin/modules/"""
        response = self.client.get(reverse('core_admin_index_modules'))
        self.assertRedirects(response, reverse('user_login'))

    # Users
    def test_index_users_out(self):
        """Test index users page at /admin/users/"""
        response = self.client.get(reverse('core_admin_index_users'))
        self.assertRedirects(response, reverse('user_login'))

    def test_core_user_add_out(self):
        """Test user add at /admin/user/add"""
        response = self.client.get(reverse('core_admin_user_add'))
        self.assertRedirects(response, reverse('user_login'))

    def test_core_user_invite_out(self):
        """Test user invite at /admin/user/invite"""
        response = self.client.get(reverse('core_admin_user_invite'))
        self.assertRedirects(response, reverse('user_login'))

    # Groups
    def test_index_groups_out(self):
        """Test index groups at /admin/groups/"""
        response = self.client.get(reverse('core_admin_index_groups'))
        self.assertRedirects(response, reverse('user_login'))

    def test_core_group_add_out(self):
        """Test group add at /admin/group/add"""
        response = self.client.get(reverse('core_admin_group_add'))
        self.assertRedirects(response, reverse('user_login'))

    def test_core_group_view_out(self):
        """Test group view at /admin/group/view/<group_id>"""
        response = self.client.get(reverse('core_admin_group_view', args=[self.group.id]))
        self.assertRedirects(response, reverse('user_login'))

    def test_core_group_edit_out(self):
        """Test group edit at /admin/group/edit/<group_id>"""
        response = self.client.get(reverse('core_admin_group_edit', args=[self.group.id]))
        self.assertRedirects(response, reverse('user_login'))

    def test_core_group_delete_out(self):
        """Test group delete at /admin/group/delete/<group_id>"""
        response = self.client.get(reverse('core_admin_group_delete', args=[self.group.id]))
        self.assertRedirects(response, reverse('user_login'))

    # Settings
    def test_core_settings_view_out(self):
        """Test isettings view at /admin/settings/view/"""
        response = self.client.get(reverse('core_settings_view'))
        self.assertRedirects(response, reverse('user_login'))

    def test_core_settings_edit_out(self):
        """Test settings edit at /admin/settings/edit/"""
        response = self.client.get(reverse('core_settings_edit'))
        self.assertRedirects(response, reverse('user_login'))


class MiddlewareChatTest(TestCase):
    """Midleware chat tests"""
    username = "test"
    password = "password"

    def setUp(self):
        self.group, created = Group.objects.get_or_create(name='test')
        duser, created = DjangoUser.objects.get_or_create(username=self.username)
        duser.set_password(self.password)
        duser.save()

        self.perspective = Perspective(name='test')
        self.perspective.set_default_user()
        self.perspective.save()

    def test_chat_get_new_messages(self):
        """Test get_new_messages"""
        response = self.client.post(
            '/chat', {'json': '{"cmd":"Get", "location":"#"}'})
        self.assertEqual(response.status_code, 200)

    def test_chat_connect(self):
        """Test connect"""
        response = self.client.post(
            '/chat', {'json': '{"cmd":"Connect", "location":"#"}'})
        self.assertEqual(response.status_code, 200)

    def test_chat_disconnect(self):
        """Test disconnect"""
        response = self.client.post(
            '/chat', {'json': '{"cmd":"Disconnect", "location":"#"}'})
        self.assertEqual(response.status_code, 200)

    def test_chat_add_new_message(self):
        """Test add_new_message"""
        response = self.client.post(
            '/chat', {
                'json': '{"cmd":"Message","data":{"id":"test_b5e6d0470a5f4656c3bc77f879c3dbbc","text":"test message"},"location":"#"}'})  # noqa
        self.assertEqual(response.status_code, 200)

    def test_chat_exit_from_conference(self):
        """Test exit_from_conference"""
        response = self.client.post(
            '/chat', {'json': '{"cmd":"Exit","data":{"id":"test_b5e6d0470a5f4656c3bc77f879c3dbbc"},"location":"#"}'})
        self.assertEqual(response.status_code, 200)

    def test_chat_add_users_in_conference(self):
        """Test add_users_in_conference"""
        response = self.client.post(
            '/chat', {
                'json': '{"cmd":"Add","data":{"id":"guest_006f721c4a59a44d969b9f73fb6360a5","users":["test"]},"location":"#"}'})  # noqa
        self.assertEqual(response.status_code, 200)

    def test_chat_create_conference(self):
        """Test create_conference"""
        response = self.client.post(
            '/chat', {'json': '{"cmd":"Create","data":{"title":["Admin"],"users":["admin"]},"location":"#"}'})
        self.assertEqual(response.status_code, 200)

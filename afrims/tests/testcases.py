import datetime
import string
import random
from contextlib import contextmanager

from django.test import TestCase
from django.db import DEFAULT_DB_ALIAS
from django.core.management import call_command
from django.contrib.auth.models import User, Permission

from rapidsms.contrib.messagelog.models import Message
from rapidsms.models import Connection, Contact, Backend
from rapidsms.tests.scripted import TestScript

from afrims.apps.groups.models import Group


UNICODE_CHARS = [unichr(x) for x in xrange(1, 0xD7FF)]


class CreateDataTest(TestCase):
    """ Base test case that provides helper functions to create data """

    def random_string(self, length=255, extra_chars=''):
        chars = string.letters + extra_chars
        return ''.join([random.choice(chars) for i in range(length)])

    def random_number_string(self, length=4):
        numbers = [str(x) for x in random.sample(range(10), 4)]
        return ''.join(numbers)

    def random_unicode_string(self, max_length=255):
        output = u''
        for x in xrange(random.randint(1, max_length/2)):
            c = UNICODE_CHARS[random.randint(0, len(UNICODE_CHARS)-1)]
            output += c + u' '
        return output

    def create_backend(self, data={}):
        defaults = {
            'name': self.random_string(12),
        }
        defaults.update(data)
        return Backend.objects.create(**defaults)

    def create_contact(self, data={}):
        defaults = {
            'name': self.random_string(12),
        }
        defaults.update(data)
        return Contact.objects.create(**defaults)

    def create_connection(self, data={}):
        defaults = {
            'identity': self.random_string(10),
        }
        defaults.update(data)
        if 'backend' not in defaults:
            defaults['backend'] = self.create_backend()
        return Connection.objects.create(**defaults)

    def create_group(self, data={}):
        defaults = {
            'name': self.random_string(12),
        }
        defaults.update(data)
        return Group.objects.create(**defaults)

    def create_message(self, data=None):
        data = data or {}
        defaults = {
            'direction': 'I',
            'date': datetime.datetime.now(),
            'text': 'Oh Hai!',
        }
        defaults.update(data)
        if 'contact' not in defaults:
            defaults['contact'] = self.create_contact()
        return Message.objects.create(**defaults)

    def create_user(self, data=None):
        data = data or {}
        defaults = {
            'username': self.random_string(),
            'email': '',
            'password': self.random_string(),
        }
        defaults.update(data)
        return User.objects.create_user(**defaults)
        


class FlushTestScript(TestScript):
    """ 
    To avoid an issue related to TestCases running after TransactionTestCases,
    extend this class instead of TestScript in RapidSMS. This issue may
    possibly be related to the use of the django-nose test runner in RapidSMS.
    
    See this post and Karen's report here:
    http://groups.google.com/group/django-developers/browse_thread/thread/3fb1c04ac4923e90
    """

    def _fixture_teardown(self):
        call_command('flush', verbosity=0, interactive=False,
                     database=DEFAULT_DB_ALIAS)


class TabPermissionsTest(TestCase):
    """
    Some common code for testing tab permissions.
    """
    def setUp(self):
        super(TabPermissionsTest, self).setUp()
        self.user = User.objects.create_user('test', 'a@b.com', 'abc')
        self.client.login(username='test', password='abc')

    def check_with_perms(self, url, permission_name, status=200, method='get'):
        """ Test that when user has the specified permission, the
            request gets the specified status """
        perm = Permission.objects.get(codename=permission_name)
        self.user.user_permissions.add(perm)
        self.user.save()
        if method == 'get':
            response = self.client.get(url)
        else:
            response = self.client.post(url)
        self.assertEquals(response.status_code, status)
        if status == 302:
            self.assertFalse('/access_denied/' in response['Location'])

    def check_without_perms(self, url, permission_name, method='get'):
        """ Test that when user does not have the specified permission,
            the request gets redirected to the Access denied page """
        perm = Permission.objects.get(codename=permission_name)
        self.user.user_permissions.remove(perm)
        self.user.save()
        if method == 'get':
            response = self.client.get(url)
        else:
            response = self.client.post(url)
        self.assertEquals(response.status_code, 302)
        self.assertTrue('/access_denied/' in response['Location'])

class SettingDoesNotExist:
    pass


@contextmanager
def patch_settings(**kwargs):
    from django.conf import settings
    old_settings = []
    for key, new_value in kwargs.items():
        old_value = getattr(settings, key, SettingDoesNotExist)
        old_settings.append((key, old_value))
        setattr(settings, key, new_value)
    yield
    for key, old_value in old_settings:
        if old_value is SettingDoesNotExist:
            delattr(settings, key)
        else:
            setattr(settings, key, old_value)

import string
import random

from django.test import TestCase
from django.db import DEFAULT_DB_ALIAS
from django.core.management import call_command

from rapidsms.models import Connection, Contact, Backend
from rapidsms.tests.scripted import TestScript

from afrims.apps.groups.models import Group


class CreateDataTest(TestCase):
    """ Base test case that provides helper functions to create data """

    def random_string(self, length=255, extra_chars=''):
        chars = string.letters + extra_chars
        return ''.join([random.choice(chars) for i in range(length)])

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

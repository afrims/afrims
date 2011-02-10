import logging
import string
import random
import datetime
from dateutil.relativedelta import relativedelta

from django.test import TransactionTestCase, TestCase

from rapidsms.tests.harness import MockRouter, MockBackend
from rapidsms.models import Connection, Contact, Backend
from rapidsms.messages.outgoing import OutgoingMessage
from rapidsms.messages.incoming import IncomingMessage

from afrims.apps.broadcast.models import Broadcast
from afrims.apps.broadcast.app import BroadcastApp


class CreateDataTest(TestCase):
    """ Base test case that provides helper functions to create data """

    def random_string(self, length=255, extra_chars=''):
        chars = string.letters + extra_chars
        return ''.join([random.choice(chars) for i in range(length)])

    def create_contact(self, data={}):
        defaults = {
            'name': self.random_string(12),
        }
        defaults.update(data)
        return Contact.objects.create(**defaults)
    
    def create_broadcast(self, data={}):
        defaults = {
            'body': self.random_string(160),
        }
        defaults.update(data)
        return Broadcast.objects.create(**defaults)


class BroadcastDateTest(CreateDataTest):

    def setUp(self):
        self.contact = self.create_contact()

    def test_future_start_date(self):
        """
        date_next_notified should equal schedule_start_date if in future
        """
        now = datetime.datetime.now()
        delta = relativedelta(days=1)
        broadcast = self.create_broadcast()
        broadcast.schedule_start_date = now + delta
        broadcast.schedule_frequency = 'daily'
        self.assertEqual(broadcast.get_next_date(), now + delta)

    def test_near_past(self):
        """
        date_next_notified should equal schedule_start_date if in near past
        """
        now = datetime.datetime.now()
        delta = relativedelta(days=1)
        broadcast = self.create_broadcast()
        broadcast.schedule_start_date = now - delta + relativedelta(hours=+1)
        broadcast.schedule_frequency = 'daily'
        self.assertEqual(broadcast.get_next_date(),
                         broadcast.schedule_start_date + delta)

    def test_one_time(self):
        """
        date_next_notified should equal schedule_start_date if one time
        """
        now = datetime.datetime.now()
        broadcast = self.create_broadcast()
        broadcast.schedule_start_date = now
        broadcast.schedule_frequency = 'one-time'
        self.assertEqual(broadcast.get_next_date(),
                         broadcast.schedule_start_date)


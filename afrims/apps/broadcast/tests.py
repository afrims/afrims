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

from afrims.apps.reminder.models import Group


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

    def create_group(self, data={}):
        defaults = {
            'name': self.random_string(12),
        }
        defaults.update(data)
        return Group.objects.create(**defaults)

    def create_broadcast(self, when='', data={}):
        defaults = {
            'body': self.random_string(160),
        }
        defaults.update(data)
        groups = defaults.pop('groups', [])
        # simple helper flag to create broadcasts in the past or future
        now = datetime.datetime.now()
        delta = relativedelta(days=1)
        if when == 'past':
            defaults.update({'schedule_frequency': 'daily',
                             'date_next_notified': now,
                             'schedule_start_date': now - (delta * 2)})
        elif when == 'future':
            defaults.update({'schedule_frequency': 'daily',
                             'date_next_notified': now + delta,
                             'schedule_start_date': now})
        broadcast = Broadcast.objects.create(**defaults)
        if groups:
            broadcast.groups = groups
        return broadcast


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

    def test_next_date_increment(self):
        """ set_next_date will only increment ready broadcasts """
        # ready broadcasts will increment
        broadcast = self.create_broadcast(when='past')
        old_notify_date = broadcast.date_next_notified
        broadcast.set_next_date()
        new_notify_date = broadcast.date_next_notified
        self.assertTrue(new_notify_date > old_notify_date)
        # non-ready broadcasts will remain the same
        broadcast = self.create_broadcast(when='future')
        old_notify_date = broadcast.date_next_notified
        broadcast.set_next_date()
        new_notify_date = broadcast.date_next_notified
        self.assertEqual(new_notify_date, old_notify_date)


class BroadcastAppTest(CreateDataTest):

    def setUp(self):
        self.contact = self.create_contact()
        self.router = MockRouter()
        self.app = BroadcastApp(router=self.router)

    def test_queue_creation(self):
        """ Test broadcast messages are queued properly """
        c1 = self.create_contact()
        g1 = self.create_group()
        c1.groups.add(g1)
        c2 = self.create_contact()
        g2 = self.create_group()
        c2.groups.add(g2)
        broadcast = self.create_broadcast(data={'groups': [g1]})
        broadcast.queue_outgoing_messages()
        self.assertEqual(broadcast.messages.count(), 1)
        contacts = broadcast.messages.values_list('recipient', flat=True)
        self.assertTrue(c1.pk in contacts)
        self.assertFalse(c2.pk in contacts)

    def test_ready_manager(self):
        """ test Broadcast.ready manager returns broadcasts ready to go out """
        b1 = self.create_broadcast(when='past')
        b2 = self.create_broadcast(when='future')
        ready = Broadcast.ready.values_list('id', flat=True)
        self.assertTrue(b1.pk in ready)
        self.assertFalse(b2.pk in ready)



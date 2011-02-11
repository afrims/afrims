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
from rapidsms.tests.scripted import TestScript

from afrims.apps.broadcast.models import Broadcast
from afrims.apps.broadcast.app import BroadcastApp, scheduler_callback

from afrims.apps.reminder.models import Group


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

    def create_broadcast(self, when='', commit=True, data={}):
        now = datetime.datetime.now()
        defaults = {
            'date': now,
            'schedule_frequency': 'daily',
            'body': self.random_string(160),
        }
        defaults.update(data)
        groups = defaults.pop('groups', [])
        # simple helper flag to create broadcasts in the past or future
        delta = relativedelta(days=1)
        if when == 'ready':
            defaults.update({'date': now - delta})
        elif when == 'future':
            defaults.update({'date': now + delta})
        broadcast = Broadcast.objects.create(**defaults)
        if groups:
            broadcast.groups = groups
        return broadcast


class BroadcastDateTest(CreateDataTest):

    def test_get_next_date_future(self):
        """ get_next_date shouln't increment if date is in the future """
        date = datetime.datetime.now() + relativedelta(hours=1)
        broadcast = self.create_broadcast(data={'date': date})
        self.assertEqual(broadcast.get_next_date(), date)
        broadcast.set_next_date()
        self.assertEqual(broadcast.date, date,
                         "set_next_date should do nothing")

    def test_get_next_date_past(self):
        """ get_next_date should increment if date is in the past """
        date = datetime.datetime.now() - relativedelta(hours=1)
        broadcast = self.create_broadcast(data={'date': date})
        self.assertTrue(broadcast.get_next_date() > date)
        broadcast.set_next_date()
        self.assertTrue(broadcast.date > date,
                        "set_next_date should increment date")

    def test_one_time_broadcast(self):
        """ one-time broadcasts should disable and not increment """
        date = datetime.datetime.now()
        data = {'date': date, 'schedule_frequency': 'one-time'}
        broadcast = self.create_broadcast(data=data)
        self.assertEqual(broadcast.get_next_date(), None,
                         "one-time broadcasts have no next date")
        broadcast.set_next_date()
        self.assertEqual(broadcast.date, date,
                         "set_next_date shoudn't change date of one-time")
        self.assertEqual(broadcast.schedule_frequency, '',
                         "set_next_date should disable one-time")


class BroadcastAppTest(CreateDataTest):

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
        print b1
        self.assertTrue(b1.pk in ready)
        self.assertFalse(b2.pk in ready)


class BroadcastScriptedTest(TestScript, CreateDataTest):
    def test_entire_stack(self):
        self.startRouter()
        contact = self.create_contact()
        backend = self.create_backend(data={'name': 'mockbackend'})
        connection = self.create_connection({'contact': contact,
                                             'backend': backend})
        # ready broadcast
        g1 = self.create_group()
        contact.groups.add(g1)
        b1 = self.create_broadcast(when='past', data={'groups': [g1]})
        # non-ready broadcast
        g2 = self.create_group()
        contact.groups.add(g2)
        b2 = self.create_broadcast(when='future', data={'groups': [g2]})
        # run cronjob
        scheduler_callback(self.router)
        queued = contact.broadcast_messages.filter(status='queued').count()
        sent = contact.broadcast_messages.filter(status='sent').count()
        # nothing should be queued (future broadcast isn't ready)
        self.assertEqual(queued, 0)
        # only one message should be sent
        self.assertEqual(sent, 1)
        self.stopRouter()


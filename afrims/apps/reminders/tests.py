"""
Tests for the appointment reminders app.
"""

import datetime
import logging

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from rapidsms.tests.scripted import TestScript

from afrims.apps.reminders import models as reminders
from afrims.tests.testcases import CreateDataTest


class RemindersCreateDataTest(CreateDataTest):
    # add reminders-specific create_* methods here as needed
    pass


class ViewsTest(RemindersCreateDataTest):

    def setUp(self):
        self.user = User.objects.create_user('test', 'a@b.com', 'abc')
        self.user.save()
        self.client.login(username='test', password='abc')

    def test_notification_schedule(self):
        """
        Test that the notification schedule loads and updates properly.
        """
        reminders_dash = reverse('reminders_dashboard')
        response = self.client.get(reminders_dash)
        self.assertEqual(response.status_code, 200)
        post_data = {
            u'form-INITIAL_FORMS': u'0',
            u'form-TOTAL_FORMS': u'3',
            u'form-0-num_days': u'2',
            u'form-1-num_days': u'11',
            u'form-2-num_days': u'',
        }
        response = self.client.post(reminders_dash, post_data)
        self.assertRedirects(response, reminders_dash)
        self.assertEqual(reminders.Notification.objects.count(), 2)


class RemindersScriptedTest(TestScript, RemindersCreateDataTest):

    def test_scheduler(self):
        self.startRouter()
        self.router.logger.setLevel(logging.DEBUG)
        contact = self.create_contact()
        backend = self.create_backend(data={'name': 'mockbackend'})
        connection = self.create_connection({'contact': contact,
                                             'backend': backend})
        notification = reminders.Notification.objects.create(num_days=1)
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        reminders.Patient.objects.create(contact=contact,
                                         date_enrolled=datetime.date.today(),
                                         subject_number='1234',
                                         mobile_number='tester',
                                         next_visit=tomorrow)
        # run cronjob
        from afrims.apps.reminders.app import scheduler_callback
        scheduler_callback(self.router)
        queued = contact.sent_notifications.filter(status='queued').count()
        sent = contact.sent_notifications.filter(status='sent').count()
        # nothing should be queued (future broadcast isn't ready)
        self.assertEqual(queued, 0)
        # only one message should be sent
        self.assertEqual(sent, 1)
        message = contact.sent_notifications.filter(status='sent')[0]
        self.assertTrue(message.date_sent is not None)
        self.stopRouter()

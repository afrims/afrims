"""
Tests for the appointment reminders app.
"""

import datetime
import logging
import random
import re
from lxml import etree

from django.test import TestCase
from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Permission
from django.core.exceptions import ValidationError

from rapidsms.tests.harness import MockRouter, MockBackend
from rapidsms.messages.incoming import IncomingMessage
from rapidsms.messages.outgoing import OutgoingMessage

from afrims.apps.groups.models import Group
from afrims.apps.reminders import models as reminders
from afrims.tests.testcases import (CreateDataTest, FlushTestScript,
                                    patch_settings, TabPermissionsTest)
from afrims.apps.reminders.app import RemindersApp
from afrims.apps.reminders.importer import parse_payload, parse_patient


class RemindersCreateDataTest(CreateDataTest):
    # add reminders-specific create_* methods here as needed

    def _node(self, name, value=None):
        element = etree.Element(name)
        if value:
            element.text = value
        return element

    def create_xml_patient(self, data=None):
        """
        <Table>
            <Subject_Number>xxx-nnnnn</Subject_Number>
            <Date_Enrolled>Mar  8 2011 </Date_Enrolled>
            <Mobile_Number>08-11111111</Mobile_Number>
            <Pin_Code>1234</Pin_Code>
            <Next_Visit>Apr  7 2011 </Next_Visit>
            <Reminder_Time>12:00</Reminder_Time>
        </Table>
        """
        data = data or {}
        now = datetime.datetime.now()
        delta = datetime.timedelta(days=random.randint(1, 10) * -1)
        enrolled = now - delta
        delta = datetime.timedelta(days=random.randint(1, 10))
        next_visit = now + delta
        defaults = {
            'Subject_Number': self.random_string(10),
            'Pin_Code': self.random_number_string(4),
            'Date_Enrolled': enrolled.strftime('%b  %d %Y '),
            'Next_Visit': next_visit.strftime('%b  %d %Y '),
            'Mobile_Number': '12223334444',
        }
        defaults.update(data)
        empty_items = [k for k, v in defaults.iteritems() if not v]
        for item in empty_items:
            del defaults[item]
        root = self._node('Table')
        for key, value in defaults.iteritems():
            root.append(self._node(key, value))
        return root

    def create_xml_payload(self, nodes):
        root = self._node('NewDataSet')
        for node in nodes:
            root.append(node)
        return etree.tostring(root)

    def create_payload(self, nodes):
        raw_data = self.create_xml_payload(nodes)
        return reminders.PatientDataPayload.objects.create(raw_data=raw_data)

    def create_patient(self, data=None):
        data = data or {}
        today = datetime.date.today()
        defaults = {
            'subject_number': self.random_string(12),
            'mobile_number': self.random_number_string(15),
            'pin': self.random_number_string(4),
            'date_enrolled': today,
            'next_visit': today + datetime.timedelta(weeks=1),
        }
        defaults.update(data)
        if 'contact' not in defaults:
            defaults['contact'] = self.create_contact()
        return reminders.Patient.objects.create(**defaults)

    def create_notification(self, data=None):
        data = data or {}
        defaults = {
            'num_days': random.choice(reminders.Notification.NUM_DAY_CHOICES)[0],
            'time_of_day': '12:00',
            'recipients': random.choice(reminders.Notification.RECIPIENTS_CHOICES)[0],
        }
        defaults.update(data)
        return reminders.Notification.objects.create(**defaults)

    def create_sent_notification(self, data=None):
        data = data or {}
        today = datetime.date.today()
        defaults = {
            'status': random.choice(reminders.SentNotification.STATUS_CHOICES)[0],
            'appt_date': today,
            'date_queued': today,
            'date_to_send': today,
            'message': self.random_string(),
        }
        defaults.update(data)
        if 'recipient' not in defaults:
            defaults['recipient'] = self.create_patient().contact
        if 'notification' not in defaults:
            defaults['notification'] = self.create_notification()
        return reminders.SentNotification.objects.create(**defaults)

    def create_confirmed_notification(self, patient, appt_date=None):
        appt_date = appt_date or datetime.date.today()
        return self.create_sent_notification(data={
            'status': 'confirmed',
            'date_sent': appt_date - datetime.timedelta(days=1),
            'date_confirmed': appt_date - datetime.timedelta(days=1),
            'appt_date': appt_date,
            'recipient': patient.contact
        })

    def create_unconfirmed_notification(self, patient, appt_date=None):
        appt_date = appt_date or datetime.date.today()
        return self.create_sent_notification(data={
            'status': 'sent',
            'date_sent': appt_date - datetime.timedelta(days=1),
            'date_confirmed': None,
            'appt_date': appt_date,
            'recipient': patient.contact
        })


class RemindersTabPermissionsTest(TabPermissionsTest):
    """ Test tab permissions for reminders tabs """

    def test_reminder_tab_without_perms(self):
        """
        Test that the tab cannot be loaded without the proper Permission
        """
        self.check_without_perms(reverse('reminders_dashboard'),
                                 'can_use_appointment_reminders_tab')

class ViewsTest(RemindersCreateDataTest):

    def setUp(self):
        self.user = User.objects.create_user('test', 'a@b.com', 'abc')
        perm = Permission.objects.get(codename='can_use_appointment_reminders_tab')
        self.user.user_permissions.add(perm)
        self.user.save()
        self.client.login(username='test', password='abc')
        self.dashboard_url = reverse('reminders_dashboard')

    def get_valid_data(self):
        data = {
            'num_days': random.choice(reminders.Notification.NUM_DAY_CHOICES)[0],
            'time_of_day': '12:00',
            'recipients': random.choice(reminders.Notification.RECIPIENTS_CHOICES)[0],
        }
        return data

    def test_notification_schedule(self):
        """
        Test that the notification schedule loads properly.
        """

        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        
    def test_get_create_page(self):
        """
        Test retriving the create notification schedule form.
        """

        url = reverse('create-notification')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_notification(self):
        """
        Test creating notification via form.
        """

        start_count = reminders.Notification.objects.count()
        url = reverse('create-notification')
        data = self.get_valid_data()
        response = self.client.post(url, data)
        self.assertRedirects(response, self.dashboard_url)
        end_count = reminders.Notification.objects.count()
        self.assertEqual(end_count, start_count + 1)

    def test_get_edit_page(self):
        """
        Test retriving the edit notification schedule form.
        """

        data = self.get_valid_data()
        notification = reminders.Notification.objects.create(**data)
        url = reverse('edit-notification', args=[notification.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_edit_notification(self):
        """
        Test editing notification via form.
        """

        data = self.get_valid_data()
        notification = reminders.Notification.objects.create(**data)
        start_count = reminders.Notification.objects.count()
        url = reverse('edit-notification', args=[notification.pk])
        response = self.client.post(url, data)
        self.assertRedirects(response, self.dashboard_url)
        end_count = reminders.Notification.objects.count()
        self.assertEqual(end_count, start_count)

    def test_get_delete_page(self):
        """
        Test retriving the delete notification schedule form.
        """

        data = self.get_valid_data()
        notification = reminders.Notification.objects.create(**data)
        url = reverse('delete-notification', args=[notification.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_delete_notification(self):
        """
        Test delete notification via form.
        """

        data = self.get_valid_data()
        notification = reminders.Notification.objects.create(**data)
        start_count = reminders.Notification.objects.count()
        url = reverse('delete-notification', args=[notification.pk])
        response = self.client.post(url, data)
        self.assertRedirects(response, self.dashboard_url)
        end_count = reminders.Notification.objects.count()
        self.assertEqual(end_count, start_count - 1)


class RemindersConfirmHandlerTest(RemindersCreateDataTest):

    def setUp(self):
        self.contact = self.create_contact()
        self.backend = self.create_backend(data={'name': 'mockbackend'})
        self.unreg_conn = self.create_connection({'backend': self.backend})
        self.reg_conn = self.create_connection({'contact': self.contact,
                                                'backend': self.backend})
        self.router = MockRouter()
        self.app = RemindersApp(router=self.router)
        self.patient = self.create_patient(data={'contact': self.contact})

    def _send(self, conn, text):
        msg = IncomingMessage(conn, text)
        self.app.handle(msg)
        return msg

    def test_unregistered(self):
        """ test the response from an unregistered user """
        msg = self._send(self.unreg_conn, '1')
        self.assertEqual(len(msg.responses), 1)
        self.assertEqual(msg.responses[0].text,
                         self.app.not_registered)

    def test_registered_no_notifications(self):
        """
        test the response from a registered user without any notifications
        """
        msg = self._send(self.reg_conn, '1')
        self.assertEqual(len(msg.responses), 1)
        self.assertEqual(msg.responses[0].text,
                         self.app.no_reminders)

    def test_registered_pin_required(self):
        """
        test the response from a registered user without any notifications
        """
        self.contact.pin = '1234'
        self.contact.save()
        msg = self._send(self.reg_conn, '1')
        self.assertEqual(len(msg.responses), 1)
        self.assertEqual(msg.responses[0].text,
                         self.app.pin_required)

    def test_registered_incorrect_pin(self):
        """
        test the response from a registered user without any notifications
        """
        self.contact.pin = '1234'
        self.contact.save()
        msg = self._send(self.reg_conn, '4444')
        self.assertEqual(len(msg.responses), 1)
        self.assertEqual(msg.responses[0].text,
                         self.app.incorrect_pin)

    def test_registered_with_notification(self):
        """ test the response from a user with a pending notification """
        now = datetime.datetime.now()
        notification = reminders.Notification.objects.create(num_days=1,
                                                             time_of_day=now)
        reminders.SentNotification.objects.create(notification=notification,
                                                  recipient=self.contact,
                                                  status='sent',
                                                  message='abc',
                                                  appt_date=now,
                                                  date_to_send=now)
        msg = self._send(self.reg_conn, '1')
        self.assertEqual(len(msg.responses), 1)
        self.assertEqual(msg.responses[0].text,
                         self.app.thank_you)
        sent_notif = reminders.SentNotification.objects.all()
        self.assertEqual(sent_notif.count(), 1)
        self.assertEqual(sent_notif[0].status, 'confirmed')

    def test_registered_with_notification_and_pin(self):
        """ test the response from a user with a pending notification """
        now = datetime.datetime.now()
        self.contact.pin = '1234'
        self.contact.save()
        notification = reminders.Notification.objects.create(num_days=1,
                                                             time_of_day=now)
        reminders.SentNotification.objects.create(notification=notification,
                                                  recipient=self.contact,
                                                  status='sent',
                                                  message='abc',
                                                  appt_date=now,
                                                  date_to_send=now)
        msg = self._send(self.reg_conn, '1234')
        self.assertEqual(len(msg.responses), 1)
        self.assertEqual(msg.responses[0].text,
                         self.app.thank_you)
        sent_notif = reminders.SentNotification.objects.all()
        self.assertEqual(sent_notif.count(), 1)
        self.assertEqual(sent_notif[0].status, 'confirmed')

    def test_forward_broadcast(self):
        """Confirmations should be forwarded to DEFAULT_CONFIRMATIONS_GROUP_NAME"""
        now = datetime.datetime.now()
        notification = reminders.Notification.objects.create(num_days=1,
                                                             time_of_day=now)
        reminders.SentNotification.objects.create(notification=notification,
                                                  recipient=self.contact,
                                                  status='sent',
                                                  message='abc',
                                                  appt_date=now,
                                                  date_to_send=now)
        msg = self._send(self.reg_conn, '1')
        group = Group.objects.get(name=settings.DEFAULT_CONFIRMATIONS_GROUP_NAME)
        broadcasts = group.broadcasts.filter(schedule_frequency='one-time')
        self.assertEqual(broadcasts.count(), 1)
        expected_msg_re = re.compile(r'From %s \(%s\): Appointment on \d{4}-\d{2}-\d{2} confirmed.' % (self.reg_conn.identity, self.patient.subject_number))
        logging.debug('Broadcast="%s"' % broadcasts[0].body)
        self.assertTrue(expected_msg_re.match(broadcasts[0].body))

class RemindersScriptedTest(FlushTestScript, RemindersCreateDataTest):

    def test_scheduler(self):
        self.startRouter()
        self.router.logger.setLevel(logging.DEBUG)
        contact = self.create_contact({'pin': '1234'})
        backend = self.create_backend(data={'name': 'mockbackend'})
        connection = self.create_connection({'contact': contact,
                                             'backend': backend})
        now = datetime.datetime.now()
        notification = reminders.Notification.objects.create(num_days=1,
                                                             time_of_day=now)
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

    def test_patient_reminder_time(self):
        self.startRouter()
        self.router.logger.setLevel(logging.DEBUG)
        contact = self.create_contact({'pin': '1234'})
        backend = self.create_backend(data={'name': 'mockbackend'})
        connection = self.create_connection({'contact': contact,
                                             'backend': backend})
        now = datetime.datetime.now()
        notification = reminders.Notification.objects.create(num_days=1,
                                                             time_of_day=now)
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        next_hour = now + + datetime.timedelta(hours=1)
        patient = reminders.Patient.objects.create(contact=contact,
                                         date_enrolled=datetime.date.today(),
                                         subject_number='1234',
                                         mobile_number='tester',
                                         next_visit=tomorrow,
                                         reminder_time=next_hour.time())
        # run cronjob
        from afrims.apps.reminders.app import scheduler_callback
        scheduler_callback(self.router)
        queued = contact.sent_notifications.filter(status='queued').count()
        sent = contact.sent_notifications.filter(status='sent').count()
        # patient message should be queued since they have asked for a later time
        self.assertEqual(queued, 1)
        # no messages ready to be sent
        self.assertEqual(sent, 0)
        message = contact.sent_notifications.filter(status='queued')[0]
        self.assertTrue(message.date_sent is None)
        self.assertEqual(message.date_to_send, datetime.datetime.combine(now, patient.reminder_time))
        self.stopRouter()


class ImportTest(RemindersCreateDataTest):

    def setUp(self):
        self.user = User.objects.create_user('test', 'a@b.com', 'pass')
        self.url = reverse('patient-import')

    def _authorize(self):
        self.client.login(username='test', password='pass')
        permission = Permission.objects.get(codename='add_patientdatapayload')
        self.user.user_permissions.add(permission)

    def _get(self, data={}):
        return self.client.get(self.url, content_type='text/xml')

    def _post(self, data={}):
        return self.client.post(self.url, data, content_type='text/xml')

    def test_view_security(self):
        """ Make sure patient import view has proper security measures """
        # create empty XML payload
        data = self._node('NewDataSet')
        data = etree.tostring(data)
        # GET method not allowed
        response = self._get(data)
        self.assertEqual(response.status_code, 405)
        # Unauthorized, requires add_patientdatapayload permission
        self.client.login(username='test', password='pass')
        response = self._post(data)
        self.assertEqual(response.status_code, 401)
        permission = Permission.objects.get(codename='add_patientdatapayload')
        self.user.user_permissions.add(permission)
        response = self._post(data)
        self.assertEqual(response.status_code, 200)

    def test_payload_patient_creation(self):
        """ Test basic import through the entire stack """
        self._authorize()
        data = {
            'Subject_Number': '000-1111',
            'Pin_Code': '1234',
            'Date_Enrolled': datetime.datetime.now().strftime('%b  %d %Y '),
            'Mobile_Number': '12223334444',
        }
        patient = self.create_xml_patient(data)
        payload = self.create_xml_payload([patient])
        response = self._post(payload)
        self.assertEqual(response.status_code, 200)
        patients = reminders.Patient.objects.all()
        self.assertEqual(patients.count(), 1)

    def test_invalid_xml(self):
        """ Invalid XML should raise a validation error """
        data = '---invalid xml data---'
        payload = reminders.PatientDataPayload.objects.create(raw_data=data)
        self.assertRaises(ValidationError, parse_payload, payload)
        payload = reminders.PatientDataPayload.objects.all()[0]
        self.assertEqual(payload.status, 'error')
        self.assertNotEqual(payload.error_message, '')

    def test_email_sent_on_failure(self):
        """ Failed XML payloads should send email to ADMINS """
        self._authorize()
        data = {
            'Subject_Number': '000-1111',
            'Pin_Code': '1234',
            'Date_Enrolled': datetime.datetime.now().strftime('%b  %d %Y '),
            'Mobile_Number': '2223334444',
        }
        patient = self.create_xml_patient(data)
        payload = self.create_xml_payload([patient])
        response = self._post(payload)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(len(mail.outbox), 1)

    def test_patient_creation(self):
        """ Test that patients get created properly """
        node = self.create_xml_patient({'Mobile_Number': '12223334444'})
        payload = self.create_payload([node])
        parse_patient(node, payload)
        payload = reminders.PatientDataPayload.objects.all()[0]
        self.assertEqual(payload.status, 'success')
        patients = reminders.Patient.objects.all()
        self.assertEqual(patients.count(), 1)
        self.assertEqual(patients[0].mobile_number, '+12223334444')
        self.assertEqual(patients[0].raw_data.pk, payload.pk)
        self.assertTrue(patients[0].contact is not None)

    def test_patient_creation_without_country_code(self):
        """ Test patients missing country code are still inserted """
        node = self.create_xml_patient({'Mobile_Number': '2223334444'})
        payload = self.create_payload([node])
        with patch_settings(COUNTRY_CODE='66', INTERNATIONAL_DIALLING_CODE='+'):
            parse_patient(node, payload)
            patients = reminders.Patient.objects.all()
            self.assertEqual(patients[0].mobile_number, '+662223334444')

    def test_invalid_patient_field(self):
        """ Invalid patient data should return a 500 status code """
        self._authorize()
        patient = self.create_xml_patient({'Mobile_Number': 'invalid'})
        payload = self.create_xml_payload([patient])
        response = self._post(payload)
        self.assertEqual(response.status_code, 500)

    def test_new_contact_association(self):
        """ Test that contacts get created for patients """
        node = self.create_xml_patient({'Mobile_Number': '12223334444',
                                        'Pin_Code': '4444'})
        payload = self.create_payload([node])
        parse_patient(node, payload)
        patient = payload.patients.all()[0]
        self.assertTrue(patient.contact is not None)
        self.assertEqual(patient.contact.phone, '+12223334444')
        self.assertEqual(patient.contact.pin, '4444')

    def test_update_contact_association(self):
        """ Test that contacts get updated for patients """
        patient1 = self.create_patient({'mobile_number': '12223334444'})
        patient2 = self.create_patient()
        subject_number = patient1.subject_number
        node = self.create_xml_patient({'Subject_Number': subject_number,
                                        'Mobile_Number': '43332221111'})
        payload = self.create_payload([node])
        parse_patient(node, payload)
        patient = payload.patients.all()[0]
        self.assertNotEqual(patient.pk, patient2.pk)
        self.assertEqual(patient.pk, patient1.pk)
        self.assertNotEqual(patient.contact.pk, patient2.contact.pk)
        self.assertEqual(patient.contact.pk, patient1.contact.pk)
        self.assertEqual(patient.mobile_number, '+43332221111')
        self.assertEqual(patient.contact.phone, '+43332221111')

    def test_multi_patient_creation(self):
        """ Test that multiple patients are inserted properly """
        node1 = self.create_xml_patient()
        node2 = self.create_xml_patient()
        node3 = self.create_xml_patient()
        payload = self.create_payload([node1, node2, node3])
        parse_payload(payload)
        payload = reminders.PatientDataPayload.objects.all()[0]
        self.assertEqual(payload.status, 'success')
        self.assertEqual(payload.patients.count(), 3)

    def test_formatted_number(self):
        """ Test that contacts get created for patients """
        node = self.create_xml_patient({'Mobile_Number': '(33)-0001112222'})
        payload = self.create_payload([node])
        parse_patient(node, payload)
        patient = payload.patients.all()[0]
        self.assertEqual(patient.contact.phone, '+330001112222')

    def test_next_visit_not_required(self):
        """ Next_Visit shoudn't be required """
        node = self.create_xml_patient({'Next_Visit': ''})
        payload = self.create_payload([node])
        parse_patient(node, payload)
        self.assertEqual(payload.patients.count(), 1)

    def test_reminder_time(self):
        """ Parse patient preferred reminder time """
        node = self.create_xml_patient({'Reminder_Time': '12:00'})
        payload = self.create_payload([node])
        parse_patient(node, payload)
        self.assertEqual(payload.patients.count(), 1)
        patient = payload.patients.all()[0]
        self.assertEqual(patient.reminder_time, datetime.time(12, 0))

    def test_reminder_time_format(self):
        """ Errors parsing Reminder_Time """
        node = self.create_xml_patient({'Reminder_Time': 'XX:XX'})
        payload = self.create_payload([node])
        self.assertRaises(ValidationError, parse_payload, payload)

    def test_reminder_time_not_required(self):
        """ Reminder_Time is not required """
        node = self.create_xml_patient({'Reminder_Time': ''})
        payload = self.create_payload([node])
        parse_patient(node, payload)
        self.assertEqual(payload.patients.count(), 1)
        patient = payload.patients.all()[0]
        self.assertFalse(patient.reminder_time)

    def test_mobile_number_not_required(self):
        """ Mobile_Number shoudn't be required """
        node = self.create_xml_patient({'Mobile_Number': ''})
        payload = self.create_payload([node])
        parse_patient(node, payload)
        self.assertEqual(payload.patients.count(), 1)


class PatientManagerTest(RemindersCreateDataTest):
    """Tests for patient manager methods"""

    def setUp(self):
        super(PatientManagerTest, self).setUp()
        self.test_patient = self.create_patient()
        self.other_patient = self.create_patient()
        self.unrelated_patient = self.create_patient()

    def test_simple_confirmed(self):
        """Basic confirmed query test."""
        appt_date = datetime.date.today()
        reminders.Patient.objects.filter(
            pk__in=[self.test_patient.pk, self.other_patient.pk]
        ).update(next_visit=appt_date)
        confirmed = self.create_confirmed_notification(self.test_patient, appt_date)
        unconfirmed = self.create_unconfirmed_notification(self.other_patient, appt_date)
        qs = reminders.Patient.objects.confirmed_for_date(appt_date)
        self.assertTrue(self.test_patient in qs)
        self.assertFalse(self.other_patient in qs)
        self.assertFalse(self.unrelated_patient in qs)

    def test_simple_unconfirmed(self):
        """Basic unconfirmed query test."""
        appt_date = datetime.date.today()
        reminders.Patient.objects.filter(
            pk__in=[self.test_patient.pk, self.other_patient.pk]
        ).update(next_visit=appt_date)
        confirmed = self.create_confirmed_notification(self.test_patient, appt_date)
        unconfirmed = self.create_unconfirmed_notification(self.other_patient, appt_date)
        qs = reminders.Patient.objects.unconfirmed_for_date(appt_date)
        self.assertFalse(self.test_patient in qs)
        self.assertTrue(self.other_patient in qs)
        self.assertFalse(self.unrelated_patient in qs)

    def test_multiple_notifications_confirmed(self):
        """Confirmed patients returned should be distinct."""
        appt_date = datetime.date.today()
        self.test_patient.next_visit = appt_date
        self.test_patient.save()
        confirmed = self.create_confirmed_notification(self.test_patient, appt_date)
        confirmed_again = self.create_confirmed_notification(self.test_patient, appt_date)
        qs = reminders.Patient.objects.confirmed_for_date(appt_date)
        self.assertTrue(self.test_patient in qs)
        self.assertTrue(qs.count(), 1)

    def test_multiple_notifications_unconfirmed(self):
        """Unconfirmed patients returned should be distinct."""
        appt_date = datetime.date.today()
        self.test_patient.next_visit = appt_date
        self.test_patient.save()
        notified = self.create_unconfirmed_notification(self.test_patient, appt_date)
        notified_again = self.create_unconfirmed_notification(self.test_patient, appt_date)
        qs = reminders.Patient.objects.unconfirmed_for_date(appt_date)
        logging.debug(qs)
        self.assertTrue(self.test_patient in qs)
        self.assertTrue(qs.count(), 1)

    def test_mixed_messages_confirmed(self):
        """Only need to confirm once to be considered confirmed."""
        appt_date = datetime.date.today()
        self.test_patient.next_visit = appt_date
        self.test_patient.save()
        notified = self.create_unconfirmed_notification(self.test_patient, appt_date)
        confirmed = self.create_confirmed_notification(self.test_patient, appt_date)
        notified_again = self.create_unconfirmed_notification(self.test_patient, appt_date)
        qs = reminders.Patient.objects.confirmed_for_date(appt_date)
        self.assertTrue(self.test_patient in qs)
        self.assertTrue(qs.count(), 1)


class DailyReportTest(FlushTestScript, RemindersCreateDataTest):

    def setUp(self):
        super(DailyReportTest, self).setUp()
        group_name = settings.DEFAULT_DAILY_REPORT_GROUP_NAME
        self.group = self.create_group(data={'name': group_name})
        self.test_contact = self.create_contact(data={'email': 'test@example.com'})
        self.group.contacts.add(self.test_contact)
        self.test_patient = self.create_patient()
        self.other_patient = self.create_patient()
        self.unrelated_patient = self.create_patient()

    def assertPatientInMessage(self, message, patient):
        self.assertTrue(patient.subject_number in message.body)

    def assertPatientNotInMessage(self, message, patient):
        self.assertFalse(patient.subject_number in message.body)

    def test_sending_mail(self):
        """Test email goes out the contacts in the daily report group."""

        appt_date = datetime.date.today() + datetime.timedelta(days=7) # Default for email
        reminders.Patient.objects.filter(
            pk__in=[self.test_patient.pk, self.other_patient.pk]
        ).update(next_visit=appt_date)
        confirmed = self.create_confirmed_notification(self.test_patient, appt_date)

        self.startRouter()
        self.router.logger.setLevel(logging.DEBUG)

        # run email job
        from afrims.apps.reminders.app import daily_email_callback
        daily_email_callback(self.router)

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertTrue(self.test_contact.email in message.to)
        self.stopRouter()


    def test_appointment_date(self):
        """Test email contains info for the appointment date."""
        appt_date = datetime.date.today() + datetime.timedelta(days=7) # Default for email
        reminders.Patient.objects.filter(
            pk__in=[self.test_patient.pk, self.other_patient.pk]
        ).update(next_visit=appt_date)
        confirmed = self.create_confirmed_notification(self.test_patient, appt_date)
        unconfirmed = self.create_unconfirmed_notification(self.other_patient, appt_date)

        self.startRouter()
        self.router.logger.setLevel(logging.DEBUG)

        # run email job
        from afrims.apps.reminders.app import daily_email_callback
        daily_email_callback(self.router)

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertPatientInMessage(message, self.test_patient)
        self.assertPatientInMessage(message, self.other_patient)
        self.assertPatientNotInMessage(message, self.unrelated_patient)
        self.stopRouter()

    def test_changing_date(self):
        """Test changing appointment date via callback kwarg."""
        days = 2
        appt_date = datetime.date.today() + datetime.timedelta(days=days)
        reminders.Patient.objects.filter(
            pk__in=[self.test_patient.pk, self.other_patient.pk]
        ).update(next_visit=appt_date)
        confirmed = self.create_confirmed_notification(self.test_patient, appt_date)
        unconfirmed = self.create_unconfirmed_notification(self.other_patient, appt_date)

        self.startRouter()
        self.router.logger.setLevel(logging.DEBUG)

        # run email job
        from afrims.apps.reminders.app import daily_email_callback
        daily_email_callback(self.router, days=days)

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertPatientInMessage(message, self.test_patient)
        self.assertPatientInMessage(message, self.other_patient)
        self.assertPatientNotInMessage(message, self.unrelated_patient)
        self.stopRouter()

    def test_skip_blank_emails(self):
        """Test handling contacts with blank/null email addresses."""
        appt_date = datetime.date.today() + datetime.timedelta(days=7) # Default for email
        reminders.Patient.objects.filter(
            pk__in=[self.test_patient.pk, self.other_patient.pk]
        ).update(next_visit=appt_date)
        confirmed = self.create_confirmed_notification(self.test_patient, appt_date)
        blank_contact = self.create_contact(data={'email': ''})
        null_contact = self.create_contact(data={'email': None})
        self.group.contacts.add(blank_contact)
        self.group.contacts.add(null_contact)

        self.startRouter()
        self.router.logger.setLevel(logging.DEBUG)
        # run email job
        from afrims.apps.reminders.app import daily_email_callback
        daily_email_callback(self.router)

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(len(message.to), 1)
        self.stopRouter()

    def test_skip_if_no_patients(self):
        """Skip sending the email if there are not patients for this date."""

        appt_date = datetime.date.today() + datetime.timedelta(days=5)
        reminders.Patient.objects.filter(
            pk__in=[self.test_patient.pk, self.other_patient.pk]
        ).update(next_visit=appt_date)
        confirmed = self.create_confirmed_notification(self.test_patient, appt_date)

        self.startRouter()
        self.router.logger.setLevel(logging.DEBUG)
        # run email job
        from afrims.apps.reminders.app import daily_email_callback
        daily_email_callback(self.router)

        self.assertEqual(len(mail.outbox), 0)
        self.stopRouter()


class ManualConfirmationTest(RemindersCreateDataTest):

    def setUp(self):
        self.user = User.objects.create_user('test', 'a@b.com', 'abc')
        perm = Permission.objects.get(codename='can_use_appointment_reminders_tab')
        self.user.user_permissions.add(perm)
        self.user.save()
        self.client.login(username='test', password='abc')
        self.test_patient = self.create_patient()
        self.appt_date = datetime.date.today()
        self.unconfirmed = self.create_unconfirmed_notification(self.test_patient, self.appt_date)
        self.url = reverse('manually-confirm-patient', args=[self.unconfirmed.pk])

    def test_get_page(self):
        """Get manual confirmation page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_manually_confirm(self):
        """Test manually confirming a patient reminder."""
        data = {}
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('reminders_dashboard'))

        reminder = reminders.SentNotification.objects.get(pk=self.unconfirmed.pk)
        self.assertEqual(reminder.status, 'manual')
        self.assertEqual(reminder.date_confirmed.date(), datetime.date.today())

    def test_redirect(self):
        """Test post redirect."""
        next_url = reverse('reminders-report')
        data = {'next': next_url}
        response = self.client.post(self.url, data)
        self.assertRedirects(response, next_url)

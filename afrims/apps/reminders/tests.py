"""
Tests for the appointment reminders app.
"""

import datetime
import logging
import random
from lxml import etree

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Permission
from django.core.exceptions import ValidationError

from rapidsms.tests.harness import MockRouter, MockBackend
from rapidsms.messages.incoming import IncomingMessage
from rapidsms.messages.outgoing import OutgoingMessage

from afrims.apps.reminders import models as reminders
from afrims.tests.testcases import CreateDataTest, FlushTestScript
from afrims.apps.reminders.app import RemindersApp
from afrims.apps.reminders.importer import parse_payload, parse_patient


class RemindersCreateDataTest(CreateDataTest):
    # add reminders-specific create_* methods here as needed

    def _node(self, name, value=None):
        element = etree.Element(name)
        if value:
            element.text = value
        return element

    def create_xml_patient(self, data={}):
        """
        <Table>
            <Subject_Number>xxx-nnnnn</Subject_Number>
            <Date_Enrolled>Mar  8 2011 </Date_Enrolled>
            <Mobile_Number>08-11111111</Mobile_Number>
            <Pin_Code>1234</Pin_Code>
            <Next_Visit>Apr  7 2011 </Next_Visit>
        </Table>
        """
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

    def create_patient(self, data={}):
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
            u'form-0-time_of_day': u'12:00',
            u'form-0-recipients': u'all',
            u'form-1-num_days': u'11',
            u'form-1-time_of_day': u'15:00:00',
            u'form-1-recipients': u'all',
            u'form-2-num_days': u'',
            u'form-2-recipients': u'all',
        }
        response = self.client.post(reminders_dash, post_data)
        self.assertRedirects(response, reminders_dash)
        self.assertEqual(reminders.Notification.objects.count(), 2)


class RemindersConfirmHandlerTest(RemindersCreateDataTest):

    def setUp(self):
        self.contact = self.create_contact()
        self.backend = self.create_backend(data={'name': 'mockbackend'})
        self.unreg_conn = self.create_connection({'backend': self.backend})
        self.reg_conn = self.create_connection({'contact': self.contact,
                                                'backend': self.backend})
        self.router = MockRouter()
        self.app = RemindersApp(router=self.router)

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

    def test_patient_creation(self):
        """ Test that patients get created properly """
        node = self.create_xml_patient({'Mobile_Number': '12223334444'})
        payload = self.create_payload([node])
        parse_patient(node, payload)
        payload = reminders.PatientDataPayload.objects.all()[0]
        self.assertEqual(payload.status, 'success')
        patients = reminders.Patient.objects.all()
        self.assertEqual(patients.count(), 1)
        self.assertEqual(patients[0].mobile_number, '12223334444')
        self.assertEqual(patients[0].raw_data.pk, payload.pk)
        self.assertTrue(patients[0].contact is not None)

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
        self.assertEqual(patient.contact.phone, '12223334444')
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
        self.assertEqual(patient.mobile_number, '43332221111')
        self.assertEqual(patient.contact.phone, '43332221111')

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
        self.assertEqual(patient.contact.phone, '330001112222')

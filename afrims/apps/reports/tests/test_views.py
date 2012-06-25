import datetime

from django.core.urlresolvers import reverse
from django.utils import simplejson as json

from rapidsms.models import Contact

from afrims.apps.broadcast.tests import BroadcastCreateDataTest
from afrims.apps.reminders.tests import RemindersCreateDataTest
from afrims.apps.reports import views 


class ReportDataTest(BroadcastCreateDataTest, RemindersCreateDataTest):
    "Base test class for creating necessary data."

    def setUp(self):
        # Create some base initial data
        self.test_staff = self.create_contact()
        self.test_patient = self.create_patient()


class MessageStatsTest(ReportDataTest):
    "Aggregate messages by direction with applied filters."

    def test_all_messages(self):
        "All messages collected by direction."
        self.create_message(data={'direction': 'I'})
        self.create_message(data={'direction': 'I'})
        self.create_message(data={'direction': 'O'})
        results = views.messages_by_direction()
        self.assertEqual(results['incoming'], 2)
        self.assertEqual(results['outgoing'], 1)

    def test_staff_messages(self):
        "Filter messages sent to or from staff members."
        self.create_message(data={'direction': 'I', 'contact': self.test_staff})
        self.create_message(data={'direction': 'I', 'contact': self.test_patient.contact})
        self.create_message(data={'direction': 'O', 'contact': self.test_staff})
        staff_filter = {'contact__in': Contact.objects.filter(patient__isnull=True)}
        results = views.messages_by_direction(filters=staff_filter)
        self.assertEqual(results['incoming'], 1)
        self.assertEqual(results['outgoing'], 1)

    def test_patient_messages(self):
        "Filter messages sent to or from staff members."
        self.create_message(data={'direction': 'I', 'contact': self.test_staff})
        self.create_message(data={'direction': 'I', 'contact': self.test_patient.contact})
        self.create_message(data={'direction': 'O', 'contact': self.test_staff})
        patient_filter = {'contact__in': Contact.objects.filter(patient__isnull=False)}
        results = views.messages_by_direction(filters=patient_filter)
        self.assertEqual(results['incoming'], 1)
        self.assertFalse('outgoing' in results)

    def test_date_filter(self):
        "Filter messages in the same month as a given date."
        today = datetime.datetime.now()
        last_month = today - datetime.timedelta(days=today.day + 1)
        self.create_message(data={'direction': 'I', 'date': last_month})
        self.create_message(data={'direction': 'I'})
        self.create_message(data={'direction': 'O'})
        results = views.messages_by_direction(day=today)
        self.assertEqual(results['incoming'], 1)
        self.assertEqual(results['outgoing'], 1)
        results = views.messages_by_direction(day=last_month)
        self.assertEqual(results['incoming'], 1)
        self.assertFalse('outgoing' in results)


class AppointmentStatsTest(ReportDataTest):
    "Appointment statistics by month or to date."

    def test_appointments_to_date(self):
        "Aggregrate appointment stats to date."
        today = datetime.datetime.now()
        self.create_confirmed_notification(patient=self.test_patient, appt_date=today)
        self.create_confirmed_notification(patient=self.test_patient, appt_date=today + datetime.timedelta(days=1))
        self.create_confirmed_notification(patient=self.test_patient, appt_date=today + datetime.timedelta(days=2))
        self.create_unconfirmed_notification(patient=self.test_patient, appt_date=today + datetime.timedelta(days=3))
        results = views.appointment_stats()
        self.assertEqual(results['total'], 4)
        self.assertEqual(results['confirmed'], 3)
        self.assertAlmostEqual(results['percent'], 75.0)

    def test_no_appointments(self):
        "Handle no appointments for the given range."
        results = views.appointment_stats()
        self.assertEqual(results['total'], 0)
        self.assertEqual(results['confirmed'], 0)
        self.assertAlmostEqual(results['percent'], 0.0)

    def test_multiple_reminders(self):
        "Don't double count reminders for the same appointment date."
        today = datetime.datetime.now()
        # Today's appointment is both confirmed and unconfirmed
        self.create_confirmed_notification(patient=self.test_patient, appt_date=today)
        self.create_unconfirmed_notification(patient=self.test_patient, appt_date=today)
        self.create_confirmed_notification(patient=self.test_patient, appt_date=today + datetime.timedelta(days=1))
        self.create_confirmed_notification(patient=self.test_patient, appt_date=today + datetime.timedelta(days=2))
        self.create_unconfirmed_notification(patient=self.test_patient, appt_date=today + datetime.timedelta(days=3))
        results = views.appointment_stats()
        self.assertEqual(results['total'], 4)
        self.assertEqual(results['confirmed'], 3)
        self.assertAlmostEqual(results['percent'], 75.0)

    def test_date_filtered(self):
        "Restrict report to dates in a given month."
        today = datetime.datetime.now()
        last_month = today - datetime.timedelta(days=today.day + 1)
        self.create_confirmed_notification(patient=self.test_patient, appt_date=today)
        self.create_confirmed_notification(patient=self.test_patient, appt_date=last_month)
        self.create_confirmed_notification(patient=self.test_patient, appt_date=today + datetime.timedelta(days=2))
        self.create_unconfirmed_notification(patient=self.test_patient, appt_date=today + datetime.timedelta(days=3))
        results = views.appointment_stats(today)
        self.assertEqual(results['total'], 3)
        self.assertEqual(results['confirmed'], 2)
        self.assertAlmostEqual(results['percent'], 66.666666666666)
        results = views.appointment_stats(last_month)
        self.assertEqual(results['total'], 1)
        self.assertEqual(results['confirmed'], 1)
        self.assertAlmostEqual(results['percent'], 100.0)


class ReminderStatsTest(ReportDataTest):
    "Reminder statistics by month or to date."

    def test_reminders_to_date(self):
        "Aggregrate reminder stats to date."
        today = datetime.datetime.now()
        self.create_confirmed_notification(patient=self.test_patient, appt_date=today)
        self.create_confirmed_notification(patient=self.test_patient, appt_date=today + datetime.timedelta(days=1))
        self.create_confirmed_notification(patient=self.test_patient, appt_date=today + datetime.timedelta(days=2))
        self.create_unconfirmed_notification(patient=self.test_patient, appt_date=today + datetime.timedelta(days=3))
        results = views.reminder_stats()
        self.assertEqual(results['total'], 4)
        self.assertEqual(results['confirmed'], 3)
        self.assertAlmostEqual(results['percent'], 75.0)

    def test_no_reminders(self):
        "Handle no reminders for the given range."
        results = views.reminder_stats()
        self.assertEqual(results['total'], 0)
        self.assertEqual(results['confirmed'], 0)
        self.assertAlmostEqual(results['percent'], 0.0)

    def test_multiple_reminders(self):
        "Multiple reminders per appointment date should be counted separately."
        today = datetime.datetime.now()
        # Today's appointment is both confirmed and unconfirmed
        self.create_confirmed_notification(patient=self.test_patient, appt_date=today)
        self.create_unconfirmed_notification(patient=self.test_patient, appt_date=today)
        self.create_confirmed_notification(patient=self.test_patient, appt_date=today + datetime.timedelta(days=1))
        self.create_confirmed_notification(patient=self.test_patient, appt_date=today + datetime.timedelta(days=2))
        self.create_unconfirmed_notification(patient=self.test_patient, appt_date=today + datetime.timedelta(days=3))
        results = views.reminder_stats()
        self.assertEqual(results['total'], 5)
        self.assertEqual(results['confirmed'], 3)
        self.assertAlmostEqual(results['percent'], 60.0)

    def test_date_filtered(self):
        "Restrict report to dates in a given month."
        today = datetime.datetime.now()
        last_month = today - datetime.timedelta(days=today.day + 1)
        self.create_confirmed_notification(patient=self.test_patient, appt_date=today)
        self.create_confirmed_notification(patient=self.test_patient, appt_date=last_month)
        self.create_confirmed_notification(patient=self.test_patient, appt_date=today + datetime.timedelta(days=2))
        self.create_unconfirmed_notification(patient=self.test_patient, appt_date=today + datetime.timedelta(days=3))
        results = views.reminder_stats(today)
        self.assertEqual(results['total'], 3)
        self.assertEqual(results['confirmed'], 2)
        self.assertAlmostEqual(results['percent'], 66.666666666666)
        results = views.reminder_stats(last_month)
        self.assertEqual(results['total'], 1)
        self.assertEqual(results['confirmed'], 1)
        self.assertAlmostEqual(results['percent'], 100.0)


class UserStatsTest(ReportDataTest):
    "User statistics by month or to date."

    def test_all_users(self):
        "Get staff/patient breakdown to date."
        results = views.user_stats()
        self.assertEqual(results['total'], 2)
        self.assertEqual(results['patients'], 1)
        self.assertEqual(results['staff'], 1)

    def test_date_filtered_no_messages(self):
        "No one is active if there are no incoming messages."
        today = datetime.datetime.now()
        results = views.user_stats(day=today)
        self.assertEqual(results['total'], 0)
        self.assertEqual(results['patients'], 0)
        self.assertEqual(results['staff'], 0)

    def test_date_filtered(self):
        "Filter users who were active in a given month. Sent message within 90 days."
        self.create_message(data={'direction': 'I', 'contact': self.test_staff})
        self.create_message(data={'direction': 'I', 'contact': self.test_patient.contact})
        today = datetime.datetime.now()
        ninety_days_ago = today - datetime.timedelta(days=90)
        inactive_staff = self.create_contact()
        self.create_message(data={'direction': 'I', 'contact': inactive_staff, 'date': ninety_days_ago - datetime.timedelta(days=3)})        
        results = views.user_stats(day=today)
        self.assertEqual(results['total'], 2)
        self.assertEqual(results['patients'], 1)
        self.assertEqual(results['staff'], 1)


class BroadcastStatsTest(ReportDataTest):
    "Broadcast message usage statistics by month or to date."

    def setUp(self):
        super(BroadcastStatsTest, self).setUp()
        # Create the Cold Chain and Callback request forwarding rules
        self.coldchain = self.create_forwarding_rule(data={
            'rule_type': 'Cold Chain',
            'label': 'Cold Chain Alert',
        })
        self.callback = self.create_forwarding_rule(data={
            'rule_type': 'Subject',
            'label': 'Callback Request',
        })

    def create_broadcast_message(self, data=None):
        data = data or {}
        defaults = {
            'date_sent': datetime.datetime.now(),
            'status': 'sent',
        }
        defaults.update(data)
        return super(BroadcastStatsTest, self).create_broadcast_message(data=defaults)

    def test_all_broadcasts(self):
        "Current broadcast usage to date."
        self.create_broadcast_message(data={'recipient': self.test_staff})
        self.create_broadcast_message(data={'recipient': self.test_staff})
        self.create_broadcast_message(data={'recipient': self.test_patient.contact})
        results = views.broadcast_stats()
        self.assertEqual(results['total'], 3)
        self.assertEqual(results['patients'], 1)
        self.assertEqual(results['staff'], 2)
        self.assertEqual(results['callbacks'], 0)
        self.assertEqual(results['coldchain'], 0)

    def test_all_callbacks(self):
        "Count callback requests."
        # Callbacks are as one-time broadcasts which have null frequency once they are sent
        broadcast = self.create_broadcast(data={'forward': self.callback, 'schedule_frequency': None})
        self.create_broadcast_message(data={'recipient': self.test_staff, 'broadcast': broadcast})
        self.create_broadcast_message(data={'recipient': self.test_staff})
        self.create_broadcast_message(data={'recipient': self.test_patient.contact})
        self.create_broadcast_message(data={'recipient': self.test_patient.contact, 'broadcast': broadcast})
        results = views.broadcast_stats()
        self.assertEqual(results['total'], 4)
        self.assertEqual(results['patients'], 2)
        self.assertEqual(results['staff'], 2)
        self.assertEqual(results['callbacks'], 2)
        self.assertEqual(results['coldchain'], 0)

    def test_all_coldchain(self):
        "Count cold chain forwards."
        # Cold chains are as one-time broadcasts which have null frequency once they are sent
        broadcast = self.create_broadcast(data={'forward': self.coldchain, 'schedule_frequency': None})
        self.create_broadcast_message(data={'recipient': self.test_staff, 'broadcast': broadcast})
        self.create_broadcast_message(data={'recipient': self.test_staff})
        self.create_broadcast_message(data={'recipient': self.test_patient.contact})
        results = views.broadcast_stats()
        self.assertEqual(results['total'], 3)
        self.assertEqual(results['patients'], 1)
        self.assertEqual(results['staff'], 2)
        self.assertEqual(results['callbacks'], 0)
        self.assertEqual(results['coldchain'], 1)

    def test_broadcasts_by_date(self):
        "Filter broadcasts to a given month."
        today = datetime.datetime.now()
        last_month = today - datetime.timedelta(days=today.day + 1)
        self.create_broadcast_message(data={'recipient': self.test_staff, 'date_sent': last_month})
        self.create_broadcast_message(data={'recipient': self.test_staff})
        self.create_broadcast_message(data={'recipient': self.test_patient.contact})
        results = views.broadcast_stats(day=today)
        self.assertEqual(results['total'], 2)
        self.assertEqual(results['patients'], 1)
        self.assertEqual(results['staff'], 1)
        results = views.broadcast_stats(day=last_month)
        self.assertEqual(results['total'], 1)
        self.assertEqual(results['patients'], 0)
        self.assertEqual(results['staff'], 1)

    def test_callbacks_by_date(self):
        "Filter callback requests to a given month."
        today = datetime.datetime.now()
        last_month = today - datetime.timedelta(days=today.day + 1)
        broadcast = self.create_broadcast(data={'forward': self.callback, 'schedule_frequency': None})
        self.create_broadcast_message(data={
            'recipient': self.test_staff, 'broadcast': broadcast, 'date_sent': last_month
        })
        self.create_broadcast_message(data={'recipient': self.test_staff})
        results = views.broadcast_stats(day=today)
        self.assertEqual(results['total'], 1)
        self.assertEqual(results['patients'], 0)
        self.assertEqual(results['staff'], 1)
        self.assertEqual(results['callbacks'], 0)
        results = views.broadcast_stats(day=last_month)
        self.assertEqual(results['total'], 1)
        self.assertEqual(results['patients'], 0)
        self.assertEqual(results['staff'], 1)
        self.assertEqual(results['callbacks'], 1)

    def test_coldchain_by_date(self):
        "Filter coldchain requests to a given month."
        today = datetime.datetime.now()
        last_month = today - datetime.timedelta(days=today.day + 1)
        broadcast = self.create_broadcast(data={'forward': self.coldchain, 'schedule_frequency': None})
        self.create_broadcast_message(data={
            'recipient': self.test_staff, 'broadcast': broadcast, 'date_sent': last_month
        })
        self.create_broadcast_message(data={'recipient': self.test_staff})
        results = views.broadcast_stats(day=today)
        self.assertEqual(results['total'], 1)
        self.assertEqual(results['patients'], 0)
        self.assertEqual(results['staff'], 1)
        self.assertEqual(results['coldchain'], 0)
        results = views.broadcast_stats(day=last_month)
        self.assertEqual(results['total'], 1)
        self.assertEqual(results['patients'], 0)
        self.assertEqual(results['staff'], 1)
        self.assertEqual(results['coldchain'], 1)

    def test_queued_messages(self):
        "Don't count messages which haven't been sent."
        self.create_broadcast_message(data={'recipient': self.test_staff, 'status': 'queued'})
        self.create_broadcast_message(data={'recipient': self.test_staff})
        self.create_broadcast_message(data={'recipient': self.test_patient.contact})
        results = views.broadcast_stats()
        self.assertEqual(results['total'], 2)
        self.assertEqual(results['patients'], 1)
        self.assertEqual(results['staff'], 1)


class BaseGraphViewTest(ReportDataTest):
    "Base test case for testing graph data AJAX views."

    url_name = ''

    def setUp(self):
        super(BaseGraphViewTest, self).setUp()
        # Create a super user
        username = 'super'
        password = 'abc'
        self.user = self.create_user(data={'username': username, 'password': password})
        self.user.is_superuser = True        
        self.user.save()
        self.client.login(username=username, password=password)
        self.url = reverse(self.url_name)

    def get(self, *args, **kwargs):
        "Wrapper around client.get to load json data."
        response = self.client.get(*args, **kwargs)
        return json.loads(response.content)


class ReminderGraphViewTest(BaseGraphViewTest):
    "View for generating data for the reminder usage graph."

    url_name = 'report-reminder-usage'

    def test_data_to_date(self):
        "Without giving a range will return the totals to date."
        results = self.get(self.url)
        self.assertTrue('to_date' in results)


class UsageGraphViewTest(BaseGraphViewTest):
    "View for generating data for the system usage graphs."

    url_name = 'report-system-usage'

    def test_data_to_date(self):
        "Without giving a range will return the totals to date."
        results = self.get(self.url)
        self.assertTrue('to_date' in results)

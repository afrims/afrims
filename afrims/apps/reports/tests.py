import datetime

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


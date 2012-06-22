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

"""
Tests for the Catch All app.
"""

import datetime
import logging

from rapidsms.tests.harness import MockRouter
from rapidsms.messages.incoming import IncomingMessage
from rapidsms.apps.base import AppBase

from afrims.tests.testcases import CreateDataTest, FlushTestScript

from afrims.apps.catch_all.app import CatchAllApp
from afrims.apps.reminders import models as reminders
from afrims.apps.reminders.tests import RemindersCreateDataTest

class OtherApp(AppBase):

    name = 'other-app'

    def handle(self, msg):
        if msg.text == 'other-app-should-catch':
            msg.respond('caught')
            return True


class CatchAllDefaultTest(CreateDataTest):

    def setUp(self):
        self.router = MockRouter()
        self.app = CatchAllApp(router=self.router)

    def _send(self, conn, text):
        msg = IncomingMessage(conn, text)
        self.app.default(msg)
        return msg

    def test_unhandled_incoming_message(self):
        """ The catch_all app should always reply """
        connection = self.create_connection()
        msg = self._send(connection, 'uncaught-message-test')
        self.assertEqual(len(msg.responses), 1)
        self.assertEqual(msg.responses[0].text, self.app.non_patient_template)


class CatchAllTest(FlushTestScript):

    def test_full_stack(self):
        """ Test catch all functionality alongside other apps """
        self.router.apps = [OtherApp(self.router), CatchAllApp(self.router)]
        self.startRouter()
        self.router.logger.setLevel(logging.DEBUG)
        self.runScript("""1112223333 > other-app-should-catch
                          1112223333 < caught
                          1112223333 > uncaught-message-test
                          1112223333 < %s""" % CatchAllApp.non_patient_template)
        self.stopRouter()

class PatientStrangeMessageTest(FlushTestScript, RemindersCreateDataTest):

    def test_patient_bad_message_response(self):
        app = CatchAllApp(self.router)
        contact = self.create_contact({'pin': '1234'})
        backend = self.create_backend(data={'name': 'mockbackend'})
        connection = self.create_connection({'contact': contact,
                                             'backend': backend})
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        reminders.Patient.objects.create(contact=contact,
                                         date_enrolled=datetime.date.today(),
                                         subject_number='1234',
                                         mobile_number='tester',
                                         next_visit=tomorrow)

        text = "Strange message"
        msg = IncomingMessage(connection, text)

        app.default(msg)
        self.assertEquals(len(msg.responses), 1)
        self.assertEquals(msg.responses[0].text, CatchAllApp.patient_template)

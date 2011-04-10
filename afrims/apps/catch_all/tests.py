"""
Tests for the Catch All app.
"""

import logging

from rapidsms.tests.harness import MockRouter
from rapidsms.messages.incoming import IncomingMessage
from rapidsms.apps.base import AppBase

from afrims.tests.testcases import CreateDataTest, FlushTestScript

from afrims.apps.catch_all.app import CatchAllApp


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
        self.assertEqual(msg.responses[0].text, self.app.template)


class CatchAllTest(FlushTestScript):

    apps = [OtherApp, CatchAllApp]

    def test_full_stack(self):
        """ Test catch all functionality alongside other apps """
        self.runScript("""1112223333 > other-app-should-catch
                          1112223333 < caught
                          1112223333 > uncaught-message-test
                          1112223333 > %s""" % CatchAllApp.template)

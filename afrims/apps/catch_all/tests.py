"""
Tests for the Catch All app.
"""

from rapidsms.tests.harness import MockRouter
from rapidsms.messages.incoming import IncomingMessage

from afrims.tests.testcases import CreateDataTest

from afrims.apps.catch_all.app import CatchAllApp


class CatchAllTest(CreateDataTest):

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

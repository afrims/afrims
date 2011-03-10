"""
Tests for the pincode app.
"""

import datetime
import logging

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from rapidsms.tests.scripted import TestScript
from rapidsms.tests.harness import MockRouter, MockBackend
from rapidsms.messages.incoming import IncomingMessage
from rapidsms.messages.outgoing import OutgoingMessage

from afrims.apps.pincode import models as pincode
from afrims.tests.testcases import CreateDataTest
from afrims.apps.pincode.app import PinCodeApp
from afrims.apps.pincode.messages import PinVerifiedOutgoingMessage


class PinCodeCreateDataTest(CreateDataTest):
    # add pincode-specific create_* methods here as needed
    pass


class PinCodeTest(PinCodeCreateDataTest):

    def setUp(self):
        self.contact_pin = self.create_contact({'pin': '1234'})
        self.contact_nopin = self.create_contact()
        self.backend = self.create_backend(data={'name': 'mockbackend'})
        self.unreg_conn = self.create_connection({'backend': self.backend})
        self.reg_conn_nopin = self.create_connection({'contact': self.contact_nopin,
                                                      'backend': self.backend})
        self.reg_conn_pin = self.create_connection({'contact': self.contact_pin,
                                                    'backend': self.backend})
        self.router = MockRouter()
        self.app = PinCodeApp(router=self.router)

    def _send(self, conn, text):
        msg = IncomingMessage(conn, text)
        self.app.handle(msg)
        return msg

    def test_unregistered(self):
        """
        Tests the response from an unregistered user.
        """
        msg = self._send(self.unreg_conn, '1111')
        self.assertEqual(len(msg.responses), 1)
        self.assertEqual(msg.responses[0].text,
                         self.app.no_pin)

    def test_registered_no_pin(self):
        """
        Tests the response from a registered user without a PIN.
        """
        msg = self._send(self.reg_conn_nopin, '1111')
        self.assertEqual(len(msg.responses), 1)
        self.assertEqual(msg.responses[0].text,
                         self.app.no_pin)

    def test_registered_incorrect_pin(self):
        """
        Tests the response from a registered user with a PIN, when an invalid
        PIN is supplied.
        """
        msg = self._send(self.reg_conn_pin, '1111')
        self.assertEqual(len(msg.responses), 1)
        self.assertEqual(msg.responses[0].text,
                         self.app.incorrect_pin)

    def test_registered_correct_pin_no_msgs(self):
        """
        Tests the response from a registered user with a PIN, when an valid
        PIN is supplied but no messages are waiting.
        """
        msg = self._send(self.reg_conn_pin, '1234')
        self.assertEqual(len(msg.responses), 1)
        self.assertEqual(msg.responses[0].text,
                         self.app.no_messages)

    def test_registered_correct_pin_with_msg(self):
        """
        Tests the response from a registered user with a PIN, when an valid
        PIN is supplied but no messages are waiting.
        """
        now = datetime.datetime.now()
        private_msg = pincode.OutgoingMessage.objects.create(
                                                  connection=self.reg_conn_pin,
                                                  text='private msg',
                                                  date_queued=now,
                                                  status='queued')
        msg = self._send(self.reg_conn_pin, '1234')
        self.assertEqual(len(msg.responses), 1)
        self.assertEqual(msg.responses[0].text,
                         private_msg.text)


class RemindersScriptedTest(TestScript, PinCodeCreateDataTest):
        
    def test_send_msg_nopin(self):
        """
        Tests that PinVerifiedOutgoingMessage properly queues outgoing messages
        in the database when the contact has a PIN set.
        """
        self.startRouter()
        self.router.logger.setLevel(logging.DEBUG)
        contact = self.create_contact({'pin': '1234', 'first_name': 'John',
                                       'last_name': 'Smith'})
        backend = self.create_backend(data={'name': 'mockbackend'})
        connection = self.create_connection({'contact': contact,
                                             'backend': backend})
        msg = PinVerifiedOutgoingMessage(connection=connection,
                                         template='private message')
        msg.send()
        sent_messages = self.receiveAllMessages()
        self.assertEqual(len(sent_messages), 1)
        pin_reqrd_msg = PinVerifiedOutgoingMessage.pin_reqrd_msg
        self.assertEqual(sent_messages[0].text,
                         pin_reqrd_msg.format(name='John Smith'))
        self.assertEqual(pincode.OutgoingMessage.objects.count(), 1)
        queued_msg = pincode.OutgoingMessage.objects.all()[0]
        self.assertEqual(queued_msg.text, 'private message')
        self.stopRouter()

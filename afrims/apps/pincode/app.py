import datetime
import re

from rapidsms.apps.base import AppBase
from rapidsms.messages import OutgoingMessage
from rapidsms.contrib.scheduler.models import EventSchedule

from afrims.apps.pincode import models as pincode

# In RapidSMS, message translation is done in OutgoingMessage, so no need
# to attempt the real translation here.  Use _ so that ./manage.py makemessages
# finds our text.
_ = lambda s: s


class PinCodeApp(AppBase):
    """ RapidSMS app to verify outgoing messages with a pin code """

    pin_regex = re.compile(r'^\d{4,6}$')
    no_pin = _('You do not have a PIN registered on your account.')
    incorrect_pin = _('That is not your PIN code. Please reply with the '
                      'correct PIN code.')
    no_messages = _('You do not have any messages at this time.')

    def handle(self, msg):
        """
        Handles messages that look like a PIN code, and sends out any pending
        messages for that connection.
        """
        msg_parts = msg.text.split()
        if not msg_parts:
            return False
        pin = msg_parts[0]
        contact = msg.connection.contact
        if not contact or not contact.pin:
            msg.respond(self.no_pin)
            return True
        if contact.pin != pin:
            msg.respond(self.incorrect_pin)
            return True
        pending_msgs = pincode.OutgoingMessage.objects.filter(
                                                     connection=msg.connection)
        if not pending_msgs.exists():
            msg.respond(self.no_messages)
            return True
        for pending_msg in pending_msgs:
            msg.respond(pending_msg.text)
            pending_msg.status = 'sent'
            pending_msg.date_sent = datetime.datetime.now()
            pending_msg.save()

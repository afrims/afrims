import datetime

from rapidsms.messages.outgoing import OutgoingMessage

from afrims.apps.pincode import models as pincode

# In RapidSMS, message translation is done in OutgoingMessage, so no need
# to attempt the real translation here.  Use _ so that ./manage.py makemessages
# finds our text.
_ = lambda s: s

class PinVerifiedOutgoingMessage(OutgoingMessage):
    """
    Extension of the RapidSMS OutgoingMessage class that verifies a PIN code,
    if available, with the remote contact before delivering the original
    message.
    """

    pin_reqrd_msg = _('Hello, {name}. You have a new message waiting. Please '
                      'reply with your pin code to view it.')

    def send(self):
        # we can only verify the PIN if the connection has an associated
        # contact with a PIN set
        if self.connection and self.connection.contact and \
          self.connection.contact.pin:
            # queue up the original message for delivery upon PIN entry
            now = datetime.datetime.now()
            pincode.OutgoingMessage.objects.create(connection=self.connection,
                                                   text=self.text,
                                                   status='queued',
                                                   date_queued=now)
            # erase the original and add the "pin required" message
            self._parts = []
            name = self.connection.contact.name
            self.append(self.pin_reqrd_msg.format(name=name))
        super(PinVerifiedOutgoingMessage, self).send()

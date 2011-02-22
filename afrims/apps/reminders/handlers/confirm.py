import datetime

from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler

from afrims.apps.reminders import models as reminders

# In RapidSMS, message translation is done in OutgoingMessage, so no need
# to attempt the real translation here.  Use _ so that ./manage.py makemessages
# finds our text.
_ = lambda s: s


class ConfirmHandler(KeywordHandler):
    """
    Simple keyword handler that updates the SentNotification status to
    'confirmed' for the given user and replies with a thank you message.
    """

    keyword = "1"

    NOT_REGISTERED = _('Sorry, your mobile number is not registered.')
    NO_REMINDERS = _('Sorry, I could not find any reminders awaiting '
                     'confirmation.')
    THANK_YOU = _('Thank you for confirming your upcoming appointment.')  

    def handle(self, text):
        contact = self.msg.connection.contact
        if not contact:
            self.msg.respond(self.NOT_REGISTERED)
            return
        notifs = reminders.SentNotification.objects.filter(recipient=contact)
        if not notifs.exists():
            self.msg.respond(self.NO_REMINDERS)
            return
        sent_notification = notifs.order_by('-date_sent')[0]
        sent_notification.status = 'confirmed'
        sent_notification.date_confirmed = datetime.datetime.now()
        sent_notification.save()
        self.respond(self.THANK_YOU)

import datetime

from rapidsms.apps.base import AppBase
from rapidsms.contrib.scheduler.models import EventSchedule

from afrims.apps.reminders import models as reminders
from afrims.apps.pincode.messages import PinVerifiedOutgoingMessage

# In RapidSMS, message translation is done in OutgoingMessage, so no need
# to attempt the real translation here.  Use _ so that ./manage.py makemessages
# finds our text.
_ = lambda s: s


def scheduler_callback(router):
    """
    Basic rapidsms.contrib.scheduler.models.EventSchedule callback
    function that runs RemindersApp.cronjob()
    """
    app = router.get_app("afrims.apps.reminders")
    app.cronjob()


class RemindersApp(AppBase):
    """ RapidSMS app to send appointment reminders """

    # for production, we'll probably want something like:
#    cron_schedule = {'minutes': ['0'], 'hours': ['10']}
    # for testing and debugging, run every minute:
    cron_schedule = {'minutes': '*'}
    cron_name = 'reminders-cron-job'
    cron_callback = 'afrims.apps.reminders.app.scheduler_callback'

    appt_message = _('Hello, {name}. You have an upcoming appointment in '
                     '{days} days, on {date}. Please reply with 1 to confirm.')
    not_registered = _('Sorry, your mobile number is not registered.')
    no_reminders = _('Sorry, I could not find any reminders awaiting '
                     'confirmation.')
    thank_you = _('Thank you for confirming your upcoming appointment.')  

    def start(self):
        """ setup event schedule to run cron job """
        try:
            schedule = EventSchedule.objects.get(description=self.name)
        except EventSchedule.DoesNotExist:
            schedule = EventSchedule.objects.create(description=self.name,
                                                    callback=self.cron_callback,
                                                    **self.cron_schedule)
        schedule.callback = self.cron_callback
        for key, val in self.cron_schedule.iteritems():
            if hasattr(schedule, key):
                setattr(schedule, key, val)
        schedule.save()
        self.info('started')

    def handle(self, msg):
        """
        Handles messages that start with a '1' (to ease responding in
        alternate character sets).
        
        Updates the SentNotification status to 'confirmed' for the given user
        and replies with a thank you message.
        """
        msg_parts = msg.text.split()
        if not msg_parts or msg_parts[0] != '1':
            return False
        contact = msg.connection.contact
        if not contact:
            msg.respond(self.not_registered)
            return True
        notifs = reminders.SentNotification.objects.filter(recipient=contact)
        if not notifs.exists():
            msg.respond(self.no_reminders)
            return True
        sent_notification = notifs.order_by('-date_sent')[0]
        sent_notification.status = 'confirmed'
        sent_notification.date_confirmed = datetime.datetime.now()
        sent_notification.save()
        msg.respond(self.thank_you)

    def queue_outgoing_notifications(self):
        """ generate queued appointment reminders """
        # TODO: make sure this task is atomic
        for notification in reminders.Notification.objects.all():
            self.info('Scheduling notifications for %s' % notification)
            days_delta = datetime.timedelta(days=notification.num_days)
            appt_date = datetime.date.today() + days_delta
            patients = reminders.Patient.objects.filter(next_visit=appt_date,
                                                        contact__isnull=False,)
            patients = patients.exclude(contact__sent_notifications__appt_date=appt_date,
                                        contact__sent_notifications__notification=notification)
            self.info('Queuing reminders for %s patients.' % patients.count())
            for patient in patients:
                self.debug('Creating notification for %s' % patient)
                msg_data = {
                    'days': notification.num_days,
                    'date': appt_date,
                    'name': patient.contact.name,
                }
                message = self.appt_message.format(**msg_data)
                notification.sent_notifications.create(
                                        recipient=patient.contact,
                                        appt_date=appt_date,
                                        date_queued=datetime.datetime.now(),
                                        message=message)

    def send_notifications(self):
        """ send queued for delivery messages """
        notifications = reminders.SentNotification.objects.filter(status='queued')
        count = notifications.count()
        self.info('found {0} notification(s) to send'.format(count))
        for notification in notifications:
            connection = notification.recipient.get_primary_connection()
            if not connection:
                self.debug('no connection found for recipient {0}, unable '
                           'to send'.format(notification.recipient))
                continue
            msg = PinVerifiedOutgoingMessage(connection=connection,
                                             template=notification.message)
            success = True
            try:
                msg.send()
            except Exception, e:
                self.exception(e)
                success = False
            if success:
                self.debug('notification sent successfully')
                notification.status = 'sent'
                notification.date_sent = datetime.datetime.now()
            else:
                self.debug('notification failed to send')
                notification.status = 'error'
            notification.save()

    def cronjob(self):
        self.debug('{0} running'.format(self.cron_name))
        # grab all reminders ready to go out and queue their messages
        self.queue_outgoing_notifications()
        # send queued notifications
        self.send_notifications()

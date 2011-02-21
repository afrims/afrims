import datetime

from rapidsms.apps.base import AppBase
from rapidsms.messages import OutgoingMessage
from rapidsms.contrib.scheduler.models import EventSchedule

from afrims.apps.reminders import models as reminders

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

    cron_schedule = {'minutes': '*'}
    cron_name = 'reminders-cron-job'
    cron_callback = 'afrims.apps.reminders.app.scheduler_callback'

    appt_message = _('Hello, {name}. You have an upcoming appointment in '
                     '{days} days, on {date}. Please reply with 1 to confirm.')

    def start(self):
        """ setup event schedule to run cron job every hour """
        try:
            schedule = EventSchedule.objects.get(description=self.name)
        except EventSchedule.DoesNotExist:
            schedule = EventSchedule.objects.create(description=self.name,
                                                    callback=self.cron_callback,
                                                    minutes=['0'], hours=['10'])
        schedule.callback = self.cron_callback
        for key, val in self.cron_schedule.iteritems():
            if hasattr(schedule, key):
                setattr(schedule, key, val)
        schedule.save()
        self.info('started')

    def queue_outgoing_notifications(self):
        """ generate queued appointment reminders """
        # TODO: make sure this task is atomic
        for notification in reminders.Notification.objects.all():
            self.info('Scheduling notifications for %s' % notification)
            days_delta = datetime.timedelta(days=notification.num_days)
            appt_date = datetime.date.today() + days_delta
            patients = reminders.Patient.objects.filter(next_visit=appt_date,
                                                        contact__isnull=False)
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
                                        date_queued=datetime.datetime.now(),
                                        message=message)

    def send_notifications(self):
        """ send queued for delivery messages """
        notifications = reminders.SentNotification.objects.filter(status='queued')
        count = notifications.count()
        self.info('found {0} notification(s) to send'.format(count))
        for notification in notifications:
            connection = notification.recipient.default_connection
            msg = OutgoingMessage(connection=connection,
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

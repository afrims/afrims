import datetime
import logging
import re

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q, signals
from django.template.loader import render_to_string
from django.utils.translation import ugettext

from rapidsms.apps.base import AppBase
from rapidsms.contrib.scheduler.models import EventSchedule
from rapidsms.messages.outgoing import OutgoingMessage
from rapidsms.models import Contact

from afrims.apps.broadcast.models import Broadcast
from afrims.apps.groups import models as groups
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


def daily_email_callback(router, *args, **kwargs):
    """
    Send out daily email report of confirmed/unconfirmed appointments.
    """
    days = kwargs.get('days', 7)
    try:
        days = int(days)
    except ValueError:
        logging.debug('ValueError for specified days in daily_email_callback. Value used was %s. Using default value:7' % days)
        days = 7
    today = datetime.date.today()
    appt_date = today + datetime.timedelta(days=days)
    confirmed_patients = reminders.Patient.objects.confirmed_for_date(appt_date)
    unconfirmed_patients = reminders.Patient.objects.unconfirmed_for_date(appt_date)
    context = {
        'appt_date': appt_date,
        'confirmed_patients': confirmed_patients,
        'unconfirmed_patients': unconfirmed_patients,
    }
    patients_exist = confirmed_patients or unconfirmed_patients
    if patients_exist:
        subject_template = u'Confirmation Report For Appointments on {appt_date}'
        subject = subject_template.format(**context)
        body = render_to_string('reminders/emails/daily_report_message.html', context)
        group_name = settings.DEFAULT_DAILY_REPORT_GROUP_NAME
        group, created = groups.Group.objects.get_or_create(name=group_name)
        if not created:
            emails = [c.email for c in group.contacts.all() if c.email]
            if emails:
                send_mail(subject, body, None, emails, fail_silently=True)


class RemindersApp(AppBase):
    """ RapidSMS app to send appointment reminders """

    # for production, we'll probably want something like:
#    cron_schedule = {'minutes': ['0'], 'hours': ['10']}
    # for testing and debugging, run every minute:
    cron_schedule = {'minutes': '*'}
    cron_name = 'reminders-cron-job'
    cron_callback = 'afrims.apps.reminders.app.scheduler_callback'

    pin_regex = re.compile(r'^\d{4,6}$')
    conf_keyword = '1'

    future_appt_msg = _('You have an upcoming appointment in '
                        '{days} days, on {date}. Please reply with '
                        '{confirm_response} to confirm.')
    near_appt_msg = _('You have an appointment {day}, {date}. '
                       'Please reply with {confirm_response} to confirm.')
    not_registered = _('Sorry, your mobile number is not registered.')
    no_reminders = _('Sorry, I could not find any reminders awaiting '
                     'confirmation.')
    incorrect_pin = _('That is not your PIN code. Please reply with the '
                      'correct PIN code.')
    pin_required = _('Please confirm appointments by sending your PIN code.')
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
        # Daily email schedule
        name = 'reminders-daily-email'
        info = {
            'callback': 'afrims.apps.reminders.app.daily_email_callback',
            'hours': [12],
            'minutes': [0],
            'callback_kwargs': {'days': 7},
        }
        schedule, created = EventSchedule.objects.get_or_create(description=name,
            defaults=info
        )
#        if not created:
#            for key, val in info.iteritems():
#                if hasattr(schedule, key):
#                    setattr(schedule, key, val)  
#        schedule.save()        
        group_name = settings.DEFAULT_DAILY_REPORT_GROUP_NAME
        group, _ = groups.Group.objects.get_or_create(name=group_name)
        group_name = settings.DEFAULT_CONFIRMATIONS_GROUP_NAME
        group, _ = groups.Group.objects.get_or_create(name=group_name)
        self.info('started')

    @classmethod
    def _notification_msg(cls, appt_date, confirm_response=None):
        """
        Formats an appointment reminder message for the given notification,
        appointment date, and confirm response (usually the confirm keyword or
        'your PIN').
        """
        num_days = (appt_date - datetime.date.today()).days
        if confirm_response is None:
            confirm_response = cls.conf_keyword
        month_for_translate = appt_date.strftime('%B')
        month_for_translate = ugettext(month_for_translate)
        msg_data = {
            'days': num_days,
            'date': '%s %s' % (appt_date.strftime('%d'), month_for_translate),
            'confirm_response': confirm_response,
        }
        if num_days == 0:
            msg_data['day'] = ugettext('today')
            message = ugettext(cls.near_appt_msg)
        elif num_days == 1:
            msg_data['day'] = ugettext('tomorrow')
            message = ugettext(cls.near_appt_msg)
        else:
            message = ugettext(cls.future_appt_msg)
        return message.format(**msg_data)

    def handle(self, msg):
        """
        Handles messages that start with a '1' (to ease responding in
        alternate character sets).
        
        Updates the SentNotification status to 'confirmed' for the given user
        and replies with a thank you message.
        """
        msg_parts = msg.text.split()
        if not msg_parts:
            return False

        response = msg_parts[0]
        if response != self.conf_keyword and not self.pin_regex.match(response):
            return False
        contact = msg.connection.contact
        if not contact:
            msg.respond(self.not_registered)
            return True
        if contact.pin and response == self.conf_keyword:
            msg.respond(self.pin_required)
            return True
        if contact.pin and response != contact.pin:
            msg.respond(self.incorrect_pin)
            return True
        notifs = reminders.SentNotification.objects.filter(recipient=contact,
                                                           status='sent')
        if not notifs.exists():
            msg.respond(self.no_reminders)
            return True
        now = datetime.datetime.now()        
        sent_notification = notifs.order_by('-date_sent')[0]
        sent_notification.status = 'confirmed'
        sent_notification.date_confirmed = now
        sent_notification.save()

        contact = msg.connection.contact
        patient = reminders.Patient.objects.get(contact=contact)
        study_id = patient.subject_number
        msg_text = u'Appointment on %s confirmed.' % sent_notification.appt_date
        full_msg = u'From {number} ({study_id}): {body}'.format(
            number=msg.connection.identity, body=msg_text,
            study_id=study_id,
        )
        broadcast = Broadcast.objects.create(
            date_created=now, date=now,
            schedule_frequency='one-time', body=full_msg
        )
        group_name = settings.DEFAULT_CONFIRMATIONS_GROUP_NAME
        group, _ = groups.Group.objects.get_or_create(name=group_name)
        broadcast.groups.add(group)
        msg.respond(self.thank_you)

    def queue_outgoing_notifications(self):
        """ generate queued appointment reminders """
        # TODO: make sure this task is atomic
        today = datetime.date.today()
        for notification in reminders.Notification.objects.all():
            self.info('Scheduling notifications for %s' % notification)
            days_delta = datetime.timedelta(days=notification.num_days)
            appt_date = today + days_delta
            patients = reminders.Patient.objects.filter(next_visit=appt_date,
                                                        contact__isnull=False,)
            already_sent = Q(contact__sent_notifications__appt_date=appt_date) &\
                           Q(contact__sent_notifications__notification=notification)
            confirmed = Q(contact__sent_notifications__appt_date=appt_date) &\
                        Q(contact__sent_notifications__status__in=['confirmed', 'manual'])
            # .exclude() generates erroneous results - use filter(~...) instead
            patients = patients.filter(~already_sent)
            if notification.recipients == 'confirmed':
                patients = patients.filter(confirmed)
            elif notification.recipients == 'unconfirmed':
                # unconfirmed should include those to whom we haven't sent
                # any reminders yet, so just exclude the confirmed ones
                patients = patients.filter(~confirmed)
            self.info('Queuing reminders for %s patients.' % patients.count())
            for patient in patients:
                # _() is not an alias for gettext, since normally translation
                # is done in the OutgoingMessage class.  In the code below, we
                # force translation by calling ugettext directly, since the
                # message gets queued in the database before being passed to
                # OutgoingMessage.
                self.debug('Creating notification for %s' % patient)
                if patient.contact.pin:
                    confirm_response = ugettext('your PIN')
                else:
                    confirm_response = self.conf_keyword
                message = self._notification_msg(appt_date, confirm_response)
                time_of_day = patient.reminder_time or notification.time_of_day
                date_to_send = datetime.datetime.combine(today, time_of_day)
                notification.sent_notifications.create(
                                        recipient=patient.contact,
                                        appt_date=appt_date,
                                        date_queued=datetime.datetime.now(),
                                        date_to_send=date_to_send,
                                        message=message)

    def send_notifications(self):
        """ send queued for delivery messages """
        notifications = reminders.SentNotification.objects.filter(
                                    status='queued',
                                    date_to_send__lt=datetime.datetime.now())
        count = notifications.count()
        if count > 0:
            self.info('found {0} notification(s) to send'.format(count))
        for notification in notifications:
            connection = notification.recipient.default_connection
            if not connection:
                self.debug('no connection found for recipient {0}, unable '
                           'to send'.format(notification.recipient))
                continue
            msg = OutgoingMessage(connection=connection,
                                  template=notification.message)
            success = True
            try:
                msg.send()
            except Exception, e:
                self.exception(e)
                success = False
            if success and (msg.sent or msg.sent is None):
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

def queue_message_to_contact(contact, text):
    """Just queue a single message to a contact"""
    now = datetime.datetime.now()
    broadcast = Broadcast(schedule_frequency='one-time',
                          date=now,
                          body=text)
    broadcast.save()
    broadcast.messages.create(recipient=contact)

def new_contact_created(sender, **kwargs):
    """When a new contact is created, send a welcome message"""
    created = kwargs['created']
    if created:
        contact = kwargs['instance']
        connection = contact.default_connection
        if not connection:
            logging.debug('no connection found for recipient {0}, unable '
                       'to send'.format(contact))
            return
        text = _("You have been registered for TrialConnect.")
        try:
            queue_message_to_contact(contact, text)
            logging.debug("Sending wecome message '%s' to '%s'." % (text, contact))
        except Exception, e:
            logging.exception(e)

signals.post_save.connect(new_contact_created, sender=Contact,
               dispatch_uid='just once per new contact created')

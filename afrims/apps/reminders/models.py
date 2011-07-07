import datetime

from django.db import models
from django.db.models import F, Q, Max

from rapidsms import models as rapidsms

from afrims.apps.groups.utils import format_number


class Notification(models.Model):
    '''
    An appointment notifications to be sent to trial participants.
    '''
    NUM_DAY_CHOICES = [(x, u'{0} day{1} before appointment'.format(x, x > 1 and 's' or ''))
                       for x in xrange(1, 15)]
    NUM_DAY_CHOICES.insert(0, (0, u'On the appointment day'))
    RECIPIENTS_CHOICES = [
        ('all', 'All patients'),
        ('unconfirmed', 'Unconfirmed patients only'),
        ('confirmed', 'Confirmed patients only'),
    ]
    num_days = models.IntegerField('An appointment reminder will go out',
                                   choices=NUM_DAY_CHOICES)
    time_of_day = models.TimeField()
    recipients = models.CharField('Send to', max_length=15, default='all',
                                  choices=RECIPIENTS_CHOICES)

    class Meta:
        ordering = ('num_days',)

    def __unicode__(self):
        return u'{0} day'.format(self.num_days)

    @property
    def formatted_time(self):
        return self.time_of_day.strftime('%I:%M %p')


class SentNotificationManager(models.Manager):

    def for_current_appointment(self):
        """SentNotifications for the patient's current next
        appointment date"""
        return self.filter(appt_date = F('recipient__patient__next_visit'))

    # Should these be based on appointment dates or when they were sent?

    def confirmed_for_range(self, start_date, end_date):
        return self.filter(
            appt_date__range=(start_date, end_date),
            status__in=['confirmed', 'manual'],
        ).distinct()

    def unconfirmed_for_range(self, start_date, end_date):
        return self.for_current_appointment().filter(
            ~Q(status__in=['confirmed', 'manual']),
            appt_date__range=(start_date, end_date),  
        ).distinct()


class SentNotification(models.Model):
    '''
    A notification sent to a trial participant.
    '''
    STATUS_CHOICES = (
        ('queued', 'Queued'),
        ('sent', 'Sent'),
        ('error', 'Error'),
        ('confirmed', 'Confirmed'),
        ('manual', 'Manually Confirmed'),
    )
    notification = models.ForeignKey(Notification,
                                    related_name='sent_notifications',
                                    help_text='The related notification '
                                    'for which this message was sent.')
    recipient = models.ForeignKey(rapidsms.Contact,
                                  related_name='sent_notifications',
                                  help_text='The recipient of this '
                                  'notification.')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                              default='queued')
    appt_date = models.DateField(help_text='The date of the appointment.')
    date_queued = models.DateTimeField(help_text='The date and time this '
                                       'notification was initially created.')
    date_to_send = models.DateTimeField(help_text='The date and time this noti'
                                        'fication is scheduled to be sent.')
    date_sent = models.DateTimeField(null=True, blank=True,
                                     help_text='The date and time this '
                                     'notification was sent.')
    date_confirmed = models.DateTimeField(null=True, blank=True,
                                          help_text='The date and time we '
                                          'received a receipt confirmation '
                                          'from the recipient.')
    message = models.CharField(max_length=160, help_text='The actual message '
                               'that was sent to the user.')
    
    objects = SentNotificationManager()

    def __unicode__(self):
        return u'{notification} for {recipient} created on {date}'.format(
                                        notification=self.notification,
                                        recipient=self.recipient,
                                        date=self.date_queued)

    def manually_confirm(self):
        self.date_confirmed = datetime.datetime.now()
        self.status = 'manual'
        self.save()

    @property
    def formatted_phone(self):
        return format_number(self.mobile_number)
class PatientDataPayload(models.Model):
    ''' Dumping area for incoming patient data XML snippets '''

    STATUS_CHOICES = (
        ('received', 'Received'),
        ('error', 'Error'),
        ('success', 'Success'),
    )

    raw_data = models.TextField()
    submit_date = models.DateTimeField()
    status = models.CharField(max_length=16, default='received',
                              choices=STATUS_CHOICES)
    error_message = models.TextField(blank=True)

    def save(self, **kwargs):
        if not self.pk:
            self.submit_date = datetime.datetime.now()
        return super(PatientDataPayload, self).save(**kwargs)

    def __unicode__(self):
        msg = u'Raw Data Payload, submitted on: {date}'
        return msg.format(date=self.submit_date)


class PatientManager(models.Manager):

    def confirmed_for_date(self, appt_date):
        return self.filter(
            contact__sent_notifications__appt_date=appt_date,
            contact__sent_notifications__status__in=['confirmed', 'manual']
        ).annotate(
            confirm_time=Max('contact__sent_notifications__date_confirmed')
        ).distinct()

    def unconfirmed_for_date(self, appt_date):
        return self.filter(
            ~Q(contact__sent_notifications__status__in=['confirmed', 'manual']),
            contact__sent_notifications__appt_date=appt_date,
            next_visit=appt_date,
        ).annotate(
            last_reminder_time=Max('contact__sent_notifications__date_sent'),
            reminder_id=Max('contact__sent_notifications__id'),
        ).distinct()


class Patient(models.Model):
    # Patients may be manually created, so raw data can be null
    raw_data = models.ForeignKey(PatientDataPayload, null=True, blank=True,
                                 related_name='patients')
    contact = models.ForeignKey(rapidsms.Contact, unique=True)
    subject_number = models.CharField(max_length=20, unique=True)
    date_enrolled = models.DateField()
    mobile_number = models.CharField(max_length=30)
    pin = models.CharField(max_length=4, blank=True,
                           help_text="A 4-digit pin code for sms "
                                     "authentication workflows.")
    next_visit = models.DateField(blank=True, null=True)
    reminder_time = models.TimeField(blank=True, null=True)

    objects = PatientManager()

    def __unicode__(self):
        msg = u'Patient, Subject ID:{id}, Enrollment Date:{date_enrolled}'
        return msg.format(id=self.subject_number,
                          date_enrolled=self.date_enrolled)

    @property
    def formatted_phone(self):
        return format_number(self.mobile_number)

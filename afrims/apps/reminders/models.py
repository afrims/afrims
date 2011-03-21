from django.db import models

from rapidsms import models as rapidsms


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


class SentNotification(models.Model):
    '''
    A notification sent to a trial participant.
    '''
    STATUS_CHOICES = (
        ('queued', 'Queued'),
        ('sent', 'Sent'),
        ('error', 'Error'),
        ('confirmed', 'Confirmed'),
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

    def __unicode__(self):
        return u'{notification} for {recipient} created on {date}'.format(
                                        notification=self.notification,
                                        recipient=self.recipient,
                                        date=self.date_queued)


class PatientDataPayload(models.Model):
    '''
        Dumping area for incoming patient data xml snippets
    '''
    raw_data = models.TextField()
    submit_date = models.DateTimeField()

    def __unicode__(self):
        return u'Raw Data Payload, submitted on: {date}'.format(date=self.submit_date)


class Patient(models.Model):
    raw_data = models.ForeignKey(PatientDataPayload, null=True, blank=True) #we might create Patients manually
    subject_number = models.CharField(max_length=20)
    date_enrolled = models.DateField()
    mobile_number = models.CharField(max_length=30)
    pin = models.CharField(max_length=4, blank=True,help_text="A 4-digit pin code for sms authentication workflows.")
    next_visit = models.DateField(blank=True,null=True)
    contact = models.ForeignKey(rapidsms.Contact, null=True, blank=True)


    def __unicode__(self):
        return u'Patient, Subject ID:{id}, Enrollment Date:{date_enrolled}'.format(id=self.subject_number,
                                                  date_enrolled=self.date_enrolled)


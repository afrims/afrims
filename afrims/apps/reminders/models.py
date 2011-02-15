from django.db import models

from rapidsms import models as rapidsms


class Notification(models.Model):
    '''
    An appointment notifications to be sent to trial participants.
    '''
    num_days = models.IntegerField(help_text='Number of days before the '
                                   'scheduled appointment to send a reminder.')

    def __unicode__(self):
        return u'{0} day'.format(self.num_days)


class SentNotification(models.Model):
    '''
    A notification sent to a trial participant.
    '''
    STATUS_CHOICES = (
        ('queued', 'Queued'),
        ('delivered', 'Delivered'),
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
    date_queued = models.DateTimeField(help_text='The date and time this '
                                       'notification was initially created.')
    date_delivered = models.DateTimeField(null=True, blank=True,
                                          help_text='The date and time this '
                                          'notification was delivered.')
    date_confirmed = models.DateTimeField(null=True, blank=True,
                                          help_text='The date and time we '
                                          'received a receipt confirmation '
                                          'from the recipient.')
    message = models.CharField(max_length=160, help_text='The actual message '
                               'that was delivered to the user.')

    def __unicode__(self):
        return u'{notification} for {recipient} created on {date}'.format(
                                        notification=self.notification,
                                        recipient=self.recipient,
                                        date=self.date_queued)

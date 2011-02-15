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
    notification = models.ForeignKey(Notification,
                                    related_name='sent_notifications')
    recipient = models.ForeignKey(rapidsms.Contact,
                                  related_name='sent_notifications')
    date_logged = models.DateTimeField()
    message = models.CharField(max_length=160)
    
    def __unicode__(self):
        return u'{notification} sent to {recipient} on {date}'.format(
                                        notification=self.notification,
                                        recipient=self.recipient,
                                        date=self.date_logged)

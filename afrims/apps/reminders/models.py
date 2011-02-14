from django.db import models


class Notification(models.Model):
    """
    Appointment notifications to be sent to trial participants.
    """
    num_days = models.IntegerField(help_text='Number of days before the '
                                   'scheduled appointment to send a reminder.')

    def __unicode__(self):
        return u'{0} days'.format(self.num_days)

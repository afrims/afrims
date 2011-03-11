from django.db import models

from rapidsms import models as rapidsms


class OutgoingMessage(models.Model):
    STATUS_CHOICES = (
        ('queued', 'Queued'),
        ('sent', 'Sent'),
        ('error', 'Error'),
    )
    connection = models.ForeignKey(rapidsms.Connection)
    text = models.CharField(max_length=160)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                              default='queued')
    date_queued = models.DateTimeField()
    date_sent = models.DateTimeField(blank=True, null=True)
    error_message = models.TextField(blank=True)

    def __unicode__(self):
        return self.text

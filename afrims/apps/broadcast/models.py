# vim: ai ts=4 sts=4 et sw=4
import datetime
from dateutil.relativedelta import relativedelta

from django.db import models

from rapidsms.models import Contact, Connection
from rapidsms.contrib.messagelog.models import Message

from afrims.apps.reminder.models import Group


class BroadcastReadyManager(models.Manager):
    def get_query_set(self):
        qs = super(BroadcastReadyManager, self).get_query_set()
        qs = qs.filter(date_next_notified__lt=datetime.datetime.now())
        qs = qs.exclude(schedule_start_date__isnull=True,
                        schedule_frequency='')
        return qs


class Broadcast(models.Model):
    """ General broadcast message """

    REPEAT_CHOICES = (
        ('', 'Disabled'),
        ('one-time', 'One Time'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    )

    date_created = models.DateTimeField()
    date_last_notified = models.DateTimeField(null=True, blank=True,
                                              db_index=True)
    date_next_notified = models.DateTimeField(null=True, blank=True,
                                              db_index=True)
    schedule_start_date = models.DateTimeField(null=True, blank=True)
    schedule_frequency = models.CharField(max_length=16, blank=True,
                                          choices=REPEAT_CHOICES, default='')
    body = models.TextField()
    groups = models.ManyToManyField(Group, related_name='broadcasts')

    objects = models.Manager()
    ready = BroadcastReadyManager()

    def get_next_date(self):
        """ calculate next date based on configured characteristics """
        # TODO: update to use rrule and discrete frequencies
        if self.schedule_start_date and self.schedule_frequency:
            next_date = self.schedule_start_date
            frequency_map = {
                'daily': relativedelta(days=+1),
                'weekly': relativedelta(weeks=+1),
                'monthly': relativedelta(months=+1),
            }
            if self.schedule_frequency in frequency_map:
                now = datetime.datetime.now()
                delta = frequency_map[self.schedule_frequency]
                while next_date < now:
                    next_date += delta
            return next_date

    def set_next_date(self):
        """ update broadcast to be ready for next date """
        now = datetime.datetime.now()
        # Disable this broadcast if it was a one-time notification (we just
        # sent it). This will make get_next_date() return None below.
        if self.schedule_frequency == 'one-time':
            self.schedule_frequency = ''
        self.date_last_notified = now
        self.date_next_notified = self.get_next_date()

    def queue_outgoing_messages(self):
        """ generate queued outgoing messages """
        contacts = Contact.objects.distinct().filter(groups__broadcasts=self)
        for contact in contacts:
            self.messages.create(recipient=contact)

    def save(self, **kwargs):
        if not self.pk:
            self.date_created = datetime.datetime.now()
        return super(Broadcast, self).save(**kwargs)


class BroadcastMessage(models.Model):
    """ Message to individual recipient of broadcast """

    STATUS_CHOICES = (
        ('queued', 'Queued'),
        ('sent', 'Sent'),
        ('error', 'Error'),
    )

    broadcast = models.ForeignKey(Broadcast, related_name='messages')
    recipient = models.ForeignKey(Contact, related_name='broadcast_messages')
    date_created = models.DateTimeField()
    date_sent = models.DateTimeField(null=True, blank=True, db_index=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES,
                              default='queued')

    def save(self, **kwargs):
        if not self.pk:
            self.date_created = datetime.datetime.now()
        return super(BroadcastMessage, self).save(**kwargs)


class BroadcastResponse(models.Model):
    
    broadcast = models.ForeignKey(BroadcastMessage)
    contact   = models.ForeignKey(Contact)
    text      = models.TextField()
    date      = models.DateTimeField(default=datetime.datetime.utcnow)
    
    logger_message = models.ForeignKey(Message)
    
    def __unicode__(self):
        return "%s from %s in response to %s" % \
            (self.text, self.contact, self.broadcast)
             
    

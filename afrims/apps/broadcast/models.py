# vim: ai ts=4 sts=4 et sw=4
import logging
import datetime
from dateutil.relativedelta import relativedelta
from dateutil import rrule

from django.db import models

from rapidsms.models import Contact, Connection
from rapidsms.contrib.messagelog.models import Message

from afrims.apps.reminder.models import Group


logger = logging.getLogger('broadcast.models')


class DateAttribute(models.Model):
    """ Simple model to store weekdays and months """

    ATTRIBUTE_TYPES = (
        ('weekday', 'Weekday'),
        ('month', 'Month'),
    )
    WEEKDAY_CHOICES = (
        (0, 'Sunday'),
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
    )
    MONTH_CHOICES = (
        (0, 'January'),
        (1, 'February'),
        (2, 'March'),
        (3, 'April'),
        (4, 'May'),
        (5, 'June'),
        (6, 'July'),
        (7, 'August'),
        (8, 'September'),
        (9, 'October'),
        (10, 'November'),
        (11, 'December'),
    )

    name = models.CharField(max_length=32, unique=True)
    value = models.PositiveSmallIntegerField()
    type = models.CharField(max_length=16, choices=ATTRIBUTE_TYPES)

    class Meta(object):
        unique_together = ('type', 'value')
        ordering = ('value',)

    def __unicode__(self):
        return self.name


class BroadcastReadyManager(models.Manager):
    def get_query_set(self):
        qs = super(BroadcastReadyManager, self).get_query_set()
        qs = qs.filter(date__lt=datetime.datetime.now())
        qs = qs.exclude(schedule_frequency__isnull=True)
        return qs


class Broadcast(models.Model):
    """ General broadcast message """

    REPEAT_CHOICES = (
        (None, 'Disabled'),
        ('one-time', 'One Time'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    )

    date_created = models.DateTimeField()
    date_last_notified = models.DateTimeField(null=True, blank=True,
                                              db_index=True)
    date = models.DateTimeField(db_index=True)
    schedule_end_date = models.DateTimeField(null=True, blank=True)
    schedule_frequency = models.CharField(max_length=16, blank=True, null=True,
                                          choices=REPEAT_CHOICES)
    weekdays = models.ManyToManyField(DateAttribute, blank=True,
                                      limit_choices_to={'type': 'weekday'},
                                      related_name='broadcast_weekdays')
    months = models.ManyToManyField(DateAttribute, blank=True,
                                    limit_choices_to={'type': 'month'},
                                    related_name='broadcast_months')
    body = models.TextField()
    groups = models.ManyToManyField(Group, related_name='broadcasts')

    objects = models.Manager()
    ready = BroadcastReadyManager()

    def __unicode__(self):
        if self.schedule_frequency:
            freq = self.schedule_frequency
        else:
            freq = 'disabled'
        if self.date:
            date = self.date.isoformat(' ')
        else:
            date = 'None'
        return '{0} broadcast (date {1})'.format(freq, date)

    def get_next_date(self):
        """ calculate next date based on configured characteristics """
        logger.debug('get_next_date - {0}'.format(self))
        now = datetime.datetime.now()
        # return current date if it's in the future
        if self.date > now:
            return self.date
        # no next date if broadcast is disabled or one-time
        one_time = self.schedule_frequency == 'one-time'
        if not self.schedule_frequency or one_time:
            return None
        freq_map = {
            'daily': rrule.DAILY,
            'weekly': rrule.WEEKLY,
            'monthly': rrule.MONTHLY,
            'yearly': rrule.YEARLY,
        }
        freq = freq_map.get(self.schedule_frequency)
        kwargs = {'dtstart': self.date}
        if freq == rrule.WEEKLY:
            weekdays = self.weekdays.values_list('value', flat=True)
            if weekdays:
                kwargs['byweekday'] = weekdays
        dates = rrule.rrule(freq, **kwargs)
        for date in dates:
            logger.debug('looking for next date {0}'.format(date))
            if date > now:
                logger.debug('next date {0}'.format(date))
                return date

    def set_next_date(self):
        """ update broadcast to be ready for next date """
        logger.debug('set_next_date start - {0}'.format(self))
        now = datetime.datetime.now()
        next_date = self.get_next_date()
        # Disable this broadcast if it was a one-time notification (we just
        # sent it). This will make get_next_date() return None below.
        if self.schedule_frequency == 'one-time':
            self.schedule_frequency = None
        self.date_last_notified = now
        if next_date:
            self.date = next_date
        logger.debug('set_next_date end - {0}'.format(self))

    def queue_outgoing_messages(self):
        """ generate queued outgoing messages """
        contacts = Contact.objects.distinct().filter(groups__broadcasts=self)
        print contacts
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
             
    

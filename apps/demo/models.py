# vim: ai ts=4 sts=4 et sw=4
from django.db import models
from rapidsms.contrib.messagelog.models import Message
from rapidsms.models import Contact
from datetime import datetime


HOLIDAY_MESSAGE_STATUS = (
                    (u'initial', u'Initial Message'),
                    (u'travelling',u'Is Travelling'),
                    (u'hasPhone', u'Travelling With Phone'),
                    (u'altNumber', u'Travelling Without Phone w/ alt number'),
                    (u'noAltNumber', u'Travelling Without Phone w/out alt number'),
                    (u'resolved', u''),
                    )

class OffSiteMessage(models.Model):
    contact = models.ForeignKey(Contact, related_name="broadcast_messages")
    holiday_date = models.DateField()
    message_status = models.CharField(max_length=255, choices=HOLIDAY_MESSAGE_STATUS)
    alt_number = models.CharField(max_length=13, blank=True)
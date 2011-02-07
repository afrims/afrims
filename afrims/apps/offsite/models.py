# vim: ai ts=4 sts=4 et sw=4
from django.db import models
from rapidsms.contrib.messagelog.models import Message
from rapidsms.models import Contact
from datetime import datetime,date


HOLIDAY_MESSAGE_STATUS = (
                    (u'initial', u'Initial Message'), #"Merry Christmas! Will you be traveling for the holiday? Please reply with YES or NO"
                    (u'traveling',u'Is Traveling'), #"Will you have your phone with you? Please reply with YES or NO"
                    (u'noTravel', u'Not Traveling'),
                    (u'hasPhone', u'Travelling With Phone'), 
                    (u'noHasPhone', u'Traveling Without their Phone'),
                    (u'altNumber', u'Travelling Without Phone w/ alt number'),
                    (u'noAltNumber', u'Travelling Without Phone w/out alt number'),
                    )
def get_status_initial():
    return HOLIDAY_MESSAGE_STATUS[0][0]

def get_status_traveling():
    return HOLIDAY_MESSAGE_STATUS[1][0]

def get_status_noTravel():
    return HOLIDAY_MESSAGE_STATUS[2][0]

def get_status_hasPhone():
    return HOLIDAY_MESSAGE_STATUS[3][0]

def get_status_noHasPhone():
    return HOLIDAY_MESSAGE_STATUS[4][0]

def get_status_hasAltNumber():
    return HOLIDAY_MESSAGE_STATUS[5][0]

def get_status_noAltNumber():
    return HOLIDAY_MESSAGE_STATUS[6][0]

class HolidayPeriod(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(blank=True,null=True)
    travel_message = models.CharField(max_length=160)
    broadcast_sent = models.BooleanField()

class OffSiteMessage(models.Model):
    contact = models.ForeignKey(Contact)
    holiday = models.ForeignKey(HolidayPeriod)
    message_status = models.CharField(max_length=255, choices=HOLIDAY_MESSAGE_STATUS)
    
    

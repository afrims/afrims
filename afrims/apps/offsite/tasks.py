'''
Created on Jan 13, 2011

@author: adewinter
'''
import datetime
import logging

from rapidsms.models import Connection,Contact
from rapidsms.messages.outgoing import OutgoingMessage
from datetime import date,timedelta

from apps.offsite.models import HolidayPeriod, OffSiteMessage
from apps.offsite import models as status


default_travel_message = "It's Holiday season soon! Will you be travelling? Please send YES or NO"
default_broadcast_window = 15 #Days before holiday starts to begin broadcasting
default_volunteer_group = None

def create_new_holiday(holiday_name,start_date,end_date=None,travel_message=default_travel_message):
    '''Makes a new holiday and saves it.'''
    holiday = HolidayPeriod(name=holiday_name,start_date=start_date,end_date=end_date,travel_message=travel_message)
    holiday.save()   


def check_for_holiday_and_broadcast(router=None,msg_group=default_volunteer_group,broadcast_window=default_broadcast_window):
    '''
    Does what it says on the tin. 
    Broadcast window must be given in days and means number of days from Holiday Start Date.
    '''
    events = HolidayPeriod.objects.filter(broadcast_sent=False)
    for event in events:
        if (date.today() > (event.start_date - timedelta(days=broadcast_window))):
            _broadcast_to_volunteers(event,msg_group=msg_group)
            event.broadcast_sent = True
            event.save()

def _broadcast_to_volunteers(holiday, msg_group=default_volunteer_group):
    if msg_group is not None:
        connections = Connection.objects.filter(contact__groups__name=msg_group).distinct()
    else:
        connections = Connection.objects.filter(contact__isnull=False).distinct()
    for connection in connections:
        msg = OutgoingMessage(connection,holiday.travel_message)
        ofm = OffSiteMessage(contact=connection.contact,holiday=holiday,message_status=status.get_status_initial())
        ofm.save()
        msg.send()
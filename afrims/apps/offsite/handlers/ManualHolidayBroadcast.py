'''
Created on Jan 10, 2011

@author: adewinter
'''
from rapidsms.models import Contact
from rapidsms.messages.outgoing import OutgoingMessage
from apps.offsite import tasks
from datetime import datetime, timedelta
from apps.offsite.models import HolidayPeriod
from rapidsms.contrib.handlers.handlers.base import BaseHandler

class DemoHandler(BaseHandler):
    group_name = ""
    keyword = "Holiday"    #This is the keyword used to trigger a response from this handler.
    msg_help_txt = "Sent out holiday broadcast messages to volunteer group."
    
    def handle(self, text):
        if text.lower() == 'kill':
            h = HolidayPeriod.objects.filter(name="bobs holiday").delete()
        self.respond("Test holidays deleted")
    
    def help(self):
        # make some cases and whatnot
        tasks.create_new_holiday("bobs holiday", datetime.today(), datetime.today()+timedelta(days=2), "It's Holiday Time! Are you traveling? Please Send YES or NO")
        tasks.check_for_holiday_and_broadcast(msg_group=None)
        return self.respond(self.msg_help_txt)

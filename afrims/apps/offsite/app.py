from rapidsms.apps.base import AppBase
from apps.offsite.models import OffSiteMessage
from apps.offsite import models as HMS
from datetime import date,timedelta
class App (AppBase):
    msg_xmas_thx =              "Thanks for your response. Enjoy the holidays!"
    msg_xmas_have_phone_q =     "Will you have your phone with you? Please reply with YES or NO"
    msg_xmas_has_phone =        "Please keep your phone with you in case we need to contact you while you are travelling"
    msg_xmas_alt_number_q =     "Do you have an alternative number we can reach you on? Please reply with YES or NO"
    msg_xmas_has_alt_number =   "Please contact your Study Clinic to provide them with the alternative number. Hope you have a Merry Christmas!"
    msg_xmas_no_has_alt_number ="Please contact the clinic if you notice any fever symptoms while you travel. Have a safe journey!"
    

    ''' Checks which holiday message chain they're responding to (if any)'''
    DAYS_VALID = 30
    
    
    def handle(self, message):
        tokens = message.text.strip().lower().split(' ')
        if len(tokens) <= 0:
            return
        
        if tokens[0].lower() in ['yes','no']:
            #check to see if they're responding to a holiday message
            contact = message.contact
            half_window = timedelta(days=self.DAYS_VALID)
            now = date.today()
            OFM_set = OffSiteMessage.objects.filter(contact=contact)
            for r in OFM_set: #check if we're in a holiday date range (otherwise it doesn't matter)
                a_date = r.holiday.start_date - half_window
                b_date = r.holiday.start_date + half_window
                if (now >= a_date) and (now <= b_date):
                    return self.do_check(message,tokens, r) #it's holiday time! Do something useful
            
        return
    

    def do_check(self, message, tokens, OFM):
        '''
        Checks to see at what stage in the OffSiteMessage (OFM is the model) chain we're in
        then handles the YES or NO responses accordingly.
        First token MUST be either 'YES' or 'NO'
        '''
        status = OFM.message_status
        kw = tokens[0].upper()
        if status == HMS.get_status_initial():
            if kw == 'YES':
                OFM.message_status = HMS.get_status_traveling()
                OFM.save()
                message.respond(self.msg_xmas_have_phone_q)
            elif kw == 'NO':
                OFM.message_status = HMS.get_status_noTravel()
                OFM.save()
                message.respond(self.msg_xmas_thx)
                
            return True
        
        elif status == HMS.get_status_traveling():
            if kw == 'YES':
                OFM.message_status = HMS.get_status_hasPhone()
                OFM.save()
                message.respond(self.msg_xmas_has_phone)
            elif kw == 'NO':
                OFM.message_status = HMS.get_status_noHasPhone()
                OFM.save()
                message.respond(self.msg_xmas_alt_number_q)
            return True
        
        elif status == HMS.get_status_noHasPhone():
            if kw == 'YES':
                OFM.message_status = HMS.get_status_hasAltNumber()
                OFM.save()
                message.respond(self.msg_xmas_has_alt_number)
            elif kw == 'NO':
                OFM.message_status = HMS.get_status_noAltNumber()
                OFM.save()
                message.respond(self.msg_xmas_no_has_alt_number)
            return True
        
        pass
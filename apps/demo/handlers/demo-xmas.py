'''
Created on Jan 10, 2011

@author: adewinter

This is a simple registration keyword to be used for demo purposes. 

Should be turned off (read: removed) at production time.
'''
from apps.broadcast.handlers.base import BroadcastHandler
from rapidsms.models import Contact
from rapidsms.messages.outgoing import OutgoingMessage

class DemoHandler(BroadcastHandler):
    group_name = ""
    keyword = "demo"    #This is the keyword used to trigger a response from this handler.
    msg_zero_args = "Please use some keywords. E.g. 'demo broadcast hello world'"
    msg_xmas = "Merry Christmas! Will you be travelling for the holiday? Please reply with YES or NO"
    msg_bcast_no_text = "You must include a message after the broadcast keyword"
    msg_bcast_all_not_allowed = "You need to enable broadcasting to all in the demo! See the demo.py handler"
    msg_unrecognized_subkeyword = "Unrecognized subkeyword (demo handler)"
    msg_too_long = "Your message is too long to fit into one SMS. Please shorten and try again."
    BROADCAST_TO_ALL = True;
    
#    HOLIDAY_MESSAGE_STATUS = (
#                    (u'initial', u'Initial Message'),
#                    (u'travelling',u'Is Travelling'),
#                    (u'hasPhone', u'Travelling With Phone'),
#                    (u'altNumber', u'Travelling Without Phone w/ alt number'),
#                    (u'noAltNumber', u'Travelling Without Phone w/out alt number'),
#                    (u'resolved', u''),
#                    )

    
    def handle(self, text):
        tokens = text.split(' ')
        if len(tokens) <= 0:
            return self.respond(self.msg_zero_args)
        
        subkw = tokens[0]
        self.group_name = 'all'  #bit of a hack here to make it work with the broadcast code below
        if subkw == 'broadcast':
            if len(tokens) > 1 and self.BROADCAST_TO_ALL:
                contacts = Contact.objects.all().exclude(name=self.msg.contact.name)
                txt_send = ""
                for t in tokens[1:]:
                    txt_send += t.strip() + " "
                return self.broadcast(contacts, txt_send.strip())
            elif len(tokens) == 1:
                return self.respond(self.msg_bcast_no_text)
            elif not self.BROADCAST_TO_ALL:
                return self.respond(self.msg_bcast_all_not_allowed)
        elif subkw == 'reminder':
            contacts = Contact.objects.all().exclude(name=self.msg.contact.name)
            return self.broadcast(contacts, self.msg_scheduled_reminder.strip(),send_info=False)
        elif subkw == 'xmas':
            return self.respond(self.msg_xmas)     
        else:
            return self.respond(self.msg_unrecognized_subkeyword)
    
    
    
    def help(self):
        self.respond(self.msg_zero_args)
        
        

    def broadcast(self, contacts, text, send_info=True):
        ''' 
        This method was ripped right out of the broadcasting app 
        and modified slightly to suite the demo's needs. It should
        never be reused (use the actual broadcast method for that)
        '''
        if send_info:
            message_body = "%(text)s [from %(user)s to %(group)s]"
        else:
            message_body = "%(text)s"
        body_len = len(text) + 29 #29 chars for info bit at the end
        if body_len > 160:
            return self.respond(self.msg_too_long)
        for contact in contacts:
            if contact.default_connection is None:
                self.info("Can't send to %s as they have no connections" % contact)
            else:
                OutgoingMessage(contact.default_connection, message_body,
                                **{"text": text, 
                                   "user": self.msg.contact.name, 
                                   "group": self.group_name}).send()
        
        logger_msg = getattr(self.msg, "logger_msg", None) 
        if not logger_msg:
            self.error("No logger message found for %s. Do you have the message log app running?" %\
                       self.msg)
        return True
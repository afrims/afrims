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
    msg_xmas = "This is the example xmas message"
    msg_bcast_no_text = "You must include a message after the broadcast keyword"
    msg_bcast_all_not_allowed = "You need to enable broadcasting to all in the demo! See the demo.py handler"
    msg_scheduled_reminder = "Your second vaccine needs to be scheduled in the next 10 days. Someone will be calling you soon."
    msg_unrecognized_subkeyword = "Unrecognized subkeyword (demo hanlder)"
    BROADCAST_TO_ALL = True;
    
    
    def handle(self, text):
        tokens = text.split(' ')
        if len(tokens) <= 0:
            return self.respond(self.msg_zero_args)
        
        subkw = tokens[0]
        
        if subkw == 'broadcast':
            if len(tokens) > 1 & self.BROADCAST_TO_ALL:
                contacts = Contact.objects.all().exclude(self.msg.contact)
                txt_send = ""
                for t in tokens:
                    txt_send += t.strip() + " "
                return self.broadcast(contacts, txt_send.strip())
            elif len(tokens) == 1:
                return self.respond(self.msg_bcast_no_text)
            elif not self.BROADCAST_TO_ALL:
                return self.respond(self.msg_bcast_all_not_allowed)
        elif subkw == 'reminder':
            return self.respond(self.msg_scheduled_reminder)
        elif subkw == 'xmas':
            return self.respond(self.msg_xmas)     
        else:
            return self.respond(self.msg_unrecognized_subkeyword)
    
    
    
    def help(self):
        self.respond(self.msg_zero_args)
        
        

    def broadcast(self, contacts, text):
        ''' 
        This method was ripped right out of the broadcasting app 
        and modified slightly to suite the demo's needs. It should
        never be reused (use the actual broadcast method for that)
        '''
        message_body = "%(text)s [from %(user)s to %(group)s]"
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
'''
Created on Jan 10, 2011

@author: adewinter



This is a simple registration keyword to be used for demo purposes. 

Should be turned off (read: removed) at production time.
'''
from apps.broadcast.handlers.base import BroadcastHandler
from rapidsms.models import Contact
from apps.reminder.models import Group
from django.core.exceptions import ObjectDoesNotExist

class RegisterHandler(BroadcastHandler):
    group_name = ""
    keyword = "register"    #This is the keyword used to trigger a response from this handler.
    help_txt = "send 'register demo <groupname>' to register, groupname is optional"
    BROADCAST_TO_ALL = False;
    
    
    def handle(self, text):
        tokens = self.get_tokens(text)
        if len(tokens) == 1:
            contact = Contact.objects.create(name=tokens[0])
            self.msg.connection.contact = contact
            self.msg.connection.save()
            self.respond("Thanks for registering")
        elif len(tokens) > 1:
            contact = Contact.objects.create(name=tokens[0])
            for group_name in tokens[1:]:
                try:
                    g = Group.objects.get(name=group_name)
                    contact
                except ObjectDoesNotExist:
                    return self.respond('daawwwwwww')
                    
                
        self.respond("token length="+str(len(tokens))+"last token="+str(tokens[len(tokens)-1]))
    
    
    
    def help(self):
        self.respond(self.help_txt)
        
        
    def get_tokens(self, msg_text):
        msg_obj = msg_text.split(' ')
        if not msg_obj:
            self.respond("malformed message")
            return True
        return msg_obj
'''
Created on Jan 10, 2011

@author: adewinter
'''
from apps.broadcast.handlers.base import BroadcastHandler
from rapidsms.models import Contact
from rapidsms.messages.outgoing import OutgoingMessage

class DemoHandler(BroadcastHandler):
    group_name = ""
    keyword = "demo"    #This is the keyword used to trigger a response from this handler.
    msg_help_txt = "You've requested help with the system.\
                    A System Administrator will be calling you shortly.\
                    Please call your care provider in case of emergency."
    
    def handle(self, text):
        return self.help()
    
    def help(self):
        return self.respond(self.msg_help_txt)
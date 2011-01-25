# vim: ai ts=4 sts=4 et sw=4
from rapidsms.models import Contact
from apps.broadcast.handlers.base import BroadcastHandler
from apps.broadcast.handlers.base import UNREGISTERED
import re
from apps.reminder.models import Group
from django.core.exceptions import ObjectDoesNotExist


class MsgHandler(BroadcastHandler):
    
    group_name = ""
    msg_text = ""
    keyword = "msg"    #This is the keyword used to trigger a response from this handler.

    HELP_TEXT = ("To send a message SEND: MSG <GROUP> <your message>.")
    GROUP_NOT_FOUND_TEXT = "There is no group by the name \"%s\". Please try again or send: HELP"
    NO_CONTACTS_IN_GROUP_TEXT = "Sorry there are no contacts in the group you specified (Group:%s)"
    MALFORMED_MESSAGE_TEXT = "Sorry the system did not understand your message. Please try again."
    PATTERN = re.compile(r"^(\w)(\s+)(.{1,})$", re.IGNORECASE)
    
    MESSAGE_EVERYONE_ALLOWED = False;
    
    ######## Canned Responses ##########
    def help(self):
        self.respond(self.HELP_TEXT)
        
    def group_not_found(self, group):
        self.respond(self, (self.GROUP_NOT_FOUND_TEXT % group))
        
    def no_contacts_in_group(self, group):
        self.respond(self, (self.NO_CONTACTS_IN_GROUP_TEXT % group))
        
    def malformed_message(self):
        self.respond(self, self.MALFORMED_MESSAGE_TEXT)
    
    
    
    
    ######### Meat and Potatoes #########
    @property
    def group_name(self):
        return self.get_tokens[0]
        
    def get_tokens(self):
        msg_obj = self.PATTERN.search(self.msg_text.strip())
        if not msg_obj:
            self.malformed_message()
            return True
        groups = msg_obj.groups()
        if not groups:
            self.malformed_message()
            return True
        
        if len(groups) == 0:
            self.MALFORMED_MESSAGE_TEXT
            return True
        
        return groups
    
    def handle(self, text):
        if self.msg.contact is None:
                self.respond(UNREGISTERED)
                return
            
        self.msg_text = text
        tokens = self.get_tokens
        group = tokens[0]
        
        if(group.lower() == "all" and self.MESSAGE_EVERYONE_ALLOWED):
            #send this message to everyone. USE WITH CARE!
            contacts = Contact.objects.all().exclude(self.msg.contact)
        else:
            #check to see if the specified group actually exists
            try:
                Group.objects.get(name__iexact=group)
            except ObjectDoesNotExist:
                self.group_not_found(group)
                return False;
            
            #attempt to get all the contacts from the specified group
            contacts = Contact.objects.filter(group__name=group)
            
        if len(contacts) == 0:
            self.no_contacts_in_group(group)
        
        txt_send = ""
        for t in tokens:
            txt_send += t.strip() + " "
        return self.broadcast(txt_send.strip(), contacts)
        

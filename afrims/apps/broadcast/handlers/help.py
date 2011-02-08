# vim: ai ts=4 sts=4 et sw=4
from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler


class AbcHandler(KeywordHandler):
    
    keyword = "HELP|HLEP|halp" #THIS CAN BE A REGULAR EXPRESSION!


    response_text = "A System Administrator will be calling you shortly.  Please call your care provider in case of emergency. For more features send: INFO"
    def help(self):
        self.respond(self.response_text)
    
    def handle(self, text):
        """
        Handling a message that matches the keyword goes here.
        The keyword at the beginning of the message and the result is stored
        in the 'text' keyword argument of this function.
        
        To let the system know that the message has succesfully been handled
        the function needs to return True (usually by using something like
        return self.respond('some message here')
        
        If the message wasn't handled and you want it to continue onto some other handler
        return without a value (ie just return or let the function finish with no return
        statement)
        """
        
        return self.help()
        
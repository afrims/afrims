from rapidsms.apps.base import AppBase


class CatchAllApp(AppBase):
    """ RapidSMS app to reply to unhandled messages """

    template = """Thank you for contacting us. Please reply with 2 to be """ \
               """called back within 2 days."""

    def default(self, msg):
        """ If we reach the default phase here, always reply with help text """
        msg.respond(self.template)
        return True

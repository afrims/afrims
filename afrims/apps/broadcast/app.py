#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import time
from rapidsms.conf import settings
from rapidsms.apps.base import AppBase
from rapidsms.backends.base import BackendBase
from rapidsms.messages import IncomingMessage, OutgoingMessage
from django.conf import settings


class App(AppBase):
    """
    What
    """


    def _wait_for_message(self, msg):
        countdown = settings.MESSAGE_TESTER_TIMEOUT
        interval  = settings.MESSAGE_TESTER_INTERVAL

        while countdown > 0:
            if msg.processed:
                break

            # messages are usually processed before the first interval,
            # but pause a (very) short time before checking again, to
            # avoid pegging the cpu.
            countdown -= interval
            time.sleep(interval)


    def start(self):
        try:
            self.backend

        except KeyError:
            self.info(
                "To use the message tester app, you must add a bucket " +\
                "backend named 'message_tester' to your INSTALLED_BACKENDS")


    @property
    def backend(self):
        return self.router.backends[settings.BROADCAST_SENDER_BACKEND]


    def ajax_POST_send(self, get, post):
        '''
        send's a broadcast message, params:
        post.get("identity", None) = sender ident
        post.get("text", "")) = message text
        post.get("recipients", None) = recipients, list of connection identities
        '''

        sender_ident = post.get("identity", None)
        msg_text = post.get("text", "") + '::Broadcast from %s' % sender_ident
        idents = post.get("recipients", None)
        if not idents:
            raise Exception('must have recipients for a broadcast message!')
            return

        idents = idents.split(',')

        for ident in idents:
            try:
                conn = Connection.objects.get(identity=ident)
                msg = OutgoingMessage(connection__identity=ident,template=msg_text)
                msg.send()

        return True



#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import time
from rapidsms.conf import settings
from rapidsms.apps.base import AppBase
from rapidsms.models import Contact
from rapidsms.backends.base import BackendBase
from rapidsms.messages import IncomingMessage, OutgoingMessage
from django.conf import settings


class BroadcastApp(AppBase):
    """ RapidSMS app to send broadcast messages """

    cron_schedule = {'minutes': '*'}
    cron_name = 'broadcast-cron-job'
    cron_callback = 'afrims.apps.broadcast.app.scheduler_callback'

    def start(self):
        try:
            schedule = EventSchedule.objects.get(description=self.name)
        except EventSchedule.DoesNotExist:
            schedule = EventSchedule.objects.create(description=self.name,
                                                    callback=self.cron_callback,
                                                    minutes='*')
        schedule.callback = self.cron_callback
        for key, val in self.cron_schedule.iteritems():
            if hasattr(schedule, key):
                setattr(schedule, key, val)
        schedule.save()
        self.info('started')

    def queue_outgoing_messages(self):
        """ generate queued messages for scheduled broadcasts """
        now = datetime.datetime.now()
        broadcasts = Broadcast.objects.filter(date_next_notified__lt=now)
        broadcasts = broadcasts.exclude(schedule_start_date__isnull=True,
                                        schedule_frequency='')
        for broadcast in broadcasts:
            broadcast.queue_outgoing_messages()
            broadcast.set_next_date()
            broadcast.save()

    def send_messages(self, dry_run=False):
        self.debug('{0} running'.format(self.cron_name))
        # grab all broadcasts ready to go out and queue their messages
        self.queue_outgoing_messages()

        messages = BroadcastMessage.objects.filter(status='queued')
        self.info('found {0} messages'.format(messages.count()))
        for message in messages:
            connection = message.recipient.default_connection
            msg = OutgoingMessage(connection=recipient, template=message.text)
            success = True
            if not dry_run:
                try:
                    msg.send()
                except Exception, e:
                    self.exception(e)
                    success = False
            if success:
                message.status = str(OutgoingLog.DELIVERED)
            else:
                message.status = str(OutgoingLog.FAILED)
            message.save()

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


    #def start(self):
    #    try:
    #        self.backend
    #
    #    except KeyError:
    #        self.info(
    #            "To use the message tester app, you must add a bucket " +\
    #            "backend named 'message_tester' to your INSTALLED_BACKENDS")


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
            conn = Connection.objects.get(identity=ident)
            msg = OutgoingMessage(connection__identity=ident,template=msg_text)
            msg.send()

        return True


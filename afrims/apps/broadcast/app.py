#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
import datetime

from rapidsms.apps.base import AppBase
from rapidsms.messages import OutgoingMessage
from rapidsms.contrib.scheduler.models import EventSchedule

from afrims.apps.broadcast.models import Broadcast, BroadcastMessage


def scheduler_callback(router):
    """
    Basic rapidsms.contrib.scheduler.models.EventSchedule callback
    function that runs BroadcastApp.cronjob()
    """
    app = router.get_app("afrims.apps.broadcast")
    app.cronjob()


class BroadcastApp(AppBase):
    """ RapidSMS app to send broadcast messages """

    cron_schedule = {'minutes': '*'}
    cron_name = 'broadcast-cron-job'
    cron_callback = 'afrims.apps.broadcast.app.scheduler_callback'

    def start(self):
        """ setup event schedule to run cron job every minute """
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
        broadcasts = Broadcast.ready.all()
        self.info('found {0} ready broadcast(s)'.format(broadcasts.count()))
        for broadcast in Broadcast.ready.all():
            # TODO: make sure this process is atomic
            count = broadcast.queue_outgoing_messages()
            self.debug('queued {0} broadcast message(s)'.format(count))
            broadcast.set_next_date()
            broadcast.save()

    def send_messages(self):
        """ send queued for delivery messages """
        messages = BroadcastMessage.objects.filter(status='queued')[:50]
        self.info('found {0} message(s) to send'.format(messages.count()))
        for message in messages:
            connection = message.recipient.get_primary_connection()
            msg = OutgoingMessage(connection=connection,
                                  template=message.broadcast.body)
            success = True
            try:
                msg.send()
            except Exception, e:
                self.exception(e)
                success = False
            if success:
                self.debug('message sent successfully')
                message.status = 'sent'
                message.date_sent = datetime.datetime.now()
            else:
                self.debug('message failed to send')
                message.status = 'error'
            message.save()

    def cronjob(self):
        self.debug('{0} running'.format(self.cron_name))
        # grab all broadcasts ready to go out and queue their messages
        self.queue_outgoing_messages()
        # send queued messages
        self.send_messages()


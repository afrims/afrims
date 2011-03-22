#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
import datetime

from rapidsms.apps.base import AppBase
from rapidsms.messages import OutgoingMessage
from rapidsms.contrib.scheduler.models import EventSchedule

from afrims.apps.broadcast.models import Broadcast, BroadcastMessage,\
                                         ForwardingRule


# In RapidSMS, message translation is done in OutgoingMessage, so no need
# to attempt the real translation here.  Use _ so that ./manage.py makemessages
# finds our text.
_ = lambda s: s


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
    
    not_registered = _('Sorry, your mobile number is not registered in the '
                       'required group for this keyword.')
    thank_you = _('Thank you, your message has been queued for delivery.')

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

    def _forwarding_rules(self):
        """ Returns a dictionary mapping rule keywords to rule objects """
        rules = ForwardingRule.objects.all()
        return dict([(rule.keyword.lower(), rule) for rule in rules])

    def handle(self, msg):
        """
        Handles messages that match the forwarding rules in this app.
        """
        msg_parts = msg.text.split()
        rules = self._forwarding_rules()
        if not msg_parts:
            return False
        keyword = msg_parts[0].lower()
        if keyword not in rules:
            return False
        rule = rules[keyword]
        contact = msg.connection.contact
        if not contact or \
          not rule.source.contacts.filter(pk=contact.pk).exists():
            msg.respond(self.not_registered)
            return True
        now = datetime.datetime.now()
        msg_text = [rule.message, ' '.join(msg_parts[1:])]
        msg_text = [m for m in msg_text if m]
        msg_text = ' '.join(msg_text)
        full_msg = 'From {name} ({number}): {body}'\
                   .format(name=contact.name, number=msg.connection.identity,
                           body=msg_text)
        broadcast = Broadcast.objects.create(date_created=now, date=now,
                                             schedule_frequency='one-time',
                                             body=full_msg)
        broadcast.groups.add(rule.dest)
        msg.respond(self.thank_you)

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
            connection = message.recipient.default_connection
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


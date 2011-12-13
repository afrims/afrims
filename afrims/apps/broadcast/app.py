#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.template.loader import render_to_string

from rapidsms.apps.base import AppBase
from rapidsms.messages import OutgoingMessage
from rapidsms.contrib.scheduler.models import EventSchedule

from afrims.apps.broadcast.models import Broadcast, BroadcastMessage,\
                                         ForwardingRule
from afrims.apps.broadcast.views import usage_report_context
from afrims.apps.groups import models as groups
from afrims.apps.reminders.models import Patient


# In RapidSMS, message translation is done in OutgoingMessage, so no need
# to attempt the real translation here.  Use _ so that ./manage.py makemessages
# finds our text.
_ = lambda s: s

JUNK = [':', '\'', '\"', '`', '(', ')',' ']

def scheduler_callback(router):
    """
    Basic rapidsms.contrib.scheduler.models.EventSchedule callback
    function that runs BroadcastApp.cronjob()
    """
    app = router.get_app("afrims.apps.broadcast")
    app.cronjob()


def usage_email_callback(router, *args, **kwargs):
    """
    Send out month email report of broadcast usage.
    """

    today = datetime.date.today()
    report_date = today - datetime.timedelta(days=today.day)
    start_date = datetime.date(report_date.year, report_date.month, 1)
    end_date = report_date
    context = usage_report_context(start_date, end_date)
    context['report_month'] = report_date.strftime('%B')
    context['report_year'] = report_date.strftime('%Y')
    subject_template = _(u'TrialConnect Monthly Report - {report_month} {report_year}')
    subject = subject_template.format(**context)
    body = render_to_string('broadcast/emails/usage_report_message.html', context)
    group_name = settings.DEFAULT_MONTHLY_REPORT_GROUP_NAME
    group, created = groups.Group.objects.get_or_create(name=group_name)
    if not created:
        emails = [c.email for c in group.contacts.all() if c.email]
        send_mail(subject, body, None, emails, fail_silently=True)


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
        name = 'broadcast-monthly-email'
        info = {
            'callback': 'afrims.apps.broadcast.app.usage_email_callback',
            'days_of_month': [1],
            'hours': [12],
            'minutes': [0],
        }
        schedule, created = EventSchedule.objects.get_or_create(description=name,
            defaults=info
        )
        # Uncommenting these lines will reset the schedule every time the router
        # is started.
#        if not created:
#            for key, val in info.iteritems():
#                if hasattr(schedule, key):
#                    setattr(schedule, key, val)  
#        schedule.save()        
        group_name = settings.DEFAULT_MONTHLY_REPORT_GROUP_NAME
        group, _ = groups.Group.objects.get_or_create(name=group_name)
        self.info('started')

    def _forwarding_rules(self):
        """ Returns a dictionary mapping rule keywords to rule objects """
        rules = ForwardingRule.objects.all()
        return dict([(self._clean_keyword(rule.keyword.lower()), rule) for rule in rules])

    def _should_forward_all_from_this_source(self, msg):
        contact = msg.connection.contact
        identifier = contact.name
        rules = self._forwarding_rules()
        for key in rules:
            rule = rules[key]
            if not rule.forward_all_from_source:
                continue
            else: #has checked forward everything from specific source
                if rule.source.contacts.filter(pk=contact.pk).exists(): #this contact is in the group listed as 'source'
                  return (True, rule)
        return (False, None)


    def handle(self, msg):
        """
        Handles messages that match the forwarding rules in this app.
        """
        rules = self._forwarding_rules()
        contact = msg.connection.contact
        if not contact:
            self.debug('No contact found. Returning True')
            msg.respond(self.not_registered)
            return True
        identifier = contact.name
        msg_parts = msg.text.split()
        if not msg_parts:
            self.debug('No message parts. Returning False')
            return False
        forward_all_from_source, forward_all_rule = self._should_forward_all_from_this_source(msg)
        keyword = self._clean_keyword(msg_parts[0].lower())
        if (keyword not in rules) and not forward_all_from_source:
            self.debug(u'{0} keyword not found in rules'.format(keyword))
            return False
        rule = forward_all_rule if forward_all_from_source else rules[keyword]
        if rule.source and not rule.source.contacts.filter(pk=contact.pk).exists():
            self.debug('Responding not registered for regular forwarding rule then Return True')
            msg.respond(self.not_registered)
            return True
        now = datetime.datetime.now()
        msg_text = [rule.message, u' '.join(msg_parts[1:])]
        msg_text = [m for m in msg_text if m]
        msg_text = u' '.join(msg_text)
        identifier = contact.name
        try:
            patient = Patient.objects.get(contact=contact)
            identifier = patient.subject_number
        except ObjectDoesNotExist:
            pass
        full_msg = u'From {name} ({number}): {body}'\
                   .format(name=identifier, number=msg.connection.identity,
                           body=msg_text)
        broadcast = Broadcast.objects.create(date_created=now, date=now,
                                             schedule_frequency='one-time',
                                             body=full_msg, forward=rule)
        broadcast.groups.add(rule.dest)
        msg.respond(self.thank_you)
        
    def _clean_keyword(self, keyword):
        for j in JUNK:
            keyword = keyword.strip(j)
        return keyword

    def queue_outgoing_messages(self):
        """ generate queued messages for scheduled broadcasts """
        broadcasts = Broadcast.ready.all()
        if broadcasts.count() > 0:
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
        if messages.count() > 0:
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
            if success and msg.sent:
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


from datetime import datetime
import re
import urllib2

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest

from rapidsms.backends.http import RapidHttpBackend
from rapidsms.messages.incoming import IncomingMessage as BaseIncoming
from rapidsms.messages.outgoing import OutgoingMessage as BaseOutgoing


class OutgoingMessage(BaseOutgoing):
    pass


class IncomingMessage(BaseIncoming):

    def respond(self, template=None, cls=OutgoingMessage, **kwargs):
        msg = cls(self.connection, template, **kwargs)
        pid = getattr(self, 'pid', None)
        if pid:
            setattr(msg, 'pid', pid)
        self.responses.append(msg)
        return msg


class MegaMobileBackend(RapidHttpBackend):
    default_timeout = 8

    def configure(self, host="localhost", port=8080, config=None, **kwargs):
        if "params_incoming" not in kwargs:
            kwargs["params_incoming"] = "cel=%(phone_number)s&msg=%(message)s"
        if "params_outgoing" not in kwargs:
            kwargs["params_outgoing"] = "cel=%(phone_number)s&msg=%(message)s&pid=%(pid)s"
        if "gateway_url" not in kwargs:
            kwargs["gateway_url"] = "http://api.mymegamobile.com/api.php"
        super(MegaMobileBackend, self).configure(host, port, **kwargs)
        self.config = config or {}

    def message(self, identity, text, received_at=None):
        # import the models here, rather than at the top, to give the
        # orm a chance to initialize. (avoids SETTINGS_MODULE errors.)
        from rapidsms.models import Connection

        # ensure that a persistent connection instance exists for this
        # backend+identity pair. silently create one, if not.
        conn, created = Connection.objects.get_or_create(
            backend=self.model,
            identity=identity)

        return IncomingMessage(
            conn, text, received_at)

    def handle_request(self, request):
        self.debug('Received request: %s' % request.GET)
        sms = request.GET.get(self.incoming_message_param, '')
        sender = request.GET.get(self.incoming_phone_number_param, '')
        if not sms or not sender:
            error_msg = 'ERROR: Missing %(msg)s or %(phone_number)s. parameters received are: %(params)s' % \
                         { 'msg' : self.incoming_message_param, 
                           'phone_number': self.incoming_phone_number_param,
                           'params': unicode(request.GET)
                         }
            self.error(error_msg)
            return HttpResponseBadRequest(error_msg)
        # Megamobile doesn't include our country code on the incoming phone number, apparently
        country_code = settings.COUNTRYCODE
        if not sender.startswith(country_code) and not sender.startswith("+" + country_code):
            sender = "+%s%s" % (country_code, sender)
        pid = request.GET.get('pid', None)
        now = datetime.utcnow()
        try:
            msg = self.message(sender, sms, now)
            if pid:
                # Set pid for responding to this message
                setattr(msg, 'pid', pid)
        except Exception, e:
            self.exception(e)
            raise        
        self.route(msg)
        return HttpResponse('OK')


    def send(self, message):
        self.info('Sending message: %s' % message)
        text = message.text
        if isinstance(text, unicode):
            text = text.encode('utf-8')
        # we do this since http_params_outgoing is a user-defined settings
        # and we don't want things like "%(doesn'texist)s" to throw an error
        http_params_outgoing = self.http_params_outgoing.replace('%(message)s', urllib2.quote(text))
        identity = message.connection.identity
        non_digit = re.compile(r'\D')
        identity = non_digit.sub('', identity)
        http_params_outgoing = http_params_outgoing.replace('%(phone_number)s', urllib2.quote(identity))
        default_pid = self.config.get('default_pid', 0)
        pid = getattr(message, 'pid', default_pid)
        http_params_outgoing = http_params_outgoing.replace('%(pid)s', urllib2.quote(str(pid)))
        url = "%s?%s" % (self.gateway_url, http_params_outgoing)
        try:
            self.debug('Sending: %s' % url)
            response = urllib2.urlopen(url)
        except Exception, e:
            self.exception(e)
            return False
        self.info('SENT')
        info = 'RESPONSE %s' % response.info()
        info = info.replace('\n',' ').replace('\r',',')
        
        self.debug(info)
        return True

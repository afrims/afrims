import datetime
import re
import urllib
import urllib2
import uuid

from django import http
from django.core.exceptions import ImproperlyConfigured

from rapidsms.backends.http import RapidHttpBackend


class TxtNationImproperlyConfigured(ImproperlyConfigured):
    pass


class TxtNationBackend(RapidHttpBackend):
    default_timeout = 8
    encoding = 'UTF-16'

    def configure(self, host="localhost", port=8080, config=None, **kwargs):
        if "params_incoming" not in kwargs:
            kwargs["params_incoming"] = "number=%(phone_number)s&message=%(message)s"
        if "params_outgoing" not in kwargs:
            kwargs["params_outgoing"] = "id=%(id)s&network=%(network)s&number=%(phone_number)s&message=%(message)s"
        if "gateway_url" not in kwargs:
            kwargs["gateway_url"] = "http://client.txtnation.com/mbill.php"
        super(TxtNationBackend, self).configure(host, port, **kwargs)
        self.config = config
        if 'ekey' not in self.config:
            raise TxtNationImproperlyConfigured(u"TxtNation backend missing account ekey")
        if 'cc' not in self.config:
            raise TxtNationImproperlyConfigured(u"TxtNation backend missing account company code")

    def handle_request(self, request):
        if request.method != 'POST':
            self.info(u"Received request but wasn't POST. Doing nothing.")
            return http.HttpResponseNotAllowed(['POST'])
        self.info(u"Received request: %s" % request.POST)
        if 'report' in request.POST:
            self.report(request.POST)
            return http.HttpResponse("OK")
        else:
            msg = self.message(request.POST)
            if msg:
                self.route(msg)
                return http.HttpResponse("OK")
            else:
                return http.HttpResponseBadRequest("")

    def message(self, data):
        sms = data.get(self.incoming_message_param, '')
        sender = data.get(self.incoming_phone_number_param, '')
        if not sms or not sender:
            error_msg = u"ERROR: Missing %(msg)s or %(phone_number)s. parameters received are: %(params)s" % {
                "msg" : self.incoming_message_param, 
                "phone_number": self.incoming_phone_number_param,
                "params": unicode(data)
            }
            self.error(error_msg)
            return None
        now = datetime.datetime.utcnow()
        try:
            msg = super(TxtNationBackend, self).message(sender, sms, now)
        except Exception, e:
            self.exception(e)
            raise
        return msg

    def report(self, data):
        self.info("Delivery Report recieved.")
        from rapidsms.models import DeliveryReport
        action = request.POST.get('action', '')[:255]
        number = request.POST.get('number', '')[:255]
        report_id = request.POST.get('id', '')[:255]
        report = request.POST.get('report', '')[:255]
        DeliveryReport.objects.create(
            report_id=report_id, action=action,
            number=number, report=report,
        )

    def prepare_message(self, message):
        destination = message.connection.identity
        msg = message.text
        is_ascii = self._is_ascii(msg)
        if not is_ascii:
            msg = msg.encode(self.__class__.encoding, 'ignore')
        non_digit = re.compile(r'\D')
        destination = non_digit.sub('', destination)
        data = {
            'message': msg,
            'number':destination,
            'id': uuid.uuid4().hex,
            'reply': str(0),
            'network': self.config.get('network', 'international'),
            'ekey': self.config['ekey'],
            'cc': self.config['cc'],
            'currency': self.config.get('currency', 'usd'),
            'value': self.config.get('value', '0'),
            'title': self.config.get('title', ''),
        }
        return data

    def _is_ascii(self, msg):
        try:
            test = msg.encode('ascii', 'strict')
            return True
        except (UnicodeEncodeError, UnicodeDecodeError, ):
            return False

    def send(self, message):
        self.info(u"Sending message: %s" % message)
        data = self.prepare_message(message)
        self.debug(u"Sending data: %s" % data)
        timeout = self.config.get('timeout', self.default_timeout)
        url = self.gateway_url
        data = urllib.urlencode(data)
        try:
            req = urllib2.Request(url, data)
            self.debug('Sending:: URL: %s, %s' % (url, str(data)))
            response = urllib2.urlopen(req, timeout=timeout)
        except Exception, e:
            self.exception(e)
            return False
        self.info('SENT')
        self.debug(response.read())
        return True

from afrims.settings import *

ADMINS = (
    ('Development Team', 'afrims-dev@dimagi.com'),
)
MANAGERS = ADMINS

INSTALLED_BACKENDS = {
    "message_tester": {
        "ENGINE": "rapidsms.backends.bucket",
    },
    "txtnation" : {"ENGINE":  "afrims.backends.http",
                   "host":"0.0.0.0",
            "port": 9088,
            "gateway_url": "http://client.txtnation.com/mbill.php",
            "params_outgoing": "reply=%(reply)s&id=%(id)s&network=%(network)s&number=%(phone_number)s&message=%(message)s&ekey=<SECRET_EKEY>&cc=dimagi&currency=THB&value=0&title=trialcnct",
            "params_incoming": "action=action&id=%(id)s&number=%(phone_number)s&network=%(network)s&message=%(message)s&shortcode=%(sc)s&country=%(country_code)&billing=%(bill_code)s"
    },
    "twilio": {
        "ENGINE": "rtwilio.backend",
        'host': '173.203.221.48', 'port': '8081',
        'config': {'encoding': 'UTF-8'},
    },
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "afrimsdb",
        "USER": "afrims",
        "PASSWORD": "", # provided by localsettings.py
        "HOST": "localhost",
        "PORT": "5433",
    },
}

#The default backend to be used when creating new patient contacts
#on POST submission of patient data from their server
DEFAULT_BACKEND_NAME = "txtnation"

DEBUG = True

LOG_LEVEL = "DEBUG"
LOG_FILE = '/home/afrims/www/staging/log/router.log'
LOG_FORMAT = "%(asctime)s %(levelname)-8s - %(name)-26s %(message)s"
LOG_SIZE = 33554432 # 2^25
LOG_BACKUPS = 10 # number of logs to keep


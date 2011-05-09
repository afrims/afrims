from afrims.settings import *

ADMINS = (
    ('Development Team', 'afrims-dev@dimagi.com'),
)
MANAGERS = ADMINS

INSTALLED_BACKENDS = {
    "message_tester": {
        "ENGINE": "rapidsms.backends.bucket",
    },
    "twilio": {
        "ENGINE": "rtwilio.backend",
        'host': '173.203.221.48', 'port': '9081',
        'config': {'encoding': 'UTF-8'},
    },
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "afrimsdemo",
        "USER": "afrims",
        "PASSWORD": "", # provided by localsettings.py
        "HOST": "localhost",
        "PORT": "5433",
    },
}

#The default backend to be used when creating new patient contacts
#on POST submission of patient data from their server
DEFAULT_BACKEND_NAME = "twilio"
# unless overridden, all outgoing messages will be sent using this backend
PRIMARY_BACKEND = "twilio"

DEBUG = True

LOG_LEVEL = "DEBUG"
LOG_FILE = '/home/afrims/www/demo/log/router.log'
LOG_FORMAT = "%(asctime)s %(levelname)-8s - %(name)-26s %(message)s"
LOG_SIZE = 33554432 # 2^25
LOG_BACKUPS = 10 # number of logs to keep

COUNTRY_CODE = '1'

# Remove this line to restore the patient import error emails
NOTIFY_ON_PATIENT_IMPORT_ERROR = False

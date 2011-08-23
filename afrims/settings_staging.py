from afrims.settings import *

ADMINS = (
    ('Development Team', 'afrims-dev@dimagi.com'),
)
MANAGERS = ADMINS

INSTALLED_BACKENDS = {
    "message_tester": {
        "ENGINE": "rapidsms.backends.bucket",
    },
    "txtnation" : {
        "ENGINE":  "afrims.backends.txtnation",
        "port": '9087',
        "config": {
            'ekey': '', # In local settings
            'cc': 'dimagi',
            'currency': 'THB',
        }
    },
#    "txtnation" : {"ENGINE":  "afrims.backends.http",
#                   "host":"0.0.0.0",
#            "port": 9088,
#            "gateway_url": "http://client.txtnation.com/mbill.php",
#            "params_outgoing": "reply=%(reply)s&id=%(id)s&network=%(network)s&number=%(phone_number)s&message=%(message)s&ekey=<SECRET_EKEY>&cc=dimagi&currency=THB&value=0&title=trialcnct",
#            "params_incoming": "action=action&id=%(id)s&number=%(phone_number)s&network=%(network)s&message=%(message)s&shortcode=%(sc)s&country=%(country_code)&billing=%(bill_code)s"
#    },
    "twilio": {
        "ENGINE": "rtwilio.backend",
        'host': '173.203.221.48', 'port': '8081',
        'config': {'encoding': 'UTF-8'},
    },
    "mach": {
        "ENGINE": "rmach.backend",
        'host': 'localhost', 'port': '9090', # used for spawned backend WSGI server
        'config': {
            'encoding': 'UTF-8', # optional message encoding
            'encoding_errors': 'ignore', # optional encoding handling 
        }
    },
    "megamobile": {
        "ENGINE": "afrims.backends.megamobile",
        "params_outgoing": "cel=%(phone_number)s&msg=%(message)s&pid=%(pid)s&src=dimagi",
        "gateway_url": "http://api.mymegamobile.com/dimagi",
        "port": "9191",
        'config': {
            'default_pid': '0-156-11884', # for dimagi initiated messages
        }
    },
    "kannel-cebu" : {
        "ENGINE":  "rapidsms.backends.kannel",
        "host": "173.203.221.48",
        "port": 8080,
        "sendsms_url": "http://119.93.159.212:13013/cgi-bin/sendsms",
        "sendsms_params": {"smsc": "usb0-modem",
                           "from": "+639164787841", # not set automatically by SMSC
                           "username": "rapidsms",
                           "password": ""}, # set in localsettings.py
        "coding": 0,
        "charset": "ascii",
        "encode_errors": "ignore", # strip out unknown (unicode) characters
    }
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
DEFAULT_BACKEND_NAME = "kannel-cebu"
# unless overridden, all outgoing messages will be sent using this backend
PRIMARY_BACKEND = 'kannel-cebu'
# if set, the message tester app will always use this backend
TEST_MESSAGER_BACKEND = 'kannel-cebu'

AJAX_PROXY_PORT = 9999

DEBUG = True

LOG_LEVEL = "DEBUG"
LOG_FILE = '/home/afrims/www/staging/log/router.log'
LOG_FORMAT = "%(asctime)s %(levelname)-8s - %(name)-26s %(message)s"
LOG_SIZE = 33554432 # 2^25
LOG_BACKUPS = 10 # number of logs to keep

COUNTRY_CODE = '1'

# Remove this line to restore the patient import error emails
NOTIFY_ON_PATIENT_IMPORT_ERROR = False

# Note the last GIT commit if known
if os.path.exists(os.path.join(PROJECT_PATH,"GIT_LAST_COMMIT")):
    GIT_LAST_COMMIT = open(os.path.join(PROJECT_PATH,"GIT_LAST_COMMIT")).read()



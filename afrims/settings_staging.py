from afrims.settings import *

ADMINS = (
    ('Development Team', 'afrims-dev@dimagi.com'),
)
MANAGERS = ADMINS

INSTALLED_BACKENDS = {
    "message_tester": {
        "ENGINE": "rapidsms.backends.bucket",
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
    }
}

DEBUG = True

LOG_LEVEL = "DEBUG"
LOG_FILE = '/home/afrims/www/staging/log/router.log'
LOG_FORMAT = "%(asctime)s %(levelname)-8s - %(name)-26s %(message)s"
LOG_SIZE = 33554432 # 2^25
LOG_BACKUPS = 10 # number of logs to keep


from afrims.settings import *

INSTALLED_BACKENDS = {
    "message_tester": {
        "ENGINE": "rapidsms.backends.bucket",
    },
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "afrims_staging",
        "USER": "afrims",
        "PASSWORD": "",
        "HOST": "localhost",
    }
}

DEBUG = True


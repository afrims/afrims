from afrims.settings import *

# you should configure your database here before doing any real work.
# see: http://docs.djangoproject.com/en/dev/ref/settings/#databases

# for sqlite3:
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "db.sqlite3",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
# since we might hit the database from any thread during testing, the
# in-memory sqlite database isn't sufficient. it spawns a separate
# virtual database for each thread, and syncdb is only called for the
# first. this leads to confusing "no such table" errors. We create
# a named temporary instance instead.
# in addition, put the database in a ramdisk to speed test runs.
        "TEST_NAME": "/dev/shm/test_db.sqlite3",
    }
}

# for postgresql:
#DATABASES = {
#    "default": {
#        "ENGINE": "django.db.backends.postgresql_psycopg2",
#        "NAME": "afrims_legacy",
#        "USER": "",
#        "PASSWORD": "",
#        "HOST": "",
#    }
#}

# south configuration
SKIP_SOUTH_TESTS = True

PRIMARY_BACKEND = ''
DEFAULT_BACKEND_NAME = 'test-backend'

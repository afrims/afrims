#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
# encoding=utf-8
import os

PROJECT_PATH = os.path.abspath('%s' % os.path.dirname(__file__))

# -------------------------------------------------------------------- #
#                          MAIN CONFIGURATION                          #
# -------------------------------------------------------------------- #

VERSION = '0.2.1' #This doesn't do anything yet, but what the hey.

BROADCAST_SENDER_BACKEND='message_tester'

# to help you get started quickly, many django/rapidsms apps are enabled
# by default. you may wish to remove some and/or add your own.
INSTALLED_APPS = [

    # the essentials.
    "djtables",
    "rapidsms",

    # common dependencies (which don't clutter up the ui).
    "rapidsms.contrib.handlers",
    "rapidsms.contrib.ajax",

    #audit utils
    "auditcare",

    # enable the django admin using a little shim app (which includes
    # the required urlpatterns), and a bunch of undocumented apps that
    # the AdminSite seems to explode without.
    "django.contrib.sites",
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.sessions",
    "django.contrib.contenttypes",
    
    "pagination",
    "django_sorting",
    "south",
    "django_nose",
	"staticfiles",
    "rosetta",
    # "gunicorn",
    "afrims.apps.groups",
    "afrims.apps.broadcast",
    "afrims.apps.reminders",
    "afrims.apps.test_messager",
    "afrims.apps.default_connection",

    # the rapidsms contrib apps.
    # "rapidsms.contrib.export",
    "rapidsms.contrib.httptester",
    "rapidsms.contrib.messagelog",
    "rapidsms.contrib.messaging",
    "rapidsms.contrib.registration",
    "rapidsms.contrib.scheduler",

    "couchlog",

    # this app should be last, as it will always reply with a help message
    "afrims.apps.catch_all",
]


# this rapidsms-specific setting defines which views are linked by the
# tabbed navigation. when adding an app to INSTALLED_APPS, you may wish
# to add it here, also, to expose it in the rapidsms ui.
RAPIDSMS_TABS = [
    ("afrims.apps.broadcast.views.dashboard", "Dashboard"),    
    ("afrims.apps.broadcast.views.send_message", "Send a Message"),
    ("afrims.apps.reminders.views.dashboard", "Appointment Reminders"),
    ("broadcast-forwarding", "Forwarding"),
    ("afrims.apps.groups.views.list_groups", "Groups"),
    ("afrims.apps.groups.views.list_contacts","People"),
#    ("settings", "Settings"),
#    ("rapidsms.contrib.messagelog.views.message_log",       "Message Log"),

#    ("rapidsms.contrib.messaging.views.messaging",          "Messaging"),
#    ("rapidsms.contrib.locations.views.locations",          "Map"),
#    ("rapidsms.contrib.scheduler.views.index",              "Event Scheduler"),
 #   ("rapidsms.contrib.httptester.views.generate_identity", "Message Tester"),

#    ("afrims.apps.reminder.views.dashboard", "Reminder"),

]



# -------------------------------------------------------------------- #
#                         BORING CONFIGURATION                         #
# -------------------------------------------------------------------- #


# debug mode is turned on as default, since rapidsms is under heavy
# development at the moment, and full stack traces are very useful
# when reporting bugs. don't forget to turn this off in production.
DEBUG = TEMPLATE_DEBUG = True


# after login (which is handled by django.contrib.auth), redirect to the
# dashboard rather than 'accounts/profile' (the default).
LOGIN_REDIRECT_URL = "/"


# use django-nose to run tests. rapidsms contains lots of packages and
# modules which django does not find automatically, and importing them
# all manually is tiresome and error-prone.
TEST_RUNNER = "django_nose.NoseTestSuiteRunner"


# for some reason this setting is blank in django's global_settings.py,
# but it is needed for static assets to be linkable.
MEDIA_URL = "/media/"
ADMIN_MEDIA_PREFIX = "/static/admin/"
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(PROJECT_PATH, '..', 'static_files')


# Specify a logo URL for the dashboard layout.html. This logo will show up
# at top left for every tab
LOGO_LEFT_URL = '%simages/trialconnect.png' % STATIC_URL
LOGO_RIGHT_URL = '%simages/tatrc_logo.png' % STATIC_URL
SITE_TITLE = " "
BASE_TEMPLATE = "layout.html"

# this is required for the django.contrib.sites tests to run, but also
# not included in global_settings.py, and is almost always ``1``.
# see: http://docs.djangoproject.com/en/dev/ref/contrib/sites/
SITE_ID = 1


# these weird dependencies should be handled by their respective apps,
# but they're not, so here they are. most of them are for django admin.
TEMPLATE_CONTEXT_PROCESSORS = [
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "staticfiles.context_processors.static",

    #this is for a custom logo on the dashboard (see LOGO_*_URL in settings, above)
    "rapidsms.context_processors.logo",
    "afrims.apps.reminders.context_processors.messages",
    "couchlog.context_processors.static_workaround"
]


MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'django_sorting.middleware.SortingMiddleware',
    'auditcare.middleware.AuditMiddleware',
]
    
# -------------------------------------------------------------------- #
#                           HERE BE DRAGONS!                           #
#        these settings are pure hackery, and will go away soon        #
# -------------------------------------------------------------------- #

AJAX_PROXY_HOST = '127.0.0.1'
AJAX_PROXY_PORT = 9988

MEDIA_ROOT = os.path.join(PROJECT_PATH, 'static')

TEMPLATE_DIRS = [
    os.path.join(PROJECT_PATH, 'templates'),
]

# these apps should not be started by rapidsms in your tests, however,
# the models and bootstrap will still be available through django.
TEST_EXCLUDED_APPS = [
    "django.contrib.sessions",
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rapidsms",
    "rapidsms.contrib.ajax",
    "rapidsms.contrib.httptester",
]

# the project-level url patterns

LANGUAGE_CODE = 'en'

LANGUAGES = (
    ('en', 'English'),
    ('th', 'Thai'),
    ('tl', 'Filipino'),
)

TIME_INPUT_FORMATS = ['%H:%M', '%H:%M:%S']

ROOT_URLCONF = "afrims.urls"

TIME_ZONE = 'America/New_York'

LOGIN_URL = '/account/login/'

SOUTH_MIGRATION_MODULES = {
    'rapidsms': 'afrims.migrations.rapidsms',
}



AUDIT_VIEWS = [
    'afrims.apps.groups.views.list_groups',
    'afrims.apps.groups.views.create_edit_group',
    'afrims.apps.groups.views.delete_group',
    'afrims.apps.groups.views.list_contacts',
    'afrims.apps.groups.views.create_edit_contact',
    'afrims.apps.groups.views.delete_contact',
    'afrims.apps.broadcast.views.send_message',
    'afrims.apps.broadcast.views.list_messages',
    'afrims.apps.broadcast.views.create_edit_rule',
    'afrims.apps.broadcast.views.delete_rule',
    'afrims.apps.broadcast.views.report_graph_data',
    'afrims.apps.reminders.views.create_edit_notification',
    'afrims.apps.reminders.views.delete_notification',
    'afrims.apps.reminders.views.manually_confirm',
    'afrims.apps.reminders.views.dashboard',
    'afrims.apps.reminders.views.report',
    'afrims.apps.reminders.views.receive_patient_record',
    ]

#The default group subjects are added to when their information
#is POSTed to us
DEFAULT_SUBJECT_GROUP_NAME = 'Subjects'
DEFAULT_DAILY_REPORT_GROUP_NAME = 'Daily Report Recipients'
DEFAULT_MONTHLY_REPORT_GROUP_NAME = 'Monthly Report Recipients'
DEFAULT_CONFIRMATIONS_GROUP_NAME = 'Confirmation Recipients'

#The default backend to be used when creating new patient contacts
#on POST submission of patient data from their server
DEFAULT_BACKEND_NAME = "twilio"
# unless overridden, all outgoing messages will be sent using this backend
PRIMARY_BACKEND = 'twilio'
# if set, the message tester app will always use this backend
TEST_MESSAGER_BACKEND = 'twilio'

STATICFILES_DIRS = (os.path.join(PROJECT_PATH, 'static'),
                    os.path.join(PROJECT_PATH, 'templates'))

#STATICFILES_EXCLUDED_APPS = (
#    'django.contrib.admin',
#)

# Note the last GIT commit if known
if os.path.exists(os.path.join(PROJECT_PATH,"GIT_LAST_COMMIT")):
    GIT_LAST_COMMIT = open(os.path.join(PROJECT_PATH,"GIT_LAST_COMMIT")).read()

INTERNATIONAL_DIALLING_CODE = '+'

# RapidSMS wants this to be set
RAPIDSMS_HANDLERS_EXCLUDE_APPS = []

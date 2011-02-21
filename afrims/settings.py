#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
# encoding=utf-8
import os

# -------------------------------------------------------------------- #
#                          MAIN CONFIGURATION                          #
# -------------------------------------------------------------------- #

VERSION = '0.2.1' #This doesn't do anything yet, but what the hey.

BROADCAST_SENDER_BACKEND='message_tester'

# to help you get started quickly, many django/rapidsms apps are enabled
# by default. you may wish to remove some and/or add your own.
INSTALLED_APPS = [

    # the essentials.
    "django_nose",
    "djtables",
    "rapidsms",

    # common dependencies (which don't clutter up the ui).
    "rapidsms.contrib.handlers",
    "rapidsms.contrib.ajax",

    # enable the django admin using a little shim app (which includes
    # the required urlpatterns), and a bunch of undocumented apps that
    # the AdminSite seems to explode without.
    "django.contrib.sites",
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.sessions",
    "django.contrib.contenttypes",
    
    "pagination",
    "south",
    # "gunicorn",
    "afrims.apps.groups",
    "afrims.apps.broadcast",
    "afrims.apps.offsite",
    "afrims.apps.reminders",
    "afrims.apps.test_messager",

    # the rapidsms contrib apps.
    "rapidsms.contrib.default",
    "rapidsms.contrib.export",
    "rapidsms.contrib.httptester",
    "rapidsms.contrib.locations",
    "rapidsms.contrib.messagelog",
    "rapidsms.contrib.messaging",
    "rapidsms.contrib.registration",
    "rapidsms.contrib.scheduler",
    "rapidsms.contrib.echo",
]


# this rapidsms-specific setting defines which views are linked by the
# tabbed navigation. when adding an app to INSTALLED_APPS, you may wish
# to add it here, also, to expose it in the rapidsms ui.
RAPIDSMS_TABS = [
    ("afrims.apps.broadcast.views.send_message", "Send a Message"),
    ("afrims.apps.reminders.views.dashboard", "Appointment Reminders"),
    ("afrims.apps.groups.views.dashboard", "Cold Chain"),
    ("afrims.apps.groups.views.dashboard", "Groups"),
    ("rapidsms.contrib.registration.views.registration","People"),
    ("afrims.apps.groups.views.dashboard", "Settings"),
#    ("rapidsms.contrib.messagelog.views.message_log",       "Message Log"),

#    ("rapidsms.contrib.messaging.views.messaging",          "Messaging"),
#    ("rapidsms.contrib.locations.views.locations",          "Map"),
#    ("rapidsms.contrib.scheduler.views.index",              "Event Scheduler"),
 #   ("rapidsms.contrib.httptester.views.generate_identity", "Message Tester"),

#    ("afrims.apps.reminder.views.dashboard", "Reminder"),

]



# Specify a logo URL for the dashboard layout.html. This logo will show up
# at top left for every tab
LOGO_LEFT_URL = '/static/images/trialconnect.png'
LOGO_RIGHT_URL = '/static/images/tatrc.png'


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
MEDIA_URL = "/static/"
ADMIN_MEDIA_PREFIX = "/static/admin/"


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

    #this is for a custom logo on the dashboard (see LOGO_*_URL in settings, above)
    "rapidsms.context_processors.logo",
]


MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'pagination.middleware.PaginationMiddleware',
]

#The default group subjects are added to when their information
#is POSTed to us
DEFAULT_SUBJECT_GROUP_NAME = 'subjects'


#The default backend to be used when creating new patient contacts
#on POST submission of patient data from their server
DEFAULT_BACKEND_NAME = "txtnation"
    
# -------------------------------------------------------------------- #
#                           HERE BE DRAGONS!                           #
#        these settings are pure hackery, and will go away soon        #
# -------------------------------------------------------------------- #

AJAX_PROXY_HOST = '127.0.0.1'
AJAX_PROXY_PORT = 9988

PROJECT_PATH = os.path.abspath('%s' % os.path.dirname(__file__))

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

LANGUAGE_CODE='en'

ROOT_URLCONF = "afrims.urls"

TIME_ZONE = 'America/New_York'

LOGIN_URL = '/account/login/'


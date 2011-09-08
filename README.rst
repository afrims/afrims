AFRIMS
======

The RapidSMS AFRIMS project...

Development Workflow
====================

We are using git-flow to help manage our development process.

Learn how to use git-flow at:
  http://jeffkreeftmeijer.com/2010/why-arent-you-using-git-flow/

You can download and install git-flow from:
  https://github.com/nvie/gitflow

Learn more about the methodology behind it at:
  http://nvie.com/posts/a-successful-git-branching-model/

Developer Setup
===============

**Prerequisites:**

* A Linux-based development environment including Python 2.6.  Ubuntu 10.04 or
  later is recommended.  At present, Windows-based environments are not
  actively supported.

* PostgreSQL and the appropriate Python bindings (``psycopg2``).  In
  Debian-based distributions, you can install these using ``apt-get``, e.g.::

    sudo apt-get install postgresql python-psycopg2 libpq-dev

* The following additional build dependencies::

    sudo apt-get install libxslt1-dev libxml2-dev

* CouchDB is required for logging and audit tracking purposes::

    sudo apt-get install couchdb

See
  http://wiki.apache.org/couchdb/Installing_on_Ubuntu
for more information about couch.


* Install pip and virtualenv, and make sure virtualenv is up to date, e.g.::

    easy_install pip
    pip install -U virtualenv
    pip install -U virtualenvwrapper

* Install git-flow (see above).

**To setup a local development environment, follow these steps:**

#. Clone the code from git, checkout the ``develop`` branch, and initialize
   git-flow::

    git clone git@github.com:afrims/afrims.git
    cd afrims
    git checkout develop
    git flow init # just accept all the default answers
  
#. Create a Python virtual environment for this project::

    mkvirtualenv --distribute afrims-dev
    workon afrims-dev

#. Install the project dependencies into the virtual environment::

    ./bootstrap.py

#. Create local settings file and initialize a development database::

    cp localsettings.py.example localsettings.py
    createdb afrims_devel
    ./manage.py syncdb

#. Update the submodules::

    git submodule init
    git submodule update

#. In one terminal, start RapidSMS router::

    mkdir logs
    ./manage.py runrouter

#. In another terminal, start the Django development server::

    ./manage.py runserver

#. Open http://localhost:8000 in your web browser and you should see an
   **Installation Successful!** screen.


Production Setup
================

#. Sync the production server with network (or otherwise correct) time e.g. using NTP.

#. Set the TIME_ZONE setting in Django to reflect the right time zone.

#. Specify the default language for SMS (where?)

#. Update the django EMAIL settings so that email reports don't get sent from webmaster@localhost


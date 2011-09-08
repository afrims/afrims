#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import sys, os
from os.path import exists, join
from django.core.management import execute_manager


# use a default settings module if none was specified on the command line
DEFAULT_SETTINGS = 'afrims.localsettings'
DEFAULT_TEST_SETTINGS = 'afrims.test_localsettings'
settings_specified = any([arg.startswith('--settings=') for arg in sys.argv])
if not settings_specified and len(sys.argv) >= 2:
    if sys.argv[1] == 'test':
        settings = DEFAULT_TEST_SETTINGS
    else:
        settings = DEFAULT_SETTINGS
    if 'RAPIDSMS_SETTINGS' in os.environ:
        settings = os.environ['RAPIDSMS_SETTINGS']
    sys.argv.append('--settings=%s' % settings)
    print "NOTICE: using default settings module '%s'" % settings

filedir = os.path.dirname(__file__)
sys.path.append(os.path.join(filedir,'..','submodules','auditcare'))
sys.path.append(os.path.join(filedir,'..','submodules','dimagi-utils'))
sys.path.append(os.path.join(filedir,'..','submodules','couchlog'))

if __name__ == "__main__":
    # all imports should begin with the full Python package ('afrims.'):
    project_root = os.path.abspath(os.path.dirname(__file__))
    # TODO: rename all apps.* imports to afrims.apps.*
    # if project_root in sys.path:
    #     sys.path.remove(project_root)
    sys.path.insert(0, os.path.dirname(project_root))
    sys.path.append(os.path.abspath(os.path.join(project_root,'..','submodules','rapidsms','lib')))

    from afrims import settings
    execute_manager(settings)


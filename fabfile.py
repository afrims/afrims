"""
Server layout:
    ~/services/
        This contains two subfolders
            /apache/
            /supervisor/
        which hold the configurations for these applications
        for each environment (staging, demo, etc) running on the server.
        Theses folders are included in the global /etc/apache2 and
        /etc/supervisor configurations.

    ~/www/
        This folder contains the code, python environment, and logs
        for each environment (staging, demo, etc) running on the server.
        Each environment has its own subfolder named for its evironment
        (i.e. ~/www/staging/logs and ~/www/demo/logs).
"""

import os, sys

from fabric.api import *
from fabric.contrib import files, console
from fabric.contrib.project import rsync_project
from fabric import utils
from fabric.decorators import hosts


RSYNC_EXCLUDE = (
    '.DS_Store',
    '.git',
    '*.pyc',
    '*.example',
    '*.db',
)
env.home = '/home/afrims'
env.project = 'afrims'
env.code_repo = 'git://github.com/afrims/afrims.git'


def _join(*args):
    """
    We're deploying on Linux, so hard-code that path separator here.
    """
    return '/'.join(args)


def _setup_path():
    env.root = _join(env.home, 'www', env.environment)
    env.log_dir = _join(env.home, 'www', env.environment, 'log')
    env.code_root = _join(env.root, 'code_root')
    env.project_root = _join(env.code_root, env.project)
    env.project_media = _join(env.code_root, 'media')
    env.project_static = _join(env.project_root, 'static')
    env.virtualenv_root = _join(env.root, 'python_env')
    env.services = _join(env.home, 'services')

 

def setup_dirs():
    """ create (if necessary) and make writable uploaded media, log, etc. directories """
    sudo('mkdir -p %(log_dir)s' % env, user=env.sudo_user)
    sudo('chmod a+w %(log_dir)s' % env, user=env.sudo_user)
    # sudo('mkdir -p %(project_media)s' % env, user=env.sudo_user)
    # sudo('chmod a+w %(project_media)s' % env, user=env.sudo_user)
    # sudo('mkdir -p %(project_static)s' % env, user=env.sudo_user)
    sudo('mkdir -p %(services)s/apache' % env, user=env.sudo_user)
    sudo('mkdir -p %(services)s/supervisor' % env, user=env.sudo_user)


def staging():
    """ use staging environment on remote host"""
    env.code_branch = 'develop'
    env.sudo_user = 'afrims'
    env.environment = 'staging'
    env.thb_router_port = '9087' # TxtNation
    env.php_router_port = '9191' # Mega mobile
    env.server_port = '9002'
    env.server_name = 'staging-trialconnect.dimagi.com'
    env.hosts = ['173.203.221.48']
    env.settings = '%(project)s.localsettings' % env
    _setup_path()


def demo():
    """ use demo environment on remote host"""
    env.code_branch = 'develop'
    env.sudo_user = 'afrims'
    env.environment = 'demo'
    env.thb_router_port = '9081'
    env.php_router_port = '9081'
    env.server_port = '9003'
    env.server_name = 'demo-trialconnect.dimagi.com'
    env.hosts = ['173.203.221.48']
    env.settings = '%(project)s.localsettings' % env
    _setup_path()


def production():
    """ use production environment on remote host"""
    env.code_branch = 'master'
    env.sudo_user = 'afrims'
    env.environment = 'production'
    env.router_port = '9089'
    env.server_port = '9002'
    env.server_name = 'kpp-trialconnect.dimagi.com'
    env.hosts = ['10.84.168.245']
    env.settings_files=['kpp','cebu']
    env.settings = ['afrims.localsettings_production_%s' % (env.settings_files[0]), 'afrims.localsettings_production_%s' % env.settings_files[1]]
    _setup_path()


def production_kpp():
    """ use production environment on remote host"""
    env.code_branch = 'master'
    env.sudo_user = 'afrims'
    env.environment = 'production-kpp'
    env.router_port = '9089'
    env.server_port = '9002'
    env.server_name = 'kpp-trialconnect.dimagi.com'
    env.hosts = ['10.84.168.245']
    env.settings = '%(project)s.localsettings' % env
    _setup_path()


def production_cebu():
    """ use production environment on remote host"""
    env.code_branch = 'master'
    env.sudo_user = 'afrims'
    env.environment = 'production-cebu'
    env.router_port = '9088'
    env.server_port = '9001'
    env.server_name = 'cebu-trialconnect.dimagi.com'
    env.hosts = ['10.84.168.245']
    env.settings = '%(project)s.localsettings' % env
    _setup_path()


def bootstrap():
    """ initialize remote host environment (virtualenv, deploy, update) """
    require('root', provided_by=('staging', 'production'))
    if env.environment == 'production':
        utils.abort("Bootstrap to production aborted! Bootstrap scripts not fully functional/tested for production env!")
    sudo('mkdir -p %(root)s' % env, user=env.sudo_user)
    clone_repo()
    setup_dirs()
    update_services()
    create_virtualenv()
    update_requirements()
    setup_translation()
    fix_locale_perms()


def create_virtualenv():
    """ setup virtualenv on remote host """
    require('virtualenv_root', provided_by=('staging', 'production'))
    args = '--clear --distribute --no-site-packages'
    sudo('virtualenv %s %s' % (args, env.virtualenv_root), user=env.sudo_user)


def clone_repo():
    """ clone a new copy of the git repository """
    with cd(env.root):
        sudo('git clone %(code_repo)s %(code_root)s' % env, user=env.sudo_user)


def deploy():
    """ deploy code to remote host by checking out the latest via git """
    require('root', provided_by=('staging', 'production'))
    if env.environment == 'production':
        if not console.confirm('Are you sure you want to deploy production?',
                               default=False):
            utils.abort('Production deployment aborted.')
    with settings(warn_only=True):
        stop()
    fix_locale_perms()
    with cd(env.code_root):
        sudo('git pull', user=env.sudo_user)
        sudo('git checkout %(code_branch)s' % env, user=env.sudo_user)
        sudo('git rev-parse HEAD >%(project_root)s/GIT_LAST_COMMIT' % env, user=env.sudo_user)
        sudo('git submodule init')
        sudo('git submodule update')
    if env.environment == 'production':
        migrate_production()
    else:
        migrate()
    collectstatic()
    touch()
    start()


def update_requirements():
    """ update external dependencies on remote host """
    require('code_root', provided_by=('staging', 'production'))
    requirements = _join(env.code_root, 'requirements')
    with cd(requirements):
        cmd = ['pip install']
        cmd += ['-E %(virtualenv_root)s' % env]
        cmd += ['--requirement %s' % _join(requirements, 'apps.txt')]
        sudo(' '.join(cmd), user=env.sudo_user)


def touch():
    """ touch wsgi file to trigger reload """
    require('code_root', provided_by=('staging', 'production'))
    with cd(env.project_root):
        sudo('touch %s.wsgi' % env.environment, user=env.sudo_user)


def update_services():
    """ upload changes to services such as nginx """

    with settings(warn_only=True):
        stop()
    upload_supervisor_conf()
    upload_apache_conf()
    start()
    netstat_plnt()


def configtest():    
    """ test Apache configuration """
    require('root', provided_by=('staging', 'production'))
    run('apache2ctl configtest')


def apache_reload():    
    """ reload Apache on remote host """
    require('root', provided_by=('staging', 'production'))
    run('sudo /etc/init.d/apache2 reload')


def apache_restart():
    """ restart Apache on remote host """
    require('root', provided_by=('staging', 'production'))
    run('sudo /etc/init.d/apache2 restart')


def netstat_plnt():
    """ run netstat -plnt on a remote host """
    require('hosts', provided_by=('production', 'staging'))
    run('sudo netstat -plnt')


def stop():
    """ stop server and router on remote host """
    require('environment', provided_by=('staging', 'demo', 'production'))
    if env.environment == 'production':
        production_routers_stop()
        production_servers_stop()
    else:
        _supervisor_command('stop %(environment)s:*' % env)


def start():
    """ start server and router on remote host """
    require('environment', provided_by=('staging', 'demo', 'production'))
    if env.environment == 'production':
        production_routers_start()
        production_servers_start()
    else:
        _supervisor_command('start %(environment)s:*' % env)

def router_start():  
    """ start router on remote host """
    require('environment', provided_by=('staging', 'demo', 'production'))
    _supervisor_command('start  %(environment)s-router' % env)


def router_stop():  
    """ stop router on remote host """
    require('environment', provided_by=('staging', 'demo', 'production'))
    _supervisor_command('stop  %(environment)s-router' % env)


def servers_start():
    ''' Start the gunicorn servers '''
    require('environment', provided_by=('staging', 'demo', 'production'))
    _supervisor_command('start  %(environment)s-server' % env)


def servers_stop():
    ''' Stop the gunicorn servers '''
    require('environment', provided_by=('staging', 'demo', 'production'))
    _supervisor_command('stop  %(environment)s-server' % env)


def migrate():
    """ run south migration on remote environment """
    require('project_root', provided_by=('production', 'demo', 'staging'))
    with cd(env.project_root):
        run('%(virtualenv_root)s/bin/python manage.py syncdb --all --noinput --settings=%(settings)s' % env)
        run('%(virtualenv_root)s/bin/python manage.py migrate --noinput --settings=%(settings)s' % env)


def migrate_production():
    ''' run south migration on remote production environment '''
    require('project_root', provided_by=('production'))
    with cd(env.project_root):
        for i,settings_path in enumerate(env.settings_files):
            run('%s/bin/python manage.py syncdb --noinput --settings=%s' % (env.virtualenv_root, env.settings[i]))
            run('%s/bin/python manage.py migrate --noinput --settings=%s' % (env.virtualenv_root, env.settings[i]))

def collectstatic():
    """ run collectstatic on remote environment """
    require('project_root', provided_by=('production', 'demo', 'staging'))
    with cd(env.project_root):
        if env.environment == 'production':
            for i,settings_path in enumerate(env.settings_files):
                sudo('%s/bin/python manage.py collectstatic --noinput --settings=%s' % (env.virtualenv_root,env.settings[i]), user=env.sudo_user)
        else:
            sudo('%(virtualenv_root)s/bin/python manage.py collectstatic --noinput --settings=%(settings)s' % env, user=env.sudo_user)


def reset_local_db():
    """ Reset local database from remote host """
    require('code_root', provided_by=('production', 'staging'))
    if env.environment == 'production':
        utils.abort('Local DB reset is for staging environment only')
    question = 'Are you sure you want to reset your local ' \
               'database with the %(environment)s database?' % env
    sys.path.append('.')
    if not console.confirm(question, default=False):
        utils.abort('Local database reset aborted.')
    if env.environment == 'staging':
        from afrims.settings_staging import DATABASES as remote
    else:
        from afrims.settings_production import DATABASES as remote
    from afrims.localsettings import DATABASES as loc
    local_db = loc['default']['NAME']
    remote_db = remote['default']['NAME']
    with settings(warn_only=True):
        local('dropdb %s' % local_db)
    local('createdb %s' % local_db)
    host = '%s@%s' % (env.user, env.hosts[0])
    local('ssh -C %s sudo -u afrims pg_dump -Ox %s | psql %s' % (host, remote_db, local_db))


def setup_translation():
    """ Setup the git config for commiting .po files on the server """
    run('sudo -H -u %s git config --global user.name "AFRIMS Translators"' % env.sudo_user)
    run('sudo -H -u %s git config --global user.email "afrims-dev@dimagi.com"' % env.sudo_user)


def fix_locale_perms():
    """ Fix the permissions on the locale directory """
    require('root', provided_by=('staging', 'production'))
    locale_dir = '%s/afrims/locale/' % env.code_root
    sudo('chown -R afrims %s' % locale_dir)
    sudo('chgrp -R www-data %s' % locale_dir)
    sudo('chmod -R g+w %s' % locale_dir)


def commit_locale_changes():
    """ Commit locale changes on the remote server and pull them in locally """
    fix_locale_perms()
    with cd(env.code_root):
        run('sudo -H -u %s git add afrims/locale' % env.sudo_user)
        run('sudo -H -u %s git commit -m "updating translation"' % env.sudo_user)
    local('git pull ssh://%s%s' % (env.host, env.code_root))


def upload_supervisor_conf():
    """Upload and link Supervisor configuration from the template."""
    require('environment', provided_by=('staging', 'demo', 'production'))
    template = os.path.join(os.path.dirname(__file__), 'services', 'templates', 'supervisor.conf')
    destination = '/var/tmp/supervisor.conf'
    files.upload_template(template, destination, context=env)
    enabled =  os.path.join(env.services, u'supervisor/%(environment)s.conf' % env)
    run('sudo chown -R afrims %s' % destination)
    run('sudo chgrp -R www-data %s' % destination)
    run('sudo chmod -R g+w %s' % destination)
    run('sudo -u %s mv -f %s %s' % (env.sudo_user, destination, enabled))
    _supervisor_command('update')


def upload_apache_conf():
    """Upload and link Supervisor configuration from the template."""
    require('environment', provided_by=('staging', 'demo', 'production'))
    template = os.path.join(os.path.dirname(__file__), 'services', 'templates', 'apache.conf')
    destination = '/var/tmp/apache.conf'
    files.upload_template(template, destination, context=env)
    enabled =  os.path.join(env.services, u'apache/%(environment)s.conf' % env)
    run('sudo chown -R afrims %s' % destination)
    run('sudo chgrp -R www-data %s' % destination)
    run('sudo chmod -R g+w %s' % destination)
    run('sudo -u %s mv -f %s %s' % (env.sudo_user, destination, enabled))
    apache_reload()

def production_servers_stop():
    require('environment', provided_by=('production'))
    _supervisor_command('stop production-cebu:production-server-cebu')
    _supervisor_command('stop production-kpp:production-server-kpp')

def production_servers_start():
    require('environment', provided_by=('production'))
    _supervisor_command('start production-cebu:production-server-cebu')
    _supervisor_command('start production-kpp:production-server-kpp')

def production_servers_restart():
    require('environment', provided_by=('production'))
    _supervisor_command('restart production-cebu:production-server-cebu')
    _supervisor_command('restart production-kpp:production-server-kpp')

def production_routers_stop():
    require('environment', provided_by=('production'))
    _supervisor_command('stop production-cebu:production-router-cebu')
    _supervisor_command('stop production-kpp:production-router-kpp')

def production_routers_start():
    require('environment', provided_by=('production'))
    _supervisor_command('start production-cebu:production-router-cebu')
    _supervisor_command('start production-kpp:production-router-kpp')

def production_routers_restart():
    require('environment', provided_by=('production'))
    _supervisor_command('restart production-cebu:production-router-cebu')
    _supervisor_command('restart production-kpp:production-router-kpp')

def _supervisor_command(command):
    require('hosts', provided_by=('staging', 'production'))
    sudo('supervisorctl %s' % command)

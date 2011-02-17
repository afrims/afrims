import os

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
env.home = '/home/afrims/'
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
    env.settings = '%(project)s.localsettings' % env


def setup_dirs():
    """ create (if necessary) and make writable uploaded media, log, etc. directories """
    run('mkdir -p %(log_dir)s' % env)
    run('chmod a+w %(log_dir)s' % env)
    # run('mkdir -p %(project_media)s' % env)
    # run('chmod a+w %(project_media)s' % env)
    # run('mkdir -p %(project_static)s' % env)
    run('mkdir -p %(services)s' % env)


def staging():
    """ use staging environment on remote host"""
    env.code_branch = 'develop'
    env.user = 'afrims'
    env.environment = 'staging'
    env.hosts = ['173.203.221.48']
    _setup_path()


def production():
    """ use production environment on remote host"""
    utils.abort('Production deployment not yet implemented.')


def bootstrap():
    """ initialize remote host environment (virtualenv, deploy, update) """
    require('root', provided_by=('staging', 'production'))
    run('mkdir -p %(root)s' % env)
    clone_repo()
    setup_dirs()
    create_virtualenv()
    deploy()
    update_requirements()


def create_virtualenv():
    """ setup virtualenv on remote host """
    require('virtualenv_root', provided_by=('staging', 'production'))
    args = '--clear --distribute'
    run('virtualenv %s %s' % (args, env.virtualenv_root))


def clone_repo():
    """ clone a new copy of the git repository """
    with cd(env.root):
        run('git clone %(code_repo)s %(code_root)s' % env)


def deploy():
    """ deploy code to remote host by checking out the latest via git """
    require('root', provided_by=('staging', 'production'))
    if env.environment == 'production':
        if not console.confirm('Are you sure you want to deploy production?',
                               default=False):
            utils.abort('Production deployment aborted.')
    router_stop()
    with cd(env.code_root):
        run('git checkout %(code_branch)s' % env)
        run('git pull')
    touch()
    router_start()


def update_requirements():
    """ update external dependencies on remote host """
    require('code_root', provided_by=('staging', 'production'))
    requirements = _join(env.code_root, 'requirements')
    with cd(requirements):
        cmd = ['pip install']
        cmd += ['-q -E %(virtualenv_root)s' % env]
        cmd += ['--requirement %s' % _join(requirements, 'apps.txt')]
        run(' '.join(cmd))


def touch():
    """ touch wsgi file to trigger reload """
    require('code_root', provided_by=('staging', 'production'))
    with cd(env.project_root):
        run('touch %s.wsgi' % env.environment)


def update_services():
    """ upload changes to services such as nginx """
    rsync_project(remote_dir=env.home, local_dir="services")
    apache_reload()
    router_stop()
    router_start()
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


def router_start():  
    """ start router on remote host """
    require('root', provided_by=('staging', 'production'))
    run('sudo start afrims-router')


def router_stop():  
    """ stop router on remote host """
    require('root', provided_by=('staging', 'production'))
    run('sudo stop afrims-router')


def migrate():
    """ run south migration on remote environment """
    require('project_root', provided_by=('production', 'staging'))
    with cd(env.project_root):      
        run('%(virtualenv_root)s/bin/python manage.py syncdb --noinput --settings=%(settings)s' % env)        
        run('%(virtualenv_root)s/bin/python manage.py migrate --noinput --settings=%(settings)s' % env)


def collectstatic():
    """ run collectstatic on remote environment """
    require('project_root', provided_by=('production', 'staging'))
    with cd(env.project_root):      
        run('%(virtualenv_root)s/bin/python manage.py collectstatic --noinput --settings=%(settings)s' % env)


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
    env.settings = '%(project)s.localsettings' % env


def setup_dirs():
    """ create (if necessary) and make writable uploaded media, log, etc. directories """
    sudo('mkdir -p %(log_dir)s' % env, user=env.sudo_user)
    sudo('chmod a+w %(log_dir)s' % env, user=env.sudo_user)
    # sudo('mkdir -p %(project_media)s' % env, user=env.sudo_user)
    # sudo('chmod a+w %(project_media)s' % env, user=env.sudo_user)
    # sudo('mkdir -p %(project_static)s' % env, user=env.sudo_user)
    sudo('mkdir -p %(services)s' % env, user=env.sudo_user)


def staging():
    """ use staging environment on remote host"""
    env.code_branch = 'develop'
    env.sudo_user = 'afrims'
    env.environment = 'staging'
    env.hosts = ['173.203.221.48']
    _setup_path()


def production():
    """ use production environment on remote host"""
    utils.abort('Production deployment not yet implemented.')


def bootstrap():
    """ initialize remote host environment (virtualenv, deploy, update) """
    require('root', provided_by=('staging', 'production'))
    sudo('mkdir -p %(root)s' % env, user=env.sudo_user)
    clone_repo()
    setup_dirs()
    create_virtualenv()
    deploy()
    update_requirements()


def create_virtualenv():
    """ setup virtualenv on remote host """
    require('virtualenv_root', provided_by=('staging', 'production'))
    args = '--clear --distribute'
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
        router_stop()
    with cd(env.code_root):
        sudo('git checkout %(code_branch)s' % env, user=env.sudo_user)
        sudo('git pull', user=env.sudo_user)
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
        sudo(' '.join(cmd), user=env.sudo_user)


def touch():
    """ touch wsgi file to trigger reload """
    require('code_root', provided_by=('staging', 'production'))
    with cd(env.project_root):
        sudo('touch %s.wsgi' % env.environment, user=env.sudo_user)


def update_services():
    """ upload changes to services such as nginx """
    with settings(warn_only=True):
        router_stop()
    # use a two stage rsync process because we are not connecting as the
    # afrims user
    remote_dir = 'tmp-services/'
    rsync_project(remote_dir=remote_dir, local_dir="services/", delete=True)
    sudo("rsync -av --delete %s %s" %
         (remote_dir, _join(env.home, 'services')), user=env.sudo_user)
    # copy the upstart script to /etc/init
    run("sudo cp %s /etc/init" % _join(env.home, 'services', env.environment,
                                       'upstart', 'afrims-router.conf'))
    apache_reload()
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


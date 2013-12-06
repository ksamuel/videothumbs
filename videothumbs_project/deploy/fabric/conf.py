# -*- coding: utf-8 -*-


from __future__ import unicode_literals, absolute_import


from path import path

import getpass
import re
import os
import sys

from fabric.api import task, env


PROJECT_NAME = "videothumbs"
CUR_DIR = path(__file__).realpath().parent

sys.path.append(CUR_DIR)


@task
def conf(repo_dir, user=None, hosts=None, project_name=PROJECT_NAME, stage='prod',
        port=22, django_settings_module=PROJECT_NAME + '_project.settings.local_settings',
        **kwargs):
    """
        Configure shared variables for all tasks. Call it before anything
    """

    env.hosts = hosts
    env.port = port
    env.stage = stage
    env.project_name = project_name
    env.user = user or project_name
    env.user_dir = path('/home') / env.user

    env.local_repo_dir = CUR_DIR.parent.parent.parent.parent
    env.local_deploy_dir = env.local_repo_dir / 'src' / (PROJECT_NAME + '_project') / 'deploy'

    env.venv_dir =  env.user_dir / '.virtualenvs' / project_name
    env.python_bin = env.venv_dir / 'bin' / 'python'

    env.repo_dir = path(repo_dir)
    env.src_dir = env.repo_dir  / 'src'

    env.project_dir = env.src_dir / (project_name + '_project')
    env.settings_dir = env.project_dir / 'settings'
    env.deploy_dir = env.project_dir / 'deploy'
    env.local_settings = env.settings_dir / 'local_settings.py'

    env.etc_dir = env.src_dir.parent / 'etc'
    env.var_dir = env.src_dir.parent / 'var'

    env.log_dir = env.var_dir / 'log'
    env.upload_dir = env.var_dir / 'upload'
    env.pics_dir = env.var_dir / 'pictures'
    env.static_dir = env.var_dir / 'static'
    env.img_dir = env.var_dir / 'static' / 'img'

    env.deploy_dir = env.project_dir / 'deploy'

    env.wsgi_server_socket = '127.0.0.1:7777'

    env.django_settings_module = django_settings_module

    os.environ['DJANGO_SETTINGS_MODULE'] = django_settings_module

    for name, value in kwargs.items():
        setattr(env, name, value)


@task
def dev(user=getpass.getuser(), hosts=None, port=22, *args, **kwargs):
    """
        Shortcut to configure most options for dev.
    """
    hosts = hosts or ['127.0.0.1']

    # try to switch the port to the proper one automatically when on localhost
    if hosts == ['127.0.0.1'] or hosts == ['localhost']:
        try:
            m = re.search('Port\s+(\d+)\s*', open('/etc/ssh/sshd_config').read())
            port = int(m.groups()[0])
        except (IOError, OSError, AttributeError, ValueError):
            pass

    conf(user=user, hosts=hosts or ['127.0.0.1'], port=port,
         repo_dir=CUR_DIR.parent.parent.parent.parent, site_port=6666,
         domain_name='localhost', stage='dev')


@task
def prod(user=PROJECT_NAME, hosts=['62.210.132.15'], port=22, *args, **kwargs):
    """
        Shortcut to configure most options for prod.
    """
    repo_dir = path('/home') / PROJECT_NAME / 'repo'
    conf(user=user, hosts=hosts, port=port, repo_dir=repo_dir,
         site_port=80, domain_name=hosts[0])

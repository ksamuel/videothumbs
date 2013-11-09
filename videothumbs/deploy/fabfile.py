#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

"""
  Global deployment script for the common parts of the SF project.

  Call it doing :

  fab -u username -H host_ip command[:args]

  E.G:

  fab -u test -H 192.168.0.1 setup:role=prod

"""

from __future__ import unicode_literals, absolute_import

import getpass
import re

from path import path

import fabtools
from fabtools import require

from fabric.api import task, env

# TODO: ensure server time is set to UTC

PROJECT_NAME = "videothumbs"
CUR_DIR = path(__file__).realpath().parent

@task
def conf(user=None, hosts=None, project_dir=None, project_name=PROJECT_NAME,
        port=22):
    """
        Configure shared variables for all tasks. Call it before anything
    """
    env.hosts = hosts
    env.port = port
    env.user = user or project_name
    env.user_dir = path('/home') / user

    env.venv_dir =  env.user_dir / '.virtualenvs' / project_name

    env.project_dir = project_dir or (env.user_dir / "src" / PROJECT_NAME)
    env.src_dir = env.project_dir.parent
    env.etc_dir = env.src_dir.parent / 'etc'
    env.var_dir = env.src_dir.parent / 'var'


@task
def dev(user=getpass.getuser(), hosts=None, port=22, *args, **kwargs):
    """
        Give some
    """
    hosts = hosts or ['127.0.0.1']

    # try to switch the port to the proper one automatically when on localhost
    if hosts == ['127.0.0.1'] or hosts == ['localhost']:
        try:
            m = re.search('Port\s+(\d+)\s*', open('/etc/ssh/sshd_config').read())
            port = int(m.groups()[0])
        except (IOError, OSError, AttributeError, ValueError):
            pass

    conf(user, hosts=hosts or ['127.0.0.1'], port=port, project_dir=CUR_DIR.parent)


@task
def setup_user(password, ssh_key):
    """
        First command to user before running general setup. Create the
        user under which you will run the other commands.

        Usage exemple:

        fab dev setup_user:password="IOPF8!7@04$",ssh_key="/home/you/.ssh/id_dsa.pub"\
             --port 34 --user root
    """
    require.user(PROJECT_NAME, password=password, ssh_public_keys=ssh_key)


@task
def setup_dirs():
    """
        Create some empty dirs for the static and config files.
    """
    for d in env.etc_dir, env.var_dir:
        require.directory(d, owner=env.user)


@task
def setup(database_password=None):
    """
        General setup for the project. Will call setup_db and setup_dirs after
        settings up the virtual env and installing required
        deb and pypi packages.

        Usage example :

            fab dev setup:database_password=jkfsd-78% --port 34
    """

    require.deb.packages([
        'python',
        'python-dev',
        'virtualenvwrapper',
        'gcc',
        'build-dep',

        # redis
        'redis-server',

    ])

    require.service.redis()

    # ensure virtualenv configuration (ex: line in bashrc)
    # with from fabric.contrib.files import append, contains, exists

    require.python.virtualenv(env.venv_dir, user=env.user)
    require.python.pip()

    with fabtools.python.virtualenv(env.venv_dir):
        require.python.requirements(CUR_DIR / "requirements.txt")

    setup_dirs()



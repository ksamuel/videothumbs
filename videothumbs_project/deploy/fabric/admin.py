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


from fabric.api import task, sudo, env
from fabric.contrib.console import confirm

from fabtools import require, postgres

from . import setup


@task
def supervisorctl(service=None, command='restart'):
    """
        Run command
    """
    service = service or env.project_name
    sudo('supervisorctl "%s" "%s"' % (command, service))


@task
def repo(url="git@github.com:CharlesdeG/Vdeothumbs.git", dest=None):
    """
        Update repo from `url` to remote `dest`.
    """

    require.git.working_copy(url, dest or env.repo_dir)


@task
def deploy():
    repo()
    supervisorctl()


@task
def destroy_database(database):
    confirmation = confirm('This will detroy the database %s'
                           ' for good. Are you sure?' % database, default=False)
    if confirmation:
        sql = 'DROP DATABASE %s' % database
        postgres._run_as_pg('''psql -t -A -c "%s"''' % sql)


@task
def reset_db(project_name):
    project_name = project_name or env.project_name
    destroy_database(project_name)
    setup.db(project_name, project_name)
    setup.django_project(project_name)

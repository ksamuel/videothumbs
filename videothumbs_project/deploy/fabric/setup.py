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

from path import path

from fabric.api import task, env, sudo, settings, shell_env, run, cd
from fabric.contrib.files import sed, put, append, exists, contains

import fabtools
from fabtools import require, postgres

from render_template import render

from videothumbs_project.deploy.fabric.utils import manage_py


@task
def time(tz='UTC', restart_cron=True):
    """
        Ensure time is set to UTC and synchronized with an NTP server.
    """
    sed('/etc/timezone', '.*', tz, use_sudo=True)
    sudo('dpkg-reconfigure  --frontend noninteractive  tzdata')

    if restart_cron:
        require.service.restarted('cron')

    require.deb.packages(['ntp'])


@task
def user(password, ssh_key):
    """
        First command to user before running general setup. Create the
        user under which you will run the other commands.

        Usage exemple:

        fab dev user:password="IOPF8!7@04$",ssh_key="/home/you/.ssh/id_dsa.pub"\
             --port 34 --user root
    """
    require.user(env.project_name, password=password, ssh_public_keys=ssh_key)


@task
def repo(url="git@github.com:CharlesdeG/Vdeothumbs.git", dest=None, key_file=None):
    """
        Clone repo from `url` to remote `dest` using LOCAL `key_file`.

        `key_file` will be uploaded to the user .ssh dir.
    """
    ssh_dir = env.user_dir / '.ssh'

    if not key_file:
        key_file = env.local_deploy_dir / 'videothumbs_fabric_rsa'

    put(unicode(key_file), unicode(ssh_dir))
    put(key_file + '.pub', unicode(ssh_dir))

    append(ssh_dir / 'config', 'Host github.com')
    append(ssh_dir / 'config', '    IdentityFile %s' % (ssh_dir / key_file.namebase))
    run('chmod 700 "%s" -R' % ssh_dir)

    require.git.working_copy(url,  dest or env.repo_dir)


@task
def fs():
    """
        Create some empty dirs for the static and config files.
    """
    for name, value in env.items():
        if name.endswith('dir') and 'local' not in name:
            require.directory(value, owner=env.user)

    if not exists(env.settings_dir / 'local_settings.py'):
        append(env.local_settings, ('# -*- coding: utf-8 -*-\n\n'
                                    'from __future__ import unicode_literals, '
                                    'absolute_import\n\n'
                                    'from .{} import *\n\n').format(env.stage))


@task
def db(password, db_name=None, user=None):
    """
        Install and setup a postgres DB, creating a database with rights
        given to the current user.
    """
    db_name = db_name or env.project_name
    user = user or db_name
    require.deb.packages(['python-psycopg2', 'libpq-dev'])
    require.postgres.server()
    require.postgres.user(user, password=password)
    require.postgres.database(db_name, user)

    # add power to manage the DB to the user so it can create and delete
    # test database
    sql = " ALTER ROLE %s WITH CREATEDB;" % user
    postgres._run_as_pg('''psql -t -A -c "%s"''' % sql)

    # add pwd to local_settings
    if not contains(env.local_settings, password):
        db_settings = "DATABASES['default']['PASSWORD'] = '''{password}'''"
        append(env.local_settings, db_settings.format(password=password))

    # allow connection using password
    sed('/etc/postgresql/9.1/main/pg_hba.conf',
        'local   all             all                                     peer',
        'local   all             all                                     md5',
        use_sudo=True)

    require.service.restarted('postgresql')


@task
def image_support():
    require.deb.packages([
        # image magick
        'imagemagick',
        'libjpeg8',
        'libjpeg8-dev',
    ])

    require.deb.packages([
        # PIL
        'libjpeg62',
        'libjpeg62-dev',
        'zlib1g-dev'
    ])

@task
def redis():
    require.deb.packages([
        'redis-server',
    ])

    require.service.started('redis-server')


@task
def base_packages():
    require.deb.packages([
        'python',
        'python-dev',
        'virtualenvwrapper',
        'gcc',
        'curl', # for pip
        # for lxml
        'libxslt1-dev',
        'libxml2-dev'
    ])
    require.python.pip()


@task
def confort_packages():
    require.deb.packages([
        'vim',
        'screen'
    ])


@task
def nginx(template=None, output=None, link_name=None,
          engine='django', **vars):
    """
        Install nginx, configure it to proxy a WSGI site and serve static
        images.
    """

    link_name = link_name or (env.project_name + '.conf')
    require.nginx.server()
    template = template or (env.local_deploy_dir / 'templates' / 'nginx_wsgi.conf')
    output =  output or (env.etc_dir / 'nginx_wsgi.conf')

    if not vars:
        vars = env

    render(template, output, engine='django', use_sudo=True, **vars)

    link = path('/etc/nginx/sites-enabled') / link_name
    with settings(warn_only=True, hide=('warnings', 'running', 'stdout', 'stderr')):
        sudo("rm %s" % link)
    sudo("ln -s %(output)s %(link)s" % locals())

    require.service.restarted('nginx')


@task
def email(password):
    if not contains(env.local_settings, password):
        email_settings = "EMAIL_HOST_PASSWORD = '''{}'''".format(password)
        append(env.local_settings, email_settings)


@task
def supervisor():
    """
        Install and run supervisor, and ensure it starts a gunicorn
        process serving the django site.
    """
    require.deb.packages([
        'supervisor',
    ])

    require.supervisor.process(
            name=env.project_name,
            command=('%s manage.py run_gunicorn localhost:7777 '
                     '--settings=%s_project.settings.local_settings '
                     '--workers 3 ') % (env.python_bin, env.project_name),
            directory=env.src_dir,
            user=env.user,
            stdout_logfile=env.log_dir / 'gunicorn.log')


    # TODO : add ./manage.py celery  worker  --autoscale=1,2
    # TODO: add ./manage.py celery  beat --schedule var/celerybeat-schedule

    with settings(warn_only=True):
        require.service.restarted('supervisor')

    sudo('supervisorctl restart ' + env.project_name)



@task
def python_libs():
    require.python.virtualenv(env.venv_dir, user=env.user)

    s = 'export DJANGO_SETTINGS_MODULE="videothumbs_project.settings.local_settings"'
    append(env.venv_dir / 'bin' / 'postactivate', s)

    with fabtools.python.virtualenv(env.venv_dir):
        require.python.requirements(env.deploy_dir / "requirements.txt")


@task
def django_project(superuser_pwd, settings_module=None):
    """
        Run manage.py commands
    """
    settings_module = settings_module or env.django_settings_module
    with cd(env.src_dir):
        with shell_env(DJANGO_SETTINGS_MODULE=settings_module):

            manage_py('syncdb --noinput')
            manage_py('collectstatic --noinput')

            create_super_user = ("from django.contrib.auth.models import User; "
                                 "User.objects.filter(username='{user}').count() or User.objects.create_superuser('{user}', "
                                 "'context@{domain}', password='{password}')").format(
                                    user= env.user,
                                    domain=env.domain_name,
                                    password=superuser_pwd)

            set_site_domain = ("from django.contrib.sites.models import Site; "
                               "Site.objects.filter(domain='example.com')"
                               ".update(domain='{domain}', name='{name}')").format(
                                 domain= env.domain_name,
                                 name=env.project_name)

            with fabtools.python.virtualenv(env.venv_dir):
                with cd(env.src_dir):
                    run('echo "' + create_super_user + '" | ./manage.py shell')
                    run('echo "' + set_site_domain + '" | ./manage.py shell')

            manage_py('migrate django_extensions')
            manage_py('migrate djcelery')
            manage_py('migrate userena')
            manage_py('migrate guardian')
            manage_py('migrate core')
            manage_py('migrate music')

            manage_py('check_permissions')


@task
def all(db_password, su_password):
    """
        General setup for the project. Will call db and dirs after
        settings up the virtual env and installing required
        deb and pypi packages.

        Usage example :

            fab dev setup:database_password=jkfsd-78% --port 34
    """

    # Setup ssh key got github and clone repo or update to last item
    repo()
    # Setup server so it uses UTC
    time()
    # Setup empty directories for static, logs, etc. And local_settings.Py
    fs()
    # Just add email settings to local_settings
    email()
    # Install python packages and requirements package for futur compilation
    base_packages()
    # Lib spécifically required for image processing
    image_support()
    # Install and run redis
    redis()
    # Install and run nginx. Add a WSGI site to it.
    nginx()
    # Install and run posgres. Create users, tables... And add db credentials to
    # project settings.
    db(db_password)
    # Install requirements.txt
    python_libs()
    # Run manage.py boilerplate (syncdb, collectatic, migrate, etc)
    django_project(su_password)
    # Install and run supervisor with a gunicorn instance
    supervisor()

    # Packages used when you are manually connecting to the server via SSH
    confort_packages()


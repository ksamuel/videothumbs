# -*- coding: utf-8 -*-


import fabtools
from fabric.api import task, env, cd, run


@task
def manage_py(command):
    """
        Run a manage.py command
    """
    with fabtools.python.virtualenv(env.venv_dir):
        with cd(env.src_dir):
            run('./manage.py %s' % command)



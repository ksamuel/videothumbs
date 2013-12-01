#! /bin/bash

export PYTHONPATH=.
export DJANGO_SETTINGS_MODULE='videothumbs_project.settings.test_settings'
py.test --reuse-db --capture=no --verbose $@

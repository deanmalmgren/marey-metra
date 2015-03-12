"""
Use to run development server on remote machine.
"""
# standard library
import sys

# 3rd party
from fabric.api import env, task, local, run, settings, cd, sudo, lcd, hide

# local
import decorators


@task(default=True)
@decorators.needs_environment
def default():
    """Run the django development server."""
    with cd(env.remote_path):
        run('./web/manage.py runserver 0.0.0.0:8000')

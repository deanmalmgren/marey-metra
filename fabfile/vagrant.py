# standard library
import os

# 3rd party
from fabric.api import env, task, local
from fabric import colors

# local
import utils
import decorators

@task
@decorators.needs_environment
def up():

    # bring up ze box
    local((
        "vagrant up "
        "--provider=%(provider)s "
        "--no-provision "
        "%(host_string)s "
    ) % env)

    # friendly reminder to provision account
    print(colors.green((
        "server '%(host_string)s' launched! "
        "remember to provision when all servers are launched with\n"
        "    fab %(host_string)s provision"
    )) % env)

@task
@decorators.needs_environment
def destroy():
    local('vagrant destroy -f %(host_string)s' % env)

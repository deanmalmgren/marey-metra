# 3rd party
from fabric.api import env, task, execute

# local
import utils
import provision

from fabtools.vagrant import vagrant

# shared environment between local machines and remote machines
# (anything that is different gets overwritten in environment-setting
# functions)
env.mysql_root_password = 'tiyp,marey'
env.django_user = 'marey'
env.django_password = 'tiyp,marey'
env.django_db = 'marey'


@task
def dev():
    """define development server"""
    env.provider = "virtualbox"
    env.remote_path = '/vagrant'
    utils.set_hosts_from_config()

    # TODO do we want to start all the hosts?
    # or just the first one?
    if env.hosts:
        execute(vagrant, env.hosts[0])
    else:
        msg = "No hosts defined in the configuration file"
        raise FabricException(msg)

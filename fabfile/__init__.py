# 3rd party
from fabric.api import env, task, execute

# local
import utils
import provision

from fabtools.vagrant import vagrant

@task
def dev():
    """define development server"""
    env.provider = "virtualbox"
    utils.set_hosts_from_config()
    
    # TODO do we want to start all the hosts?
    # or just the first one?
    if env.hosts:
        execute(vagrant, env.hosts[0])
    else:
        msg = "No hosts defined in the configuration file"
        raise FabricException(msg)

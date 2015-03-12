import os

from fabric.api import env, task, execute
from fabtools.vagrant import vagrant

import utils
import provision
import launch
import serve

# shared environment between local machines and remote machines
# (anything that is different gets overwritten in environment-setting
# functions)
env.mysql_root_password = 'tiyp,marey'
env.django_user = 'marey'
env.django_password = 'tiyp,marey'
env.django_db = 'marey'
env.repository_path = 'git@github.com:deanmalmgren/marey-metra.git'
env.ssh_directory = os.path.expanduser(os.path.join('~', '.ssh'))
env.site_name = 'marey-metra.datasco.pe'

@task
def dev():
    """define development server"""
    env.provider = "virtualbox"
    env.remote_path = '/vagrant'
    env.config_type = 'development'
    env.use_repository = False

    utils.set_hosts_from_config()
    execute(vagrant, env.hosts[0])

@task
def prod():
    env.provider = "digitalocean"
    env.remote_path = '/srv/www/marey-metra'
    env.config_type = 'production'
    env.branch = 'master'
    env.use_repository = True

    utils.set_env_with_ssh('marey-metra')

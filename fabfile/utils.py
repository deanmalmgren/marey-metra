# standard library
import os
import ConfigParser

# 3rd party
import requests
from fabric.api import *
from fabric import colors
import fabtools
from paramiko import SSHConfig

# local
import exceptions

def fabfile_root():
    return os.path.dirname(os.path.abspath(__file__))

def fabfile_templates_root():
    return os.path.join(fabfile_root(), "templates")

def project_root():
    return os.path.dirname(fabfile_root())

def remote_project_root():
    return env.remote_path

def remote_templates_root():
    return os.path.join(remote_project_root(), "fabfile/templates")

def requirements_root():
    return os.path.join(project_root(), "requirements")

def remote_requirements_root():
    return os.path.join(remote_project_root(), "requirements")

def get_config_parser():
    parser = ConfigParser.RawConfigParser()
    parser.read(os.path.join(project_root(), "config.ini"))
    return parser

def set_hosts_from_config():
    parser = get_config_parser()
    env.hosts = parser.get('servers', env.provider).split(",")

def ssh_config(ssh_config_filename, name):
    config = SSHConfig()
    with open(ssh_config_filename) as stream:
        config.parse(stream)
    return config.lookup(name)

def set_env_with_ssh(host):
    ssh_config_filename = os.path.join(env.ssh_directory, 'config')
    ssh_config_object = ssh_config(ssh_config_filename, host)
    env.user = ssh_config_object['user']
    env.hosts = [ssh_config_object['hostname']]

    # can't specify relative path in ssh config file for IdentityFile,
    # so it's easiest to configure this here.
    env.key_filename = os.path.join(env.ssh_directory, 'id_rsa')
    env.disable_known_hosts = True  # emulating vagrant-ssh

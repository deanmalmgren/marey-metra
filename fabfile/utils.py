# standard library
import os
import ConfigParser

# 3rd party
import requests
from fabric.api import *
from fabric import colors
import fabtools

# local
import exceptions

def fabfile_root():
    return os.path.dirname(os.path.abspath(__file__))

def fabfile_templates_root():
    return os.path.join(fabfile_root(), "templates")

def project_root():
    return os.path.dirname(fabfile_root())

def remote_project_root():
    return "/vagrant"

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

"""
Functions for provisioning environments with fabtools (eat shit puppet!)
"""
# standard library
import sys
import copy
import os
from distutils.util import strtobool

# 3rd party
import fabric
from fabric.context_managers import quiet
from fabric.api import env, task, local, run, settings, cd, sudo, lcd
import fabtools
from fabtools.vagrant import vagrant_settings

# local
import decorators
import utils

@task
@decorators.needs_environment
def apt_get_update(max_age=86400*7):
    """refresh apt-get index if its more than max_age out of date
    """
    try:
        fabtools.require.deb.uptodate_index(max_age=max_age)
    except AttributeError:
        msg = (
            "Looks like your fabtools is out of date. "
            "Try updating fabtools first:\n"
            "    sudo pip install fabtools==0.17.0"
        )
        raise Exception(msg)


@task
@decorators.needs_environment
def python_packages():
    """install python packages"""
    filename = os.path.join(utils.remote_requirements_root(), "python")
    fabtools.require.python.requirements(filename, use_sudo=True)


@task
@decorators.needs_environment
def debian_packages():
    """install debian packages"""
    
    # get the list of packages
    filename = os.path.join(utils.requirements_root(), "debian")
    with open(filename, 'r') as stream:
        packages = stream.read().strip().splitlines()

    # install them all with fabtools.
        fabtools.require.deb.packages(packages)


@task
@decorators.needs_environment
def packages():
    """install all packages"""
    debian_packages()
    python_packages()


@task
@decorators.needs_environment
def setup_shell_environment():
    """setup the shell environment on the remote machine"""

    # change into the /vagrant directory by default
    template = os.path.join(
        utils.fabfile_templates_root(),
        '.bash_profile',
    )
    fabtools.require.files.file(
        path="/home/vagrant/.bash_profile",
        contents="cd /vagrant",
    )


@task
@decorators.needs_environment
def setup_analysis():
    """prepare analysis environment"""
        
    # write a analysis.ini file that has the provider so we can
    # easily distinguish between development and production
    # environments when we run our analysis
    template = os.path.join(
        utils.fabfile_templates_root(), 
        "server_config.ini",
    )
    fabtools.require.files.template_file(
        path="/vagrant/server_config.ini",
        template_source=template,
        context=env,
    )

    # create a data directory where all of the analysis and raw
    # data is stored. 
    data_dir = "/vagrant/data"
    fabtools.require.files.directory(data_dir)


def set_timezone(timezone='America/Chicago', restart_services=()):
    """Set system timezone, and optional require a list of services to be
    restarted. See:
    https://github.com/ronnix/fabtools/issues/142
    http://en.wikipedia.org/wiki/List_of_tz_database_time_zones
    http://askubuntu.com/a/41616/76346

    """
    fabtools.utils.run_as_root('echo "%s" > /etc/timezone' % timezone)
    fabtools.utils.run_as_root('dpkg-reconfigure --frontend noninteractive tzdata')
    for service in restart_services:
        fabtools.require.service.restarted(service)


def require_timezone(timezone='America/Chicago', restart_services=()):
    """See docstring for set_timezone."""

    # grep the /etc/timezone file to check if it's set
    command = 'grep -q "^%s$" /etc/timezone' % timezone
    with quiet():
        result = run(command)

    # don't do anything if time zone is already set correctly
    if result.return_code == 0:
        return None
    
    # set timezone if needed
    elif result.return_code == 1:
        set_timezone(timezone, restart_services=restart_services)

    # don't know how this would happen
    else:
        msg = "Unexpected return code '%s' from '%s'" % \
            (result.return_code, command)
        raise FabricException(msg)


@task(default=True)
@decorators.needs_environment
def default(do_rsync=True):
    """run all provisioning tasks"""
    # http://stackoverflow.com/a/19536667/564709
    if isinstance(do_rsync, (str, unicode,)):
        do_rsync = bool(strtobool(do_rsync))

    # run all of these provisioning tasks in the order specified here
    apt_get_update()

    # install debian packages first to make sure any compiling python
    # packages have necessary dependencies
    packages()

    # set time zone
    require_timezone()

    # set up anything else that should be done on the virtual machine
    # to get it into the same state for everyone
    setup_shell_environment()
    setup_analysis()

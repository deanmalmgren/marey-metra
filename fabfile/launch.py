import os

from fabric.api import env, task, local, run, settings, cd, sudo, lcd
import fabtools

import decorators
import utils

@task(default=True)
@decorators.needs_environment
def initialize():
    """A lot of what `vagrant up` does (maybe everything?) is it creates
    a virtual server, sets up the 'vagrant' user, and configures
    ssh. Instead of running `vagrant up` for our production
    environment, we manually created a server on linode (running
    Ubuntu 12.04). Now we need to run this command to finish setting
    up the users and ssh configuration.

    - Need to write an .ssh/config file with the information about the
      production server.

    - Need to generate a ssh key with ssh-keygen, and put in .ssh
      directory. Then the key needs to be added as a "deploy key" on
      github once on the repository.

    """
    # going to run with root, but set up for the user specified in
    # environment, so store this before entering user=root context
    user = env.user

    with settings(user='root'):

        # make a user with sudo privileges and www-data access
        fabtools.require.user(
            user,
            shell='/bin/bash',
            extra_groups=['www-data'],
        )
        fabtools.require.users.sudoer(user)

        # set up passwordless ssh for the user
        public_key_path = os.path.join(
            utils.project_root(),
            env.ssh_directory,
            'id_rsa.pub',
        )
        fabtools.user.add_ssh_public_key(user, public_key_path)

        # put the private key on the production server to be used as
        # the "deploy key" on github, see:
        # https://help.github.com/articles/managing-deploy-keys
        private_key_path = os.path.join(
            utils.project_root(),
            env.ssh_directory,
            'id_rsa',
        )
        fabtools.require.files.directory('/home/%s/.ssh' % user)
        fabtools.require.files.file('/home/%s/.ssh/id_rsa' % user,
                                    source=private_key_path,
                                    owner=user,
                                    mode='600')

        # make sure that a directory exists and has correct permissions
        # where we'll put the repository
        parent_dir = os.path.dirname(env.remote_path)
        fabtools.require.files.directory(parent_dir,
                                         owner=user, group='www-data')

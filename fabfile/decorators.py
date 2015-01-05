import functools

from fabric.api import env

import exceptions

def needs_environment(function):
    """Make sure the environment is set up for deployment commands."""

    @functools.wraps(function)
    def wrapper(*args, **kwargs):

        # check for host_string
        if env.host_string is None:
            raise exceptions.UnspecifiedHostError

        # do the original function
        return function(*args, **kwargs)

    return wrapper

from fabric.colors import *

class FabricException(Exception):

    # make sure the exception output is red
    def __str__(self):
        return red(super(FabricException, self).__str__())

class UnspecifiedHostError(FabricException):
    def __init__(self):
        super(UnspecifiedHostError, self).__init__(
            "no hosts specified --- call this fabric task after a task "
            "that sets up the environment"
        )

class VagrantSshConfigNotReady(FabricException):
    def __init__(self):
        super(VagrantSshConfigNotReady, self).__init__(
            "fill me in with a useful error message"
        )

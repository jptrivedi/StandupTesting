import os
import pymongo
import systems
import uuid

from fabric.api import run, sudo
from fabric.contrib.files import *
from fabric.decorators import parallel
from fabric.utils import abort

env.warn_only = True

def run_through_test(sysname='ubuntu'):
    #get our operator
    #TODO use getattr here to load the class
    operator = None
    if sysname == 'debian':
        operator = systems.debian_operator()
    elif sysname == 'ubuntu':
        operator = systems.ubuntu_operator()
    elif sysname == 'rhel':
        operator = systems.rhel_operator()
    else:
        systems.abort_with_message('Could not find system: ' + sysname)

    operator.install_old('2.6.1')
    operator.check_installed(version='2.6.1')

    operator.start()
    operator.check_started()

    operator.restart()
    operator.check_started()

    operator.stop()
    operator.check_stopped()

    #install current / upgrade
    operator.install()
    operator.check_installed()

    operator.start()
    operator.check_started()

    operator.restart()
    operator.check_started()

    operator.stop()
    operator.check_stopped()

    print "SUCCEEDED"

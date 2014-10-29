import os
import pymongo
import systems
import uuid

from fabric.api import run, sudo
from fabric.contrib.files import *
from fabric.decorators import parallel
from fabric.utils import abort

env.warn_only = True

def get_operator(sysname, spawn_host):
    #TODO use getattr here to load the class
    operator = None
    if sysname == 'debian':
        operator = systems.debian_operator()
    elif sysname == 'ubuntu14':
        operator = systems.ubuntu_operator('trusty')
    elif sysname == 'ubuntu12':
        operator = systems.ubuntu_operator('precise')
    elif sysname == 'rhel7':
        operator = systems.rhel_operator(7, spawn_host)
    elif sysname == 'rhel6':
        operator = systems.rhel_operator(6, spawn_host)
    elif sysname == 'rhel5':
        operator = systems.rhel_operator(5, spawn_host)
    else:
        systems.abort_with_message('Could not find system: ' + sysname)

    return operator

def execute_start_stop_tests(operator):
    operator.start()
    operator.check_started()

    operator.restart()
    operator.check_started()

    operator.stop()
    operator.check_stopped()

def str_to_bool(s):
    if s.lower() in ('True', 'true'):
        return True
    else:
        return False

def run_through_test(sysname='ubuntu', enterprise=False, upgrade=True, spawn_host=True):
    operator = get_operator(sysname, spawn_host)
    upgrade = str_to_bool(upgrade)
    enterprise = str_to_bool(enterprise)

    if upgrade:
        operator.install_old('2.6.1', enterprise=enterprise)
        operator.check_installed(version='2.6.1')
        execute_start_stop_tests(operator)

    #install current / upgrade
    operator.install(enterprise=enterprise)
    operator.check_installed()
    execute_start_stop_tests(operator)

    print "SUCCEEDED"

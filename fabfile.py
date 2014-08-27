import os
import pymongo
import uuid

from fabric.api import cd, get, lcd, local, put, run, settings, sudo
from fabric.contrib.files import *
from fabric.decorators import parallel
from fabric.utils import abort

HOST_NAME = 'ec2-54-91-10-1.compute-1.amazonaws.com'
USER_NAME = 'admin'
KEYP = '/Users/ace/keys/spawntest'

env.hosts = [HOST_NAME]
env.user = USER_NAME
env.key_filename = KEYP


def abort_with_message(message):
    abort(message)   

def install_mongod():
    sudo('apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10')
    sudo('echo deb http://downloads-distro.mongodb.org/repo/debian-sysvinit dist 10gen > /etc/apt/sources.list.d/mongodb.list')
    sudo('apt-get update')
    sudo('apt-get -y install mongodb-org')

def check_mongod_installed():
    basemsg = 'check_mongod_installed failed: '
    #check existence of config file
    if not exists('/etc/mongod.conf'):
         abort_with_message(basemsg + 'config file not found')
    #TODO should we the contents of the config file?

    #check existence of binaries
    if not exists('/usr/bin/mongod'):
        abort_with_message(basemsg + 'mongod binary not found')
    #TODO should we check other binaries?

    #check existence of data dir?
    if not exists('/var/lib/mongodb'):
        abort_with_message(basemsg + 'mongod binary not found')

def start_mongod():
    sudo('service mongod start')

def check_mongod_started():
    basemsg = 'check_mongod_started failed: '
    #confirm log exists
    if not exists('/var/log/mongodb/mongod.log'):
        abort_with_message(basemsg + 'mongod log not found')

    #confirm lockfile exists
    if not exists('/var/lib/mongodb/mongod.lock'):
        abort_with_message(basemsg + 'mongod lock not found')

    #confirm pidfile exists
    if not exists('/var/run/mongod.pid'):
        abort_with_message(basemsg + 'mongod pidfile not found')

    #confirm we can get open a connection to mongodb 
    #TODO should retry in case of connection failure
    client  = pymongo.MongoClient(HOST_NAME)
    db = client['test']
    pingresult = db.command({'ping': 1})
    if res.get('ok', 0.0) != 1.0:
        abort_with_message(basemsg + 'could not connect to mongod')


def stop_mongod():
    sudo('service mongod stop')


def check_mongod_stopped():
    basemsg = 'check_mongod_stopped failed: '

    #confirm that lockfile doesnt exist
    if exists('/var/lib/mongodb/mongod.lock'):
        abort_with_message(basemsg + 'mongod lock found')

    #confirm pidfile is removed
    if exists('/var/run/mongod.pid'):
        abort_with_message(basemsg + 'mongod pidfile found')

    #TODO should we check that we cannot connect with pymongo?

def restart_mongod():
    sudo('service mongod restart')


def run_through_test():
    install_mongod()
    check_mongod_installed()

    start_mongod()
    check_mongod_started()

    restart_mongod()
    check_mongod_started()

    stop_mongod()
    check_mongod_stopped()

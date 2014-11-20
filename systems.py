from fabric.api import run, sudo
from fabric.contrib.files import exists, contains, append
from fabric.utils import abort

#utility functions
def abort_with_message(message):
    abort(message)

def basic_install_check(message, config_loc, mongod_bin_loc, data_dir_loc):
    #check existence of config file
    if not exists(config_loc):
         abort_with_message(message + 'config file not found')
    #TODO should we the contents of the config file?

    #check existence of binaries
    if not exists(mongod_bin_loc):
        abort_with_message(message + 'mongod binary not found')
    #TODO should we check other binaries?

    #check existence of data dir
    if not exists(data_dir_loc):
        abort_with_message(message + 'mongod data directory not found')

def basic_running_check(message, log_loc, lock_file_loc):
    #confirm log exists
    if not exists(log_loc):
        abort_with_message(message + 'mongod log not found')

    #confirm lockfile exists
    if not contains(lock_file_loc, '[0123456789]', escape=False):
        abort_with_message(message + 'mongod lock not found')

def basic_stopped_check(message, lock_file_loc):
    #confirm that lockfile doesnt exist
    if contains(lock_file_loc, '[0123456789]', escape=False):
        abort_with_message(message + 'mongod lock not empty')



#systems
class system_operator(object):

    def __init__(self):
        pass

    def install(self, enterprise=False):
        pass

    def install_old(self, version, enterprise=False):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def restart(self):
        pass

    def check_installed(self, version=None):
        pass

    def check_started(self):
        pass

    def check_stopped(self):
        pass

    def remove(self, enterprise=False):
        pass

class debian_operator(system_operator):
    def __init__(self):
        self.name = 'debian'
        self.locations = {}
        self.locations['config_loc'] = '/etc/mongod.conf'
        self.locations['mongod_bin_loc'] = '/usr/bin/mongod'
        self.locations['data_dir_loc'] = '/var/lib/mongodb'
        self.locations['log_loc'] = '/var/log/mongodb/mongod.log'
        self.locations['lock_file_loc'] = '/var/lib/mongodb/mongod.lock'
        self.locations['pid_file_loc'] = '/var/run/mongod.pid'

    def install(self, enterprise=False):
        if enterprise:
            sudo('apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10')
            #Note: 2.8 is only put to test rc builds
            append('/etc/apt/sources.list.d/mongodb-enterprise-2.8.list', 'deb http://repo.mongodb.com/apt/debian wheezy/mongodb-enterprise/2.8 main', use_sudo=True)
            sudo('apt-get update')
            sudo('apt-get -y install mongodb-enterprise=2.8.0~rc0 mongodb-enterprise-server=2.8.0~rc0 mongodb-enterprise-shell=2.8.0~rc0 mongodb-enterprise-mongos=2.8.0~rc0 mongodb-enterprise-tools=2.8.0~rc0')
        else:
            sudo('apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10')
            # append('/etc/apt/sources.list.d/mongodb.list', 'deb http://downloads-distro.mongodb.org/repo/debian-sysvinit dist 10gen', use_sudo=True)
            append('/etc/apt/sources.list.d/mongodb.list', 'deb http://distro-deb2.build.10gen.cc/repo.2012-11-12/debian-sysvinit dist 10gen', use_sudo=True)
            sudo('apt-get update')
            sudo('apt-get -y install mongodb-org')

    def install_old(self, version, enterprise=False):
        if enterprise:
            sudo('apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10')
            #Note that versioning works differently here version should be something like '2.6' not '2.6.1'
            append('/etc/apt/sources.list.d/mongodb-enterprise.list', 'deb http://repo.mongodb.com/apt/debian wheezy/mongodb-enterprise/' + version + ' main', use_sudo=True)
            sudo('apt-get update')
            sudo('apt-get -y install mongodb-enterprise')
        else:
            sudo('apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10')
            # append('/etc/apt/sources.list.d/mongodb.list', 'deb http://downloads-distro.mongodb.org/repo/debian-sysvinit dist 10gen', use_sudo=True)
            append('/etc/apt/sources.list.d/mongodb.list', 'deb http://distro-deb2.build.10gen.cc/repo.2012-11-12/debian-sysvinit dist 10gen', use_sudo=True)
            sudo('apt-get update')
            sudo('apt-get -y install mongodb-org=' + version +  ' mongodb-org-server=' + version + ' mongodb-org-shell=' + version + ' mongodb-org-mongos=' + version + ' mongodb-org-tools=' + version)

    def start(self):
        sudo('service mongod start')

    def stop(self):
        sudo('service mongod stop')

    def restart(self):
        sudo('service mongod restart')

    def check_installed(self, version=None):
        basemsg = 'check_installed failed: '
        basic_install_check(basemsg,
                            self.locations['config_loc'],
                            self.locations['mongod_bin_loc'],
                            self.locations['data_dir_loc'])

        if version is not None:
            #confirm the binaries are of the correct version
            foundversion = run(self.locations['mongod_bin_loc'] + ' --version')
            if version != foundversion:
                abort_with_message(basemsg + 'version is not correct')


    def check_started(self):
        basemsg = 'check_started failed: '
        basic_running_check(basemsg,
                            self.locations['log_loc'],
                            self.locations['lock_file_loc'])

        #confirm pidfile exists
        if not exists(self.locations['pid_file_loc']):
            abort_with_message(basemsg + 'mongod pidfile not found')

    def check_stopped(self):
        basemsg = 'check_mongod_stopped failed: '
        basic_stopped_check(basemsg,
                            self.locations['lock_file_loc'])

    def remove(self, enterprise=False):
        if enterprise:
            sudo("apt-get remove mongodb-enterprise-*")
        else:
            #TODO: remove community packages
            pass

class ubuntu_operator(system_operator):
    def __init__(self, ubuntuname):
        self.name = 'ubuntu'
        self.locations = {}
        self.locations['config_loc'] = '/etc/mongod.conf'
        self.locations['mongod_bin_loc'] = '/usr/bin/mongod'
        self.locations['data_dir_loc'] = '/var/lib/mongodb'
        self.locations['log_loc'] = '/var/log/mongodb/mongod.log'
        self.locations['lock_file_loc'] = '/var/lib/mongodb/mongod.lock'
        self.ubuntuname = ubuntuname

    def install(self, enterprise=False):
        if enterprise:
            sudo('apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10')
            append('/etc/apt/sources.list.d/mongodb-enterprise.list', 'deb http://repo.mongodb.com/apt/ubuntu ' + self.ubuntuname + '/mongodb-enterprise/stable multiverse', use_sudo=True)
            sudo('apt-get update')
            sudo('apt-get -y install mongodb-enterprise')
        else:
            sudo('apt-key adv --keyserver hkp://keyserver.ubuntu.com --recv 7F0CEB10')
            # append('/etc/apt/sources.list.d/mongodb.list', 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen', use_sudo=True)
            append('/etc/apt/sources.list.d/mongodb.list', 'deb http://distro-deb2.build.10gen.cc/repo.2012-11-12/ubuntu-upstart dist 10gen', use_sudo=True)
            sudo('apt-get update')
            sudo('apt-get -y install mongodb-org')

    def install_old(self, version, enterprise=False):
        if enterprise:
            sudo('apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10')
            append('/etc/apt/sources.list.d/mongodb-enterprise.list', 'deb http://repo.mongodb.com/apt/ubuntu ' + self.ubuntuname + '/mongodb-enterprise/stable multiverse', use_sudo=True)
            sudo('apt-get update')
            sudo('apt-get -y install mongodb-enterprise=' + version + ' mongodb-enterprise-server=' + version + ' mongodb-enterprise-shell=' + version + ' mongodb-enterprise-mongos=' + version + ' mongodb-enterprise-tools=' + version)
        else:
            sudo('apt-key adv --keyserver hkp://keyserver.ubuntu.com --recv 7F0CEB10')
            append('/etc/apt/sources.list.d/mongodb.list', 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen', use_sudo=True)
            sudo('apt-get update')
            sudo('apt-get -y install mongodb-org=' + version + ' mongodb-org-server=' + version + ' mongodb-org-shell=' + version + ' mongodb-org-mongos=' + version + ' mongodb-org-tools=' + version)

    def start(self):
        sudo('service mongod start')

    def stop(self):
        sudo('service mongod stop')

    def restart(self):
        sudo('service mongod restart')

    def check_installed(self, version=None):
        basemsg = 'check_installed failed: '
        basic_install_check(basemsg,
                            self.locations['config_loc'],
                            self.locations['mongod_bin_loc'],
                            self.locations['data_dir_loc'])
        if version is not None:
            foundversion = run(self.locations['mongod_bin_loc'] + ' --version')
            if version not in foundversion:
                abort_with_message(basemsg + 'version is not correct')

    def check_started(self):
        basemsg = 'check_mongod_started failed: '
        basic_running_check(basemsg,
                            self.locations['log_loc'],
                            self.locations['lock_file_loc'])

    def check_stopped(self):
        basemsg = 'check_mongod_stopped failed: '
        basic_stopped_check(basemsg,
                            self.locations['lock_file_loc'])

class rhel_operator(system_operator):
    def __init__(self, version, spawn_host):
        self.name = 'rhel'
        self.locations = {}
        self.locations['config_loc'] = '/etc/mongod.conf'
        self.locations['mongod_bin_loc'] = '/usr/bin/mongod'
        self.locations['data_dir_loc'] = '/var/lib/mongo'
        self.locations['log_loc'] = '/var/log/mongodb/mongod.log'
        self.locations['lock_file_loc'] = '/var/lib/mongo/mongod.lock'
        self.locations['pid_file_loc'] = '/var/run/mongodb/mongod.pid'
        self.version = version
        self.spawn_host = spawn_host

    def install(self, enterprise=False):
        if enterprise:
            if self.version in (7, 6) and self.spawn_host:
                repo = '[mongodb-enterprise-2.8]\nname=MongoDB Enterprise 2.8 Repository\nbaseurl=https://repo.mongodb.com/yum/redhat/$releasever/mongodb-enterprise/2.8/$basearch/\ngpgcheck=0\nenabled=1\n'
                append('/etc/yum.repos.d/mongodb-enterprise-2.8.repo', repo)
                # repo = '[mongodb-enterprise]\nname=MongoDB Enterprise Repository\nbaseurl=https://repo.mongodb.com/yum/redhat/$releasever/mongodb-enterprise/stable/$basearch/\ngpgcheck=0\nenabled=1\n'
                # append('/etc/yum.repos.d/mongodb-enterprise.repo', repo)
                run('yum -y install mongodb-enterprise')
            else:
                repo = '[mongodb-enterprise-2.8]\nname=MongoDB Enterprise 2.8 Repository\nbaseurl=https://repo.mongodb.com/yum/redhat/$releasever/mongodb-enterprise/2.8/$basearch/\ngpgcheck=0\nenabled=1\n'
                append('/etc/yum.repos.d/mongodb-enterprise-2.8.repo', repo, use_sudo=True)
                sudo('yum -y install mongodb-enterprise')
        else:
            if self.version in (7, 6) and self.spawn_host:
                repo = '[mongodb]\nname=MongoDB Repository\nbaseurl=http://distro-deb2.build.10gen.cc/repo.2012-11-12/redhat/os/x86_64/\ngpgcheck=0\nenabled=1\n'
                append('/etc/yum.repos.d/mongodb.repo', repo)
                run('yum -y install mongodb-org')
            else:
                repo = '[mongodb]\nname=MongoDB Repository\nbaseurl=http://distro-deb2.build.10gen.cc/repo.2012-11-12/redhat/os/x86_64/\ngpgcheck=0\nenabled=1\n'
                append('/etc/yum.repos.d/mongodb.repo', repo, use_sudo=True)
                sudo('yum -y install mongodb-org')

    def install_old(self, version, enterprise=False):
        if enterprise:
            if self.version in (7, 6) and self.spawn_host:
                repo = '[mongodb-enterprise]\nname=MongoDB Enterprise Repository\nbaseurl=https://repo.mongodb.com/yum/redhat/$releasever/mongodb-enterprise/stable/$basearch/\ngpgcheck=0\nenabled=1\n'
                append('/etc/yum.repos.d/mongodb-enterprise-2.6.repo', repo)
                run('yum -y install mongodb-enterprise')
            else:
                repo = '[mongodb-enterprise]\nname=MongoDB Enterprise Repository\nbaseurl=https://repo.mongodb.com/yum/redhat/$releasever/mongodb-enterprise/stable/$basearch/\ngpgcheck=0\nenabled=1\n'
                append('/etc/yum.repos.d/mongodb-enterprise-2.6.repo', repo, use_sudo=True)
                # sudo('yum -y install mongodb-enterprise-2.6.1 mongodb-enterprise-server-2.6.1 mongodb-enterprise-shell-2.6.1 mongodb-enterprise-mongos-2.6.1 mongodb-enterprise-tools-2.6.1')
                sudo('yum -y install mongodb-enterprise')
        else:
            if self.version in (7, 6) and self.spawn_host:
                repo = '[mongodb]\nname=MongoDB Repository\nbaseurl=http://downloads-distro.mongodb.org/repo/redhat/os/x86_64/\ngpgcheck=0\nenabled=1\n'
                append('/etc/yum.repos.d/mongodb.repo', repo)
                run('yum -y install mongodb-org-' + version + ' mongodb-org-server-' + version + ' mongodb-org-shell-' + version +' mongodb-org-mongos-' + version + ' mongodb-org-tools-' + version)
            else:
                repo = '[mongodb]\nname=MongoDB Repository\nbaseurl=http://downloads-distro.mongodb.org/repo/redhat/os/x86_64/\ngpgcheck=0\nenabled=1\n'
                append('/etc/yum.repos.d/mongodb.repo', repo, use_sudo=True)
                sudo('yum -y install mongodb-org-' + version + ' mongodb-org-server-' + version + ' mongodb-org-shell-' + version +' mongodb-org-mongos-' + version + ' mongodb-org-tools-' + version)


    def start(self):
        if self.version in (7, 6) and self.spawn_host:
            run("service mongod start")
        else:
            sudo('service mongod start')

    def stop(self):
        if self.version in (7, 6) and self.spawn_host:
            run("service mongod stop")
        else:
            sudo('service mongod stop')

    def restart(self):
        if self.version in (7, 6) and self.spawn_host:
            run("service mongod restart")
        else:
            sudo('service mongod restart')

    def check_installed(self, version=None):
        basemsg = 'check_installed failed: '
        basic_install_check(basemsg,
                            self.locations['config_loc'],
                            self.locations['mongod_bin_loc'],
                            self.locations['data_dir_loc'])
        if version is not None:
            foundversion = run(self.locations['mongod_bin_loc'] + ' --version')
            if version not in foundversion:
                abort_with_message(basemsg + 'version is not correct')

    def check_started(self):
        basemsg = 'check_mongod_started failed: '
        basic_running_check(basemsg,
                            self.locations['log_loc'],
                            self.locations['lock_file_loc'])

        #confirm pidfile exists
        if not exists(self.locations['pid_file_loc']):
            abort_with_message(basemsg + 'mongod pidfile not found')

    def check_stopped(self):
        basemsg = 'check_mongod_stopped failed: '
        basic_stopped_check(basemsg,
                            self.locations['lock_file_loc'])

class suse_operator(system_operator):
    def __init__(self, version, spawn_host):
        self.name = 'suse'
        self.locations = {}
        self.locations['config_loc'] = '/etc/mongod.conf'
        self.locations['mongod_bin_loc'] = '/usr/bin/mongod'
        self.locations['data_dir_loc'] = '/var/lib/mongo'
        self.locations['log_loc'] = '/var/log/mongodb/mongod.log'
        self.locations['lock_file_loc'] = '/var/lib/mongo/mongod.lock'
        self.locations['pid_file_loc'] = '/var/run/mongodb/mongod.pid'
        self.version = version
        self.spawn_host = spawn_host

    def install(self, enterprise=False):
        sudo('zypper removerepo mongodb')
        if enterprise:
            sudo('zypper addrepo --no-gpgcheck http://repo.mongodb.com/zypper/suse/11/mongodb-enterprise/2.8/x86_64/ mongodb')
            sudo('zypper install mongodb-enterprise')
        else:
            # sudo('zypper addrepo --no-gpgcheck http://downloads-distro.mongodb.org/repo/suse/os/x86_64/ mongodb')
            sudo('zypper addrepo --no-gpgcheck http://distro-deb2.build.10gen.cc/repo.2012-11-12/suse/os/x86_64/ mongodb')
            sudo('zypper install mongodb-org')

    def install_old(self, version, enterprise=False):
        sudo('zypper removerepo mongodb')
        if enterprise:
            sudo('zypper addrepo --no-gpgcheck http://repo.mongodb.com/zypper/suse/11/mongodb-enterprise/stable/x86_64/ mongodb')
            sudo('zypper install mongodb-enterprise')
        else:
            sudo('zypper addrepo --no-gpgcheck http://downloads-distro.mongodb.org/repo/suse/os/x86_64/ mongodb')
            sudo('zypper install mongodb-org-' + version + ' mongodb-org-server-' + version + ' mongodb-org-shell-' + version +' mongodb-org-mongos-' + version + ' mongodb-org-tools-' + version)

    def start(self):
        sudo('service mongod start')

    def stop(self):
        sudo('service mongod stop')

    def restart(self):
        sudo('service mongod restart')

    def check_installed(self, version=None):
        basemsg = 'check_installed failed: '
        basic_install_check(basemsg,
                            self.locations['config_loc'],
                            self.locations['mongod_bin_loc'],
                            self.locations['data_dir_loc'])
        if version is not None:
            foundversion = run(self.locations['mongod_bin_loc'] + ' --version')
            if version not in foundversion:
                abort_with_message(basemsg + 'version is not correct')

    def check_started(self):
        basemsg = 'check_mongod_started failed: '
        basic_running_check(basemsg,
                            self.locations['log_loc'],
                            self.locations['lock_file_loc'])

        #confirm pidfile exists
        if not exists(self.locations['pid_file_loc']):
            abort_with_message(basemsg + 'mongod pidfile not found')

    def check_stopped(self):
        basemsg = 'check_mongod_stopped failed: '
        basic_stopped_check(basemsg,
                            self.locations['lock_file_loc'])


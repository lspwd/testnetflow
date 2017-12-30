import os
from datetime import datetime

import paramiko

from exceptions.FileNotFoundError import FileNotFoundError
from exceptions.PythonNotFoundError import PythonNotFoundError
from impl.SudoHelper import SudoHelper


class SSHHelper:
    def __init__(self, ip, username, password, mutex, userargs, tid, logger):
        self.ip = ip
        self.username = username
        self.password = password
        self.mutex = mutex
        self.userargs = userargs
        self.tid = tid
        self.logger = logger
        self.uploaded = False

    def sshConnect(self):
        try:
            self.mutex.acquire()
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if self.userargs.stdout:
                print ("DEBUG STDOUT: " + self.tid + " Username: \"%s\", Password: \"%s\" and ip address: \"%s\"" %
                       self.username, self.password, self.ip)
            self.logger.debug('%s - Server class - __sshConnect(): Connecting with Username: \"%s\",'
                              ' Password \"%s\" and ip \"%s\"',
                              self.tid, self.username, self.password, self.ip)
            client.connect(self.ip, username=self.username, password=self.password, timeout=2,
                           allow_agent=False, look_for_keys=False)
            return client

        except  Exception as e:
            raise NameError("Error in __sshConnect() method --- on server: " + self.ip + " " + str(e))

        finally:
            self.mutex.release()

    def __versiontuple__(self, v):
        return tuple(map(int, v.split(".")))

    def testListenState(self, ip, port, client):

        cmd = '/bin/netstat -ntl | /bin/egrep -o ''\'' + ip + ':' \
              + port + '[ ]{1}|0.0.0.0:' + port + '[ ]{1}|::.*:' + port + '\''
        stdin, stdout, stderr = client.exec_command(cmd)
        result = stdout.read().strip('\n')
        # resulterr = stderr.read().strip("\n")

        if not result:
            if self.userargs.stdout:
                print("DEBUG STDOUT: " + str(datetime.now())[:-3] + " --- " + self.tid
                      + " KO \"%s:%s\" socket has not been found in LISTEN state" % (ip, port))
            self.logger.debug('%s \"%s:%s\" socket has not been found in LISTEN state', self.tid,
                              ip, port)
            return False
        else:
            if self.userargs.stdout:
                print("DEBUG STDOUT: " + str(datetime.now())[:-3] + " --- " + self.tid
                      + " %s:%s socket has been found in LISTEN state" % (ip, port))
            self.logger.debug('OK %s \"%s:%s\" socket has been found in LISTEN state', self.tid, ip, port)
            return True

    def checkPythonPath(self, client):
        cmd = "which python"
        stdin, stdout, stderr = client.exec_command(cmd)
        if stdout:
            return stdout.read.rstrip("\n")
        else:
            raise PythonNotFoundError("Python was not found on the remote machine $PATH")

    def checkPythonVersion(self, python_min_version, client):
        try:
            python = self.checkPythonPath(client)
            cmd = python + " -V 2>&1 | awk '{print $2}' "
            stdin, stdout, stderr = client.exec_command(cmd)
            if stdout:
                version = stdout.read().rstrip("\n")
                return self.__versiontuple__(version) >= self.__versiontuple__(python_min_version)
            else:
                raise RuntimeError("Unable to execute python on the remote machine")
        except Exception as e:
            raise RuntimeError("Unable to verify python version on the remote machine: " + str(e))

    def checkSudo(self, client):
        try:
            chan = client.invoke_shell()
            chan.set_combine_stderr(True)
            chan.settimeout(20)
            custom_ps1 = "end1> "
            helper = SudoHelper(custom_ps1, self.username, self.password, chan, self.logger, "sudo -k echo test")
            response = helper.doSudo().replace("\r", "").split("\n")
            return "test" in response
        except Exception as e:
            raise e

    def isUploaded(self):
        return self.uploaded

    def upload(self, client, script, remote_path):
        if os.path.isfile(script):
            sftp_client = client.open_sftp()
            file_attr = sftp_client.put(script, remote_path + script)
            if file_attr:
                self.setUploadedStatus(True)
                return True
            else:
                raise RuntimeError("Unable to upload " + script + "on the remote machine")
        else:
            raise FileNotFoundError("The script " + script + "was not found on the local machine")

    def chmodOnScript(self, client, permissionBit, script):
        cmd = "chmod +" + permissionBit + " " + script
        # ignore the return  from chmod here since it's empty..
        client.exec_command(cmd)
        cmd = "ls -ltr " + script + " | awk '{print substr( $1,4,1)} '"
        stdin, stdout, stderr = client.exec_command(cmd)
        if stdout.read().strip("\n") == permissionBit:
            return
        else:
            raise RuntimeError("Unable to set the permission bit " + permissionBit
                               + "on the remote script " + script)

    def setUploadedStatus(self, condition):
        self.uploaded = condition
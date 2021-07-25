from __future__ import print_function
import os
import paramiko
from testnetflow.exceptions.FileNotFoundError import FileNotFoundError
from testnetflow.exceptions.PythonNotFoundError import PythonNotFoundError
from testnetflow.constants.LoggingConstant import LoggingConstant
from testnetflow.exceptions.SudoError import SudoError
from paramiko import AuthenticationException

class NetHelperBase(object):

    def __init__(self, ip, username, password, mutex, userargs, tid, logger):
        self.ip = ip
        self.username = username
        self.password = password
        self.mutex = mutex
        self.userargs = userargs
        self.tid = tid
        self.logger = logger
        self.uploaded = False
        self.default_she_bang = "#!/usr/bin/python"
        self.sudoAble = False
        self.sudo_require_password = False
        self.classname = self.__class__.__name__
        self.logStrings = LoggingConstant()
        self.logging_header = self.tid + self.logStrings.SEP + self.__class__.__name__ + self.logStrings.SEP
        self.debugging_header = self.logStrings.DEBUG_STDOUT_HEADER + self.logging_header

    def ssh_connect(self):
        try:
            self.mutex.acquire()
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            msg = self.logging_header + self.logStrings.CONNECT_WITH_USERNAME \
                  + self.username + self.logStrings.ON_IP_MSG + self.ip
            self.logger.loggingDebugMessage(msg)
            self.logger.printStdoutMessage(msg, self.logStrings.DEBUG_STDOUT_HEADER)
            client.connect(self.ip, username=self.username, password=self.password, timeout=3.0,
                           auth_timeout=3.0, allow_agent=False, look_for_keys=False, gss_trust_dns=False)
            return client

        except AuthenticationException as e:
            raise e

        except ( RuntimeError, Exception ) as e:
            msg = self.logging_header + self.logStrings.EXC_HEADER + \
                  self.__class__.__name__ + self.logStrings.ON_IP_MSG \
                  + self.ip + " " + str(e)
            raise RuntimeError(msg)

        finally:
            self.mutex.release()

    def __versiontuple__(self, v):
        return tuple(map(int, v.split(".")))

    def locatebin(self, path, ssh_client):
        cmd = "which {}".format(path)
        stdin, stdout, stderr = ssh_client.exec_command(cmd, timeout=10)
        result = stdout.read().strip('\n')
        return result

    def test_listen_state(self, ip, port, client):
        #print(self.debugging_header + "begin locating netstat..")
        ss = self.locatebin("ss", client)
        if not ss:
            netstat = self.locatebin("netstat", client)
            if not netstat:
                msg = self.logging_header + self.logStrings.NETSTAT_ERROR \
                      + self.username + self.logStrings.ON_IP_MSG + self.ip
                self.logger.loggingDebugMessage(msg)
                self.logger.printStdoutMessage(msg, self.logStrings.DEBUG_STDOUT_HEADER)
                return False
            else:
                cmd = netstat + " -ntpl | grep " + str(port)
        else:
            cmd = ss + " -4nlt sport eq :{port}|grep -v State".format(port=port)

        stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
        result = stdout.read().strip('\n')

        if not result:
            msg = self.logging_header + self.logStrings.SOCKET_NOT_LISTENING + self.logStrings.ON_IP_MSG \
                  + str(ip) + " " + self.logStrings.ON_PORT_MSG + str(port)
            self.logger.loggingDebugMessage(msg)
            self.logger.printStdoutMessage(msg, self.logStrings.DEBUG_STDOUT_HEADER)
            return False
        else:
            msg = self.logging_header + self.logStrings.SOCKET_LISTENING + self.logStrings.ON_IP_MSG \
                  + str(ip) + " " + self.logStrings.ON_PORT_MSG + str(port)
            self.logger.loggingDebugMessage(msg)
            self.logger.printStdoutMessage(msg, self.logStrings.DEBUG_STDOUT_HEADER)
            return True

    def check_python_path(self, client):
        cmd = "which python"
        stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
        if stdout:
            return stdout.read().rstrip("\n")
        else:
            msg = self.logging_header + self.logStrings.EXC_HEADER + self.logStrings.PYTHON_NOT_FOUND
            raise PythonNotFoundError(msg)

    def check_python_version(self, python_min_version, client):
        try:
            python = self.check_python_path(client)
            cmd = python + " -V 2>&1 | awk '{print $2}' "
            stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
            if stdout:
                version = stdout.read().rstrip("\n")
                return self.__versiontuple__(version) >= self.__versiontuple__(python_min_version)
            else:
                msg = self.logging_header + self.logStrings.EXC_HEADER + self.logStrings.PYTHON_EXC_ERROR
                raise RuntimeError(msg)
        except Exception as e:
            msg = self.logging_header + self.logStrings.EXC_HEADER + self.logStrings.PYTHON_VER_ERROR + str(e)
            raise RuntimeError(msg)

    def check_shebang(self, python_she_bang):
        return python_she_bang == self.default_she_bang

    def change_shebang(self, client, python_she_bang, target_script):
        try:
            if not self.check_shebang(python_she_bang):
                cmd = "sed -i 's@#!/usr/bin/python@" + python_she_bang + "@g' " + target_script
                stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
                string_stderr = stderr.read()
                if len(string_stderr):
                    msg = self.logging_header + self.logStrings.EXC_HEADER + \
                          self.logStrings.SHEBANG_ERROR + str(string_stderr)
                    raise RuntimeError(msg)
        except Exception as e:
            msg = self.logging_header + self.logStrings.EXC_HEADER + \
                  self.logStrings.SHEBANG_ERROR + str(e)
            raise RuntimeError(msg)

    def is_uploaded(self):
        return self.uploaded

    def create_remote_directory(self, client, remote_dir, user):
        try:
            #print(self.debugging_header + "remote directory creation is starting " + remote_dir)
            cmd = "mkdir -p " + remote_dir
            client.exec_command(cmd, timeout=10)
            cmd = "chown " + user + ": " + remote_dir
            client.exec_command(cmd, timeout=10)
            cmd = "ls -ltrd " + remote_dir + " | awk '{print $3} '"
            stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
            if stdout.read().strip("\n") == user:
                #print(self.debugging_header + "Sucessful remote directory creation " + remote_dir)
                return
            else:
                msg = self.logging_header + self.logStrings.EXC_HEADER + self.logStrings.MKDIR_ERROR + remote_dir
                raise (RuntimeError(msg))
        except Exception as e:
            msg = self.logging_header + self.logStrings.EXC_HEADER + str(e) \
                  + self.logStrings.SEP + self.logStrings.MKDIR_ERROR + remote_dir
            raise (RuntimeError(msg))

    def upload(self, client, script_local_path, script, remote_path):
        if os.path.isfile(script_local_path):
            sftp_client = client.open_sftp()
            # print(self.debugging_header + "Setting timeout on upload channel" + str(script))
            # sftp_client.settimeout(float(10))
            #print(self.debugging_header + "begin uploading script" + str(script))
            # attr = sftp_client.stat(remote_path+script)
            # print(self.debugging_header + "File Found with following attibutes: " + str(attr)) if attr is not None \
            #    else print(self.debugging_header + remote_path + script + " was not found on remote box ")
            file_attr = sftp_client.put(script_local_path, remote_path + script)
            #print(self.debugging_header + "uploaded script -- file attr" + str(file_attr))
            if file_attr:
                self.set_uploaded_status(True)
                return True
            else:
                msg = self.logging_header + self.logStrings.EXC_HEADER + \
                      self.logStrings.UPLOAD_ERROR + str(script) + self.logStrings.ON_IP_MSG + self.ip
            raise RuntimeError(msg)
        else:
            msg = self.logging_header + self.logStrings.EXC_HEADER \
                  + self.logStrings.SCRIPT_NOT_FOUND_ERROR + script_local_path + script \
                  + self.logStrings.ON_IP_MSG + self.ip
            raise FileNotFoundError(msg)

    def do_chmod_on_script(self, client, permissionBit, script):
        cmd = "chmod +" + permissionBit + " " + script
        # ignore the return  from chmod here since it's empty..
        client.exec_command(cmd, timeout=10)
        cmd = "ls -ltr " + script + " | awk '{print substr( $1,4,1)} '"
        stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
        if stdout.read().strip("\n") == permissionBit:
            return
        else:
            msg = self.logging_header + self.logStrings.EXC_HEADER + \
                  self.logStrings.X_BIT_ERROR + script
            raise RuntimeError(msg)

    def set_uploaded_status(self, condition):
        self.uploaded = condition

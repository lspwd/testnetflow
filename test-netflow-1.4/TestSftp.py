#!/usr/bin/python

import paramiko
from paramiko import SSHClient
import os

server = "10.6.1.2"
username = "administrator"
password = "Password2"
sshclient = ""
sftp_client = ""
serverscript = "SocketServer.py"
python_min_version = "2.6"

if __name__ == '__main__':

    def versiontuple(v):
        return tuple(map(int, v.split(".")))

    try:
        sshclient = SSHClient()
        sshclient.load_system_host_keys()
        sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        sshclient.connect(server, username=username, password=password)
        cmd = "basename $(which python)"
        stdin, stdout, stderr = sshclient.exec_command(cmd)
        if stdout:
            response = stdout.read().rstrip("\n")
            print(response)
            if response == "python":
                cmd = " python -V 2>&1 | awk '{print $2}' "
                stdin, stdout, stderr = sshclient.exec_command(cmd)
                if stdout:
                    version = stdout.read().rstrip("\n")
                    print(version)
                    if versiontuple(version) >= versiontuple(python_min_version):
                        sftp_client = sshclient.open_sftp()
                        stat = sftp_client.stat("/tmp")
                        print(str(stat))
                        if os.path.isfile(serverscript):
                            print("SocketServer is a file... uploading to server " + server)
                        file_attr = sftp_client.put(serverscript, "/tmp/" + serverscript)
                        if file_attr:
                            print(serverscript + " has been copied to remote destination " + server
                                  + " and has got these params: " + str(file_attr))
                        cmd = "chmod +x /tmp/" + serverscript
                        stdin, stdout, stderr = sshclient.exec_command(cmd)
                        cmd = "ls -ltr /tmp/" + serverscript
                        stdin, stdout, stderr = sshclient.exec_command(cmd)
                        if stdout:
                            response = stdout.read()
                            print(response)
    except Exception as e:
        print(str(e))
    finally:
        if hasattr(sshclient, "close"):
            sshclient.close()
        if hasattr(sftp_client, "close"):
            sftp_client.close()

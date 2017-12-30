#!/usr/bin/python

from __future__ import print_function

import sys

import NetBaseObject
from SSHServerHelper import SSHServerHelper
from PythonNotFoundError import PythonNotFoundError


class Server(NetBaseObject):

    def __init__(self, dct, logger, exception_queue, tid,  mutex, userargs):
        super(Server, self).__init__(dct, logger, exception_queue, tid,  mutex, userargs)
        self.script = "SocketServer.py"

    # TODO Refactor in order to adopt new logic...

    def run(self):

        try:

            # Todo : Refactoring :
            # Test python;
            # Test socket listen
            # determine python path & version
            # swap the shebang
            # upload serverscript
            # start the server

            # fetch ip
            full_script_path = self.remote_path + self.script
            helper = SSHServerHelper(self.mgmtip, self.username,
                                     self.password, self.mutex, self.userargs,
                                     self.tid, self.logger)
            client = helper.sshConnect()
            pyhton_path = helper.checkPythonPath(client)
            # TODO remove this one
            print(pyhton_path)
            if helper.checkPythonVersion(self.pyhton_min_version, client):
                if not helper.isUploaded():
                    if helper.upload(client, self.script, self.remote_path):
                        helper.chmodOnScript(client, self.permission_bit, full_script_path)
                        # helper.sedTheShebang(client, pyhton_path)
                    else:
                        raise RuntimeError("Unable to upload script on the remote machine")
            else:
                raise PythonNotFoundError("Python version on the remote machine " + self.mgmtip
                                          + " is not supported, please install at least Python "
                                          + self.python_min_version)
            # print "Mgmt -> " +self.mgmtipserver +" Socket To Spawn -> " +str(self.socketlist)

            for i in self.socketlist:

                ip = i.split(":")[0]
                port = i.split(":")[1]
                if not helper.testListenState(ip, port, client):
                    if self.userargs.stdout:
                        print("DEBUG STDOUT: " + self.tid + " Going to spawn socket \"%s:%s\" " % (ip, port))
                        self.logger.debug("%s Going to spawn socket \"%s:%s\"", self.tid, ip, port)
                        self.runSocketServer(ip, port, "60", client, full_script_path)
                else:
                    if self.userargs.stdout:
                        print("DEBUG STDOUT: " + self.tid + " Socket \"%s:%s\" is already in LISTEN "
                                                            "state on the remote server" % (ip, port))
                    self.logger.debug("%s Netcat help is not needed for \"%s:%s\"", self.tid, ip, port)
            self.exception_queue.put("done")
            return
        except  (RuntimeError, Exception):
            self.exception_queue.put(sys.exc_info())
        finally:

            if hasattr(self, "client"):
                self.client.close()
                if self.userargs.stdout:
                    print("DEBUG STDOUT: " + self.tid + " the connection with %s has been closed" % self.mgmtip)
                self.logger.debug("%s: - Server Class - the connection with %s has been closed", self.tid,
                                  self.mgmtip)
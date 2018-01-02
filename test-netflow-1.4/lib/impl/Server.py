#!/usr/bin/python

from __future__ import print_function

import sys
from NetBaseObject import NetBaseObject
from SSHServerHelper import SSHServerHelper
import os


class Server(NetBaseObject):
    def __init__(self, dct, logger, exception_queue, tid, mutex, userargs):
        super(Server, self).__init__(dct, logger, exception_queue, tid, mutex, userargs)
        self.script_local_path = os.getcwd() + os.path.sep + "lib" + os.path.sep + \
                                 "scripts" + os.path.sep + "SocketServer.py"
        self.script = os.path.basename(self.script_local_path)

    # TODO Refactor in order to adopt new logic...

    def run(self):

        try:

            full_script_path = self.remote_path + self.script

            helper = SSHServerHelper(self.mgmtip, self.username,
                                     self.password, self.mutex, self.userargs,
                                     self.tid, self.logger)

            client = self.prepareTheGround(helper, self.script_local_path, self.script, self.remote_path)
            for i in self.socketlist:

                ip = i.split(":")[0]
                port = i.split(":")[1]
                if not helper.testListenState(ip, port, client):
                    if self.userargs.stdout:
                        print("DEBUG STDOUT: " + self.tid + " Going to spawn socket \"%s:%s\" " % (ip, port))
                        self.logger.debug("%s Going to spawn socket \"%s:%s\"", self.tid, ip, port)
                        helper.runSocketServer(ip, port, "20", client, full_script_path)
                else:
                    if self.userargs.stdout:
                        print("DEBUG STDOUT: " + self.tid + " Socket \"%s:%s\" is already in LISTEN "
                                                            "state on the remote server" % (ip, port))
                    self.logger.debug("%s Socket \"%s:%s\" is already in LISTEN"
                                      "state on the remote server", self.tid, ip, port)
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

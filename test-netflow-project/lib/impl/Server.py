#!/usr/bin/python

from __future__ import print_function

import os
import sys

from ConfigurationError import ConfiguationError
from NetBaseObject import NetBaseObject
from SSHServerHelper import SSHServerHelper


class Server(NetBaseObject):
    def __init__(self, username, password, mgmtip, attribute_list, logger,
                 exception_queue, result_queue, tid, mutex, userargs, server_result_list):
        super(Server, self).__init__(username, password, mgmtip, attribute_list, logger,
                                     exception_queue, result_queue, tid, mutex, userargs)
        self.script_local_path = os.getcwd() + os.path.sep + "lib" \
                                 + os.path.sep + "scripts" + os.path.sep + "SocketServer.py"
        self.script = os.path.basename(self.script_local_path)
        self.responseList = server_result_list


    def run(self):
        socket_list_index = 0
        try:
            full_script_path = self.remote_path + self.script
            helper = SSHServerHelper(self.mgmtip, self.username,
                                     self.password, self.mutex, self.userargs,
                                     self.tid, self.logger)
            client = self.prepareTheGround(helper, self.script_local_path, self.script, self.remote_path)
            for socket_list_index, socket in enumerate(self.socketlist):
                try:
                    ip = self.internalNameResolution(socket["address"])
                    port = socket["port"]
                    if not helper.testListenState(ip, port, client):
                        if self.userargs.stdout:
                            print("DEBUG STDOUT: " + self.tid + " Going to spawn socket \"%s:%s\" " % (ip, port))
                            self.logger.debug("%s Going to spawn socket \"%s:%s\"", self.tid, ip, port)
                        helper.runSocketServer(ip, port, self.userargs.servertimeout, client, full_script_path)
                        self.responseList.append({"socket": ip + ":" + port, "deployed": True})
                    else:
                        if self.userargs.stdout:
                            print("DEBUG STDOUT: " + self.tid + " Socket \"%s:%s\" is already in LISTEN "
                                                                "state on the remote server" % (ip, port))
                        self.logger.debug("%s Socket \"%s:%s\" is already in LISTEN"
                                          "state on the remote server", self.tid, ip, port)
                        self.responseList.append({"socket": ip + ":" + port, "deployed": False})

                except(RuntimeError, ConfiguationError) as ex:
                    # exc_type, exc_obj, exc_trace = sy()
                    self.exception_list.append(ex)
                    if socket_list_index != len(self.socketlist) - 1:
                        continue

            exception_result = self.exception_list
            if not self.exception_list:
                exception_result = "done"
            self.exception_queue.put(exception_result)
            self.result_queue.put(self.responseList)
            return

        except  (RuntimeError, Exception) as e:
            self.exception_list.append(e)

        finally:
            if hasattr(self, "client"):
                self.client.close()
                if self.userargs.stdout:
                    print("DEBUG STDOUT: " + self.tid + " the connection with %s has been closed" % self.mgmtip)
                self.logger.debug("%s: - Server Class - the connection with %s has been closed", self.tid,
                                  self.mgmtip)

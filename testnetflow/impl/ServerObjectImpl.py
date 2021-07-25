import os

from testnetflow.base.NetObjectBase import NetObjectBase
from testnetflow.exceptions.ConfigurationError import ConfiguationError
from testnetflow.impl.ServerHelperImpl import ServerHelperImpl
from testnetflow.exceptions.DnsError import DnsError
from paramiko import AuthenticationException

class ServerObjectImpl(NetObjectBase):

    def __init__(self, username, password,
                 mgmtip, attribute_list, logger,
                 exception_queue, result_queue,
                 to_close_queue,
                 tid, mutex, userargs, server_result_list,
                 server_to_close_list):

        super(ServerObjectImpl, self).__init__(mgmtip, tid, logger, username)
        self.script_local_path = os.path.join(os.getcwd(), "testnetflow", "scripts", "SocketServer.py")
        self.script = os.path.basename(self.script_local_path)
        self.responseList = server_result_list
        self.server_to_close_list = server_to_close_list
        self.to_close_queue = to_close_queue
        self.mgmtip = mgmtip
        self.username = username
        self.password = password
        self.socketlist = attribute_list
        self.logger = logger
        self.tid = tid
        self.mutex = mutex
        self.exception_queue = exception_queue
        self.result_queue = result_queue
        self.userargs = userargs
        self.logging_header = self.tid + self.logStrings.SEP + self.__class__.__name__ + self.logStrings.SEP
        self.debugging_header = self.logStrings.DEBUG_STDOUT_HEADER + self.logging_header
        self.full_script_path = self.remote_path + self.script

    def run(self):
        # socket_list_index = 0
        #print(self.debugging_header + "initial setup start..")
        try:
            helper = ServerHelperImpl(self.mgmtip, self.username,
                                      self.password, self.mutex, self.userargs,
                                      self.tid, self.logger)
            client = self.do_base_preparation(helper, self.script_local_path, self.script, self.remote_path)
            #print(self.debugging_header + "initial setup ended..")
            for socket_list_index, socket in enumerate(self.socketlist):
                try:
                    ip = self.internalNameResolution(socket["address"])
                    port = socket["port"]
                    self.mutex.acquire()
                    if not helper.test_listen_state(ip, port, client):
                        msg = self.logging_header + self.logStrings.SOCKET_IS_STARTING + str(ip) + ":" + str(port)
                        self.logger.printStdoutMessage(msg, self.logStrings.DEBUG_STDOUT_HEADER)
                        self.logger.loggingDebugMessage(msg)
                        helper.run_socket_server(ip, port, self.userargs.servertimeout, client, self.full_script_path)
                        self.responseList.append({"socket": ip + ":" + str(port), "deployed": True})
                        close_dict = {"binding_address": ip, "port": port, "close": True, "mgmt_ip": self.mgmtip,
                                      "username": self.username, "password": self.password}
                        self.server_to_close_list.append(close_dict)
                    else:
                        msg = self.logging_header + self.logStrings.SOCKET_ALREADY_LISTENING + str(ip) + ":" +str(port)
                        self.logger.printStdoutMessage(msg, self.logStrings.DEBUG_STDOUT_HEADER)
                        self.logger.loggingDebugMessage(msg)
                        self.responseList.append({"socket": ip + ":" + str(port), "deployed": False})


                except(RuntimeError, ConfiguationError, DnsError) as ex:
                    self.exception_list.append(ex)
                    if socket_list_index != len(self.socketlist) - 1:
                        continue
                finally:
                    self.mutex.release()

            exception_result = self.exception_list
            if not self.exception_list:
                exception_result = "done"
            self.exception_queue.put(exception_result)
            self.result_queue.put(self.responseList)
            self.to_close_queue.put(self.server_to_close_list)
            return

        except(RuntimeError, Exception, AuthenticationException) as e:
            msg = self.logging_header + self.logStrings.EXC_HEADER + str(e)
            self.exception_list.append(msg)
            self.to_close_queue.put(self.server_to_close_list)
            self.result_queue.put(self.responseList)
            self.exception_queue.put(self.exception_list)

        finally:
            try:
                if hasattr(self, "client"):
                    self.client.close()
            except NameError:
                pass
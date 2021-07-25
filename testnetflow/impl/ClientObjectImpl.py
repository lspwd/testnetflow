import os
import sys

from ClientHelperImpl import ClientHelperImpl
from testnetflow.base.NetObjectBase import NetObjectBase
from testnetflow.exceptions.ConfigurationError import ConfiguationError
from testnetflow.exceptions.DnsError import DnsError
from paramiko import AuthenticationException

class ClientObjectImpl(NetObjectBase):
    def __init__(self, username, password, mgmtip, attribute_list, logger, exception_queue,
                 result_queue, tid, mutex, userargs, server_result_list):
        super(ClientObjectImpl, self).__init__(mgmtip, tid, logger, username)
        self.result_queue = result_queue
        self.script_local_path = os.path.join(os.getcwd(), "testnetflow", "scripts", "SocketClient.py")
        self.script = os.path.basename(self.script_local_path)
        self.serverResultList = server_result_list
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


    def getClientIp(self, ipserver, sshclient):
        cmd = '/sbin/ip route get' + ' ' + ipserver \
              + '| /bin/egrep -o "src [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"|/bin/sed "s/src //g"'
        stdin, stdout, stderr = sshclient.exec_command(cmd, timeout=10)
        result = stdout.read().strip('\n')
        if result:
            return result
        else:
            msg = self.logging_header + self.logStrings.EXC_HEADER \
                  + self.logStrings.CLIENT_IP_ERROR
            raise DnsError(msg)

    def __normalizeList(self, lst):
        for (index, value) in enumerate(lst):
            if not value:
                lst.pop(index)

    def run(self):

        ipprodclient_list = []
        ipprodclient_dct = {}
        deployed = False
        full_script_path = self.remote_path + self.script

        try:
            helper = ClientHelperImpl(self.mgmtip, self.username,
                                      self.password, self.mutex, self.userargs,
                                      self.tid, self.logger)
            client = self.do_base_preparation(helper, self.script_local_path, self.script, self.remote_path)
            for socket_list_index, i in enumerate(self.socketlist):
                full_socket = i["address"] + ":" + str(i["port"])
                try:
                    if i["under_load_balancer"]:
                        if not i["load_balancer_address"]:
                            msg = self.logging_header + self.logStrings.EXC_HEADER \
                            + self.logStrings.LOAD_BALANCER_CFG_ERROR + self.logStrings.ON_IP_MSG \
                            + str(i["address"]) + ":" + str(i["port"])
                            raise ConfiguationError(msg)
                        ip = self.internalNameResolution(i["load_balancer_address"].split(":")[0])
                        port = i["load_balancer_address"].split(":")[1]
                        full_socket = ip + ":" + str(port)
                        deployed = False
                    else:
                        ip = self.internalNameResolution(i["address"])
                        port = i["port"]
                        full_socket = ip + ":" + str(i["port"])
                        for serverResult in self.serverResultList:
                            if serverResult["socket"] == full_socket:
                                deployed = serverResult["deployed"]
                    result = helper.runSocketClient(ip, port, self.userargs.clienttimeout, client, full_script_path,
                                                        deployed)
                    ipprodclient_list.append((full_socket, result))
                    try:
                        clientprodip = self.getClientIp(ip, client)
                    except DnsError:
                        clientprodip = self.mgmtip
                    ipprodclient_dct[clientprodip] = ipprodclient_list

                except (RuntimeError, ConfiguationError, DnsError) as ex:
                    self.exception_list.append(ex)
                    ipprodclient_list.append((full_socket, False))
                    if socket_list_index != len(self.socketlist) - 1:
                        continue

            exception_result = self.exception_list
            if not self.exception_list:
                exception_result = "done"
            self.exception_queue.put(exception_result)
            self.result_queue.put(ipprodclient_dct)
            return
        except (RuntimeError, ConfiguationError, Exception, AuthenticationException) as e:
            ipprodclient_dct[self.mgmtip] = ipprodclient_list
            msg = self.logging_header + self.logStrings.EXC_HEADER + str(e)
            self.result_queue.put(ipprodclient_dct)
            self.exception_list.append(msg)
            self.exception_queue.put(self.exception_list)

        finally:
            try:
                if hasattr(self, "client"):
                    self.client.close()
            except NameError:
                pass

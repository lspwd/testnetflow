import os
import sys

from ConfigurationError import ConfiguationError
from NetBaseObject import NetBaseObject
from SSHClientHelper import SSHClientHelper


class Client(NetBaseObject):
    def __init__(self, username, password, mgmtip, attribute_list, logger, exception_queue,
                 result_queue, name, mutex, userargs, server_result_list):
        super(Client, self).__init__(username, password, mgmtip, attribute_list, logger,
                                     exception_queue, result_queue, name, mutex, userargs )
        self.result_queue = result_queue
        self.script_local_path = os.getcwd() + os.path.sep + "lib" + os.path.sep \
                                 + "scripts" + os.path.sep + "SocketClient.py"
        self.script = os.path.basename(self.script_local_path)
        self.serverResultList = server_result_list

    def getClientIp(self, ipserver, sshclient):

        cmd = '/sbin/ip route get' + ' ' + ipserver \
              + '| /bin/egrep -o "src [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"|/bin/sed "s/src //g"'
        stdin, stdout, stderr = sshclient.exec_command(cmd)
        result = stdout.read().strip('\n')
        if result:
            return result
        else:
            raise RuntimeError("unable to fetch client ip")

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
            helper = SSHClientHelper(self.mgmtip, self.username,
                                     self.password, self.mutex, self.userargs,
                                     self.tid, self.logger)
            client = self.prepareTheGround(helper, self.script_local_path, self.script, self.remote_path)

            for socket_list_index, i in enumerate(self.socketlist):

                full_socket = i["address"] + ":" + i["port"]
                try:
                    # print("iteration no " + str(socket_list_index))
                    if i["under_load_balancer"]:
                        if not i["load_balancer_address"]:
                            raise ConfiguationError("Empty load balancer address property for server "
                                                    + i["address"] + ":" + i["port"])
                        ip = self.internalNameResolution(i["load_balancer_address"].split(":")[0])
                        port = i["load_balancer_address"].split(":")[1]
                        full_socket = ip + ":" + port
                        deployed = False
                    else:
                        # print("Starting name resolution...")
                        ip = self.internalNameResolution(i["address"])
                        port = i["port"]
                        full_socket = ip + ":" + i["port"]

                        for serverResult in self.serverResultList:
                            if serverResult["socket"] == full_socket:
                                deployed = serverResult["deployed"]

                        # print("Was the socket " + full_socket + " deployed by me? " + str(deployed))

                    if deployed:
                        result = helper.runSocketClient(ip, port, self.userargs.clienttimeout, client, full_script_path, True)
                    else:
                        # print("full_socket here -> " + full_socket)
                        result = helper.runSocketClient(ip, port, self.userargs.clienttimeout, client, full_script_path, False)
                    if result:
                        ipprodclient_list.append((full_socket, True))
                    else:
                        ipprodclient_list.append((full_socket, False))

                    try:
                        clientprodip = self.getClientIp(ip, client)
                    except RuntimeError:
                        clientprodip = self.mgmtip

                    ipprodclient_dct[clientprodip] = ipprodclient_list

                except (RuntimeError, ConfiguationError) as ex:
                    # print("inner Except ... " + str(ex))

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

        except (RuntimeError, ConfiguationError, Exception) as e:
            # print("Outer Except ... " +str(e))
            ipprodclient_dct[self.mgmtip] = ipprodclient_list
            self.result_queue.put(ipprodclient_dct)
            self.exception_queue.put(sys.exc_info())

        finally:
            try:
                if hasattr(self, "client"):
                    self.client.close()
                    if self.userargs.stdout:
                        print("DEBUG STDOUT: " + self.tid + " the connection with %s has been closed" % self.mgmtip)
                    self.logger.debug("%s: - Client Class - the connection with %s has been closed", self.tid,
                                      self.mgmtip)
            except NameError:
                pass

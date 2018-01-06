import sys
import os
from SSHClientHelper import SSHClientHelper
from NetBaseObject import NetBaseObject
from ConfigurationError import ConfiguationError


class Client(NetBaseObject):
    def __init__(self, username, password, mgmtip, attribute_list, logger, queue, exception_queue, name, mutex,
                 userargs, server_result_list):
        super(Client, self).__init__(username, password, mgmtip, attribute_list, logger, exception_queue, name, mutex,
                                     userargs)
        self.queue = queue
        self.script_local_path = os.getcwd() + os.path.sep + "lib" + os.path.sep + \
                                 "scripts" + os.path.sep + "SocketClient.py"
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
            for i in self.socketlist:

                if i["under_load_balancer"]:
                    if not i["load_balancer_address"]:
                        raise ConfiguationError("Empty load balancer address property for server "
                                                + i["address"] + ":" + i["port"])
                    ip = i["load_balancer_address"].split(":")[0]
                    port = i["load_balancer_address"].split(":")[1]
                    full_socket = ip + ":" + port
                    deployed = False
                else:
                    ip = i["address"]
                    port = i["port"]
                    full_socket = i["address"] + ":" + i["port"]

                    for serverResult in self.serverResultList:
                        if serverResult["socket"] == full_socket:
                            deployed = serverResult["deployed"]

                    # print("Was the socket " + full_socket + " deployed by me? " + str(deployed))

                if deployed:
                    result = helper.runSocketClient(ip, port, "3", client, full_script_path, True)
                else:
                    # print("full_socket here -> " + full_socket)
                    result = helper.runSocketClient(ip, port, "3", client, full_script_path, False)
                if result:
                    ipprodclient_list.append((full_socket, True))
                else:
                    ipprodclient_list.append((full_socket, False))

                clientprodip = self.getClientIp(ip, client)
                ipprodclient_dct[clientprodip] = ipprodclient_list

            self.exception_queue.put("Done")
            self.queue.put(ipprodclient_dct)

        except (RuntimeError, Exception):
            map(lambda socket: ipprodclient_list.append((socket["address"] + ":"
                                                         + socket["port"], False)), self.socketlist)
            ipprodclient_dct[self.mgmtip] = ipprodclient_list
            self.queue.put(ipprodclient_dct)
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

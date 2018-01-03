import sys
import os
from SSHClientHelper import SSHClientHelper
from NetBaseObject import NetBaseObject


class Client(NetBaseObject):
    # server[mgmtip],server[username],server[ password], server[socket]
    def __init__(self, dct, logger, queue, exception_queue, name, mutex, userargs, serverResultList):
        super(Client, self).__init__(dct, logger, exception_queue, name, mutex, userargs)
        self.queue = queue
        self.script_local_path = os.getcwd() + os.path.sep + "lib" + os.path.sep + \
                                 "scripts" + os.path.sep + "SocketClient.py"
        self.script = os.path.basename(self.script_local_path)
        self.serverResultList = serverResultList

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
        full_script_path = self.remote_path + self.script
        try:
            helper = SSHClientHelper(self.mgmtip, self.username,
                                     self.password, self.mutex, self.userargs,
                                     self.tid, self.logger)
            client = self.prepareTheGround(helper, self.script_local_path, self.script, self.remote_path)
            for i in self.socketlist:
                # print "*"*100
                # print "Processo in entrata su Client.run -> " +i
                # print "I in list -> " +i
                # print "*"*100
                # TODO determine whether to call a generic connect or my impl.

                deployed_lst = []
                for serverResult in self.serverResultList:
                    tmp = map(lambda x: x["deployed"] if x["socket"] == i else None, serverResult)
                    tmp = filter(lambda x: x is not None, tmp)
                    deployed_lst.append(tmp)

                try:
                    deployed = deployed_lst[-1][-1]
                except IndexError:
                    deployed = False
                print("Was the socket " + i + " deployed by me? " + str(deployed))
                ip = i.split(":")[0]
                port = i.split(":")[1]

                if deployed:
                    result = helper.runSocketClient(ip, port, "3", client, full_script_path, True)
                else:
                    result = helper.runSocketClient(ip, port, "3", client, full_script_path, False)
                if result:
                    ipprodclient_list.append((i, True))
                else:
                    ipprodclient_list.append((i, False))

                clientprodip = self.getClientIp(ip, client)
                ipprodclient_dct[clientprodip] = ipprodclient_list

            self.exception_queue.put("Done")
            self.queue.put(ipprodclient_dct)

        except (RuntimeError, Exception):
            for i in self.socketlist:
                ipprodclient_list.append((i, False))
            ipprodclient_dct[self.mgmtip] = ipprodclient_list
            # print "!"*100
            # print ipprodclient_dct
            # print "!"*100
            self.queue.put(ipprodclient_dct)
            # print "Client Exception Dict Pushed!!"
            # print "Client ip processed: " +str(self.mgmtipclient)
            # raise NameError ("Error on Server class run() method: ",e)
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

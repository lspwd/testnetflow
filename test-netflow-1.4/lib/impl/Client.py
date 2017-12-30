import sys

import NetBaseObject


class Client(NetBaseObject):
    # server[mgmtip],server[username],server[password],server[socket]
    def __init__(self, dct, logger, queue, exception_queue, name, mutex, userargs):
        super(Client, self).__init__(dct, logger, exception_queue, name, mutex, userargs)
        self.queue = queue

    def __getClientIp(self, ipserver, sshclient):
        cmd = '/sbin/ip route get' + ' ' + ipserver \
              + '| /bin/egrep -o "src [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"|/bin/sed "s/src //g"'
        stdin, stdout, stderr = sshclient.exec_command(cmd)
        result = stdout.read().strip('\n')

        if len(result) > 0:
            return result
        else:
            raise NameError("__getClientIp is unable to fetch client ip!")

    def __normalizeList(self, lst):
        for (index, value) in enumerate(lst):
            if not value:
                lst.pop(index)

    # TODO refactor :
    # Test python
    # determine python path & version
    # swap the shebang
    # upload clientrscript
    # start the client against the list of server
    # evaluate result

    def run(self):

        ipprodclient_list = []
        ipprodclient_dct = {}

        try:

            sshclient = self.__sshConnect()

            for i in self.serverlist:
                # print "*"*100
                # print "Processo in entrata su Client.run -> " +i
                # print "I in list -> " +i
                # print "*"*100
                ip = i.split(":")[0]
                port = i.split(":")[1]
                if self.__testSocket(sshclient, ip, port):
                    ipprodclient_list.append((i, True))
                else:
                    ipprodclient_list.append((i, False))
                clientprodip = self.__getClientIp(ip, sshclient)
                ipprodclient_dct[clientprodip] = ipprodclient_list

            self.exception_queue.put("Done")
            self.queue.put(ipprodclient_dct)

        except Exception:
            for i in self.serverlist:
                ipprodclient_list.append((i, False))
            ipprodclient_dct[self.mgmtipclient] = ipprodclient_list
            # print "!"*100
            # print ipprodclient_dct
            # print "!"*100
            self.queue.put(ipprodclient_dct)
            # print "Client Exception Dict Pushed!!"
            # print "Client ip processed: " +str(self.mgmtipclient)
            # raise NameError ("Error on Server class run() method: ",e)
            self.exception_queue.put(sys.exc_info())

        finally:
            # self.queue.put({},block=False)
            if hasattr(self, "client"):
                self.client.close()
                if self.userargs.stdout:
                    print "DEBUG STDOUT: " + self.tid + " the connection with %s has been closed" % self.mgmtipclient
                self.logger.debug("%s: - Client Class - the connection with %s has been closed", self.tid,
                                  self.mgmtipclient)
                # print "DEBUG STDOUT: "+self.tid  +" Client Has Attr self.client "

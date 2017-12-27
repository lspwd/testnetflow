import threading
import paramiko
import sys

from NetcatValidator import NetcatValidator

class Client(threading.Thread):
    # server[mgmtip],server[username],server[password],server[socket]
    def __init__(self, dct, logger, queue, exception_queue, netcat, name, mutex, userargs):
        super(Client, self).__init__()
        self.mgmtipclient = dct["mgmtip"]
        # print "self.mgmtipclient: " +self.mgmtipclient
        self.username = dct["username"]
        # print "self.username: " +self.username
        self.password = dct["password"]
        # print "self.password: " +str(self.password)
        self.serverlist = dct["socket"]
        self.netcat = netcat
        self.logger = logger
        self.queue = queue
        self.tid = name
        self.mutex = mutex
        self.exception_queue = exception_queue
        self.userargs = userargs

    def __sshConnect(self):
        try:
            self.mutex.acquire()
            # self.client = ""
            self.client = paramiko.SSHClient()
            self.client.load_system_host_keys()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.logger.debug(
                '%s: - Client class - ssh connection with Username: \"%s\", Password \"%s\" and ip \"%s\"', self.tid,
                self.username, self.password, self.mgmtipclient)
            if self.userargs.stdout:
                print "DEBUG STDOUT: " + self.tid \
                      + "- Client class - ssh connection with Username: \"%s\", Password: " \
                        "\"%s\" and ip address: \"%s\"" % (self.username, self.password, self.mgmtipclient)
            self.client.connect(self.mgmtipclient, username=self.username, password=self.password, timeout=2,
                                allow_agent=False, look_for_keys=False)
            return self.client

        except  Exception, e:
            raise NameError("Error in Client Class __sshConnect() method: ", e)
        finally:
            self.mutex.release()

    def __testSocket(self, sshclient, ipserver, port):
        # cmd='/usr/bin/nc -zvn -w 3'+' '+ipserver+' '+port
        prodip = self.__getClientIp(ipserver, sshclient)
        cmd = self.netcat + ' -zvn -w 3' + ' ' + ipserver + ' ' + port
        stdin, stdout, stderr = sshclient.exec_command(cmd)
        err = ""
        try:
            result = stdout.read().strip('\n')
            result.index('succeeded')
            if self.userargs.stdout:
                print "DEBUG STDOUT: " + self.tid + " : The net flow from server " + prodip + " to server " \
                      + ipserver + " on port " + port + " is fine!"
            self.logger.debug("%s The net flow from server %s to server %s on port %s is fine!", self.tid, prodip,
                              ipserver, port)
            return True

        except ValueError:
            if self.userargs.stdout:
                err = stderr.read().strip('\n')
                # print "STDERR -> " +err
                print "DEBUG STDOUT: " + self.tid + " : The net flow from server " + prodip + " to server " \
                      + ipserver + " on port " + port + " is not fine!"
            self.logger.debug("STDERR ---> %s ", err)
            self.logger.debug("%s The net flow from server %s to server %s on port %s is not fine!",
                              self.tid, prodip, ipserver, port)
            return False

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

    def run(self):

        ipprodclient_list = []
        ipprodclient_dct = {}

        try:

            sshclient = self.__sshConnect()
            netcatvalidator = NetcatValidator(sshclient, self.netcat, self.mgmtipclient, self.tid, self.logger,
                                              self.userargs)
            if not netcatvalidator.validate():
                raise NameError(
                    "Error on Server class run() method: netcat has not been found on target system "
                    + self.mgmtipclient)

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

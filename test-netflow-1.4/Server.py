import threading
import sys
import paramiko
from ChannelHelper import ChannelHelper
from NetcatValidator import NetcatValidator
from SudoHelper import SudoHelper


class Server(threading.Thread):

    def __init__(self, dct, logger, exception_queue, netcat, name, mutex, userargs):
        super(Server, self).__init__()
        self.mgmtipserver = dct["mgmtip"]
        self.username = dct["username"]
        self.password = dct["password"]
        self.socketlist = dct["socket"]
        self.netcat = netcat
        self.logger = logger
        self.exception_queue = exception_queue
        self.tid = name
        self.mutex = mutex
        self.userargs = userargs

    def __sshConnect(self):
        try:
            self.mutex.acquire()
            self.client = paramiko.SSHClient()
            self.client.load_system_host_keys()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if self.userargs.stdout:
                print "DEBUG STDOUT: " + self.tid + " Username: \"%s\", Password: \"%s\" and ip address: \"%s\"" % (
                    self.username, self.password, self.mgmtipserver)
            self.logger.debug(
                '%s - Server class - __sshConnect(): Connecting with Username: \"%s\", Password \"%s\" and ip \"%s\"',
                self.tid, self.username, self.password, self.mgmtipserver)
            self.client.connect(self.mgmtipserver, username=self.username, password=self.password, timeout=2,
                                allow_agent=False, look_for_keys=False)
            return self.client

        except  Exception as e:
            raise NameError("Error in __sshConnect() method --- on server: " + self.mgmtipserver + " " + str(e))

        finally:
            self.mutex.release()

    def __testSocket(self, ip, port, client):

        cmd = '/bin/netstat -ntl | /bin/egrep -o ''\'' + ip + ':' \
              + port + '[ ]{1}|0.0.0.0:' + port + '[ ]{1}|::.*:' + port + '\''
        stdin, stdout, stderr = client.exec_command(cmd)
        result = stdout.read().strip('\n')
        # resulterr = stderr.read().strip("\n")

        if not result:
            if self.userargs.stdout:
                print "DEBUG STDOUT: " + self.tid \
                      + " \"%s:%s\" is not in LISTEN state on server, going to deploy it via netcat" % (ip, port)
            self.logger.debug('%s \"%s:%s\" is not in LISTEN state on server, going to deploy it via netcat', self.tid,
                              ip, port)
            return True
        else:
            if self.userargs.stdout:
                print "DEBUG STDOUT: " + self.tid + " %s:%s is already in LISTEN state on server! " % (ip, port)
            self.logger.debug('%s \"%s:%s\" is already in LISTEN state on server!', self.tid, ip, port)
            return False

    def __deploySocket(self, ip, port, client):

        chan = client.invoke_shell()
        chan.set_combine_stderr(True)
        chan.settimeout(20)

        if int(port) <= 1024:
            custompattern = 'successfully.'
            # cmd = ('sudo -k -b nohup /usr/bin/nc -kl ' +ip +' ' +port +'\n')
            cmd = ('sudo -k -b nohup ' + self.netcat + ' -kl ' + ip + ' ' + port + '\n')
            sudohelper = SudoHelper(custompattern, self.username, self.password, chan, self.logger, cmd)
            try:
                sudohelper.doSudo()

                if self.__testSocket(ip, port, client):
                    self.logger.error("__deploySocket Error: check SudoHelper.doSudo() method")
                    chan.close()
                    raise NameError("Error in __deploySocket() method: check SudoHelper.doSudo() method")

                if self.userargs.stdout:
                    print "DEBUG STDOUT: " + self.tid + " Socket on \"%s:%s\" has been deployed via netcat" \
                                                        % (ip, port)
                self.logger.debug("%s Socket on \"%s:%s\" has been deployed via netcat", self.tid, ip, port)
            except Exception as e:
                self.logger.error("__deploySocket Error: %s", e)
                raise NameError("Error in __deploySocket() method: ", e)
            finally:
                if chan:
                    chan.close()
        else:
            try:
                cmd = ('nohup ' + self.netcat + ' -kl ' + ip + ' ' + port + ' 2>&1 > /dev/null &\n')
                # cmd = ('nohup /usr/bin/nc -kl ' +ip +' ' +port +' 2>&1 > /dev/null &\n')
                channelhelper = ChannelHelper(chan, self.logger, cmd)
                channelhelper.mainLogic()
                if self.__testSocket(ip, port, client):
                    self.logger.error("__deploySocket Error: check ChannelHelper.mainLogic() method")
                    chan.close()
                    raise NameError("Error in __deploySocket() method: check ChannelHelper.mainLogic() method")

                if self.userargs.stdout:
                    print "DEBUG STDOUT: " + self.tid + " Socket on \"%s:%s\" has been deployed via netcat" % (ip, port)
                self.logger.debug("%s Socket on \"%s:%s\" has been deployed via netcat", self.tid, ip, port)

            except Exception as e:
                self.logger.error("__deploySocket Error: %s", e)
                raise NameError("Error in __deploySocket() method: ", e)

            finally:
                if chan:
                    chan.close()

    def run(self):

        try:
            client = self.__sshConnect()
            netcatvalidator = NetcatValidator(client, self.netcat,
                                              self.mgmtipserver, self.tid, self.logger, self.userargs)
            if not netcatvalidator.validate():
                raise NameError(
                    "Error on Server class run() method: netcat has not been found on target system "
                    + self.mgmtipserver)
            # print "Mgmt -> " +self.mgmtipserver +" Socket To Spawn -> " +str(self.socketlist)
            for i in self.socketlist:
                ip = i.split(":")[0]
                port = i.split(":")[1]

                if self.__testSocket(ip, port, client):
                    if self.userargs.stdout:
                        print "DEBUG STDOUT: " + self.tid + " Going to call netcat for \"%s:%s\" " % (ip, port)
                    self.logger.debug("%s Going to call netcat for \"%s:%s\"", self.tid, ip, port)
                    self.__deploySocket(ip, port, client)
                else:
                    if self.userargs.stdout:
                        print "DEBUG STDOUT: " + self.tid + " Netcat help is not needed for \"%s:%s\" " % (ip, port)
                    self.logger.debug("%s Netcat help is not needed for \"%s:%s\"", self.tid, ip, port)
            self.exception_queue.put("done")
            return
        except Exception:
            self.exception_queue.put(sys.exc_info())
        finally:
            if hasattr(self, "client"):
                self.client.close()
                if self.userargs.stdout:
                    print "DEBUG STDOUT: " + self.tid + " the connection with %s has been closed" % self.mgmtipserver
                self.logger.debug("%s: - Server Class - the connection with %s has been closed", self.tid,
                                  self.mgmtipserver)

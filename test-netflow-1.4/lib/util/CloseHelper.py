import sys
import threading

import paramiko

from impl.SudoHelper import SudoHelper


class CloseHelper(threading.Thread):
    def __init__(self, dct, logger, exception_queue, netcat, name, mutex, userargs):
        super(CloseHelper, self).__init__()
        self.mgmtipserver = dct["mgmtip"]
        self.username = dct["username"]
        self.password = dct["password"]
        self.socketlist = dct["socket"]
        self.logger = logger
        self.netcat = netcat
        self.tid = name
        self.mutex = mutex
        self.exception_queue = exception_queue
        self.userargs = userargs

    def __sshConnect(self):
        try:
            self.mutex.acquire()
            self.client = paramiko.SSHClient()
            self.client.load_system_host_keys()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.logger.debug(
                '%s - CloseHelper class - __sshConnect(): '
                'Connecting with Username: \"%s\", Password \"%s\" and ip \"%s\"',
                self.tid, self.username, self.password, self.mgmtipserver)
            self.client.connect(self.mgmtipserver, username=self.username, password=self.password, timeout=2,
                                allow_agent=False, look_for_keys=False)
            return self.client

        except  Exception, e:
            raise NameError("Error in __sshConnect() method --- on server: " + self.mgmtipserver + " " + str(e))
        finally:
            self.mutex.release()

    def __closeSocket(self, sshclient):
        chan = ""
        try:
            chan = sshclient.invoke_shell()
            chan.set_combine_stderr(True)
            chan.settimeout(20)
            custompattern = 'Killed'
            # cmd = ("sudo pkill -9 -f -- \"/usr/bin/nc -kl .*\"\n")
            cmd = ("sudo pkill -9 -f -- \"" + self.netcat + " -kl .*\"\n")
            sudohelper = SudoHelper(custompattern, self.username, self.password, chan, self.logger, cmd)
            try:
                sudohelper.doSudo()
            except NameError, e:
                self.logger.error("__deploySocket Error: %s", e)
                if hasattr(chan, "close"):
                    chan.close()
                raise NameError("Error in __deploySocket() method: ", e)

        except Exception, e:
            raise NameError("Error on closeSocket() method: ", e)

        finally:
            if hasattr(chan, "close"):
                chan.close()

    def run(self):
        client = ""
        try:
            client = self.__sshConnect()
            self.__closeSocket(client)
            self.exception_queue.put("done")

        except Exception:
            # raise NameError( "Error on CloseHelper Class run() method:", e )
            self.exception_queue.put(sys.exc_info())

        finally:
            if hasattr(self, "client"):
                client.close()
                if self.userargs.stdout:
                    print "DEBUG STDOUT: " + self.tid + " the connection with %s has been closed" % self.mgmtipserver
                self.logger.debug("%s: - CloseHelper Class - the connection with %s has been closed", self.tid,
                                  self.mgmtipserver)

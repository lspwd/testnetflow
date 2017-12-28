import paramiko


class SSHHelper:
    def __init__(self, ip, username, password, mutex, userargs, tid, logger):
        self.ip = ip
        self.username = username
        self.password = password
        self.mutex = mutex
        self.userargs = userargs
        self.tid = tid
        self.logger = logger

    def sshConnect(self):
        try:
            self.mutex.acquire()
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if self.userargs.stdout:
                print ("DEBUG STDOUT: " + self.tid + " Username: \"%s\", Password: \"%s\" and ip address: \"%s\"" %
                       self.username, self.password, self.ip)
            self.logger.debug('%s - Server class - __sshConnect(): Connecting with Username: \"%s\",'
                              ' Password \"%s\" and ip \"%s\"',
                              self.tid, self.username, self.password, self.ip)
            client.connect(self.ip, username=self.username, password=self.password, timeout=2,
                           allow_agent=False, look_for_keys=False)
            return client

        except  Exception as e:
            raise NameError("Error in __sshConnect() method --- on server: " + self.ip + " " + str(e))

        finally:
            self.mutex.release()

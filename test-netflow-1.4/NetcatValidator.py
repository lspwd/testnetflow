class NetcatValidator:

    def __init__(self, sshclient, filename, ip, name, logger, userargs):
        self.client = sshclient
        self.filename = filename
        self.ip = ip
        self.tid = name
        self.logger = logger
        self.userargs = userargs

    def validate(self):
        try:
            if self.filename.find("/") >= 0 and self.filename.find("nc") >= 0:
                stdin, stdout, stderr = self.client.exec_command(self.filename)
                stderr_check = stderr.read().strip("\n")
                if stderr_check.find("usage: nc [") >= 0:
                    if self.userargs.stdout:
                        print "DEBUG STDOUT: " + self.tid + " A valid netcat binary has been found on the system " \
                              + self.ip
                    self.logger.debug("%s:  A valid Netcat binary has been found on the system %s", self.tid, self.ip)
                    return True
                else:
                    if self.userargs.stdout:
                        print "DEBUG STDOUT: " + self.tid + " netcat binary could not be found on target system " \
                              + self.ip
                    self.logger.debug("%s:  netcat binary could not be found on target system", self.tid, self.ip)
                    return False
            elif self.filename == "nc":
                stdin, stdout, stderr = self.client.exec_command(self.filename)
                stderr_check = stderr.read().strip("\n")
                if stderr_check.find("usage: nc [") >= 0:
                    if self.userargs.stdout:
                        print "DEBUG STDOUT: " + self.tid + " A valid netcat binary has been found on the system " \
                              + self.ip
                    self.logger.debug("%s:  A valid Netcat binary has been found on the system %s", self.tid, self.ip)
                    return True
                else:
                    if self.userargs.stdout:
                        print "DEBUG STDOUT: " + self.tid + " netcat binary could not be found on target system " \
                              + self.ip
                        self.logger.debug("%s:  netcat binary could not be found on target system", self.tid, self.ip)
                    return False
            else:
                if self.userargs.stdout:
                    print "DEBUG STDOUT: " + self.tid + " netcat binary could not be found on target system " + self.ip
                self.logger.debug("%s:  netcat binary could not be found on target system", self.tid, self.ip)
                return False

        except Exception, e:
            raise NameError("Error in the NetcatValidator validateNc() method: ", e)

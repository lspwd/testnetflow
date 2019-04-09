import re

from testnetflow.base.SSHHelper import SSHHelper


class SSHClientHelper(SSHHelper):
    def __init__(self, ip, username, password, mutex, userargs, tid, logger):
        super(SSHClientHelper, self).__init__(ip, username, password, mutex, userargs, tid, logger)

    # working on upload here

    def runSocketClient(self, ip, port, timeout, client, scriptname, deployed):

        try:
            # Starting Client script on the remote machine..

            cmd = scriptname + " " + ip + " " + port + " " + timeout + " " + str(deployed)
            stdin, stdout, stderr = client.exec_command(cmd)
            result = stderr.read().strip("\n")
            # print("Peek at client stderr result: " + result )
            if result:
                pattern = ".+(the remote endpoint).+"
                find = re.compile(pattern)
                match = find.match(result)
                if match is None:
                    raise RuntimeError("Exception while testing the remote endpoint")

                else:
                    # print("Track self.usersargs.. " +str(self.userargs))
                    if self.userargs.stdout:
                        print("DEBUG STDOUT: " + self.tid + " unable to connect to the remote server \"%s:%s\" "
                              % (ip, port))
                    self.logger.debug("%s unable to connect to the remote server \"%s:%s\" ", self.tid, ip, port)
                    return False
            else:
                result = stdout.read().strip("\n")
                # print("Peek client stdout result: " + result)
                if result.endswith("has been tested successfully!"):
                    if self.userargs.stdout:
                        print("DEBUG STDOUT: " + self.tid + " successful connection to server \"%s:%s\" "
                              % (ip, port))
                    self.logger.debug("%s successful connection to server \"%s:%s\" ", self.tid, ip, port)
                    return True
                else:
                    raise RuntimeError("Exception while testing the remote endpoint")

        except Exception as e:
            self.logger.error("SSHClientHelper() :" + str(e))
            raise RuntimeError("SSHClientHelper() : " + str(e))

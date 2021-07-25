import re

from testnetflow.base.NetHelperBase import NetHelperBase


class ClientHelperImpl(NetHelperBase):
    def __init__(self, ip, username, password, mutex, userargs, tid, logger):
        super(ClientHelperImpl, self).__init__(ip, username, password, mutex, userargs, tid, logger)
        self.logging_header = self.tid + self.logStrings.SEP + self.__class__.__name__ + self.logStrings.SEP

    def runSocketClient(self, ip, port, timeout, client, scriptname, deployed):
        try:
            # Starting Client script on the remote machine..
            cmd = scriptname + " " + ip + " " + str(port) + " " + timeout + " " + str(deployed) + " " + str(False)
            stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
            result = stderr.read().strip("\n")
            if result:
                pattern = ".+(the remote endpoint).+"
                find = re.compile(pattern)
                match = find.match(result)
                if match is None:
                    msg = self.logging_header + self.logStrings.EXC_HEADER \
                          + self.logStrings.NULL_RESPONSE_ERROR
                    raise RuntimeError(msg)
                else:
                    msg = self.logging_header + self.logStrings.CLIENT_CONN_ERROR + ip + ":" + str(port)
                    self.logger.printStdoutMessage(msg, self.logStrings.DEBUG_STDOUT_HEADER)
                    self.logger.loggingDebugMessage(msg)
                    return False
            else:
                result = stdout.read().strip("\n")
                if result.endswith("has been tested successfully!"):
                    msg = self.logging_header + self.logStrings.CLIENT_CONN_OK + ip + ":" + str(port)
                    self.logger.printStdoutMessage(msg, self.logStrings.DEBUG_STDOUT_HEADER)
                    self.logger.loggingDebugMessage(msg)
                    return True
                else:
                    msg = self.logging_header + self.logStrings.EXC_HEADER \
                          + self.logStrings.UNKNOWN_ERROR
                    raise RuntimeError(msg)

        except Exception as e:
            msg = self.logging_header + self.logStrings.EXC_HEADER + str(e)
            self.logger.printStdoutMessage(msg, self.logStrings.ERROR_STDOUT_HEADER)
            self.logger.loggingErrorMessage(msg)
            raise RuntimeError(msg)

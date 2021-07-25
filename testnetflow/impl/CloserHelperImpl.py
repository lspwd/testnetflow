import re

from testnetflow.base.NetHelperBase import NetHelperBase


class CloserHelperImpl(NetHelperBase):

    def __init__(self, ip, username, password, mutex, userargs, tid, logger):
        super(CloserHelperImpl, self).__init__(ip, username, password, mutex, userargs, tid, logger)
        self.logging_header = self.tid + self.logStrings.SEP + self.__class__.__name__ + self.logStrings.SEP

    def closeSocket(self, serverip, port, timeout, client, scriptname):
        try:
            self.mutex.acquire()
            if self.test_listen_state(serverip, port, client):
                cmd = scriptname + " " + serverip + " " + str(port) + " " + timeout + " " + "False True"
                stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
                result = stderr.read().strip("\n")
                if result:
                    pattern = ".+(the remote server).+"
                    find = re.compile(pattern)
                    match = find.match(result)
                    if match is None:
                        msg = self.logging_header + self.logStrings + self.logStrings.NULL_RESPONSE_ERROR + \
                              + self.logStrings.ON_IP_MSG + str(serverip)
                        raise RuntimeError(msg)
                    else:
                        msg = self.logging_header + self.logStrings.CLOSE_ERROR \
                        + str(serverip) + ":" + str(port)
                        self.logger.printStdoutMessage(msg, self.logStrings.DEBUG_STDOUT_HEADER)
                        self.logger.loggingDebugMessage(msg)
                        return False
                else:
                    result = stdout.read().strip("\n")
                    if result.endswith("has been closed successfully!"):
                        msg = self.logging_header + self.logStrings.CLOSE_OK_MGS \
                        + str(serverip) + ":" +str(port)
                        self.logger.printStdoutMessage(msg, self.logStrings.DEBUG_STDOUT_HEADER)
                        self.logger.loggingDebugMessage(msg)
                        return True
                    else:
                        msg = self.logging_header + self.logStrings.EXC_HEADER + self.logStrings.CLOSE_ERROR
                        raise RuntimeError(msg)
            else:
                msg = self.logging_header + self.logStrings.ALREADY_CLOSED_MSG \
                + str(serverip) + ":" + str(port)
                self.logger.printStdoutMessage(msg, self.logStrings.DEBUG_STDOUT_HEADER)
                self.logger.loggingDebugMessage(msg)
                return True
        except Exception as e:
            msg = self.logging_header + self.logStrings.EXC_HEADER + str(e)
            self.logger.error(msg)
            raise RuntimeError(msg)
        finally:
            self.mutex.release()

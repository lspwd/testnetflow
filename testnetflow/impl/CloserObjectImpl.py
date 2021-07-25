import os
import sys

from CloserHelperImpl import CloserHelperImpl
from testnetflow.base.NetObjectBase import NetObjectBase
from testnetflow.exceptions.ConfigurationError import ConfiguationError
from paramiko import AuthenticationException

class CloserObjectImpl(NetObjectBase):

    def __init__(self,
                 username,
                 password,
                 mgmtip,
                 binding_address,
                 port,
                 logger,
                 closed_exception_queue,
                 mutex,
                 userargs,
                 tid):

        super(CloserObjectImpl, self).__init__(mgmtip, tid, logger, username)

        self.username = username
        self.password = password
        self.mgmtip = mgmtip
        self.binding_address = binding_address
        self.port = port
        self.tid = tid
        self.closed_exception_queue = closed_exception_queue
        self.script_local_path = os.path.join(os.getcwd(), "testnetflow", "scripts", "SocketClient.py")
        self.script = os.path.basename(self.script_local_path)
        self.mutex = mutex
        self.userargs = userargs
        self.userargs = userargs
        self.logging_header = self.tid + self.logStrings.SEP + self.__class__.__name__ + self.logStrings.SEP


    def run(self):

        full_script_path = self.remote_path + self.script
        try:
            helper = CloserHelperImpl(self.mgmtip, self.username, self.password,
                                      self.mutex, self.userargs, self.tid, self.logger)

            client = self.do_base_preparation(helper, self.script_local_path, self.script, self.remote_path)
            result = helper.closeSocket(self.binding_address, self.port, self.userargs.clienttimeout, client,
                                        full_script_path)
            if result:
                msg = self.logging_header + self.logStrings.CLOSE_CONNECTION_MSG \
                + str(self.binding_address) +":"  +str(self.port)
                self.logger.printStdoutMessage(msg, self.logStrings.DEBUG_STDOUT_HEADER)
                self.logger.loggingDebugMessage(msg)
                self.closed_exception_queue.put("done")
                return
            else:
                msg = self.logging_header + self.logStrings.CLOSE_CONNECTION_ERROR \
                + str(self.binding_address) +":"  +str(self.port)
                self.logger.printStdoutMessage(msg, self.logStrings.DEBUG_STDOUT_HEADER)
                self.logger.loggingDebugMessage(msg)
                self.closed_exception_queue.put(sys.exc_info())
                return

        except (RuntimeError, ConfiguationError, Exception, AuthenticationException) as e:
            msg = self.logging_header + self.logStrings.CLOSE_CONNECTION_EXC \
            + str(e) + self.logStrings.ON_SOCKET + str(self.binding_address) +":"  +str(self.port)
            self.logger.printStdoutMessage(msg, self.logStrings.DEBUG_STDOUT_HEADER)
            self.logger.loggingDebugMessage(msg)
            self.closed_exception_queue.put(sys.exc_info())

        finally:
            try:
                if hasattr(self, "client"):
                    self.client.close()
            except NameError:
                pass

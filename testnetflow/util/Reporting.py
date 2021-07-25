import sys
import threading
from testnetflow.constants.LoggingConstant import LoggingConstant


class Reporting(threading.Thread):
    def __init__(self, dct, logger, exception_queue, tid, userargs):
        super(Reporting, self).__init__()
        self.dct = dct
        self.logger = logger
        self.exception_queue = exception_queue
        self.tid = tid
        self.userargs = userargs
        self.logStrings = LoggingConstant()
        self.logging_header = self.logStrings.INFO_STDOUT_HEADER + self.tid + self.logStrings.SEP + self.__class__.__name__ + self.logStrings.SEP


    def run(self):
        try:
            ipclient = self.dct.keys()[0]
            serverlist = self.dct.values()[0]
            for server in serverlist:
                # flow status = server[1]
                if server[1]:
                    flow_status = "enabled"
                else:
                    flow_status = "not enabled"

                msg = self.logging_header + self.logStrings.REPORTING_STATUS_MSG \
                      + str(ipclient) + " and " + str(server[0]) + " is " + flow_status
                print(msg)
                self.logger.loggingInfoMessage(msg)
            self.exception_queue.put("done")
        except Exception:
            self.exception_queue.put(sys.exc_info())

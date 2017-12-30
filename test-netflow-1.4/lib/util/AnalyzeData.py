import threading
import sys


class AnalyzeData(threading.Thread):
    def __init__(self, dct, logger, exception_queue, name, userargs):
        # threading.Thread.__init__(self)
        super(AnalyzeData, self).__init__()
        self.dct = dct
        self.logger = logger
        self.exception_queue = exception_queue
        self.tid = name
        self.userargs = userargs

    def run(self):
        try:
            ipclient = self.dct.keys()[0]
            serverlist = self.dct.values()[0]
            for server in serverlist:
                # status = server[1]
                if server[1]:
                    flow_status = "enabled"
                else:
                    flow_status = "not enabled"

                if self.userargs.stdout:
                    print ("DEBUG STDOUT: " + self.tid +
                           " The Network Flows between \"%s\" and \"%s\" are %s" %
                           (ipclient, server[0], flow_status))
                self.logger.info("The Network Flows between \"%s\" and \"%s\" are %s ",
                                 ipclient, server[0], flow_status)

            self.exception_queue.put("done")
        except Exception:
            self.exception_queue.put(sys.exc_info())

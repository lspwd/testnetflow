import threading


class NetBaseObject(threading.Thread):
    # server[mgmtip],server[username],server[password],server[socket]

    def __init__(self, dct, logger, exception_queue, tid, mutex, userargs):
        super(NetBaseObject, self).__init__()
        self.mgmtip = dct["mgmtip"]
        # print "self.mgmtipclient: " +self.mgmtipclient
        self.username = dct["username"]
        # print "self.username: " +self.username
        self.password = dct["password"]
        # print "self.password: " +str(self.password)
        self.socketlist  = dct["socket"]
        self.logger = logger
        self.tid = tid
        self.mutex = mutex
        self.exception_queue = exception_queue
        self.userargs = userargs
        self.python_min_version = "2.6"
        self.remote_path = "/tmp/"
        self.permission_bit = "x"

    def run(self):
        pass
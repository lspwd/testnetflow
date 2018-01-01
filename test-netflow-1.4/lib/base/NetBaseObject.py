import threading
from PythonNotFoundError import PythonNotFoundError

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

    def prepareTheGround(self, helper, script_local_path, script_name, script_remote_path):
        try:
            client = helper.sshConnect()
            python_she_bang = "#!" + helper.checkPythonPath(client)
            if helper.checkPythonVersion(self.python_min_version, client):
                if not helper.isUploaded():
                    if helper.upload(client, script_local_path, script_name, script_remote_path,):
                        helper.chmodOnScript(client, self.permission_bit, script_remote_path+script_name)
                        helper.sedTheSheBang(client, python_she_bang, script_remote_path+script_name)
                    else:
                        raise RuntimeError("Unable to upload script on the remote machine")
                return client
            else:
                raise PythonNotFoundError("Python version on the remote machine " + self.mgmtip
                                          + " is not supported, please install at least Python "
                                          + self.python_min_version)
        except Exception as e:
            raise RuntimeError("An exception has been caught: " + str(e))

    def run(self):
        pass
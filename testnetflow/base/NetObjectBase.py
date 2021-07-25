import socket
import threading
import time
from multiprocessing import Process, Queue
from testnetflow.constants.LoggingConstant import LoggingConstant
from testnetflow.exceptions.PythonNotFoundError import PythonNotFoundError
from testnetflow.exceptions.DnsError import DnsError
from paramiko import  AuthenticationException

class NetObjectBase(threading.Thread):

    def __init__(self, tid, mgmt_ip, logger, username):
        super(NetObjectBase, self).__init__()
        self.logger = logger
        self.tid = tid
        self.mgmt_ip = mgmt_ip
        self.python_min_version = "2.6"
        self.username = username
        self.remote_path = "/tmp/" + username + "/"
        self.permission_bit = "x"
        self.exception_list = []
        self.logStrings = LoggingConstant()
        self.logging_header = self.tid + self.logStrings.SEP + self.__class__.__name__ + self.logStrings.SEP
        self.debugging_header = self.logStrings.DEBUG_STDOUT_HEADER + self.logging_header

    def do_base_preparation(self, helper, script_local_path, script_name, script_remote_path):
        try:
            client = helper.ssh_connect()
        except AuthenticationException as e:
            print("do_base_preparation exception: " + str(e))
            raise e
        try:
            python_she_bang = "#!" + helper.check_python_path(client)
            if helper.check_python_version(self.python_min_version, client):
                if not helper.is_uploaded():
                    helper.create_remote_directory(client, script_remote_path, self.username)
                    if helper.upload(client, script_local_path, script_name, script_remote_path, ):
                        helper.do_chmod_on_script(client, self.permission_bit, script_remote_path + script_name)
                        helper.change_shebang(client, python_she_bang, script_remote_path + script_name)
                    else:
                        msg = self.logging_header + self.logStrings.EXC_HEADER \
                              + self.logStrings.UPLOAD_ERROR + self.logStrings.ON_IP_MSG + self.mgmt_ip
                        raise RuntimeError(msg)
                return client
            else:
                msg = self.logging_header + self.logStrings.EXC_HEADER \
                + self.logStrings.PYTHON_VER_UNSUPPORTED + self.python_min_version \
                      + self.logStrings.ON_IP_MSG + self.mgmt_ip
                raise PythonNotFoundError(msg)

        except (RuntimeError, Exception) as e:
               msg = self.logging_header + self.logStrings.EXC_HEADER + str(e)
               raise RuntimeError(msg)

    def dns_lookup(self, host, q):
        try:
            ret = socket.gethostbyname(host)
            q.put(ret)
        except (socket.gaierror, Exception):
            pass

    def resolveHostname(self, ip):
        p = ""
        try:
            q = Queue()
            p = Process(target=self.dns_lookup(ip, q))
            p.start()
            time.sleep(0.5)
            if q.empty():
                p.terminate()
                msg = self.logging_header + self.logStrings.EXC_HEADER \
                + self.logStrings.DNS_ERROR + ip
                raise DnsError(msg)
            else:
                ip = q.get(timeout=2)
                p.terminate()
                return ip
        except (RuntimeError, socket.gaierror) as e:
            msg = self.logging_header + self.logStrings.EXC_HEADER + str(e)
            raise DnsError(msg)
        finally:
            try:
                if hasattr(p, "terminate"):
                    p.terminate()
            except NameError:
                pass

    def internalNameResolution(self, ip):
        try:
            return self.resolveHostname(ip)
        except DnsError as e:
            raise (e)

    def run(self):
        pass
from CommandHelper import CommandHelper
from SudoHelper import SudoHelper
from SSHHelper import SSHHelper
from SudoNotFoundError import SudoNotFoundError


class SSHServerHelper(SSHHelper):
    def __init__(self, ip, username, password, mutex, userargs, tid, logger):
        super(SSHServerHelper, self).__init__(ip, username, password, mutex, userargs, tid, logger)

    # working on upload here

    def runSocketServer(self, ip, port, timeout, client, scriptname):

        chan = client.invoke_shell()
        chan.set_combine_stderr(True)
        chan.settimeout(20)
        custom_ps1 = "end1> "

        if int(port) <= 1024:

            if not self.checkSudo(chan):
                raise SudoNotFoundError("The username " + self.username
                                        + "is not able to do sudo on the remote machine")
            cmd = "sudo -k -b nohup " + scriptname + " " + ip + " " + port + " " + timeout + " >/dev/null " + "\n"
            # print("Sudo --> Executing on the remote machine: " + cmd)
            sudohelper = SudoHelper(custom_ps1, self.username, self.password, chan, self.logger, cmd)
            try:
                sudohelper.doSudo(cmd)
                if not self.testListenState(ip, port, client):
                    self.logger.error("runServerSocketScript(): unable to bring up the Socket Server "
                                      "( hint: check the SudoHelper.doSudo() ) ")
                    chan.close()
                    raise NameError("runServerSocketScript():  unable to bring up the Socket Server "
                                    "( hint: check the SudoHelper.doSudo()")

                if self.userargs.stdout:
                    print("DEBUG STDOUT: " + self.tid + " SocketServer has been started on \"%s:%s\" "
                          % (ip, port))
                self.logger.debug("%s SocketServer has been started on on \"%s:%s\" ", self.tid, ip, port)
            except Exception as e:
                self.logger.error("runServerSocketScript() " + str(e))
                raise RuntimeError("runServerSocketScript() " + str(e))
            finally:
                try:
                    if hasattr(chan, "close"):
                        chan.close()
                except NameError:
                    pass

        else:
            try:
                # Starting Server via nohup on the remote machine..
                cmd = "nohup " + scriptname + " " + ip + " " + port + " " + timeout + " >/dev/null 2>&1 &\n"
                # print("Executing on the remote machine: " + cmd)
                channelhelper = CommandHelper(custom_ps1, chan, self.logger, cmd)
                channelhelper.executeCommand()
                # Testing the LISTEN state of the socket
                if not self.testListenState(ip, port, client):
                    self.logger.error("Unable to bring up the Socket Server "
                                      "( hint: check the CommandHelper.executeCommand() ) ")
                    chan.close()
                    raise RuntimeError("Unable to bring up the Socket Server "
                                       "(hint: check the CommandHelper.executeCommand() ) ")

                if self.userargs.stdout:
                    print("DEBUG STDOUT: " + self.tid + " SocketServer has been started on \"%s:%s\" "
                          % (ip, port))
                self.logger.debug("%s SocketServer has been started on \"%s:%s\" ", self.tid, ip, port)

            except Exception as e:
                self.logger.error("runServerSocketScript() " + str(e))
                raise RuntimeError("runServerSocketScript() " + str(e))

            finally:
                try:
                    if hasattr(chan, "close"):
                        chan.close()
                except NameError:
                    pass

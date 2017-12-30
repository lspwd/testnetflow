from CommandHelper import CommandHelper
from base import SSHHelper


class SSHClientHelper(SSHHelper):
    def __init__(self, ip, username, password, mutex, userargs, tid, logger):
        super(SSHClientHelper, self).__init__(ip, username, password, mutex, userargs, tid, logger)

    # working on upload here

    def runSocketClient(self, ip, port, timeout, client, scriptname):

        chan = client.invoke_shell()
        chan.set_combine_stderr(True)
        chan.settimeout(20)

        try:
            # Starting Client script on the remote machine..
            cmd = scriptname + " " + ip + " " + port + " " + timeout
            custom_ps1 = "end1> "
            channelhelper = CommandHelper(custom_ps1, chan, self.logger, cmd)
            channelhelper.executeCommand()
            # Testing the LISTEN state of the socket
            if self.testListenState(ip, port, client):
                self.logger.error("runServerSocketScript() Exeception: unable to bring up the Socket Server "
                                  "( hint: check the ChannelHelper.mainLogic() ) ")
                chan.close()
                raise NameError("runServerSocketScript() Exeception: unable to bring up the Socket Server"
                                "( hint: check the ChannelHelper.mainLogic() ) ")

            if self.userargs.stdout:
                print("DEBUG STDOUT: " + self.tid + " Socket on \"%s:%s\" has been deployed via netcat"
                      % (ip, port))
            self.logger.debug("%s SocketServer has been started on on \"%s:%s\" ", self.tid, ip, port)

        except Exception as e:
            self.logger.error("runServerSocketScript() Exeception : %s" + str(e))
            raise NameError("runServerSocketScript() Exeception: " + str(e))

        finally:
            try:
                if hasattr(chan, "close"):
                    chan.close()
            except NameError:
                pass

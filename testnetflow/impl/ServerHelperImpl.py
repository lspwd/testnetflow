from UnprivilegedCommandHandlerImpl import UnprivilegedCommandHandlerImpl
from PrivilegedCommandHandlerImpl import PrivilegedCommandHandlerImpl
from testnetflow.base.NetHelperBase import NetHelperBase
from testnetflow.exceptions.SudoError import SudoError
import os


class ServerHelperImpl(NetHelperBase):

    def __init__(self, ip, username, password, mutex, userargs, tid, logger):
        super(ServerHelperImpl, self).__init__(ip, username, password, mutex, userargs, tid, logger)
        self.logging_header = self.tid + self.logStrings.SEP + self.__class__.__name__ + self.logStrings.SEP

    def assess_socket_status(self, ip, port, client, chan):
        if not self.test_listen_state(ip, port, client):
            msg = self.logging_header + self.logStrings.SUDO_SOCKET_ERROR
            self.logger.printStdoutMessage(msg, self.logStrings.DEBUG_STDOUT_HEADER)
            self.logger.loggingDebugMessage(msg)
            chan.close()
            raise NameError(msg)
        msg = self.logging_header + self.logStrings.SOCKET_STARTED + str(ip) + ":" +str(port)
        self.logger.printStdoutMessage(msg, self.logStrings.DEBUG_STDOUT_HEADER)
        self.logger.loggingDebugMessage(msg)

    def try_close(self, obj):
        try:
            if hasattr(obj, "close"):
                obj.close()
        except NameError:
            pass

    def privileged_socket_start(self, chan, ip, port, custom_ps1, client, cmd):
        sudohelper = PrivilegedCommandHandlerImpl(custom_ps1, self.username, self.password, chan, self.logger, cmd, self.tid)
        test_command="sudo -k -p \"password: \" echo test\n"
        actual_cmd = "sudo -k -b -p \"password: \" " + cmd
        if not sudohelper.check_sudo_password(test_command):
            # print("Sudo without a password")
            actual_cmd = actual_cmd.replace("\n", "") + " & \n"
            self.unprivileged_socket_start(chan, ip, port, custom_ps1, client, actual_cmd)
            self.assess_socket_status(ip, port, client, chan)
        else:
            try:
                if not sudohelper.do_sudo_command(actual_cmd):
                    raise SudoError(self.logging_header + self.logStrings.EXC_HEADER + self.logStrings.SUDO_ERROR)
                self.assess_socket_status(ip, port, client, chan)
            except Exception as e:
                msg = self.logging_header + self.logStrings.EXC_HEADER + str(e)
                raise SudoError(msg)
            finally:
                self.try_close(chan)

    def unprivileged_socket_start(self, chan, ip, port, custom_ps1, client, cmd):
        channelhelper = UnprivilegedCommandHandlerImpl(custom_ps1, chan, self.logger, cmd, self.tid)
        #print("unprivileged_socket_start: " + str(cmd))
        try:
            if not channelhelper.executeCommand(cmd):
                raise RuntimeError("Unable to execute remote command: " +cmd)
            self.assess_socket_status(ip, port, client, chan)
        except Exception as e:
            msg = self.logging_header + self.logStrings.EXC_HEADER + str(e)
            raise RuntimeError(msg)
        finally:
            self.try_close(chan)

    def run_socket_server(self, ip, port, timeout, client, scriptname):
        chan = client.invoke_shell()
        chan.set_combine_stderr(True)
        chan.settimeout(20)
        custom_ps1 = "end1> "
        logdir = os.path.dirname(scriptname)
        log = " >>" +logdir + "/socketServer_" + str(port) + ".log 2>&1 \n"
        log_bg = " >>" +logdir + "/socketServer_" + str(port) + ".log & \n"

        try:
            if int(port) <= 1024 and self.username != "root":
                cmd = "nohup " + scriptname + " " + ip + " " + str(port) + " " + timeout + log
                self.privileged_socket_start(chan, ip, port, custom_ps1, client, cmd)
            else:
                cmd = "nohup " + scriptname + " " + ip + " " + str(port) + " " + timeout + log_bg
                self.unprivileged_socket_start(chan, ip, port, custom_ps1, client, cmd)
        except (RuntimeError, Exception) as e:
            raise RuntimeError(e)
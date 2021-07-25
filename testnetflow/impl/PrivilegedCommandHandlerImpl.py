from testnetflow.base.TerminalHandlerBase import TerminalHandlerBase
from testnetflow.exceptions.SudoError import SudoError
import Queue


class PrivilegedCommandHandlerImpl(TerminalHandlerBase):

    def __init__(self, ps1, username, password, channel, logger, cmd, tid):
        super(PrivilegedCommandHandlerImpl, self).__init__(ps1, channel, logger, cmd, tid)
        self.userPrompt = username + ': '
        self.username = username
        self.password = password
        self.logging_header = self.tid + self.logStrings.SEP + self.__class__.__name__ + self.logStrings.SEP

    def check_sudo_password(self, cmd):
        imq = Queue.Queue()
        password_prompt="password: "
        full_cmd = "PS1=\"" + self.ps1 + "\"; export PS1; " + cmd
        self.send_ssh_all_events(full_cmd, self.chan)
        response = self.dual_pattern_terminal_parser(self.ps1, password_prompt, self.chan, imq)
        imq_res = imq.get()
        # print ("return from dual_pattern_t.parser " + str(response))
        if imq_res != "done": raise RuntimeError(str(imq_res))
        if response.endswith(self.ps1): return False
        elif response.lower().endswith(password_prompt):
            self.send_ssh_all_events(self.password+"\n", self.chan)
            response = self.single_pattern_terminal_parser(self.ps1, self.chan, imq)
            imq_res = imq.get()
            if imq_res != "done": raise RuntimeError(str(imq_res))
            if response.endswith(self.ps1):return True
        else:
            msg = self.logging_header + self.logStrings.EXC_HEADER + self.logStrings.SUDO_USER_ERROR
            raise SudoError(msg)

    def do_sudo_command(self, cmd):
        imq = Queue.Queue()
        password_prompt="password: "
        full_cmd = "PS1=\"" + self.ps1 + "\"; export PS1; " + cmd
        self.send_ssh_all_events(full_cmd, self.chan)
        response = self.dual_pattern_terminal_parser(self.ps1, password_prompt, self.chan, imq)
        imq_res = imq.get()
        # print ("return from dual_pattern_t.parser " + str(response))
        if imq_res != "done": raise RuntimeError(str(imq_res))
        if response.endswith(self.ps1): return True
        elif response.lower().endswith(password_prompt):
            self.send_ssh_all_events(self.password+"\n", self.chan)
            response = self.single_pattern_terminal_parser(self.ps1, self.chan, imq)
            imq_res = imq.get()
            if imq_res != "done": raise RuntimeError(str(imq_res))
            return response.endswith(self.ps1)
        else:
            msg = self.logging_header + self.logStrings.EXC_HEADER + self.logStrings.SUDO_USER_ERROR
            raise SudoError(msg)
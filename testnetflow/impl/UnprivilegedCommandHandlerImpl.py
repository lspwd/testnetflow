from testnetflow.base.TerminalHandlerBase import TerminalHandlerBase
import Queue

class UnprivilegedCommandHandlerImpl(TerminalHandlerBase):

    def __init__(self, ps1, channel, logger, cmd, tid):
        super(UnprivilegedCommandHandlerImpl, self).__init__(ps1, channel, logger, cmd, tid)
        self.logging_header = self.tid + self.logStrings.SEP + self.__class__.__name__ + self.logStrings.SEP

    def executeCommand(self,cmd):
        imq = Queue.Queue()
        # Set custom PS1 on the remote machine"
        # print("command is: " + cmd)
        full_cmd = "PS1=\"" + self.ps1 + "\"; export PS1; " + cmd
        self.send_ssh_all_events(full_cmd, self.chan)
        self.send_ssh_all_events("\n", self.chan)
        response = self.single_pattern_terminal_parser(self.ps1, self.chan, imq)
        imq_res = imq.get()
        # print ("return from single_pattern_t.parser " + str(response))
        if imq_res != "done": raise RuntimeError(str(imq_res))
        return response.endswith(self.ps1)
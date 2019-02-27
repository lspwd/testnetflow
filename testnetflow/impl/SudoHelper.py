from ChannelHelper import ChannelHelper


class SudoHelper(ChannelHelper):

    def __init__(self, ps1, username, password, channel, logger, cmd):
        super(SudoHelper, self).__init__(ps1, channel, logger, cmd)
        self.userPrompt = username + ': '
        self.username = username
        self.password = password

    def doSudo(self, cmd):
        sendpassword = self.password + "\n"
        # buf = ""
        try:
            # Set PS1
            self.send_ssh_events("PS1=\"" + self.ps1 + "\"; export PS1\n", self.chan)
            # Parse Prompt
            self.scan_buffer_end(self.ps1, self.chan, False)
            # Send Sudo
            self.send_ssh_events(cmd, self.chan)
            # Parse Sudo Password request
            # buf = ""
            self.scan_buffer_end(self.userPrompt, self.chan, False)
            # Send Sudo Password
            self.send_ssh_events(sendpassword, self.chan)
            # Send another "\n"
            self.send_ssh_events("\n", self.chan)
            # Parse prompt again, waiting for nc completion
            # buf = ""
            ret = self.scan_buffer_end(self.ps1, self.chan, True)
            return ret

        except Exception, e:
            raise RuntimeError("doSudo(): " + str(e))

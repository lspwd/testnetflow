import ChannelHelper


class SudoHelper(ChannelHelper):
    def __init__(self, ps1, username, password, channel, logger, cmd):
        super(SudoHelper, self).__init__(ps1, channel, logger, cmd)
        self.userPrompt = username + ': '
        self.username = username
        self.password = password + "\n"

    def doSudo(self):

        try:
            # Send First "command + \n"
            self.__send_ssh_events("PS1=\"" + self.ps1 + "\"; export PS1\n", self.chan)

            # Parse Prompt
            self.__scan_buffer_end(self.ps1, self.chan, False)

            # Send Sudo Command
            self.__send_ssh_events(self.cmd, self.chan)

            # Wait for Sudo Password request
            self.__scan_buffer_end(self.userPrompt, self.chan, False)

            # Send Sudo Password
            self.__send_ssh_events(self.password, self.chan)

            # Parse the result of the command --- could be simply ignored by the caller
            response = self.__scan_buffer_end(self.ps1, self.chan, True)
            return response

        except Exception as e:
            raise NameError("doSudo() exception: ", e)

import ChannelHelper


class CommandHelper(ChannelHelper):

    def __init__(self, ps1, channel, logger, cmd):
        super(CommandHelper, self).__init__(ps1, channel, logger, cmd)

    def executeCommand(self):
        try:
            # Set custom PS1 on the remote machine"
            self.__send_ssh_events(self.ps1, self.chan)

            # Wait for prompt
            self.__scan_buffer_end(self.ps1, self.chan, False)

            # Send the actual unix command
            self.__send_ssh_events(self.cmd, self.chan)

            # Receive the response of the command
            buffer = self.__scan_buffer_end(self.ps1, self.chan, True)
            return buffer

        except Exception as e:
            raise NameError("Class ChannelHelper -- mainLogic method() exception: " +str(e))
from testnetflow.base.ChannelHelper import ChannelHelper

class CommandHelper(ChannelHelper):

    def __init__(self, ps1, channel, logger, cmd):
        super(CommandHelper, self).__init__(ps1, channel, logger, cmd)

    def executeCommand(self):
        try:
            # Set custom PS1 on the remote machine"
            self.send_ssh_events("PS1=\"" + self.ps1 + "\"; export PS1\n", self.chan)

            # Wait for prompt
            self.scan_buffer_end(self.ps1, self.chan, False)

            # Send the actual unix command
            self.send_ssh_events(self.cmd, self.chan)

            # Receive the response of the command
            # print("starting receiving buffer...")
            buffer = self.scan_buffer_end(self.ps1, self.chan, True)
            return buffer

        except (RuntimeError, Exception) as e:
            # print("In the commandhelper class: " +str(e))
            raise RuntimeError(e)
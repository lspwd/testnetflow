import time


class ChannelHelper:
    def __init__(self, chan, logger, cmd):
        self.pattern = '~]$ '
        self.chan = chan
        self.logger = logger
        self.cmd = cmd

    def mainLogic(self):
        try:
            # Send First "\n"
            self.__send_ssh_events("\n", self.chan)
            # Parse Prompt
            self.__scan_buffer_end(self.pattern, self.chan)
            # Send Command
            self.__send_ssh_events(self.cmd, self.chan)
            # Send another "\n"
            self.__send_ssh_events("\n", self.chan)
            # Parse prompt again, waiting for nc completion
            self.__scan_buffer_end(self.pattern, self.chan)
            return

        except Exception as e:
            raise NameError("Class ChannelHelper -- mainLogic method() exception: " +str(e))

    def __send_ssh_events(self, command, channel):
        try:
            channel.send(command)
            time.sleep(5)
            return
        except  Exception as e:
            raise NameError("__send_ssh_events method got an exception!: %s", e)

    def __scan_buffer_end(self, testpattern, channel):

        count = 1
        buff = ""

        while not buff.endswith(testpattern):
            if count < 7:
                try:
                    buff += channel.recv(4096)
                    # DEBUG View prompt to STDOUT
                    # print(buff)
                    count += 1
                    # print("Count: " +str(count))
                except  Exception as e:
                    self.logger.error('scan_buffer_end(): Timeout event while scanning buffer: %s', e)
                    raise NameError("scan_buffer_end fuction got an exception!")
            else:
                self.logger.error('scan_buffer_end(): Buffer scanning error: Can not find pattern %s', testpattern)
                raise NameError("scan_buffer_end fuction got an exception!")

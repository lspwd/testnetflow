import time


class ChannelHelper:

    def __init__(self, ps1, channel, logger, cmd):

        self.ps1 = ps1
        self.chan = channel
        self.cmd = cmd + "\n"
        self.logger = logger

    def __send_ssh_events(self, command, channel):
        try:
            channel.send(command)
            time.sleep(3)
            return
        except  Exception as e:
            raise NameError("Ssh_ssh_events fuction got an exception!: %s", str(e))

    def __scan_buffer_end(self, testpattern, channel, returnvalue):
        count = 1
        buff = None
        while not buff.endswith(testpattern):

            # 7 is the loop limit, after which the loop will exit.
            if count < 7:
                try:
                    buff = channel.recv(4096)
                    # DEBUG View prompt to STDOUT
                    # print("in the __scan_buffer_end(): " + buff)
                    count += 1
                    # print("in the __scan_buffer_end(): Count: " +str(count))
                except  Exception as e:
                    self.logger.error('scan_buffer_end(): Timeout event while scanning buffer: %s', str(e))
                    raise NameError("scan_buffer_end fuction got an exception!")
            else:
                self.logger.error('scan_buffer_end(): Buffer scanning error: Can not find pattern %s', testpattern)
                raise NameError("scan_buffer_end fuction got an exception!")
        if returnvalue:
            return buff

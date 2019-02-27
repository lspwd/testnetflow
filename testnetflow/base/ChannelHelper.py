import time


class ChannelHelper(object):

    def __init__(self, ps1, channel, logger, cmd):
        self.ps1 = ps1
        self.chan = channel
        self.cmd = cmd + "\n"
        self.logger = logger

    def send_ssh_events(self, command, channel):
        try:
            channel.send(command)
            time.sleep(3)
            return
        except  Exception as e:
            raise RuntimeError("Ssh_ssh_events fuction got an exception!: %s", str(e))

    def scan_buffer_end(self, testpattern, channel, returnvalue):
        count = 1
        buff = ""
        while not buff.endswith(testpattern):
            # 7 is the loop limit, after which the loop will exit.
            if count < 7:
                try:
                    buff = channel.recv(4096)
                    # DEBUG View prompt to STDOUT
                    # print("in the __scan_buffer_end(): " + buff)
                    count += 1
                    # print("in the __scan_buffer_end(): Count: " +str(count))
                except  Exception as ex1:
                    print("scan_buffer_end(): RunTimeError " + str(ex1))
                    self.logger.error("scan_buffer_end(): Timeout event while scanning buffer: " + str(ex1))
                    raise RuntimeError("scan_buffer_end() got an exception " + str(ex1))
            else:
                self.logger.error("scan_buffer_end(): Buffer scanning error: Can not find pattern " + testpattern)
                raise RuntimeError("scan_buffer_end(): Timeout for the method reached")
        if returnvalue:
            return buff

import time


class SudoHelper:

    def __init__(self, custompattern, username, password, channel, logger, cmd):
        self.pattern1 = 'New password: '
        self.pattern2 = 'Retype new password: '
        self.pattern3 = username + ': '
        self.pattern4 = custompattern
        self.pattern5 = '~]$ '
        self.username = username
        self.password = password + "\n"
        self.chan = channel
        self.logger = logger
        self.cmd = cmd

    def doSudo(self):

        try:
            # Send First "\n"
            self.__send_ssh_events("\n", self.chan)
            # Parse Prompt
            self.__scan_buffer_end(self.pattern5, self.chan)
            # Send Sudo
            self.__send_ssh_events(self.cmd, self.chan)
            # Parse Sudo Password request
            self.__scan_buffer_end(self.pattern3, self.chan)
            # Send Sudo Password
            self.__send_ssh_events(self.password, self.chan)
            # Send another "\n"
            self.__send_ssh_events("\n", self.chan)
            # Parse prompt again, waiting for nc completion
            self.__scan_buffer_end(self.pattern5, self.chan)
            return

        except Exception, e:
            raise NameError("doSudo() exception: ", e)

    def __send_ssh_events(self, command, channel):
        try:
            channel.send(command)
            time.sleep(3)
            return
        except  Exception, e:
            raise NameError("Ssh_ssh_events fuction got an exception!: %s", e)

    def __scan_buffer_end(self, testpattern, channel):
        count = 1
        buff = ""
        while not buff.endswith(testpattern):
            if count < 7:
                try:
                    buff = channel.recv(4096)
                    # DEBUG View prompt to STDOUT
                    # print(buff)
                    count += 1
                    # print("Count: " +str(count))
                except  Exception, e:
                    self.logger.error('scan_buffer_end(): Timeout event while scanning buffer: %s',e)
                    raise NameError("scan_buffer_end fuction got an exception!")
            else:
                self.logger.error('scan_buffer_end(): Buffer scanning error: Can not find pattern %s', testpattern)
                raise NameError("scan_buffer_end fuction got an exception!")

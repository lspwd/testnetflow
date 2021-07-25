from __future__ import print_function
import time
from testnetflow.constants.LoggingConstant import LoggingConstant


class TerminalHandlerBase(object):

    def __init__(self, ps1, channel, logger, cmd, tid):
        self.tid = tid
        self.ps1 = ps1
        self.chan = channel
        self.cmd = cmd + "\n"
        self.logger = logger
        self.logStrings = LoggingConstant()
        self.logging_header = self.tid + self.logStrings.SEP + self.__class__.__name__ + self.logStrings.SEP
        self.debugging_header = self.logStrings.DEBUG_STDOUT_HEADER + self.logging_header

    def send_ssh_events(self, command, channel):
        try:
            channel.send(command)
            time.sleep(3)
        except Exception as e:
            msg = self.logging_header + self.logStrings.EXC_HEADER \
                  + self.logStrings.SEP + self.logStrings.SEND_SSH_METHOD + str(e)

            raise RuntimeError(msg)

    def send_events(self, command, channel):
        bytes = channel.send(command)
        time.sleep(3)
        return bytes

    def send_ssh_all_events(self, command, channel):
        channel.sendall(command)
        time.sleep(3)

    def scan_buffer_end(self, testpattern, channel, returnvalue):
        count = 1
        buff = ""
        while not buff.endswith(testpattern):
            # 7 is the loop limit, after which the loop will exit.
            if count < 7:
                try:
                    buff = channel.recv(4096)
                    # DEBUG View prompt to STDOUT
                    # print(str(buff))
                    count += 1
                    # print("in the __scan_buffer_end(): Count: " +str(count))
                except Exception as e:
                    # print(self.debugging_header + "Exception is: " + str(e))
                    msg = self.logging_header + self.logStrings.EXC_HEADER \
                          + self.logStrings.SEP + self.logStrings.SCAND_BUFFER_METHOD \
                          + self.logStrings.SEP + self.logStrings.TIMEOUT_MSG + str(e)
                    self.logger.printStdoutMessage(msg, self.logStrings.ERROR_STDOUT_HEADER)
                    self.logger.loggingErrorMessage(msg)
                    raise RuntimeError(msg)
            else:
                msg = self.logging_header + self.logStrings.EXC_HEADER \
                      + self.logStrings.SEP + self.logStrings.SCAND_BUFFER_METHOD \
                      + self.logStrings.SEP + self.logStrings.PATTERN_ERROR + " " + testpattern
                self.logger.printStdoutMessage(msg, self.logStrings.ERROR_STDOUT_HEADER)
                self.logger.loggingErrorMessage(msg)
                raise RuntimeError(msg)
        if returnvalue:
            return buff

    def dual_pattern_terminal_parser(self, testpattern1, testpattern2, channel, queue):
        count = 1
        flat_buffer = ""
        channel.set_combine_stderr(True)
        while not flat_buffer.endswith(testpattern1) and not flat_buffer.endswith(testpattern2):
            # 10 is the loop limit, after which the loop will exit.
            if count < 10:
                try:
                    if channel.recv_ready():
                        buff = channel.recv(4096)
                        # print("RAW BUFFER: " + buff)
                        flat_buffer = buff.replace("\r", " ").replace("\n", " ")
                        # print("FLAT: " +str(flat_buffer))
                        # print("FLAT endswith pattern: " +  str(flat_buffer.endswith(testpattern2)))
                        # print("Count " + str(count))
                        # print("in the __scan_buffer_end(): Count: " +str(count))
                        count += 1
                    else:
                        count += 1
                        continue
                except Exception as e:
                    # print(self.debugging_header + "Exception is: " + str(e))
                    msg = self.logging_header + self.logStrings.EXC_HEADER \
                          + self.logStrings.SEP + self.logStrings.SCAND_BUFFER_METHOD \
                          + self.logStrings.SEP + self.logStrings.TIMEOUT_MSG + str(e)
                    self.logger.printStdoutMessage(msg, self.logStrings.ERROR_STDOUT_HEADER)
                    self.logger.loggingErrorMessage(msg)
                    queue.put(msg)
                    raise RuntimeError(msg)
            else:
                msg = self.logging_header + self.logStrings.EXC_HEADER \
                      + self.logStrings.SEP + self.logStrings.SCAND_BUFFER_METHOD \
                      + self.logStrings.SEP + self.logStrings.PATTERN_ERROR + " " + testpattern1 + " " + testpattern2
                self.logger.printStdoutMessage(msg, self.logStrings.ERROR_STDOUT_HEADER)
                self.logger.loggingErrorMessage(msg)
                queue.put(msg)
                raise RuntimeError(msg)
        queue.put("done")
        return flat_buffer

    def single_pattern_terminal_parser(self, testpattern, channel, queue, bytes=4096):
        count = 1
        buff = ""
        flat_buffer = ""
        channel.set_combine_stderr(True)
        while not flat_buffer.endswith(testpattern):
            # 10 is the loop limit, after which the loop will exit.
            if count < 10:
                try:
                    if channel.recv_ready():
                        buff = channel.recv(bytes)
                        #print("RAW BUFFER: " + str(buff))
                        flat_buffer = buff.replace("\r","").replace("\n", " ")
                        #print("FLAT: " + str(flat_buffer))
                        #print("FLAT endswith pattern: " + str(flat_buffer.endswith(testpattern)))
                        #print("Count " + str(count))
                        count += 1
                    else:
                        #print("channel not ready....")
                        flat_buffer = ""
                        count += 1
                        continue
                except Exception as e:
                    #print(self.debugging_header + "Exception is: " + str(e))
                    msg = self.logging_header + self.logStrings.EXC_HEADER \
                          + self.logStrings.SEP + self.logStrings.SCAND_BUFFER_METHOD \
                          + self.logStrings.SEP + self.logStrings.TIMEOUT_MSG + str(e)
                    self.logger.printStdoutMessage(msg, self.logStrings.ERROR_STDOUT_HEADER)
                    self.logger.loggingErrorMessage(msg)
                    queue.put(msg)
                    raise RuntimeError(msg)
            else:
                msg = self.logging_header + self.logStrings.EXC_HEADER \
                      + self.logStrings.SEP + self.logStrings.SCAND_BUFFER_METHOD \
                      + self.logStrings.SEP + self.logStrings.PATTERN_ERROR + " " + testpattern
                self.logger.printStdoutMessage(msg, self.logStrings.ERROR_STDOUT_HEADER)
                self.logger.loggingErrorMessage(msg)
                queue.put(msg)
                raise RuntimeError(msg)
        queue.put("done")
        return flat_buffer
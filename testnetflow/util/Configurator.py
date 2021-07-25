import sys

import yaml
from yaml import YAMLError
from testnetflow.constants.LoggingConstant import LoggingConstant


class Configurator:
    def __init__(self, configfile, logger):
        self.configfile = configfile
        self.logger = logger
        self.configlist = []
        self.logStrings = LoggingConstant()
        self.logging_header = self.logStrings.MAIN_THREAD + " " + self.__class__.__name__ + self.logStrings.SEP

    def get_config(self):
        try:
            with open(self.configfile) as cfile:
                self.configlist = yaml.load(cfile)
                return self.configlist
        except (YAMLError, Exception) as err:
            msg = self.logging_header + self.logStrings.ERROR_CONFIG
            self.logger.loggingErrorMessage(msg)
            self.logger.stdoutMessage(msg, self.logStrings.ERROR_STDOUT_HEADER)
            sys.exit(1)
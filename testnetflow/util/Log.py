#!/usr/bin/python

from __future__ import print_function

import logging
import os
from logging import handlers
from testnetflow.constants.LoggingConstant import LoggingConstant

class Log:
    def __init__(self, logname, level, category):
        self.logfile = logname
        self.level = level
        self.category = category
        self.stdout = False
        self.stringConstant = LoggingConstant()
        self.logger = None

    def rotation_needed(self):
        return os.path.isfile(self.logfile)

    def set_log_level(self, level):
        self.level = level

    def get_log_level(self):
        return self.level

    def set_stdout(self,boolean_value):
        self.stdout = boolean_value

    def get_stdout(self):
        return self.stdout

    def set_logger(self,logger):
        self.logger = logger

    def create_log(self):
        logger = logging.getLogger(self.category)
        formatter = logging.Formatter('%(levelname)s:  %(asctime)s - %(message)s')
        handler = logging.handlers.RotatingFileHandler(self.logfile, backupCount=365)
        handler.setFormatter(formatter)
        logger.setLevel(self.level)
        logger.addHandler(handler)
        logger.handlers[0].doRollover() if self.rotation_needed() else None
        self.set_logger(logger)
        return self

    def loggingDebugMessage(self, message):
        if self.level == "DEBUG":
            self.logger.debug(message) if self.level == "DEBUG" else None

    def loggingErrorMessage(self, message):
        self.logger.error(message)

    def loggingInfoMessage(self, message):
        self.logger.info(message)

    def printStdoutMessage(self, message, header):
        if self.get_stdout() == True:
            print(header + message)
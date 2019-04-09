#!/usr/bin/python

import logging
import os
from logging import handlers


class Log:
    def __init__(self, logname, level, customclass):
        self.logname = logname
        self.needRoll = os.path.isfile(logname)
        self.logfile = logname
        self.level = level
        self.customclass = customclass

    def create_log(self):

        if self.customclass:
            logger = logging.getLogger(self.customclass)
        else:
            logger = logging.getLogger('Logger')
        formatter = logging.Formatter('%(levelname)s:  %(asctime)s - %(message)s')
        handler = logging.handlers.RotatingFileHandler(self.logfile, backupCount=365)
        handler.setFormatter(formatter)
        if self.level == "DEBUG":
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        self.__rollLog(logger)
        return logger

    def __rollLog(self, logger):
        if self.needRoll:
            logger.handlers[0].doRollover()

    def setLogLevel(self, logger, level):
        logger.setLevel(level)

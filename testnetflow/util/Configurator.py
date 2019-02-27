import sys

import yaml
from yaml import YAMLError


class Configurator:
    def __init__(self, configfile, logger):
        self.configfile = configfile
        self.logger = logger
        self.configlist = []

    def get_config(self):
        try:
            with open(self.configfile) as cfile:
                self.configlist = yaml.load(cfile)
                return self.configlist
        except (YAMLError,Exception) as err:
            self.logger.error('Error in parsing configuration file %s, %s', self.configfile, err)
            sys.exit(1)

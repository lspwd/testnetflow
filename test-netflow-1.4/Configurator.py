import sys
import ConfigParser


class Configurator:
    def __init__(self, configfile, logger):
        self.configfile = configfile
        self.logger = logger

    def get_config(self):
        try:
            with open(self.configfile) as cfile:
                configlist = []
                config = ConfigParser.SafeConfigParser()
                config.readfp(cfile)
                for section in config.sections():
                    configlist.append(dict(config.items(section)))
                return configlist
        except ConfigParser.ParsingError as err:
            self.logger.error('Error in parsing configuration file %s, %s', self.configfile, err)
            sys.exit(1)

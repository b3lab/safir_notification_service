import ConfigParser
import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, '../conf/safir_alarm_service.conf')


class ConfigOpts(object):
    def __init__(self, filename=CONFIG_PATH):
        self.filename = filename
        self.config_parser = ConfigParser.RawConfigParser()
        self.config_parser.read(self.filename)
        self._opts = {}

    def get_opts_of_section(self, section):
        self._opts = dict(self.config_parser.items(section))
        return self._opts

    def get_opt(self, section, optname):
        return self.config_parser.get(section, optname)

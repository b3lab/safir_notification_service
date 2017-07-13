# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import ConfigParser
import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, '../conf/safir_notification_service.conf')


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

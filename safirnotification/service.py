# -*- coding: utf-8 -*-
# Copyright 2017 TUBITAK B3LAB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import socket
import sys

from oslo_config import cfg
import oslo_i18n
from oslo_log import log

from safirnotification import version


service_opts = [
    cfg.StrOpt('host',
               default=socket.getfqdn(),
               help='Name of this node. This can be an opaque identifier. '
               'It is not necessarily a hostname, FQDN, or IP address. '
               'However, the node name must be valid within an AMQP key, '
               'and if using ZeroMQ, a valid hostname, FQDN, or IP address.')
]

cfg.CONF.register_opts(service_opts)


def prepare_service(argv=None, config_files=None):
    oslo_i18n.enable_lazy()
    log.register_options(cfg.CONF)
    log.set_defaults()

    if argv is None:
        argv = sys.argv
    cfg.CONF(argv[1:], project='safirnotification', validate_default_values=True,
             version=version.version_info.version_string(),
             default_config_files=config_files)

    log.setup(cfg.CONF, 'safirnotification')

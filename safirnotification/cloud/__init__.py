# -*- coding: utf-8 -*-
# Copyright 2017 TUBITAK B3LAB
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
# under the License

from oslo_config import cfg

# Cloud configuration options
cloud_opts = [
    cfg.StrOpt('cloud_name',
               default='cloud-admin',
               help="Cloud config name"),
    cfg.StrOpt('identity_api_version',
               default='3',
               help="Keystone identity API version"),
    cfg.StrOpt('horizon_url',
               default='http://127.0.0.1/horizon/',
               help="OpenStack Dashboard URL to be send with "
                    "notification mail"),
]

CONF = cfg.CONF
CONF.register_opts(cloud_opts, 'cloud')

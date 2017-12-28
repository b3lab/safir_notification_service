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
# under the License.

import logging
from openstack import connection
from aodhclient.v2 import client as aodh_client

from os_client_config import config as cloud_config

LOG = logging.getLogger(__name__)


class OpenstackManager(object):
    """ OpenStack cloud operation manager
    """

    def __init__(self, config_name):
        # Cloud config parameters
        # clouds.yaml file should either be in the
        # current directory or
        # ~/.config/openstack directory or
        # /etc/openstack directory.
        cc = cloud_config.OpenStackConfig()
        cloud = cc.get_one_cloud(config_name)

        # Create a context for a connection to the cloud provider
        self.conn = connection.from_config(cloud_config=cloud)

        # define identity api version
        identity_api_version = cloud.config['identity_api_version']

        if identity_api_version != '3':
            LOG.error('This version of Safir Cloud Migratory '
                      'only supports Identity version 3.')

        auth_param = cloud.config['auth']
        self.project_name = auth_param['project_name']

        # We still need to use aodhclient until alarming APIs
        # are added to openstackclient
        self.aodh_conn = aodh_client.Client(
            session=cloud.get_session_client('alarming'))

    def get_compute_server(self, instance_id):
        try:
            server = self.conn.compute.find_server(instance_id)
            if server is not None:
                return server
        except ka_exceptions.NotFound:
            return None
        return None

    def get_aodh_alarm(self, alarm_id):
        return self.aodh_conn.alarm.get(alarm_id)

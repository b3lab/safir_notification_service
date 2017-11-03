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

from keystoneauth1 import exceptions as ka_exceptions
from aodhclient.v2 import client as aodh_client
from openstack import connection
from safirnotification.utils import log
from os_client_config import config as cloud_config

LOG = log.get_logger()


class Opts:
    def __init__(self, cloud_name, debug=False):
        self.cloud = cloud_name
        self.debug = debug
        self.identity_api_version = '3'


class OpenstackConnector:
    def __init__(self, config_name):
        opts = Opts(cloud_name=config_name)

        cc = cloud_config.OpenStackConfig()
        LOG.debug("defaults: %s", cc.defaults)

        # clouds.yaml file should either be in the
        # current directory or
        # ~/.config/openstack directory or
        # /etc/openstack directory.
        cloud = cc.get_one_cloud(opts.cloud)
        LOG.debug("cloud cfg: %s", cloud.config)

        # Create a context for a connection to the cloud provider
        self.conn = connection.from_config(cloud_config=cloud,
                                           options=opts)

        identity_api_version = cloud.config['identity_api_version']
        if identity_api_version != '3':
            LOG.error('Only Identity version 3 is supported.')

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

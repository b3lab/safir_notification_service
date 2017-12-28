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
from openstack import exceptions as o_exceptions
from keystoneclient.v3 import client as keystone_client
from neutronclient.v2_0 import client as neutron_client

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

        # We still need to use neutronclient until openstackclient
        # is able to add interface router, and keystoneclient
        # until openstackclient is able to grant roles to users
        self.neutron_conn = neutron_client.Client(
            session=cloud.get_session_client('network'))
        self.keystone_conn = keystone_client.Client(
            session=cloud.get_session_client('identity'))

    def get_networks(self):
        try:
            project = self.conn.identity.find_project(self.project_name)

            nets = self.conn.network.networks(project_id=project.id,
                                              is_admin_state_up=True)
        except o_exceptions.HttpException:
            # Not allowed to find_project if not admin project
            nets = self.conn.network.networks(is_admin_state_up=True)
        except o_exceptions.SDKException as ex:
            LOG.error("Could not get networks. ERROR: %s", str(ex.message))
            return None
        return nets

    def get_flavors(self):
        try:
            flavors = self.conn.compute.flavors()
        except o_exceptions.SDKException as ex:
            LOG.error("Could not get flavors. ERROR: %s", str(ex.message))
            return None
        return flavors

    def get_keypairs(self):
        try:
            flavors = self.conn.compute.keypairs()
        except o_exceptions.SDKException as ex:
            LOG.error("Could not get flavors. ERROR: %s", str(ex.message))
            return None
        return flavors

    def upload_image(self, name, path, meta=None,
                     hw_disk_bus=None, hw_vif_model=None):
        try:
            metadata = dict()
            if meta is not None:
                metadata = meta
            if hw_disk_bus is not None:
                metadata['hw_disk_bus'] = hw_disk_bus
            if hw_vif_model is not None:
                metadata['hw_vif_model'] = hw_vif_model

            image = self.conn.image.upload_image(disk_format="qcow2",
                                                 container_format="bare",
                                                 name=name,
                                                 data=open(path, 'rb'),
                                                 meta=metadata)
        except o_exceptions.SDKException as ex:
            LOG.error("Could not upload image. ERROR: %s", str(ex.message))
            return None
        return image

    def create_server(self, name, flavor_id, image_id,
                      network_id, metadata, keypair_name=None):
        try:
            server = self.conn.compute.create_server(
                name=name,
                flavor_id=flavor_id,
                image_id=image_id,
                key_name=keypair_name,
                networks=[{"uuid": network_id}],
                metadata=metadata)
            server = self.conn.compute.wait_for_server(server)
        except o_exceptions.SDKException as ex:
            LOG.error("Could not create server. ERROR: %s", str(ex.message))
            return None
        return server

    def create_volume(self, name, image_id, metadata):
        try:
            volume = self.conn.block_storage.create_volume(
                name=name,
                image_id=image_id,
                metadata=metadata)
        except o_exceptions.SDKException as ex:
            LOG.error("Could not create volume. ERROR: %s", str(ex.message))
            return None
        return volume

    def attach_volume_to_server(self, server, volume_id):
        try:
            self.conn.compute.create_volume_attachment(
                server=server,
                volume_id=volume_id)
        except o_exceptions.SDKException as ex:
            LOG.error("Could not attach volume. ERROR: %s", str(ex.message))
            return False
        return True

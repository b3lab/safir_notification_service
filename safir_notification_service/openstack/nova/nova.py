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

from novaclient import client
from safir_notification_service.openstack.connector import OpenstackConnector

__novaclient_version__ = '2'


class NovaClient:
    def __init__(self,
                 auth_username,
                 auth_password,
                 auth_url,
                 project_name,
                 user_domain_name,
                 project_domain_name):

        openstack_connector = OpenstackConnector(
            auth_username,
            auth_password,
            auth_url,
            project_name,
            user_domain_name,
            project_domain_name)
        session = openstack_connector.get_session()

        self.nova_client = client.Client(__novaclient_version__,
                                         session=session)

    def get_instance(self, instance_id):
        return self.nova_client.servers.get(instance_id)

    def get_instance_name(self, instance_id):
        return self.nova_client.servers.get(instance_id)['name']

    def get_hosts(self):
        return self.nova_client.hosts.list()

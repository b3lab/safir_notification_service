from novaclient import client
from safir_alarm_service.openstack.connector import OpenstackConnector

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

        self.nova_client = client.Client(__novaclient_version__, session=session)

    def get_instance(self, instance_id):
        return self.nova_client.servers.get(instance_id)

    def get_instance_name(self, instance_id):
        return self.nova_client.servers.get(instance_id)['name']

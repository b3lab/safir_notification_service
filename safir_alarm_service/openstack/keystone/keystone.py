from keystoneclient.v3 import client
from safir_alarm_service.openstack.connector import OpenstackConnector


class KeystoneClient:
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

        self.keystone_client = client.Client(session=session)

    def get_projects(self):
        return self.keystone_client.projects.list()

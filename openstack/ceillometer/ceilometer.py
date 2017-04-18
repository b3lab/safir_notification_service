from ceilometerclient import client
from openstack.connector import OpenstackConnector

__ceilometerclient_version__ = '2'


class CeilometerClient:
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

        self.ceilometer_client = client.Client(__ceilometerclient_version__, session=session)

    def get_alarm(self, alarm_id):
        return self.ceilometer_client.alarms.get(alarm_id)

    def get_instance_id(self, alarm_id):
        alarm = self.get_alarm(alarm_id)
        return alarm.query['resource_id']

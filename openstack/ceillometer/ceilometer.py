from openstack.connector import CeilometerConnector


class CeilometerAlarms:
    def __init__(self,
                 identity_api_version,
                 auth_username,
                 auth_password,
                 auth_url,
                 project_name,
                 user_domain_name,
                 project_domain_name):

        ceilometer_connector = CeilometerConnector(
                                   identity_api_version,
                                   auth_username,
                                   auth_password,
                                   auth_url,
                                   project_name,
                                   user_domain_name,
                                   project_domain_name)

        self.ceilometer_client = ceilometer_connector.get_conn()

    def get_alarm(self, alarm_id):
        return self.ceilometer_client.alarms.get(alarm_id)

    def get_instance_id(self, alarm):
        return alarm.query['resource_id']


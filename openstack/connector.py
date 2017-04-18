from ceilometerclient import client
from keystoneauth1 import loading
from keystoneauth1 import session

__ceilometerclient_version__ = '2'


class CeilometerConnector:
    def __init__(self,
                 identity_api_version,
                 auth_username,
                 auth_password,
                 auth_url,
                 project_name,
                 user_domain_name,
                 project_domain_name):
        """
        Parameters
        ----------
        auth_username
        auth_password
        auth_url
        project_name

        Examples
        --------
        auth_username = 'admin'
        auth_password = 'stack'
        auth_url = 'http://192.168.122.75:5000/v2.0'
        project_id = 'admin'
        project_domain_name = 'default'
        user_domain_name = 'default'
        """

        self.auth_url = auth_url

        if identity_api_version == '3':
            loader = loading.get_plugin_loader('password')
            auth = loader.load_from_options(auth_url=auth_url,
                                            username=auth_username,
                                            password=auth_password,
                                            project_name=project_name,
                                            user_domain_name=user_domain_name,
                                            project_domain_name=project_domain_name)
            sess = session.Session(auth=auth)
            self.conn = client.Client(__ceilometerclient_version__, session=sess)
        elif identity_api_version == '2':
            self.conn = client.Client(__ceilometerclient_version__,
                                      auth_username,
                                      auth_password,
                                      project_name,
                                      auth_url
                                      )
        else:
            self.conn = None

    def get_conn(self):
        return self.conn

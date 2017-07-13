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

from keystoneauth1 import loading
from keystoneauth1 import session


class OpenstackConnector:
    def __init__(self,
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

        loader = loading.get_plugin_loader('password')
        auth = loader.load_from_options(
            auth_url=auth_url,
            username=auth_username,
            password=auth_password,
            project_name=project_name,
            user_domain_name=user_domain_name,
            project_domain_name=project_domain_name)
        self.session = session.Session(auth=auth)

    def get_session(self):
        return self.session

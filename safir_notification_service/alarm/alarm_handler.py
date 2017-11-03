# Copyright 2017 TUBITAK B3LAB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
import re

from safir_email_notifier.email_builder import EmailBuilder
from safir_email_notifier.email_notifier import EmailNotifier

from safir_notification_service.openstack.connector import OpenstackConnector
from safir_notification_service.utils import log
from safir_notification_service.utils.opts import ConfigOpts

LOG = log.get_logger()


class AlarmHandler:
    def __init__(self):
        self.openstack_connector = None

        config_opts = ConfigOpts()
        openstack_config_name = config_opts.get_opt('DEFAULT',
                                                    'openstack_config_name')
        self.openstack_connector = OpenstackConnector(openstack_config_name)

        self.monitor_panel_url = config_opts.get_opt('DEFAULT',
                                                     'monitor_panel_url')
        self.email_opts = config_opts.get_opts_of_section('email')

    def handle_alarm(self, alarm_id, current_state, previous_state, reason):

        state = ''
        if current_state == 'alarm' and previous_state != 'alarm':
            state = 'alarm'
        elif current_state == 'ok' and previous_state != 'ok':
            state = 'ok'
        else:
            print('Same state (' + str(current_state) + ') continues. Skipping...')

        alarm = self.openstack_connector.get_aodh_alarm(alarm_id)

        # description area is used to store email address
        email = alarm['description']

        instance_id = None
        threshold_rule = None
        meter_name = None
        if 'threshold_rule' in alarm:
            threshold_rule = alarm['threshold_rule']
            meter_name = 'meter_name'
            for s in alarm['threshold_rule']['query']:
                if s['field'] == 'resource_id':
                    instance_id = s['value']
        elif 'gnocchi_resources_threshold_rule' in alarm:
            threshold_rule = alarm['gnocchi_resources_threshold_rule']
            meter_name = 'metric'
            instance_id = threshold_rule['resource_id']
        else:
            LOG.error('Threshold rules not found.')

        instance_name = None
        # TODO!: Also add current flavor to message
        # flavor_id = None
        if instance_id is not None:
            instance = self.openstack_connector.get_compute_server(instance_id)
            instance_name = instance.name
            # flavor_id = instance.flavor['id']

        resource_type = ''
        if threshold_rule[meter_name] == 'cpu_util':
            resource_type = 'CPU'
        elif threshold_rule[meter_name] == 'memory_util':
            resource_type = 'RAM'
        elif threshold_rule[meter_name] == 'disk_util':
            resource_type = 'Disk'
        elif threshold_rule[meter_name] == 'network.incoming.bytes.rate':
            resource_type = 'Incoming Network Traffic'
        elif threshold_rule[meter_name] == 'network.outgoing.bytes.rate':
            resource_type = 'Outgoing Network Traffic'

        comparison_operator = ''
        if threshold_rule['comparison_operator'] == 'lt':
            comparison_operator = 'Less than'
        elif threshold_rule['comparison_operator'] == 'le':
            comparison_operator = 'Less than or equal to'
        elif threshold_rule['comparison_operator'] == 'eq':
            comparison_operator = 'Equal to'
        elif threshold_rule['comparison_operator'] == 'ne':
            comparison_operator = 'Not equal to'
        elif threshold_rule['comparison_operator'] == 'ge':
            comparison_operator = 'Greater than or equal to'
        elif threshold_rule['comparison_operator'] == 'gt':
            comparison_operator = 'Greater than'

        threshold = threshold_rule['threshold']
        evaluation_periods = threshold_rule['evaluation_periods']

        if self.is_valid_email(email):
            self.send_email(state,
                            email,
                            instance_name,
                            resource_type,
                            comparison_operator,
                            threshold,
                            evaluation_periods,
                            reason)

    def send_email(self,
                   state,
                   to_mail,
                   instance_name,
                   resource_type,
                   comparison_operator,
                   threshold,
                   evaluation_periods,
                   reason):
        try:
            mail_data = {'name': '',
                         'instance_name': instance_name,
                         'link': self.monitor_panel_url,
                         'resource_type': resource_type,
                         'comparison_operator': comparison_operator,
                         'threshold': threshold,
                         'evaluation_periods': evaluation_periods,
                         'reason': reason,
                         'email': to_mail}

            template_name = None
            if state == 'alarm':
                template_name = 'alarm_alarm'
            elif state == 'ok':
                template_name = 'alarm_ok'

            mail_builder = EmailBuilder(template_name)
            subject, text, html = mail_builder.get_mail_content(mail_data)
            mail_notifier = EmailNotifier(self.email_opts['smtp_server'],
                                          self.email_opts['smtp_port'],
                                          self.email_opts['login_addr'],
                                          self.email_opts['password'])
            mail_notifier.send_mail([to_mail], subject, text, html)

            LOG.info("Confirmation email sent successfully.")
        except Exception as ex:
            LOG.error("Confirmation email not sent. " + ex.message)
        return

    @staticmethod
    def is_valid_email(mail):
        if len(mail) > 7:
            if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", mail) is not None:
                return True
        return False

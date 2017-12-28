# -*- coding: utf-8 -*-
# !/usr/bin/env python

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


from safirnotification.cloud.openstack_manager import OpenstackManager
from safirnotification.notifier import Notifier

from oslo_config import cfg
from oslo_log import log as logging

import re

LOG = logging.getLogger(__name__)

CONF = cfg.CONF
CONF.import_opt('cloud_name', 'safirnotification.cloud', 'cloud')
CONF.import_opt('horizon_url', 'safirnotification.cloud', 'cloud')


class Worker:
    def __init__(self):
        self.openstack_connector = OpenstackManager(CONF.cloud.cloud_name)

    def handle_alarm(self, alarm_id, current_state, previous_state, reason):

        state = ''
        if current_state == 'alarm' and previous_state != 'alarm':
            state = 'alarm'
        elif current_state == 'ok' and previous_state != 'ok':
            state = 'ok'
        else:
            LOG.warning('Same state (' + str(current_state) +
                        ') continues. Skipping...')

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
            notifier = Notifier()
            mail_data = notifier.generate_mail_data(email,
                                                    instance_name,
                                                    CONF.cloud.horizon_url,
                                                    resource_type,
                                                    comparison_operator,
                                                    threshold,
                                                    evaluation_periods,
                                                    reason)
            notifier.send_notification_mail(state,
                                            mail_data,
                                            [email])

        return

    @staticmethod
    def is_valid_email(mail):
        if len(mail) > 7:
            if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
                        mail) is not None:
                return True
        return False

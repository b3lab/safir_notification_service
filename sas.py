# Copyright 2017 TUBITAK, BILGEM, B3LAB
#
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

from safir_notification_service.alarm.alarm_handler import AlarmHandler
from safir_notification_service.report.report_generator import ReportGenerator
from safir_notification_service.utils.repeated_timer import RepeatedTimer


class SafirAlarmService:
    def __init__(self):
        self.alarm_thread_list = []
        self.report_thread_list = []

    @staticmethod
    def process_alarm(alarm_id, current_state, previous_state, reason,
                      openstack_config, panel_config):
        alarm_handler = AlarmHandler(openstack_config, panel_config)
        alarm_handler.handle_alarm(alarm_id,
                                   current_state,
                                   previous_state,
                                   reason)

    def send_report(self, email_addr, report_interval,
                    openstack_config, panel_config):
        report_generator = ReportGenerator(email_addr,
                                           openstack_config,
                                           panel_config)
        rt = RepeatedTimer(report_interval, report_generator.generate_report)
        self.report_thread_list.append(rt)

    def kill_report_threads(self):
        for rt in self.report_thread_list:
            print ('killing report thread')
            rt.stop()

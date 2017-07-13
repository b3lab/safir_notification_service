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

from __future__ import print_function

from flask import Flask
from flask import request

import json
import sys

from sas import SafirAlarmService

ONE_DAY_IN_SECONDS = 86400

# host and port are set to run in a Cloud Foundry app
host = '0.0.0.0'
port = int(sys.argv[1])

# made these configurable to use with multiple platforms
openstack_config = 'openstack_connection'
panel_config = 'openstack_monitor_panel'

Flask.get = lambda self, path: self.route(path, methods=['get'])
app = Flask(__name__)

safir_notification_service = SafirAlarmService()


@app.route('/alarm', methods=['POST'])
def alarm():
    if request.method == 'POST':
        try:
            data = json.loads(request.data)

            if 'alarm_id' not in data:
                print("ERROR: Failed processing alarm! " +
                      "Alarm ID not found", file=sys.stderr)
            else:
                print ('ALARM RECEIVED. ID: ' + str(data['alarm_id']) +
                       ' Current state: ' + data['current'] +
                       ' Previous state: ' + data['previous'])

                safir_notification_service.process_alarm(
                    alarm_id=data['alarm_id'],
                    current_state=data['current'],
                    previous_state=data['previous'],
                    reason=data['reason'],
                    openstack_config=openstack_config,
                    panel_config=panel_config)

        except Exception as ex:
            print("ERROR: Failed processing alarm! " + ex.message,
                  file=sys.stderr)

    return "Ceilometer alarm received"


@app.route('/report', methods=['POST'])
def report():
    if request.method == 'POST':
        try:
            data = json.loads(request.data)
            interval = ONE_DAY_IN_SECONDS

            if 'email_addr' not in data:
                print("ERROR: Failed processing report! " +
                      "Admin e-mail address not found", file=sys.stderr)
            else:
                print ('REPORT request received. ' +
                       'Admin e-mail: ' + data['email_addr'])
                if 'report_interval' in data:
                    interval = data['report_interval']

            safir_notification_service.send_report(
                email_addr=data['email_addr'],
                report_interval=interval,
                openstack_config=openstack_config,
                panel_config=panel_config)

        except Exception as ex:
            print("ERROR: Failed processing report! " + ex.message,
                  file=sys.stderr)

    return "Report request received"


if __name__ == "__main__":
    app.run(host=host, port=port, threaded=True)
    safir_notification_service.kill_report_threads()

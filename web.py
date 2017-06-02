from __future__ import print_function
from flask import Flask
from flask import request

import json
import sys

from sas import SafirAlarmService

ONE_DAY_IN_SECONDS = 86400

host = '192.168.122.1'
port = 8080

# Comment out the following lines to run as a Cloud Foundry app
# host = '0.0.0.0'
# port = int(sys.argv[1])

Flask.get = lambda self, path: self.route(path, methods=['get'])
app = Flask(__name__)
safir_notification_service = SafirAlarmService()


@app.get('/')
def get_root():
    return 'Safir Notification Service'


@app.route('/alarm', methods=['POST'])
def alarm():
    if request.method == 'POST':
        try:
            data = json.loads(request.data)
            request_address = request.remote_addr

            if 'alarm_id' not in data:
                print("ERROR: Failed processing alarm! " +
                      "Alarm ID not found", file=sys.stderr)
            else:
                print ('ALARM RECEIVED. ID: ' + str(data['alarm_id']) +
                       ' Current state: ' + data['current'] +
                       ' Previous state: ' + data['previous'])

                openstack_config = ''
                panel_config = ''
                if '192.168.122.146' in request_address:
                    openstack_config = 'openstack_connection_local'
                    panel_config = 'openstack_monitor_panel_local'
                elif 'sencloud.b3lab.org' in request_address:
                    openstack_config = 'openstack_connection_sencloud'
                    panel_config = 'openstack_monitor_panel_sencloud'
                else:  # if 'cloud.b3lab.org' in request_address:
                    openstack_config = 'openstack_connection_cloudb3lab'
                    panel_config = 'openstack_monitor_panel_cloudb3lab'

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
    return 'Ceilometer alarm received'


@app.route('/report', methods=['POST'])
def report():
    if request.method == 'POST':
        try:
            data = json.loads(request.data)
            request_address = request.remote_addr
            interval = ONE_DAY_IN_SECONDS

            if 'email_addr' not in data:
                print("ERROR: Failed processing report! " +
                      "Admin e-mail address not found", file=sys.stderr)
            else:
                print ('REPORT request received. ' +
                       'Admin e-mail: ' + data['email_addr'])
                if 'report_interval' in data:
                    interval = data['report_interval']

            openstack_config = ''
            panel_config = ''
            if '192.168.122.146' in request_address:
                openstack_config = 'openstack_connection_local'
                panel_config = 'openstack_monitor_panel_local'
            elif 'sencloud.b3lab.org' in request_address:
                openstack_config = 'openstack_connection_sencloud'
                panel_config = 'openstack_monitor_panel_sencloud'
            else:  # if 'cloud.b3lab.org' in request_address:
                openstack_config = 'openstack_connection_cloudb3lab'
                panel_config = 'openstack_monitor_panel_cloudb3lab'

            safir_notification_service.send_report(
                    email_addr=data['email_addr'],
                    report_interval=interval,
                    openstack_config=openstack_config,
                    panel_config=panel_config)

        except Exception as ex:
            print("ERROR: Failed processing report! " + ex.message,
                  file=sys.stderr)
    return 'Report request received'


if __name__ == "__main__":
    app.run(host=host, port=port, threaded=True)
    safir_notification_service.kill_report_threads()

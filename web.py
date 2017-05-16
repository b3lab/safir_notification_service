from __future__ import print_function
from flask import Flask
from flask import request

import json
import sys

from sas import SafirAlarmService

host = '192.168.122.1'
port = 8080

# host = '0.0.0.0'
# port = int(sys.argv[1])

Flask.get = lambda self, path: self.route(path, methods=['get'])
app = Flask(__name__)
safir_alarm_service = SafirAlarmService()


@app.get('/')
def get_root():
    return 'Safir Alarm Service'


@app.route('/alarm', methods=['POST'])
def alarm():
    if request.method == 'POST':
        try:
            data = json.loads(request.data)
            if 'alarm_id' not in data:
                print("ERROR: Failed processing alarm! " +
                      "Alarm ID not found", file=sys.stderr)
            else:
                print ('ALARM RECEIVED. ID: ' + str(data['alarm_id']) +\
                       ' Current state: ' + data['current'] +\
                       ' Previous state: ' + data['previous'])
                safir_alarm_service.process_alarm(alarm_id=data['alarm_id'],
                                                  current_state=data['current'],
                                                  previous_state=data['previous'],
                                                  reason=data['reason'])
        except Exception as ex:
            print("ERROR: Failed processing alarm! " + ex.message , file=sys.stderr)
    return 'Ceilometer alarm received'


@app.route('/report', methods=['POST'])
def report():
    if request.method == 'POST':
        try:
            #data = json.loads(request.data)
            #if 'email_addr' not in data:
            #    print("ERROR: Failed processing report! " +
            #          "Admin e-mail address not found", file=sys.stderr)
            #else:
            #    print ('REPORT request received. ' +
            #           'Admin e-mail: ' + data['email_addr'])
            safir_alarm_service.send_report(email_addr='celik.esra@tubitak.gov.tr')  # data['email_addr'])
        except Exception as ex:
            print("ERROR: Failed processing report! " + ex.message , file=sys.stderr)
    return 'Report request received'


if __name__ == "__main__":
    app.run(host=host, port=port)
    safir_alarm_service.kill_report_threads()

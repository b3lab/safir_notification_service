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
                print (data['alarm_id'])
                safir_alarm_service = SafirAlarmService()
                safir_alarm_service.process_alarm(alarm_id=data['alarm_id'],
                                                  state=data['current'],
                                                  reason=data['reason'])
        except Exception as ex:
            print("ERROR: Failed processing alarm! " + ex.message , file=sys.stderr)
    return 'Ceilometer alarm received'

if __name__ == "__main__":
    app.run(host=host, port=port)

from __future__ import print_function
from flask import Flask
from flask import request

import argparse
import json
import sys

from safirnotification.alarm.alarm_handler import AlarmHandler
from safirnotification.utils import log
from safirnotification.utils.opts import ConfigOpts

LOG = log.get_logger()


Flask.get = lambda self, path: self.route(path, methods=['get'])
app = Flask(__name__)

alarm_handler = None


@app.route('/alarm', methods=['POST'])
def alarm():
    if request.method == 'POST':
        try:
            data = json.loads(request.data)

            if 'alarm_id' not in data:
                LOG.error("Failed processing alarm! " +
                          "Alarm ID not found", file=sys.stderr)
            else:
                LOG.info('ALARM RECEIVED. ID: ' + str(data['alarm_id']) +
                         ' Current state: ' + data['current'] +
                         ' Previous state: ' + data['previous'])
                alarm_handler.handle_alarm(
                        alarm_id=data['alarm_id'],
                        current_state=data['current'],
                        previous_state=data['previous'],
                        reason=data['reason'])

        except Exception as ex:
            LOG.error("Failed processing alarm! " + ex.message)

    return "AODH alarm received"


def main():
    parser = argparse.ArgumentParser(prog='safirnotification')
    parser.add_argument('-c', help='Config file path')

    args = parser.parse_args()
    config_file = args.c
    if config_file is None:
        print('usage: safirnotification -c <config-file-path>')
        sys.exit(2)

    global alarm_handler
    alarm_handler = AlarmHandler(config_file)

    config_opts = ConfigOpts(config_file)
    host = config_opts.get_opt('api', 'host')
    port = config_opts.get_opt('api', 'port')

    app.run(host=host, port=port, threaded=True)


if __name__ == "__main__":
    main()

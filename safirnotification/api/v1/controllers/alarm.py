# -*- coding: utf-8 -*-
# Copyright 2017 TUBITAK B3LAB
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import pecan
from pecan import rest
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from safirnotification.worker import Worker


class ReasonData(wtypes.Base):
    count = int
    most_recent = float
    type = wtypes.text
    disposition = wtypes.text


class Alarm(wtypes.Base):

    alarm_name = wtypes.text
    alarm_id = wtypes.text
    severity = wtypes.text
    current = wtypes.text
    previous = wtypes.text
    reason = wtypes.text
    reason_data = ReasonData

    @classmethod
    def sample(cls, alarm_name,
               alarm_id,
               severity,
               current,
               previous,
               reason,
               reason_data):
        return cls(alarm_name=alarm_name,
                   alarm_id=alarm_id,
                   severity=severity,
                   current=current,
                   previous=previous,
                   reason=reason,
                   reason_data=reason_data)

    def to_json(self):
        res_dict = {'alarm_name': self.alarm_name,
                    'alarm_id': self.alarm_id,
                    'severity': self.severity,
                    'current': self.current,
                    'previous': self.previous,
                    'reason': self.reason}
        return res_dict


class AlarmController(rest.RestController):

    @wsme_pecan.wsexpose(wtypes.text)
    def get_all(self):
        return 'success'

    @wsme_pecan.wsexpose(body=Alarm,
                         status_code=302)
    def post(self, data):

        worker = Worker()
        worker.handle_alarm(alarm_id=data.alarm_id,
                            current_state=data.current,
                            previous_state=data.previous,
                            reason=data.reason)

        pecan.response.location = pecan.request.path

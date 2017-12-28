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

import datetime
import pecan
from pecan import rest
import six
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan


class Alarm(wtypes.Base):

    alarm_id = wtypes.text
    current = wtypes.text
    previous = wtypes.text
    reason = wtypes.text

    @classmethod
    def sample(cls, alarm_id,
               current, previous,
               reason):
        return cls(alarm_id=alarm_id,
                   current=current,
                   previous=previous,
                   reason=reason)

    def to_json(self):
        res_dict = {'alarm_id': self.alarm_id,
                    'current': self.current,
                    'previous': self.previous,
                    'reason': self.reason}
        return res_dict


class AlarmController(rest.RestController):
    _custom_actions = {'alarm': ['POST']}

    @wsme_pecan.wsexpose(Alarm)
    def get_all(self):
        alarm = Alarm.sample('1', '3', '23', 'f')
        return alarm

    @wsme_pecan.wsexpose(body=Alarm,
                         status_code=302)
    def alarm(self, alarm_body):
        print(alarm_body.alarm_id)
        print(alarm_body.current)
        print(alarm_body.previous)
        print(alarm_body.reason)

        pecan.response.location = pecan.request.path

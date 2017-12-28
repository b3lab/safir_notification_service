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

    id = wtypes.text
    status = wtypes.text

    @classmethod
    def sample(cls,
               id,
               status):
        return cls(id=id,
                   status=status)

    def to_json(self):
        res_dict = {'id': self.id,
                    'status': self.status,
                    'timestamp': self.timestamp}
        return res_dict


class AlarmController(rest.RestController):

    @wsme_pecan.wsexpose(Alarm)
    def get_all(self):
        alarm = Alarm.sample('1', '3')
        return alarm

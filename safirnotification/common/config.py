# -*- coding: utf-8 -*-
# Copyright 2017 TUBITAK B3LAB
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

import copy
import itertools

import safirnotification.api.app
import safirnotification.cloud
import safirnotification.notifier
import safirnotification.service

__all__ = ['list_opts']

_opts = [
    ('api', list(itertools.chain(
        safirnotification.api.app.api_opts,))),
    ('cloud', list(itertools.chain(
        safirnotification.cloud.cloud_opts))),
    ('email_server', list(itertools.chain(
        safirnotification.notifier.email_server_opts))),
    (None, list(itertools.chain(
        safirnotification.api.app.auth_opts,
        safirnotification.service.service_opts)))
]


def list_opts():
    return [(g, copy.deepcopy(o)) for g, o in _opts]

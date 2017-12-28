
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
# under the License

from oslo_config import cfg

# Notification e-mail options
email_notifier_opts = [
    cfg.StrOpt('EMAIL_HOST',
               default='',
               help="""
E-mail Host

SMTP Server host which will be used to send notification e-mails.
"""),
    cfg.StrOpt('EMAIL_PORT',
               default='',
               help="""
E-mail Host Port nummber
"""),
    cfg.StrOpt('EMAIL_HOST_USER',
               default='',
               help="""
E-mail Host Username
"""),
    cfg.StrOpt('EMAIL_HOST_PASSWORD',
               default='',
               help="""
E-mail Host Password
"""),
    cfg.StrOpt('EMAIL_USE_TLS',
               default='True',
               help="""
Use TLS protocol if True.

Possible values:

* True, False
Possible values:

* True, False

""")
]

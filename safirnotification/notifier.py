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

import logging
from oslo_config import cfg
from safir_email_notifier.email_builder import EmailBuilder
from safir_email_notifier.email_notifier import EmailNotifier

email_server_opts = [
    cfg.StrOpt('smtp_server',
               default='',
               help="SMTP Server Host"),
    cfg.StrOpt('smtp_port',
               default='',
               help="SMTP Server Port"),
    cfg.StrOpt('login_address',
               default='',
               help="SMTP Server Login Address"),
    cfg.StrOpt('password',
               default='',
               help="SMTP Server Login Password"),
    cfg.StrOpt('use_tls',
               default='True',
               help="Use TLS protocol if True.")
]


CONF = cfg.CONF
CONF.register_opts(email_server_opts, 'email_server')

LOG = logging.getLogger(__name__)


class Notifier(object):
    """Informer

    Sends an information e-mail to users
    """

    @staticmethod
    def generate_mail_data(to_mail,
                           instance_name,
                           panel_url,
                           resource_type,
                           comparison_operator,
                           threshold,
                           evaluation_periods,
                           reason):
        """Generate e-mail content data

        :return: mail_data to fill e-mail template parameters
        :rtype: dict(str:?)
        """
        mail_data = {}
        try:
            mail_data = {'name': '',
                         'instance_name': instance_name,
                         'link': panel_url,
                         'resource_type': resource_type,
                         'comparison_operator': comparison_operator,
                         'threshold': threshold,
                         'evaluation_periods': evaluation_periods,
                         'reason': reason,
                         'email': to_mail}

        except Exception as ex:
            LOG.error("E-mail content have not generated. " + ex.message)

        return mail_data

    @staticmethod
    def send_notification_mail(state, mail_data, to_list):
        """Construct e-mail content and send notification e-mail.

        :param state: alarm state {alarm, ok}
        :param mail_data: mail data constructed by _generate_mail_data
        :param to_list: mail receptors list
        """
        try:
            template_name = None
            if state == 'alarm':
                template_name = 'alarm_alarm'
            elif state == 'ok':
                template_name = 'alarm_ok'

            # Construct e-mail
            mail_builder = EmailBuilder(template_name)
            subject, text, html = mail_builder.get_mail_content(mail_data)
            mail_notifier = EmailNotifier(
                CONF.email_server.smtp_server,
                CONF.email_server.smtp_port,
                CONF.email_server.login_address,
                CONF.email_server.password)

            # Send e-mail
            mail_notifier.send_mail(to_list, subject, text, html)
            LOG.info("Notification email sent successfully.")
        except Exception as ex:
            LOG.error("Notification email not sent. " + ex.message)
            return False
        return True

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
from safirnotification.db import api as db_api

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class Informer(object):
    """Informer

    It sends an information e-mail to users who exceed their billing limit.
    Fill the e-mail template as action type, send e-mail.

    Fill the e-mail template with neccessary parameters, send e-mail.

    Check the user in private or e-mail exception group, don't send a-mail.
    """

    def __init__(self, project_id, operation_type):
        """

        :param project_id: project id
        :param operation_type: operation type
        :type operation_type:str (TERMINATION or SUSPEND)
        """

        # Setup attributes
        self._project_id = project_id
        self._operation_type = operation_type
        self._is_status_changed = self._check_status()

    def _check_status(self):
        """Check whether the customer status has changed or not

        :return: If status changed return True else False
        :rtype: bool
        """
        customer_db = db_api.get_instance().get_customers_api()

        status = customer_db.get_customer(self._project_id).status

        if status in self._operation_type:
            return False
        else:
            return True

    def _generate_mail_data(self):
        """Generate e-mail content data

        :return: mail_data to fill e-mail template parameters
        :rtype: dict(str:?)
        """
        mail_data = {}

        try:
            # Setup database customer api's
            credit_db = db_api.get_instance().get_credits_api()
            customer_db = db_api.get_instance().get_customers_api()
            credit_load_db = db_api.get_instance().get_creditload_api()

            # Get username
            if customer_db.get_customer(self._project_id).contact_name is None:
                username = customer_db.get_customer(
                    self._project_id).company_name
            else:
                username = customer_db.get_customer(
                    self._project_id).contact_name

            # TODO(necmeddin): added link go to safir billing load credit page
            redirect_link = ''

            # Fill e-mail content parameters
            mail_data = {
                'name': username,
                'link': redirect_link
            }

        except Exception as ex:
            LOG.error("E-mail content have not generated. " + ex.message)

        return mail_data

    def _create_mail_list(self, is_cc_yourself):
        """Create e-mail list of addresses to which the e-mail is sent

        :param is_cc_yourself: A flag indicates that whether the copy of
                              the e-mail is also sent to itself or not
        :type is_cc_yourself: bool
        :return:e-mail list
        :rtype:list
        """
        email_to_list = []

        # User e-mail
        customer_db = db_api.get_instance().get_customers_api()
        user_mail_address = customer_db.get_customer(self._project_id).mail
        email_to_list.append(user_mail_address)

        if is_cc_yourself:
            # Setup e-mail to list. Send e-mail copy to yourself
            sender_email_adress = CONF.email_notifier.EMAIL_HOST_USER
            email_to_list.append(sender_email_adress)

        return email_to_list

    def send_notification_mail(self, is_cc_yourself=False):
        """Construct e-mail content and send notification e-mail.

        If user is not member of email exception group, send mail

        :param cc_yourself: A flag indicates that whether the copy of the
                           e-mail is also sent to itself or not
        :type cc_yourself: bool (defualt : False)
        :return:
        """
        print('HERE_prepaid_send_notification_email', self._operation_type)

        # If status is not changed don't resend e-mail
        if self._is_status_changed:

            # Create content for a-mail template parameters
            mail_data = self._generate_mail_data()

            # Create e-mail send list
            mail_to_list = self._create_mail_list(is_cc_yourself)

            try:

                # Construct e-mail
                mail_builder = EmailBuilder('billing_alarm')
                subject, text, html = mail_builder.get_mail_content(mail_data)
                mail_notifier = EmailNotifier(
                    CONF.email_notifier.EMAIL_HOST,
                    CONF.email_notifier.EMAIL_PORT,
                    CONF.email_notifier.EMAIL_HOST_USER,
                    CONF.email_notifier.EMAIL_HOST_PASSWORD)

                # Send e-mail
                mail_notifier.send_mail(mail_to_list, subject, text, html)

                LOG.info("Notification email sent successfully.")
            except Exception as ex:
                LOG.error("Notification email not sent. " + ex.message)
                # FIXME: If e-mail didn't send, can try resend after sleep time
        else:
            LOG.info("Notification email don't send "
                     "because of user mail exception list.")

        return

    def send_error_mail(self, server, err):
        """
        Send e-mail to administrator
        occurred any error while terminate or suspend server

        :param subject: E-mail subject
        :param text: E-mail content
        :return:
        """

        print('HERE_ERROR_MAIL')
        mail_notifier = EmailNotifier(
            CONF.email_notifier.EMAIL_HOST,
            CONF.email_notifier.EMAIL_PORT,
            CONF.email_notifier.EMAIL_HOST_USER,
            CONF.email_notifier.EMAIL_HOST_PASSWORD)

        # Construct e-mail to list
        recipients = [CONF.email_notifier.EMAIL_HOST_USER]

        # Cloud admin page
        redirect_url = ''

        # Fill e-mail content parameters
        mail_data = {
            'link': redirect_url,
            'error': err,
            'project_id': self._project_id,
            'action_type': self._operation_type,
            'server_status': server.status,
            'server_id': server.id,
            'server_name': server.name,
            'user_id': server.user_id,
            'flavor': server.flavor,
            'image': server.image,
            'created_time': server.created,
            'updated_time': server.updated
        }

        # Construct e-mail
        mail_builder = EmailBuilder('error_notification')
        subject, text, html = mail_builder.get_mail_content(mail_data)

        # Send e-mail
        mail_notifier.send_mail(recipients, subject, text, html)

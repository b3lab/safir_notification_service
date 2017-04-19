from openstack.ceillometer.ceilometer import CeilometerClient
from openstack.nova.nova import NovaClient

from notification.email_notifier import EmailNotifier
from utils.opts import ConfigOpts

import re


class SafirAlarmService:
    def __init__(self):
        self.configOpts = ConfigOpts()

        auth_username = self.configOpts.get_opt('openstack_connection',
                                                'auth_username')
        auth_password = self.configOpts.get_opt('openstack_connection',
                                                'auth_password')
        auth_url = self.configOpts.get_opt('openstack_connection',
                                           'auth_url')
        auth_project_name = self.configOpts.get_opt('openstack_connection',
                                                    'auth_project_name')
        user_domain_name = self.configOpts.get_opt('openstack_connection',
                                                   'user_domain_name')
        project_domain_name = self.configOpts.get_opt('openstack_connection',
                                                      'project_domain_name')

        self.ceilometer_client = CeilometerClient(auth_username,
                                                  auth_password,
                                                  auth_url,
                                                  auth_project_name,
                                                  user_domain_name,
                                                  project_domain_name)

        self.nova_client = NovaClient(auth_username,
                                      auth_password,
                                      auth_url,
                                      auth_project_name,
                                      user_domain_name,
                                      project_domain_name)

    def process_alarm(self, alarm_id, reason):

        alarm = self.ceilometer_client.get_alarm(alarm_id)
        print alarm
        print alarm.user_id
        user_id = 'celik.esra@tubitak.gov.tr'  # alarm.user_id
        instance_id = None
        for s in alarm.threshold_rule['query']:
            if s['field'] == 'resource_id':
                instance_id = s['value']

        instance_name = None
        flavor_id = None
        if instance_id is not None:
            instance = self.nova_client.get_instance(instance_id)
            instance_name = instance.name
            flavor_id = instance.flavor['id']

        if self.isValidEmail(user_id):
            self.send_email(user_id,
                            user_id,
                            instance_name,
                            reason)

    def send_email(self,
                   username,
                   user_email,
                   instance_name,
                   alarm_desc,
                   ):

        smtp_server = self.configOpts.get_opt('email',
                                              'smtp_server')
        smtp_port = self.configOpts.get_opt('email',
                                            'smtp_port')
        login_addr = self.configOpts.get_opt('email',
                                             'login_addr')
        password = self.configOpts.get_opt('email',
                                           'password')

        email_notifier = EmailNotifier(smtp_server, smtp_port,
                                       login_addr, password)

        text, html = self.message_template(username,
                                           instance_name,
                                           alarm_desc)
        email_notifier.send_mail(user_email,
                                 'ALARM: Safir Cloud Platform Instance Alarm',
                                 text, html)

    def isValidEmail(self, addr):
        if len(addr) > 7:
            if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", addr) is not None:
                return True
        return False

    @staticmethod
    def message_template(username, instance_name, alarm_desc):

        text = 'Dear Safir Cloud Platform User! \
                \n\n \
                We realized that the instance ' + instance_name + \
                ' of your account ' + username + ' is giving alarm. \
                \n\n \
                Alarm description is: ' + alarm_desc + \
                '\n\n \
                We suggest you to resize your instance soon. \
                \n\n \
                Sincerely,\
                \n \
                B3LAB team'
        html = '<html>\
            <body>\
                <p>Dear Safir Cloud Platform User!</p>\
                <br> <br>\
                We realized that the instance ' + instance_name + \
                ' of your account ' + username + ' is giving alarm.\
                <br> <br>\
                Alarm description is: ' + alarm_desc + \
                '<br> <br>\
                We suggest you to resize your instance soon.<br>\
                <br> <br>\
                Sincerely,\
                <br>\
                B3LAB team\
                <br>\
                <br>\
            </body>\
            </html>'

        return text, html

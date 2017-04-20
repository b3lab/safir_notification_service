from safir_alarm_service.notification.email_notifier import EmailNotifier
from safir_alarm_service.openstack.ceillometer.ceilometer import CeilometerClient
from safir_alarm_service.openstack.nova.nova import NovaClient
from safir_alarm_service.utils.opts import ConfigOpts

import os
import re

from jinja2 import Environment, FileSystemLoader

PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.join(PATH, 'safir_alarm_service/templates')),
    trim_blocks=False)


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

    def process_alarm(self, alarm_id, state, reason):

        alarm = self.ceilometer_client.get_alarm(alarm_id)
        #print alarm

        # description area is used to store email address
        email = alarm.description
        instance_id = None
        for s in alarm.threshold_rule['query']:
            if s['field'] == 'resource_id':
                instance_id = s['value']

        instance_name = None
        # TODO!: Also add current flavor to message
        # flavor_id = None
        if instance_id is not None:
            instance = self.nova_client.get_instance(instance_id)
            instance_name = instance.name
            # flavor_id = instance.flavor['id']

        if self.isValidEmail(email):
            self.send_email(state,
                            email,
                            instance_name,
                            reason)

    def send_email(self,
                   state,
                   email,
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

        subject, text, html = self.message_template(state,
                                           instance_name,
                                           alarm_desc)
        email_notifier.send_mail(email,
                                 subject,
                                 text, html)

    def isValidEmail(self, addr):
        if len(addr) > 7:
            if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", addr) is not None:
                return True
        return False

    @staticmethod
    def render_template(template_filename, context):
        return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)

    def message_template(self, state, instance_name, alarm_desc):

        filename = ''
        if state == 'alarm':
            filename = 'alarm.html'
        elif state == 'ok':
            filename = 'ok.html'

        data = {
            'instance_name': instance_name,
            'alarm_desc': alarm_desc
        }

        html = self.render_template(filename, data)

        subject = ''
        text = ''
        if state == 'alarm':
            subject = 'ALARM: Safir Cloud Platform instance alarm'
            text = 'Dear Safir Cloud Platform User! \
                    \n\n \
                    We realized that the instance ' + instance_name + \
                    ' of your account is giving alarm. \
                    \n\n \
                    Alarm description is: ' + alarm_desc + \
                    '\n\n \
                    We suggest you to resize your instance soon. \
                    \n\n \
                    Sincerely,\
                    \n \
                    B3LAB team'
        elif state == 'ok':
            subject = 'OK: Safir Cloud Platform instance back to normal'
            text = 'Dear Safir Cloud Platform User! \
                    \n\n \
                    Your instance ' + instance_name + \
                    ' of your account back to normal. \
                    \n\n \
                    Sincerely,\
                    \n \
                    B3LAB team'

        return subject, text, html

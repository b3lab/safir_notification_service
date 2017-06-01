from safir_notification_service.notification.email_notifier import EmailNotifier
from safir_notification_service.openstack.ceillometer.ceilometer import CeilometerClient
from safir_notification_service.openstack.nova.nova import NovaClient
from safir_notification_service.report.report_generator import ReportGenerator
from safir_notification_service.utils.repeated_timer import RepeatedTimer
from safir_notification_service.utils.opts import ConfigOpts
from safir_notification_service.utils import utils


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

        self.report_thread_list = []

    def process_alarm(self, alarm_id, current_state, previous_state, reason):

        state = ''
        if current_state == 'alarm' and previous_state != 'alarm':
            state = 'alarm'
        elif current_state == 'ok' and previous_state != 'ok':
            state = 'ok'
        else:
            print ('Same state (' + str(current_state) + ') continues. Skipping...')

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

        resource_type = ''
        if alarm.threshold_rule['meter_name'] == 'cpu_util':
            resource_type = 'CPU'
        elif alarm.threshold_rule['meter_name'] == 'memory_util':
            resource_type = 'RAM'
        elif alarm.threshold_rule['meter_name'] == 'disk_util':
            resource_type = 'Disk'
        elif alarm.threshold_rule['meter_name'] == 'network.incoming.bytes.rate':
            resource_type = 'Incoming Network Traffic'
        elif alarm.threshold_rule['meter_name'] == 'network.outgoing.bytes.rate':
            resource_type = 'Outgoing Network Traffic'

        comparison_operator = ''
        if alarm.threshold_rule['comparison_operator'] == 'lt':
            comparison_operator = 'Less than'
        elif alarm.threshold_rule['comparison_operator'] == 'le':
            comparison_operator = 'Less than or equal to'
        elif alarm.threshold_rule['comparison_operator'] == 'eq':
            comparison_operator = 'Equal to'
        elif alarm.threshold_rule['comparison_operator'] == 'ne':
            comparison_operator = 'Not equal to'
        elif alarm.threshold_rule['comparison_operator'] == 'ge':
            comparison_operator = 'Greater than or equal to'
        elif alarm.threshold_rule['comparison_operator'] == 'gt':
            comparison_operator = 'Greater than'

        threshold = alarm.threshold_rule['threshold']
        period = alarm.threshold_rule['period']
        evaluation_periods = alarm.threshold_rule['evaluation_periods']

        if utils.is_valid_email(email):
            self.send_email(state,
                            email,
                            instance_name,
                            resource_type,
                            comparison_operator,
                            threshold,
                            period,
                            evaluation_periods,
                            reason)

    def send_email(self,
                   state,
                   email,
                   instance_name,
                   resource_type,
                   comparison_operator,
                   threshold,
                   period,
                   evaluation_periods,
                   reason):

        smtp_server = self.configOpts.get_opt('email',
                                              'smtp_server')
        smtp_port = self.configOpts.get_opt('email',
                                            'smtp_port')
        login_addr = self.configOpts.get_opt('email',
                                             'login_addr')
        password = self.configOpts.get_opt('email',
                                           'password')

        monitor_panel_url = self.configOpts.get_opt('openstack_monitor_panel',
                                                    'monitor_panel_url')

        email_notifier = EmailNotifier(smtp_server, smtp_port,
                                       login_addr, password)

        subject, text, html = self.message_template(state,
                                           instance_name,
                                           monitor_panel_url,
                                           resource_type,
                                           comparison_operator,
                                           threshold,
                                           period,
                                           evaluation_periods,
                                           reason,
                                           email)
        email_notifier.send_mail(email,
                                 subject,
                                 text, html)
        print (subject + ' mail sent to ' + email)

    @staticmethod
    def message_template(state,
                         instance_name,
                         monitor_panel_url,
                         resource_type,
                         comparison_operator,
                         threshold,
                         period,
                         evaluation_periods,
                         reason,
                         email):

        filename = ''
        if state == 'alarm':
            filename = 'alarm.html'
        elif state == 'ok':
            filename = 'ok.html'

        data = {
            'instance_name': instance_name,
            'monitor_panel_url': monitor_panel_url,
            'resource_type': resource_type,
            'comparison_operator': comparison_operator,
            'threshold': threshold,
            'period': period,
            'evaluation_periods': evaluation_periods,
            'reason': reason,
            'email': email
        }

        html = utils.render_template(filename, data)

        subject = ''
        text = ''
        if state == 'alarm':
            subject = 'ALARM: Safir Cloud Platform instance alarm'
            text = 'Dear Safir Cloud Platform User! \
                    \n\n \
                    The instance ' + instance_name + \
                    ' of your account is giving alarm. \
                    \n\n \
                    Alarm description is: ' + reason + \
                    '\n\n \
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

    def send_report(self, email_addr, report_interval):
        report_generator = ReportGenerator(email_addr)
        report_generator.generate_report()
        #rt = RepeatedTimer(report_interval, report_generator.generate_report)
        #self.report_thread_list.append(rt)

    def kill_report_threads(self):
        for rt in self.report_thread_list:
            print ('killing report thread')
            rt.stop()

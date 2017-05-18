"""
Generate PDF reports from data included in several Pandas DataFrames
From pbpython.com
"""
from __future__ import print_function

from safir_notification_service.notification.email_notifier import EmailNotifier

from safir_notification_service.openstack.ceillometer.ceilometer import CeilometerClient
from safir_notification_service.openstack.keystone.keystone import KeystoneClient
from safir_notification_service.openstack.nova.nova import NovaClient

from safir_notification_service.utils import utils
from safir_notification_service.utils import metering as metering_utils
from safir_notification_service.utils.opts import ConfigOpts

import datetime
import os
import json
from json2html import *
import time
from weasyprint import HTML

PATH = os.path.dirname(os.path.abspath(__file__))
REPORT_CSS = os.path.join(PATH, '../templates/css/style.css')


class ReportGenerator:

    def __init__(self, email_addr):
        self.configOpts = ConfigOpts()

        self.email_addr = email_addr

        self.smtp_server = self.configOpts.get_opt('email',
                                                   'smtp_server')
        self.smtp_port = self.configOpts.get_opt('email',
                                                 'smtp_port')
        self.login_addr = self.configOpts.get_opt('email',
                                                  'login_addr')
        self.password = self.configOpts.get_opt('email',
                                                'password')

        self.admin_monitor_panel_url = self.configOpts.get_opt('openstack_monitor_panel',
                                                               'admin_monitor_panel_url')

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

        self.keystone_client = KeystoneClient(auth_username,
                                              auth_password,
                                              auth_url,
                                              auth_project_name,
                                              user_domain_name,
                                              project_domain_name)

    def generate_report(self):

        filename = './report_cache/B3LAB_CloudReport_' + time.strftime("%Y%m%d-%H%M%S") + '.pdf'

        print ('Generating report')

        data = {'title': 'B3LAB Safir Cloud Platform Daily Usage Statistics',
                'usage_statistics': []}
        #meters = {'cpu_util': 'CPU Usage'}
        meters = {'cpu_util': 'CPU Usage',
                  'memory_util': 'Memory Usage',
                  'disk_util': 'Disk Usage',
                  'network.incoming.bytes.rate': 'Incoming Network Bandwidth',
                  'network.outgoing.bytes.rate': 'Outgoing Network Bandwidth'}

        for meter,title in meters.items():
            table = self.get_meterings(meter)
            data['usage_statistics'].append([title, table])

        html_out = utils.render_template('report.html', data)
        HTML(string=html_out).write_pdf(filename, stylesheets=[REPORT_CSS])

        self.send_email(self.email_addr, filename)

    def get_meterings(self, meter):

        meter_name = meter.replace(".", "_")
        date_from = datetime.datetime.now() - datetime.timedelta(days = 1)
        date_to = datetime.datetime.now()
        stats_attr = 'avg'
        group_by = 'project'

        if group_by == 'project':
            query = metering_utils.ProjectAggregatesQuery(keystone_client=self.keystone_client,
                                                          date_from=date_from,
                                                          date_to=date_to)
        else:
            query = metering_utils.MeterQuery(keystone_client=self.keystone_client,
                                              date_from=date_from,
                                              date_to=date_to)

        resources, unit = query.query(self.ceilometer_client, meter)
        series = metering_utils.series_for_meter(resources,
                                                 group_by, meter,
                                                 meter_name, stats_attr, unit)
        meterings = {}
        for s in series:
            meterings[s['name']] = OrderedDict()
            meterings[s['name']]['Metric'] = s['meter']
            meterings[s['name']]['Usage Average'] = s['data'][0]['y']
            meterings[s['name']]['Unit'] = s['unit']

        table = json2html.convert(json = json.dumps(meterings), table_attributes="class=\"dataframe\"")
        return table


    def send_email(self,
                   email,
                   filename):

        email_notifier = EmailNotifier(self.smtp_server, self.smtp_port,
                                       self.login_addr, self.password)

        subject, text, html = self.message_template(
                                      self.admin_monitor_panel_url,
                                      email)

        email_notifier.send_mail(email,
                                 subject,
                                 text, html, [filename])
        print (subject + ' mail sent to ' + email)

    @staticmethod
    def message_template(admin_monitor_panel_url,
                         email):

        filename = 'report_mail.html'

        data = {
            'admin_monitor_panel_url': admin_monitor_panel_url,
            'email': email
        }

        html = utils.render_template(filename, data)

        subject = 'Safir Cloud Platform System Usage Report'
        text = 'Dear Safir Cloud Platform Administrator! \
                \n\n \
                The current usage statistics of Safir Cloud Platform \
                is attached to this mail.\
                \n\n \
                You can visit Safir Admin Monitor panel \
                to see the usage details. \
                \n\n \
                Sincerely,\
                \n \
                B3LAB team'

        return subject, text, html

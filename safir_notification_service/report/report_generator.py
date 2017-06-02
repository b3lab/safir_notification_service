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

bps_to_mbps = 0.000001


class ReportGenerator:

    def __init__(self, email_addr, openstack_config, panel_config):
        self.openstack_config = openstack_config
        self.panel_config = panel_config
        self.email_addr = email_addr
        self.ceilometer_client = None
        self.nova_client = None
        self.keystone_client = None

        self.connect()

    def connect(self):
        config_opts = ConfigOpts()

        auth_username = config_opts.get_opt('openstack_connection',
                                                 'auth_username')
        auth_password = config_opts.get_opt('openstack_connection',
                                                 'auth_password')
        auth_url = config_opts.get_opt('openstack_connection',
                                            'auth_url')
        auth_project_name = config_opts.get_opt('openstack_connection',
                                                     'auth_project_name')
        user_domain_name = config_opts.get_opt('openstack_connection',
                                                    'user_domain_name')
        project_domain_name = config_opts.get_opt('openstack_connection',
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

        filename = os.path.join(PATH,
                                '../report_cache/B3LAB_CloudReport_' +
                                time.strftime("%Y%m%d-%H%M%S") + '.pdf')

        print ('Generating report')

        data = {'title': 'B3LAB Safir Cloud Platform Daily Usage Statistics',
                'usage_statistics': [],
                'compute_host_statistics': []}

        meters = {'cpu_util': 'Projects\' CPU Usage',
                  'memory_util': 'Projects\' Memory Usage',
                  'disk_util': 'Projects\' Disk Usage',
                  'network.incoming.bytes.rate':
                      'Projects\' Incoming Network Bandwidth',
                  'network.outgoing.bytes.rate':
                      'Projects\' Outgoing Network Bandwidth'}

        hardware_meters = {'hardware.cpu.util': 'Compute Hosts\' CPU Usage',
                           'hardware.memory.util': 'Compute Hosts\' RAM Usage',
                           'hardware.disk.util': 'Compute Hosts\' Disk Usage',
                           'hardware.network.incoming.bytes.rate':
                               'Compute Hosts\' Incoming Network Bandwidth',
                           'hardware.network.outgoing.bytes.rate':
                               'Compute Hosts\' Outgoing Network Bandwidth'}

        for meter, title in meters.items():
            table = self.get_meterings(meter, 'project')
            data['usage_statistics'].append([title, table])

        for hardware_meter, title in hardware_meters.items():
            table = self.get_meterings(hardware_meter, 'host')
            data['compute_host_statistics'].append([title, table])

        html_out = utils.render_template('report.html', data)
        HTML(string=html_out).write_pdf(filename, stylesheets=[REPORT_CSS])

        self.send_email(self.email_addr, filename)

    def get_meterings(self, meter, group_by):

        meter_name = meter.replace(".", "_")
        date_from = datetime.datetime.now() - datetime.timedelta(days=1)
        date_to = datetime.datetime.now()
        stats_attr = 'avg'

        if group_by == 'project':
            query = metering_utils.ProjectAggregatesQuery(keystone_client=self.keystone_client,
                                                          date_from=date_from,
                                                          date_to=date_to)
        else:
            query = metering_utils.HostAggregatesQuery(nova_client=self.nova_client,
                                                       date_from=date_from,
                                                       date_to=date_to)

        resources, unit = query.query(self.ceilometer_client, meter)
        series = metering_utils.series_for_meter(resources,
                                                 group_by, meter,
                                                 meter_name, stats_attr, unit)
        meterings = []
        for s in series:
            ave = None
            unit = None
            if 'bytes.rate' in s['meter']:
                ave = "{0:.2f}".format(
                        float(s['data'][0]['y']) * 8.0 * bps_to_mbps)
                unit = 'MB/s'
            else:
                ave = "{0:.2f}".format(s['data'][0]['y'])
                unit = s['unit']

            meterings.append({
                'Resource': s['name'],
                'Metric': s['meter'],
                'Usage Average': ave,
                'Unit': unit
            })

        table = json2html.convert(json=json.dumps(meterings),
                                  table_attributes="class=\"dataframe\"")

        return table

    def send_email(self,
                   email,
                   filename):

        config_opts = ConfigOpts()

        smtp_server = config_opts.get_opt('email',
                                          'smtp_server')
        smtp_port = config_opts.get_opt('email',
                                        'smtp_port')
        login_addr = config_opts.get_opt('email',
                                         'login_addr')
        password = config_opts.get_opt('email',
                                       'password')

        admin_monitor_panel_url = config_opts.get_opt(self.panel_config,
                                                      'admin_monitor_panel_url')

        email_notifier = EmailNotifier(smtp_server, smtp_port,
                                       login_addr, password)

        subject, text, html = self.message_template(
                                      admin_monitor_panel_url,
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

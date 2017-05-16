"""
Generate PDF reports from data included in several Pandas DataFrames
From pbpython.com
"""
from __future__ import print_function

from safir_alarm_service.notification.email_notifier import EmailNotifier

from safir_alarm_service.openstack.ceillometer.ceilometer import CeilometerClient
from safir_alarm_service.openstack.keystone.keystone import KeystoneClient
from safir_alarm_service.openstack.nova.nova import NovaClient

from safir_alarm_service.utils import utils
from safir_alarm_service.utils import metering as metering_utils
from safir_alarm_service.utils.opts import ConfigOpts

import os
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
        self.get_meterings('cpu_util')

    def generate_report(self):

        filename = './report_cache/B3LAB_CloudReport_' + time.strftime("%Y%m%d-%H%M%S") + '.pdf'

        print ('Generating report')
        # We can specify any directory for the loader but for this example, use current directory
        template_vars = {'Manager_Detail': [[u'Debra Henley', u'<table border="1" class="dataframe">\n  <thead>\n    <tr>\n      <th></th>\n      <th></th>\n      <th colspan="2" halign="left">sum</th>\n      <th colspan="2" halign="left">mean</th>\n    </tr>\n    <tr>\n      <th></th>\n      <th></th>\n      <th>Price</th>\n      <th>Quantity</th>\n      <th>Price</th>\n      <th>Quantity</th>\n    </tr>\n    <tr>\n      <th>Rep</th>\n      <th>Product</th>\n      <th></th>\n      <th></th>\n      <th></th>\n      <th></th>\n    </tr>\n  </thead>\n  <tbody>\n    <tr>\n      <th rowspan="3" valign="top">Craig Booker</th>\n      <th>CPU</th>\n      <td>65000</td>\n      <td>2</td>\n      <td>32500</td>\n      <td>1</td>\n    </tr>\n    <tr>\n      <th>Maintenance</th>\n      <td>5000</td>\n      <td>2</td>\n      <td>5000</td>\n      <td>2</td>\n    </tr>\n    <tr>\n      <th>Software</th>\n      <td>10000</td>\n      <td>1</td>\n      <td>10000</td>\n      <td>1</td>\n    </tr>\n    <tr>\n      <th>Daniel Hilton</th>\n      <th>CPU</th>\n      <td>65000</td>\n      <td>2</td>\n      <td>65000</td>\n      <td>2</td>\n    </tr>\n  </tbody>\n</table>']], 'Software': [1.0, 10000.0], 'CPU': [1.3333333333333333, 43333.333333333336], 'national_pivot_table': u'<table border="1" class="dataframe">\n  <thead>\n    <tr>\n      <th></th>\n      <th></th>\n      <th></th>\n      <th colspan="2" halign="left">sum</th>\n      <th colspan="2" halign="left">mean</th>\n    </tr>\n    <tr>\n      <th></th>\n      <th></th>\n      <th></th>\n      <th>Price</th>\n      <th>Quantity</th>\n      <th>Price</th>\n      <th>Quantity</th>\n    </tr>\n    <tr>\n      <th>Manager</th>\n      <th>Rep</th>\n      <th>Product</th>\n      <th></th>\n      <th></th>\n      <th></th>\n      <th></th>\n    </tr>\n  </thead>\n  <tbody>\n    <tr>\n      <th rowspan="4" valign="top">Debra Henley</th>\n      <th rowspan="3" valign="top">Craig Booker</th>\n      <th>CPU</th>\n      <td>65000</td>\n      <td>2</td>\n      <td>32500</td>\n      <td>1</td>\n    </tr>\n    <tr>\n      <th>Maintenance</th>\n      <td>5000</td>\n      <td>2</td>\n      <td>5000</td>\n      <td>2</td>\n    </tr>\n    <tr>\n      <th>Software</th>\n      <td>10000</td>\n      <td>1</td>\n      <td>10000</td>\n      <td>1</td>\n    </tr>\n    <tr>\n      <th>Daniel Hilton</th>\n      <th>CPU</th>\n      <td>65000</td>\n      <td>2</td>\n      <td>65000</td>\n      <td>2</td>\n    </tr>\n  </tbody>\n</table>', 'title': 'National Sales Funnel Report'}
        # Render our file and create the PDF using our css style file
        html_out = utils.render_template('report.html', template_vars)
        HTML(string=html_out).write_pdf(filename, stylesheets=[REPORT_CSS])

        self.send_email(self.email_addr, filename)

    def get_meterings(self, meter):

        meter_name = meter.replace(".", "_")
        date_from = '2017-05-15'
        date_to = '2017-05-16'
        stats_attr = 'avg'
        group_by = 'project'

        try:
            date_from, date_to = metering_utils.calc_date_args(date_from,
                                                               date_to)
        except Exception as ex:
            print ('Dates cannot be recognized.')

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
        print (series)


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

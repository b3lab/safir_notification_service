"""
Generate PDF reports from data included in several Pandas DataFrames
From pbpython.com
"""
from __future__ import print_function

from safir_alarm_service.notification.email_notifier import EmailNotifier
from safir_alarm_service.utils import utils
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

    def generate_report(self):

        filename = './report_cache/B3LAB_CloudReport_' + time.strftime("%Y%m%d-%H%M%S") + '.pdf'

        print ('Generating report')
        # We can specify any directory for the loader but for this example, use current directory
        template_vars = {'Manager_Detail': [[u'Debra Henley', u'<table border="1" class="dataframe">\n  <thead>\n    <tr>\n      <th></th>\n      <th></th>\n      <th colspan="2" halign="left">sum</th>\n      <th colspan="2" halign="left">mean</th>\n    </tr>\n    <tr>\n      <th></th>\n      <th></th>\n      <th>Price</th>\n      <th>Quantity</th>\n      <th>Price</th>\n      <th>Quantity</th>\n    </tr>\n    <tr>\n      <th>Rep</th>\n      <th>Product</th>\n      <th></th>\n      <th></th>\n      <th></th>\n      <th></th>\n    </tr>\n  </thead>\n  <tbody>\n    <tr>\n      <th rowspan="3" valign="top">Craig Booker</th>\n      <th>CPU</th>\n      <td>65000</td>\n      <td>2</td>\n      <td>32500</td>\n      <td>1</td>\n    </tr>\n    <tr>\n      <th>Maintenance</th>\n      <td>5000</td>\n      <td>2</td>\n      <td>5000</td>\n      <td>2</td>\n    </tr>\n    <tr>\n      <th>Software</th>\n      <td>10000</td>\n      <td>1</td>\n      <td>10000</td>\n      <td>1</td>\n    </tr>\n    <tr>\n      <th>Daniel Hilton</th>\n      <th>CPU</th>\n      <td>65000</td>\n      <td>2</td>\n      <td>65000</td>\n      <td>2</td>\n    </tr>\n  </tbody>\n</table>']], 'Software': [1.0, 10000.0], 'CPU': [1.3333333333333333, 43333.333333333336], 'national_pivot_table': u'<table border="1" class="dataframe">\n  <thead>\n    <tr>\n      <th></th>\n      <th></th>\n      <th></th>\n      <th colspan="2" halign="left">sum</th>\n      <th colspan="2" halign="left">mean</th>\n    </tr>\n    <tr>\n      <th></th>\n      <th></th>\n      <th></th>\n      <th>Price</th>\n      <th>Quantity</th>\n      <th>Price</th>\n      <th>Quantity</th>\n    </tr>\n    <tr>\n      <th>Manager</th>\n      <th>Rep</th>\n      <th>Product</th>\n      <th></th>\n      <th></th>\n      <th></th>\n      <th></th>\n    </tr>\n  </thead>\n  <tbody>\n    <tr>\n      <th rowspan="4" valign="top">Debra Henley</th>\n      <th rowspan="3" valign="top">Craig Booker</th>\n      <th>CPU</th>\n      <td>65000</td>\n      <td>2</td>\n      <td>32500</td>\n      <td>1</td>\n    </tr>\n    <tr>\n      <th>Maintenance</th>\n      <td>5000</td>\n      <td>2</td>\n      <td>5000</td>\n      <td>2</td>\n    </tr>\n    <tr>\n      <th>Software</th>\n      <td>10000</td>\n      <td>1</td>\n      <td>10000</td>\n      <td>1</td>\n    </tr>\n    <tr>\n      <th>Daniel Hilton</th>\n      <th>CPU</th>\n      <td>65000</td>\n      <td>2</td>\n      <td>65000</td>\n      <td>2</td>\n    </tr>\n  </tbody>\n</table>', 'title': 'National Sales Funnel Report'}
        # Render our file and create the PDF using our css style file
        html_out = utils.render_template('report.html', template_vars)
        HTML(string=html_out).write_pdf(filename, stylesheets=[REPORT_CSS])

        self.send_email(self.email_addr, filename)

    def send_email(self,
                   email,
                   filename):

        email_notifier = EmailNotifier(self.smtp_server, self.smtp_port,
                                       self.login_addr, self.password)

        text = 'hello'
        html = """\
<html>
  <head></head>
  <body>
    <p>Hello!<br>
       hello
    </p>
  </body>
</html>
"""
        email_notifier.send_mail(email,
                                 'Report',
                                 text, html, [filename])
        print ('email sent')
# Copyright 2017 TUBITAK, BILGEM, B3LAB
#
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

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import basename
import smtplib


class EmailNotifier:

    def __init__(self, smtp_server, smtp_port,
                 login_addr, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.login_addr = login_addr
        self.password = password
        self.mail_server = None

    def connect(self):

        self.mail_server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        # identify ourselves to smtp client
        self.mail_server.ehlo()
        # secure our email with tls encryption
        self.mail_server.starttls()
        # re-identify ourselves as an encrypted connection
        self.mail_server.ehlo()
        self.mail_server.login(self.login_addr, self.password)

    def disconnect(self):

        self.mail_server.quit()

    def send_mail(self, to_addr, subject, text, html, files=None):

        try:
            self.connect()
            msg = MIMEMultipart('alternative')
            msg['From'] = self.login_addr
            msg['To'] = to_addr
            msg['Subject'] = subject

            text_part = MIMEText(text, 'plain', 'utf-8')
            html_part = MIMEText(html, 'html', 'utf-8')

            msg.attach(text_part)
            msg.attach(html_part)

            for f in files or []:
                with open(f, "rb") as fil:
                    part = MIMEApplication(
                        fil.read(),
                        Name=basename(f)
                    )
                    part['Content-Disposition'] = \
                        'attachment; filename="%s"' % basename(f)
                    msg.attach(part)

            self.mail_server.sendmail(self.login_addr,
                                      to_addr,
                                      msg.as_string())
        except Exception as ex:
            print ('ERROR: Email notification not sent. ' + ex.message)
        finally:
            self.disconnect()

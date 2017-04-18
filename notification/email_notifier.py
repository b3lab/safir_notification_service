import smtplib
from email_notifier.MIMEMultipart import MIMEMultipart
from email_notifier.MIMEText import MIMEText

from utils.opts import ConfigOpts


class EmailNotifier:

    def __init__(self):
        configOpts = ConfigOpts()
        self.smtp_server = configOpts.get_opt('email',
                                              'smtp_server')
        self.smtp_port = configOpts.get_opt('email',
                                            'smtp_port')
        self.login_addr = configOpts.get_opt('email',
                                             'login_addr')
        self.password = configOpts.get_opt('email',
                                           'password')

    def connect(self):

        self.mailserver = smtplib.SMTP(self.smtp_server, self.smtp_port)
        # identify ourselves to smtp client
        self.mailserver.ehlo()
        # secure our email with tls encryption
        self.mailserver.starttls()
        # re-identify ourselves as an encrypted connection
        self.mailserver.ehlo()
        self.mailserver.login(self.login_addr, self.password)

    def disconnect(self):

        self.mailserver.quit()

    def send_mail(self, to_addr, subject, message):

        msg = MIMEMultipart()
        msg['From'] = self.login_addr
        msg['To'] = to_addr
        msg['Subject'] = subject
        msg.attach(MIMEText(message))

        self.connect()
        self.mailserver.sendmail(self.login_addr, to_addr, msg.as_string())
        self.disconnect()

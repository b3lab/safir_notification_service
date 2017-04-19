import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailNotifier:

    def __init__(self, smtp_server, smtp_port,
                 login_addr, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.login_addr = login_addr
        self.password = password

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

    def send_mail(self, to_addr, subject, text, html):

        msg = MIMEMultipart('alternative')
        msg['From'] = self.login_addr
        msg['To'] = to_addr
        msg['Subject'] = subject

        textpart = MIMEText(text)
        htmlpart = MIMEText(html, 'html')

        msg.attach(textpart)
        msg.attach(htmlpart)

        self.connect()
        self.mailserver.sendmail(self.login_addr, to_addr, msg.as_string())
        self.disconnect()

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText


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

    def send_mail(self, to_addr, subject, message):

        msg = MIMEMultipart()
        msg['From'] = self.login_addr
        msg['To'] = to_addr
        msg['Subject'] = subject
        msg.attach(MIMEText(message))

        self.connect()
        self.mailserver.sendmail(self.login_addr, to_addr, msg.as_string())
        self.disconnect()

    def message_template(self, username, instance_name, alarm_desc):

        message = '<html>\
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

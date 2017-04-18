#!env python
from __future__ import print_function
from flask import Flask
from flask import request
import json

from keystoneauth1 import loading
from keystoneauth1 import session
import ceilometerclient.client

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

import sys

port = 8080
# port = int(sys.argv[1])

Flask.get = lambda self, path: self.route(path, methods=['get'])

app = Flask(__name__)

@app.get('/')
def get_root():
    output = '' 
    try: 
        output += "<p>Sending email</p>"
        send_mail()
        output += "<p>Email sent..</p>"
    except:
        print("ERR: Failed!", file=sys.stderr)
    
    return output;

@app.route('/alarm')
def alarm():
    print ('Selam dunya')
    return 'Hello, World'

@app.route('/alarmi', methods=['GET', 'POST'])
def alarmi():
    if request.method == 'POST':
        print ('post alarm')
        print (request)
        print (request.data)
        data = json.loads(request.data)
        print (request.args)
        print (request.values)
        get_project(data['alarm_id'])
    else:
        print ('get alarm')
    return 'Alarm data received'

def get_project(alarm_id):
    loader = loading.get_plugin_loader('password')
    auth = loader.load_from_options(auth_url='http://192.168.122.146:35357',
                                    username='admin',
                                    password='1234qweR',
                                    project_name='admin',
                                    user_domain_name='default',
                                    project_domain_name='default')
    s = session.Session(auth=auth)
    ceilometer_client = ceilometerclient.client.get_client('2', session=s)
    print (ceilometer_client.alarms.get(alarm_id))

def send_mail():

    msg = MIMEMultipart()
    msg['From'] = 'b3lab.iletisim@tubitak.gov.tr'
    msg['To'] = 'celik.esra@tubitak.gov.tr'
    msg['Subject'] = 'simple email in python'
    message = 'here is the email'
    msg.attach(MIMEText(message))

    mailserver = smtplib.SMTP('mta.tubitak.gov.tr',587)
    # identify ourselves to smtp client
    mailserver.ehlo()
    # secure our email with tls encryption
    mailserver.starttls()
    # re-identify ourselves as an encrypted connection
    mailserver.ehlo()
    mailserver.login('b3lab.iletisim@tubitak.gov.tr', 'b3123qwe')

    mailserver.sendmail('b3lab.iletisim@tubitak.gov.tr','celik.esra@tubitak.gov.tr',msg.as_string())

    mailserver.quit()


if __name__ == "__main__":
    app.run(host='192.168.122.1', port=port)

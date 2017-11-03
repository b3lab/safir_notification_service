################################################
SafirNotification installation and configuration
################################################

There is no release of SafirNotification as of now, the installation can be done from the git repository.

Install from source
===================

Install the services
--------------------

Install Safir Email Notifier library::

    git clone https://github.com/b3lab/safir_email_notifier.git
    cd safir_email_notifier
    python setup.py install

Retrieve and install Safir Notification Service::

    git clone https://github.com/b3lab/safir_notification_service.git
    cd safir_notification_service
    python setup.py install

This procedure installs the ``safirnotification`` python library and the
``safirnotification`` executable

Install configuration files::

    mkdir /etc/safirnotification
    cp etc/safirnotification/safirnotification.conf /etc/safirnotification/safirnotification.conf
    cp etc/safirnotification.service /etc/systemd/system/safirnotification.service

Create the log directory::

    mkdir /var/log/safirnotification/

Configuration
-------------

Make sure you have the clouds.yaml file including the credentials to connect to your OpenStack platform
inside /etc/openstack directory.

Example clouds.yaml
===================

.. sourcecode:: console

  clouds:
    cloud-admin:
      auth:
        auth_url: http://<controller_hostname>:5000/v3
        password: <password>
        project_name: admin
        username: admin
        project_domain_name: default
        user_domain_name: default
      domain_name: Default
      identity_api_version: '3'
      region_name: RegionOne

Configure safirnotification.conf for your environment

.. code-block:: ini

    [DEFAULT]

    # clouds.yaml file should either be in the current directory or
    # ~/.config/openstack directory or /etc/openstack directory.
    # openstack_config_name is the config name used in the clouds.yaml file
    openstack_config_name = cloud-admin

    # This URL will be send by email as a shortcut to
    # Safir Monitor Panel
    monitor_panel_url = http://controller/horizon/project/monitor

    [api]

    # API host URL
    host = controller

    # API port
    port = 9765

    [email]

    # E-mail server configurations to be used for notification emails

    # SMTP Server
    smtp_server = smtp.a.com

    # SMTP Port
    smtp_port = 587

    # E-mail account username
    login_addr = a@a.com

    # E-mail account password
    password = secret


Configure Horizon Safir Monitor Dashboard options to use the Safir Notification Service
Configure and add the following lines to local_settings.py file of OpenStack Dashboard::

    AODH_ALARM_ACTIONS=['http://controller:9765/alarm']
    AODH_OK_ACTIONS=['http://controller:9765/alarm']


Start service
-------------

Start safirnotification service::

    systemctl start safirnotification.service


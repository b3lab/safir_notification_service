################################################
SafirNotification installation and configuration
################################################

There is no release of SafirNotification as of now, the installation can be done from the git repository.

Install from source
===================

Install the services
--------------------

Retrieve and install safirnotification::

    git clone https://github.com/b3lab/safir_notification_service.git
    cd safir_notification_service
    python setup.py install

This procedure installs the ``safirnotification`` python library and the
following executable:

* ``safirnotification-api``: API service

Install sample configuration files::

    mkdir /etc/safirnotification
    tox -e genconfig
    cp etc/safirnotification/safirnotification.conf.sample /etc/safirnotification/safirnotification.conf
    cp etc/safirnotification/api_paste.ini /etc/safirnotification

Create the log directory::

    mkdir /var/log/safirnotification/


Configure safirnotification
===========================

Edit :file:`/etc/safirnotification/safirnotification.conf` to configure safirnotification.

For keystone (identity) API v3
------------------------------

The following shows the basic configuration items:

.. code-block:: ini

    [DEFAULT]
    debug = True

    [api]
    host_ip = 127.0.0.1
    port = 9765

    [cloud]
    cloud_name = cloud-admin

Setup Keystone
==============

safirnotification uses the clouds.yaml file in one of the following directories to connect
the OpenStack services::

    current directory or
    ~/.config/openstack directory or
    /etc/openstack directory.


Start safirnotification
=======================

Start the API and processing services::

    safirnotification-api --config-file /etc/safirnotification/safirnotification.conf


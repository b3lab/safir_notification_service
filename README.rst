==============
SafirNotification
==============
|doc-status|

.. image:: doc/source/images/safirnotification-logo.png
    :alt: safirnotification
    :align: center


Billing as a Service component
++++++++++++++++++++++++++++++

Goal
----

SafirNotification a billing service developed for OpenStack cloud platforms.


Status
------

SafirNotification has been successfully deployed in production on different OpenStack
systems.

You can find the latest documentation on readthedocs_.


Additional components
---------------------

We're providing an OpenStack dashboard (Horizon) integration, you can find the
files in the safirnotification-dashboard_ repository.

A CLI is available too in the python-safirnotificationclient_ repository.


Trying it
---------

SafirNotification can be deployed with devstack, more information can be found in the
`devstack section`_ of the documentation.


Deploying it in production
--------------------------

SafirNotification can be deployed in production on OpenStack Ocata environments, for
more information check the `installation section`_ of the documentation. Due to
oslo libraires new namespace backward compatibility is not possible. If you
want to install it on an older system, use a virtualenv.

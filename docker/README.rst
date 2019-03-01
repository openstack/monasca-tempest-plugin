===============================================
Docker image for Monasca Monasca Temptest tests
===============================================
This image could be used for running Tempest tests on Monasca installed in any
way. After providing proper environment variables container could be started
and will run tests based on what endpoints it will find in configured Keystone.
Supported endpoints are ``monitoring`` and ``logs`` (``Service Type`` in
``openstack endpoint list`` output).


Building monasca-base image
===========================
See https://github.com/openstack/monasca-common/tree/master/docker/README.rst


Building Docker image
=====================

Example:
  $ ./build_image.sh <repository_version> <upper_constrains_branch> <common_version>

Everything after ``./build_image.sh`` is optional and by default configured
to get versions from ``Dockerfile``. ``./build_image.sh`` also contain more
detailed build description.


How to start
~~~~~~~~~~~~

When using running Monasca in Docker you can connect this image to the network
where Monasca is accessible and run all tests.
Find network on machine with Monasca with ``docker network ls``.
For example you can see similar information to:
``e20533f6112c   monasca-docker_default   bridge   local``

Using this network run all tempest tests with following command:

``docker run -it --rm --network=monasca-docker_default monasca/tempest:master``

It's important to configure all necessary connection environment variables.
They are listed in the next two sections.

Example command to run tempest tests with custom variables::

``docker run -it --rm --network=monasca-docker_default --env-file=tempest_con.env monasca/tempest:master``

In this example you configure all environment variables in ``tempest_con.env``
file::

    MONASCA_URI=172.17.0.1:8070
    KEYSTONE_IDENTITY_URI=http://172.17.0.1:35357
    USE_DYNAMIC_CREDS=True
    KEYSTONE_ADMIN_USER=mini-mon
    KEYSTONE_ADMIN_PASSWORD=password
    KEYSTONE_ADMIN_PROJECT=mini-mon
    KEYSTONE_ADMIN_DOMAIN=Default
    OS_AUTH_URL=http://172.17.0.1:35357/v3
    OS_USERNAME=mini-mon
    OS_PASSWORD=password
    OS_PROJECT_NAME=mini-mon
    OS_DOMAIN_NAME=Default


Environment variables
~~~~~~~~~~~~~~~~~~~~~
========================= ============================== ==========================================
Variable                  Default                        Description
========================= ============================== ==========================================
USE_DYNAMIC_CREDS         True                           Create dynamic credentials for tests
KEYSTONE_ADMIN_USER       mini-mon                       OpenStack administrator user name
KEYSTONE_ADMIN_PASSWORD   password                       OpenStack administrator user password
KEYSTONE_ADMIN_PROJECT    mini-mon                       OpenStack administrator tenant name
KEYSTONE_ADMIN_DOMAIN     Default                        OpenStack administrator domain
OS_AUTH_URL               http://keystone:35357/v3       Versioned Keystone URL
OS_USERNAME               mini-mon                       Keystone user name
OS_PASSWORD               password                       Keystone user password
OS_PROJECT_NAME           mini-mon                       Keystone user project name
OS_DOMAIN_NAME            Default                        Keystone user domain name
IDENTITY_URI              http://keystone:35357/v2.0/    Full URI of the Keystone, v2
IDENTITY_URI_V3           http://keystone:35357/v3/      Full URI of the Keystone, v3
LOG_LEVEL                 INFO                           Log level for root logging
STAY_ALIVE_ON_FAILURE     false                          If true, container runs 2 hours after service fail
========================= ============================== ==========================================


Wait scripts environment variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
========================= ============================== ==========================================
Variable                  Default                        Description
========================= ============================== ==========================================
MONASCA_URI               http://monasca:8070            The metric pipeline endpoint
KEYSTONE_IDENTITY_URI     http://keystone:35357          URI to Keystone admin endpoint
========================= ============================== ==========================================


Scripts
~~~~~~~
start.sh
  In this starting script provide all steps that lead to the proper service
  start. Including usage of wait scripts and templating of configuration
  files. You also could provide the ability to allow running container after
  service died for easier debugging.

health_check.py
  This file will be used for checking the status of the application.


Links
~~~~~
https://docs.openstack.org/monasca-api/latest/

https://github.com/openstack/monasca-api/blob/master/README.rst

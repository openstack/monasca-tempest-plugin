ARG DOCKER_IMAGE=monasca/tempest-tests
ARG APP_REPO=https://review.opendev.org/openstack/monasca-tempest-plugin

# Branch, tag or git hash to build from.
ARG REPO_VERSION=master
ARG CONSTRAINTS_BRANCH=master

# Extra Python3 dependencies.
ARG EXTRA_DEPS="python-openstackclient python-monascaclient"

# Always start from `monasca-base` image and use specific tag of it.
ARG BASE_TAG=master
FROM monasca/base:$BASE_TAG

# Environment variables used for our service or wait scripts.
ENV \
    KEYSTONE_IDENTITY_URI=http://keystone:35357 \
    USE_DYNAMIC_CREDS=True \
    KEYSTONE_ADMIN_USER=mini-mon \
    KEYSTONE_ADMIN_PASSWORD=password \
    KEYSTONE_ADMIN_PROJECT=mini-mon \
    KEYSTONE_ADMIN_DOMAIN=Default \
    OS_AUTH_URL=http://keystone:35357/v3 \
    OS_USERNAME=mini-mon \
    OS_PASSWORD=password \
    OS_TENANT_NAME=mini-mon \
    OS_DOMAIN_NAME=Default \
    MONASCA_WAIT_FOR_API=true \
    MONASCA_API_WAIT_RETRIES=24 \
    MONASCA_API_WAIT_INTERVAL=5 \
    STAY_ALIVE_ON_FAILURE=false

# Copy all neccessary files to proper locations.
COPY tempest.conf.j2 /etc/tempest/

WORKDIR /tempest

# Run here all additionals steps your service need post installation.
# Stay with only one `RUN` and use `&& \` for next steps to don't create
# unnecessary image layers. Clean at the end to conserve space.
#RUN \
#    echo "Some steps to do after main installation." && \
#    echo "Hello when building."

# Implement start script in `start.sh` file.
CMD ["/start.sh"]

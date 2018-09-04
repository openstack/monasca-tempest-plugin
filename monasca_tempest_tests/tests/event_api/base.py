# Copyright 2019 FUJITSU LIMITED
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

from datetime import datetime
import json
from os import path
import pytz
import random
import string

from oslo_config import cfg
from tempest.common import credentials_factory as cred_factory
from tempest import test

from monasca_tempest_tests.clients import event_api as clients

CONF = cfg.CONF


def get_simple_event():
    json_file_path = path.join(path.dirname(__file__),
                               'req_simple_event.json')
    with open(json_file_path, 'r') as f:
        return json.loads(f.read())


def create_header(header={}, content_type='application/json'):
    header.update({'Content-Type': content_type,
                   'kbn-version': CONF.monitoring.kibana_version})
    return header


def generate_simple_event_type_string():
    letters = string.ascii_lowercase
    random_string = ''.join((random.choice(letters) for _ in range(15)))
    return '{}.{}'.format(random_string[:7], random_string[8:])


def generate_simple_event(event_type=None, timestamp=None, events=None, num_of_events=1):
    if event_type is None:
        event_type = generate_simple_event_type_string()
    if events is None:
        events = \
            [{
                'dimensions': {
                    'service': 'compute',
                    'topic': 'notification.sample',
                    'hostname': 'mars'},
                'project_id': '6f70656e737461636b20342065766572',
                'event': {
                    'event_type': event_type,
                    'payload': {
                        'nova_object.data': {
                            'architecture': 'x86_64',
                            'availability_zone': 'nova',
                            'created_at': '2012-10-29T13:42:11Z'}}}}] \
            * num_of_events
    if timestamp is None:
        timestamp = datetime.now(tz=pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ%z")
    return {'timestamp': timestamp,
            'events': events}


class BaseEventsTestCase(test.BaseTestCase):
    """Base test case class for all Event API tests."""

    @classmethod
    def skip_checks(cls):
        super(BaseEventsTestCase, cls).skip_checks()

    @classmethod
    def resource_setup(cls):
        super(BaseEventsTestCase, cls).resource_setup()
        auth_version = CONF.identity.auth_version
        cred_provider = cred_factory.get_credentials_provider(
            cls.__name__,
            identity_version=auth_version)
        credentials = cred_provider.get_creds_by_roles(
            ['admin']).credentials
        cls.os_primary = clients.Manager(credentials=credentials)

        cls.events_api_client = cls.os_primary.events_api_client
        cls.events_search_client = cls.os_primary.events_search_client

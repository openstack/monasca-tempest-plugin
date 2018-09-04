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

from tempest.lib.common.utils import test_utils
from tempest.lib import decorators
from tempest.lib import exceptions

from monasca_tempest_tests.tests.event_api import base

RETRY_COUNT = 15
RETRY_WAIT = 2


class BaseEventsTestCase(base.BaseEventsTestCase):

    def check_if_events_are_present_in_db(self, event_type):
        return len(self.events_search_client.search_event_by_event_type(event_type)) > 0

    def send_and_retrieve_events(self, events=None, header=None, events_number=1):
        if events is None:
            event_type = base.generate_simple_event_type_string()
            events = base.generate_simple_event(event_type, num_of_events=events_number)
        if header is None:
            header = base.create_header()
        response, _ = self.events_api_client.send_events(events, header)
        self.assertEqual(200, response.status)
        test_utils.call_until_true(self.check_if_events_are_present_in_db,
                                   RETRY_COUNT * RETRY_WAIT,
                                   RETRY_WAIT,
                                   event_type)
        response = self.events_search_client.search_event_by_event_type(event_type)

        self.assertEqual(events_number, len(response))

    @decorators.attr(type=['gate', 'smoke'])
    def test_single_event(self):
        self.send_and_retrieve_events()

    @decorators.attr(type='gate')
    def test_multiple_events(self):
        self.send_and_retrieve_events(events_number=5)

    @decorators.attr(type='gate')
    def test_missing_body(self):
        header = base.create_header()
        try:
            response, _ = self.events_api_client.send_events(None, header)
        except exceptions.UnprocessableEntity as exc:
            self.assertEqual(422, exc.resp.status)

    @decorators.attr(type='gate')
    def test_empty_event(self):
        header = base.create_header()
        body = base.generate_simple_event(events=[])
        try:
            response, _ = self.events_api_client.send_events(body, header)
        except exceptions.UnprocessableEntity as exc:
            self.assertEqual(422, exc.resp.status)

    def test_empty_content_type(self):
        body = base.generate_simple_event()
        try:
            response, _ = self.events_api_client.send_events(body, {})
        except exceptions.BadRequest as exc:
            self.assertEqual(400, exc.resp.status)

# Copyright 2015-2017 FUJITSU LIMITED
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

from tempest import config
from tempest.lib.common.utils import test_utils
from tempest.lib import decorators
from testtools import matchers

from monasca_tempest_tests.tests.log_api import base

CONF = config.CONF
_RETRY_COUNT = 15
_RETRY_WAIT = 2


class TestSingleLog(base.BaseLogsSearchTestCase):
    def _run_and_wait(self, key, data,
                      content_type='application/json',
                      headers=None, fields=None):

        headers = base._get_headers(headers, content_type)

        def wait():
            return self.logs_search_client.count_search_messages(key,
                                                                 headers) > 0

        self.assertEqual(0, self.logs_search_client.count_search_messages(key,
                         headers),
                         'Find log message in elasticsearch: {0}'.format(key))

        headers = base._get_headers(headers, content_type)
        data = base._get_data(data)

        client = self.logs_client
        response, _ = client.send_single_log(data, headers, fields)
        self.assertEqual(204, response.status)

        test_utils.call_until_true(wait, _RETRY_COUNT * _RETRY_WAIT,
                                   _RETRY_WAIT)
        response = self.logs_search_client.search_messages(key, headers)
        self.assertEqual(1, len(response))

        return response

    @decorators.attr(type=["gate", "smoke"])
    def test_small_message(self):
        self._run_and_wait(*base.generate_small_message())

    @decorators.attr(type="gate")
    def test_medium_message(self):
        self._run_and_wait(*base.generate_medium_message())

    @decorators.attr(type="gate")
    def test_big_message(self):
        self._run_and_wait(*base.generate_large_message())

    @decorators.attr(type="gate")
    def test_small_message_multiline(self):
        sid, message = base.generate_small_message()
        self._run_and_wait(sid, message.replace(' ', '\n'))

    @decorators.attr(type="gate")
    def test_medium_message_multiline(self):
        sid, message = base.generate_medium_message()
        self._run_and_wait(sid, message.replace(' ', '\n'))

    @decorators.attr(type="gate")
    def test_big_message_multiline(self):
        sid, message = base.generate_large_message()
        self._run_and_wait(sid, message.replace(' ', '\n'))

    @decorators.attr(type="gate")
    def test_send_cross_project(self):
        sid, message = base.generate_small_message()
        headers = {'X-Roles': 'admin, monitoring-delegate'}
        cross_tennant_id = '2106b2c8da0eecdb3df4ea84a0b5624b'
        fields = {'project_id': cross_tennant_id}
        response = self._run_and_wait(sid, message, headers=headers, fields=fields)
        log_msg = response[0]
        for key in CONF.monitoring.log_project_id_path:
            log_msg = log_msg.pop(key)
        self.assertThat(log_msg,
                        matchers.StartsWith(cross_tennant_id))

    # TODO(trebski) following test not passing - failed to retrieve
    # big message from elasticsearch

    # @decorators.attr(type='gate')
    # def test_should_truncate_big_message(self):
    #     message_size = base._get_message_size(0.9999)
    #     sid, message = base.generate_unique_message(size=message_size)
    #
    #     headers = base._get_headers(self.logs_clients.get_headers())
    #     response = self._run_and_wait(sid, message, headers=headers)
    #
    #     self.assertTrue(False, 'API should respond with 500')

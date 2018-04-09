# Copyright 2017 FUJITSU LIMITED
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

from monasca_common.tests.validation import test_metric_validation
from monasca_tempest_tests.tests.log_api import base

_RETRY_COUNT = 15
_RETRY_WAIT = 2
_UNICODE_CASES = test_metric_validation.UNICODE_MESSAGES


class TestUnicodeV3(base.BaseLogsTestCase):

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

    @decorators.attr(type="gate")
    def test_unicode_message(self):
        for m in _UNICODE_CASES:
            self._run_and_wait(*base.generate_small_message(m['input']), headers={
                'LA-Unicode-Case': m['case']
            })

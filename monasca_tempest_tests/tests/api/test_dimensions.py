# (C) Copyright 2016 Hewlett Packard Enterprise Development LP
# (C) Copyright 2017 SUSE LLC
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

import time

from six.moves.urllib.parse import urlencode

from tempest.lib.common.utils import data_utils
from tempest.lib import decorators
from tempest.lib import exceptions

from monasca_tempest_tests.tests.api import base
from monasca_tempest_tests.tests.api import constants
from monasca_tempest_tests.tests.api import helpers


class TestDimensions(base.BaseMonascaTest):

    @classmethod
    def resource_setup(cls):
        super(TestDimensions, cls).resource_setup()
        start_timestamp = int(round(time.time() * 1000))
        start_time_iso = helpers.timestamp_to_iso(start_timestamp)
        # NOTE (brtknr): use interval of a day because the tag based queries
        # appear to only support smallest granularity of a day, and disregard
        # time of day, which is fine for most use cases.
        day = 60 * 60 * 24 * 1000
        end_timestamp = start_timestamp + 10 * day
        end_time_iso = helpers.timestamp_to_iso(end_timestamp)

        metric_name1 = data_utils.rand_name()
        name1 = "name_1"
        name2 = "name_2"
        value1 = "value_1"
        value2 = "value_2"
        timestamp1 = start_timestamp - day
        timestamp2 = start_timestamp + day
        timestamp3 = start_timestamp + day + day
        timestamp4 = end_timestamp + day
        metric1 = helpers.create_metric(name=metric_name1,
                                        timestamp=timestamp1,
                                        dimensions={name1: value1,
                                                    name2: value2,
                                                    })
        cls.monasca_client.create_metrics(metric1)
        metric1 = helpers.create_metric(name=metric_name1,
                                        timestamp=timestamp2,
                                        dimensions={name1: value2})
        cls.monasca_client.create_metrics(metric1)

        metric_name2 = data_utils.rand_name()
        name3 = "name_3"
        value3 = "value_3"
        value4 = "value_4"
        metric2 = helpers.create_metric(name=metric_name2,
                                        timestamp=timestamp3,
                                        dimensions={name1: value3,
                                                    name3: value4,
                                                    })
        cls.monasca_client.create_metrics(metric2)

        metric_name3 = data_utils.rand_name()
        metric3 = helpers.create_metric(name=metric_name3,
                                        timestamp=timestamp4,
                                        dimensions={name2: value3})
        cls.monasca_client.create_metrics(metric3)

        cls._test_metric1 = metric1
        cls._test_metric2 = metric2
        cls._test_metric_names = {metric_name1, metric_name2, metric_name3}
        cls._dim_names_metric1 = [name1, name2]
        cls._dim_names_metric1_in_timerange = [name1]
        cls._dim_names_metric2 = [name1, name3]
        cls._dim_names_metric2_in_timerange = [name1, name3]
        cls._dim_names = sorted(set(cls._dim_names_metric1
                                    + cls._dim_names_metric2))
        cls._dim_names_in_timerange = sorted(set(
                                        cls._dim_names_metric1_in_timerange
                                        + cls._dim_names_metric2_in_timerange))
        cls._dim_name1 = name1
        cls._dim_name1_values_for_metric1 = [value1, value2]
        cls._dim_name1_values_for_metric1_in_timerange = [value2]
        cls._dim_name1_values = [value1, value2, value3]
        cls._dim_name1_values_in_timerange = [value2, value3]
        cls._start_time = start_time_iso
        cls._end_time = end_time_iso

        param = '?start_time=' + start_time_iso
        returned_name_set = set()
        for i in range(constants.MAX_RETRIES):
            resp, response_body = cls.monasca_client.list_metrics(
                param)
            elements = response_body['elements']
            metric_name1_count = 0
            for element in elements:
                returned_name_set.add(str(element['name']))
                if (str(element['name']) == metric_name1):
                    metric_name1_count += 1
            # Java version of influxdb never returns both metric1 in the list but Python does.
            if cls._test_metric_names.issubset(returned_name_set) \
                    and (metric_name1_count == 2 or i == constants.MAX_RETRIES - 1):
                return
            time.sleep(constants.RETRY_WAIT_SECS)

        assert False, 'Unable to initialize metrics'

    @classmethod
    def resource_cleanup(cls):
        super(TestDimensions, cls).resource_cleanup()

    def _test_list_dimension_values_without_metric_name(self, timerange):
        param = '?dimension_name=' + self._dim_name1
        if timerange:
            param += '&start_time=' + self._start_time
            param += '&end_time=' + self._end_time
        resp, response_body = self.monasca_client.list_dimension_values(param)
        self.assertEqual(200, resp.status)
        self.assertTrue({'links', 'elements'} == set(response_body))
        response_values_length = len(response_body['elements'])
        values = [str(response_body['elements'][i]['dimension_value'])
                  for i in range(response_values_length)]
        if timerange:
            self.assertEqual(values, self._dim_name1_values_in_timerange)
        else:
            self.assertEqual(values, self._dim_name1_values)

    @decorators.attr(type='gate')
    def test_list_dimension_values_without_metric_name(self):
        self._test_list_dimension_values_without_metric_name(timerange=False)

    @decorators.attr(type='gate')
    @decorators.attr(type='timerange')
    def test_list_dimension_values_without_metric_name_with_timerange(self):
        self._test_list_dimension_values_without_metric_name(timerange=True)

    def _test_list_dimension_values_with_metric_name(self, timerange):
        param = '?metric_name=' + self._test_metric1['name']
        param += '&dimension_name=' + self._dim_name1
        if timerange:
            param += '&start_time=' + self._start_time
            param += '&end_time=' + self._end_time
        resp, response_body = self.monasca_client.list_dimension_values(param)
        self.assertEqual(200, resp.status)
        self.assertTrue({'links', 'elements'} == set(response_body))
        response_values_length = len(response_body['elements'])
        values = [str(response_body['elements'][i]['dimension_value'])
                  for i in range(response_values_length)]
        if timerange:
            self.assertEqual(values, self._dim_name1_values_for_metric1_in_timerange)
        else:
            self.assertEqual(values, self._dim_name1_values_for_metric1)

    @decorators.attr(type='gate')
    def test_list_dimension_values_with_metric_name(self):
        self._test_list_dimension_values_with_metric_name(timerange=False)

    @decorators.attr(type='gate')
    @decorators.attr(type='timerange')
    def test_list_dimension_values_with_metric_name_with_timerange(self):
        self._test_list_dimension_values_with_metric_name(timerange=True)

    def _test_list_dimension_values_limit_and_offset(self, timerange):
        param = '?dimension_name=' + self._dim_name1
        if timerange:
            param += '&start_time=' + self._start_time
            param += '&end_time=' + self._end_time
        resp, response_body = self.monasca_client.list_dimension_values(param)
        self.assertEqual(200, resp.status)
        elements = response_body['elements']
        num_dim_values = len(elements)
        for limit in range(1, num_dim_values):
            start_index = 0
            params = [('limit', limit)]
            offset = None
            while True:
                num_expected_elements = limit
                if (num_expected_elements + start_index) > num_dim_values:
                    num_expected_elements = num_dim_values - start_index

                these_params = list(params)
                # Use the offset returned by the last call if available
                if offset:
                    these_params.extend([('offset', str(offset))])
                query_param = '?dimension_name=' + self._dim_name1
                if timerange:
                    query_param += '&start_time=' + self._start_time
                    query_param += '&end_time=' + self._end_time
                query_param += '&' + urlencode(these_params)
                resp, response_body = \
                    self.monasca_client.list_dimension_values(query_param)
                self.assertEqual(200, resp.status)
                if not response_body['elements']:
                    self.fail("No metrics returned")
                response_values_length = len(response_body['elements'])
                if response_values_length == 0:
                    self.fail("No dimension names returned")
                new_elements = [str(response_body['elements'][i]
                                    ['dimension_value']) for i in
                                range(response_values_length)]
                self.assertEqual(num_expected_elements, len(new_elements))

                expected_elements = elements[start_index:start_index + limit]
                expected_dimension_values = \
                    [expected_elements[i]['dimension_value'] for i in range(
                        len(expected_elements))]
                self.assertEqual(expected_dimension_values, new_elements)
                start_index += num_expected_elements
                if start_index >= num_dim_values:
                    break
                # Get the next set
                offset = self._get_offset(response_body)

    @decorators.attr(type='gate')
    def test_list_dimension_values_limit_and_offset(self):
        self._test_list_dimension_values_limit_and_offset(timerange=False)

    @decorators.attr(type='gate')
    @decorators.attr(type='timerange')
    def test_list_dimension_values_limit_and_offset_with_timerange(self):
        self._test_list_dimension_values_limit_and_offset(timerange=True)

    @decorators.attr(type='gate')
    @decorators.attr(type=['negative'])
    def test_list_dimension_values_no_dimension_name(self):
        self.assertRaises(exceptions.UnprocessableEntity,
                          self.monasca_client.list_dimension_values)

    @decorators.attr(type=["gate", "smoke"])
    def test_list_dimension_names(self):
        resp, response_body = self.monasca_client.list_dimension_names()
        self.assertEqual(200, resp.status)
        self.assertTrue({'links', 'elements'} == set(response_body))
        response_names_length = len(response_body['elements'])
        names = [str(response_body['elements'][i]['dimension_name']) for i
                 in range(response_names_length)]
        self.assertEqual(names, self._dim_names)

    @decorators.attr(type='gate')
    def test_list_dimension_names_with_metric_name(self):
        self._test_list_dimension_names_with_metric_name(
            self._test_metric1['name'], self._dim_names_metric1,
            timerange=False)
        self._test_list_dimension_names_with_metric_name(
            self._test_metric2['name'], self._dim_names_metric2,
            timerange=False)

    @decorators.attr(type='gate')
    @decorators.attr(type='timerange')
    def test_list_dimension_names_with_metric_name_with_timerange(self):
        self._test_list_dimension_names_with_metric_name(
            self._test_metric1['name'],
            self._dim_names_metric1_in_timerange,
            timerange=True)
        self._test_list_dimension_names_with_metric_name(
            self._test_metric2['name'],
            self._dim_names_metric2_in_timerange,
            timerange=True)

    @decorators.attr(type='gate')
    def test_list_dimension_names_limit_and_offset(self):
        resp, response_body = self.monasca_client.list_dimension_names()
        self.assertEqual(200, resp.status)
        elements = response_body['elements']
        num_dim_names = len(elements)
        for limit in range(1, num_dim_names):
            start_index = 0
            params = [('limit', limit)]
            offset = None
            while True:
                num_expected_elements = limit
                if (num_expected_elements + start_index) > num_dim_names:
                    num_expected_elements = num_dim_names - start_index

                these_params = list(params)
                # If not the first call, use the offset returned by the last
                # call
                if offset:
                    these_params.extend([('offset', str(offset))])
                query_param = '?' + urlencode(these_params)
                resp, response_body = self.monasca_client.list_dimension_names(
                    query_param)
                self.assertEqual(200, resp.status)
                if not response_body['elements']:
                    self.fail("No metrics returned")
                response_names_length = len(response_body['elements'])
                if response_names_length == 0:
                    self.fail("No dimension names returned")
                new_elements = [str(response_body['elements'][i]
                                    ['dimension_name']) for i in
                                range(response_names_length)]
                self.assertEqual(num_expected_elements, len(new_elements))

                expected_elements = elements[start_index:start_index + limit]
                expected_dimension_names = \
                    [expected_elements[i]['dimension_name'] for i in range(
                        len(expected_elements))]
                self.assertEqual(expected_dimension_names, new_elements)
                start_index += num_expected_elements
                if start_index >= num_dim_names:
                    break
                # Get the next set
                offset = self._get_offset(response_body)

    @decorators.attr(type='gate')
    @decorators.attr(type=['negative'])
    def test_list_dimension_names_with_wrong_metric_name(self):
        self._test_list_dimension_names_with_metric_name(
            'wrong_metric_name', [], timerange=False)

    def _test_list_dimension_names_with_metric_name(self, metric_name,
                                                    dimension_names,
                                                    timerange):
        param = '?metric_name=' + metric_name
        if timerange:
            param += '&start_time=' + self._start_time
            param += '&end_time=' + self._end_time
        resp, response_body = self.monasca_client.list_dimension_names(param)
        self.assertEqual(200, resp.status)
        self.assertTrue(set(['links', 'elements']) == set(response_body))
        response_names_length = len(response_body['elements'])
        names = [str(response_body['elements'][i]['dimension_name']) for i
                 in range(response_names_length)]
        self.assertEqual(names, dimension_names)

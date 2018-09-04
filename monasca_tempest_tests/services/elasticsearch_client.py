# Copyright 2015 FUJITSU LIMITED
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

from oslo_config import cfg
from oslo_serialization import jsonutils as json
from six import PY3
from tempest.lib.common import rest_client

CONF = cfg.CONF


class ElasticsearchClient(rest_client.RestClient):
    uri_prefix = "/elasticsearch"

    def __init__(self, auth_provider, service, region):
        super(ElasticsearchClient, self).__init__(
            auth_provider,
            service,
            region,
        )

    @staticmethod
    def deserialize(body):
        body = body.decode('utf-8') if PY3 else body
        return json.loads(body.replace("\n", ""))

    @staticmethod
    def serialize(body):
        return json.dumps(body)

    def get_metadata(self):
        uri = "/"

        response, body = self.get(self._uri(uri))
        self.expected_success(200, response.status)

        if body:
            body = self.deserialize(body)
        return response, body

    def count_search_messages(self, message, headers):
        return len(self.search_messages(message, headers))

    def search_messages(self, message, headers=None):
        uri = '_msearch'
        body = """
               {"index" : "*", "search_type" : "dfs_query_then_fetch"}
               {"query" : {"match" : {"message":" """ + message + """ "}}}
        """
        response, body = self.post(self._uri(uri), body, headers)
        self.expected_success(200, response.status)
        body = self.deserialize(body)
        return body['responses'][0].get('hits', {}).get('hits', [])

    def search_event_by_event_type(self, event_type):
        uri = '_msearch'
        body = """
               {"index" : "*", "search_type" : "dfs_query_then_fetch"}
               {"query" : {"match" : {"event_type":" """ + event_type + """ "}}}
        """
        header = {'kbn-version': CONF.monitoring.kibana_version}
        response, body = self.post(self._uri(uri), body, header)
        self.expected_success(200, response.status)
        body = self.deserialize(body)
        return body['responses'][0].get('hits', {}).get('hits', [])

    def search_event(self, event):
        uri = '_msearch'
        header = {'kbn-version': CONF.monitoring.kibana_version}
        event = json.dumps(event)
        body = """
               {"index" : "*", "search_type" : "dfs_query_then_fetch"}
               {"query" : {"match" : {"event":" """ + event + """ "}}}
        """
        response, body = self.post(self._uri(uri), body, header)
        self.expected_success(200, response.status)
        body = self.deserialize(body)
        return body['responses'][0].get('hits', {}).get('hits', [])

    def _uri(self, url):
        return '{}/{}'.format(self.uri_prefix, url)

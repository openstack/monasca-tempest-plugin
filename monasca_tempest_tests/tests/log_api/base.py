# coding=utf-8
#
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

import codecs
import random
import string

from oslo_config import cfg
import six
from tempest.common import credentials_factory as cred_factory
from tempest import exceptions
from tempest import test

from monasca_tempest_tests.clients import log_api as clients

CONF = cfg.CONF
_ONE_MB = 1024 * 1024  # MB


def _get_message_size(size_base):
    """Returns message size in number of characters.

    Method relies on UTF-8 where 1 character = 1 byte.

    """
    return int(round(size_base * _ONE_MB, 1))


_SMALL_MESSAGE_SIZE = _get_message_size(0.001)
_MEDIUM_MESSAGE_SIZE = _get_message_size(0.01)
_LARGE_MESSAGE_SIZE = _get_message_size(0.1)
_REJECTABLE_MESSAGE_SIZE = _get_message_size(1.1)


def generate_unique_message(message=None, size=50):
    letters = string.ascii_lowercase

    def rand(amount, space=True):
        space = ' ' if space else ''
        return ''.join((random.choice(letters + space) for _ in range(amount)))

    sid = rand(10, space=False)

    if not message:
        message = rand(size)
    return sid, sid + ' ' + message


def generate_small_message(message=None):
    return generate_unique_message(message, _SMALL_MESSAGE_SIZE)


def generate_medium_message(message=None):
    return generate_unique_message(message, _MEDIUM_MESSAGE_SIZE)


def generate_large_message(message=None):
    return generate_unique_message(message, _LARGE_MESSAGE_SIZE)


def generate_rejectable_message(message=None):
    return generate_unique_message(message, _REJECTABLE_MESSAGE_SIZE)


def _get_headers(headers=None, content_type="application/json"):
    if not headers:
        headers = {}
    headers.update({
        'Content-Type': content_type,
        'kbn-version': CONF.monitoring.kibana_version
    })
    return headers


def _get_data(message):
    data = {
        'logs': [{
            'message': message
        }]
    }
    return data


class BaseLogsTestCase(test.BaseTestCase):
    """Base test case class for all Monitoring API tests."""

    @classmethod
    def skip_checks(cls):
        super(BaseLogsTestCase, cls).skip_checks()

    @classmethod
    def resource_setup(cls):
        super(BaseLogsTestCase, cls).resource_setup()
        auth_version = CONF.identity.auth_version
        cred_provider = cred_factory.get_credentials_provider(
            cls.__name__,
            identity_version=auth_version)
        credentials = cred_provider.get_creds_by_roles(
            ['monasca-user', 'admin']).credentials
        cls.os_primary = clients.Manager(credentials=credentials)

        cls.logs_client = cls.os_primary.log_api_client
        cls.logs_search_client = cls.os_primary.log_search_client

    @staticmethod
    def cleanup_resources(method, list_of_ids):
        for resource_id in list_of_ids:
            try:
                method(resource_id)
            except exceptions.EndpointNotFound:
                pass


def _hex_to_unicode(hex_raw):
    hex_raw = six.b(hex_raw.replace(' ', ''))
    hex_str_raw = codecs.getdecoder('hex')(hex_raw)[0]
    hex_str = hex_str_raw.decode('utf-8', 'replace')
    return hex_str

# NOTE(trebskit) => http://www.cl.cam.ac.uk/~mgk25/ucs/examples/UTF-8-test.txt
UNICODE_MESSAGES = [
    # Unicode is evil...
    {'case': 'arabic', 'input': 'يونيكود هو الشر'},
    {'case': 'polish', 'input': 'Unicode to zło'},
    {'case': 'greek', 'input': 'Unicode είναι κακό'},
    {'case': 'portuguese', 'input': 'Unicode é malvado'},
    {'case': 'lao', 'input': 'unicode ເປັນຄວາມຊົ່ວຮ້າຍ'},
    {'case': 'german', 'input': 'Unicode ist böse'},
    {'case': 'japanese', 'input': 'ユニコードは悪です'},
    {'case': 'russian', 'input': 'Unicode - зло'},
    {'case': 'urdu', 'input': 'یونیسیڈ برائی ہے'},
    {'case': 'weird', 'input': '🆄🅽🅸🅲🅾🅳🅴 🅸🆂 🅴🆅🅸🅻...'},  # funky, huh ?
    # conditions from link above
    # 2.3  Other boundary conditions
    {'case': 'stress_2_3_1', 'input': _hex_to_unicode('ed 9f bf')},
    {'case': 'stress_2_3_2', 'input': _hex_to_unicode('ee 80 80')},
    {'case': 'stress_2_3_3', 'input': _hex_to_unicode('ef bf bd')},
    {'case': 'stress_2_3_4', 'input': _hex_to_unicode('f4 8f bf bf')},
    {'case': 'stress_2_3_5', 'input': _hex_to_unicode('f4 90 80 80')},
    # 3.5 Impossible byes
    {'case': 'stress_3_5_1', 'input': _hex_to_unicode('fe')},
    {'case': 'stress_3_5_2', 'input': _hex_to_unicode('ff')},
    {'case': 'stress_3_5_3', 'input': _hex_to_unicode('fe fe ff ff')},
    # 4.1 Examples of an overlong ASCII character
    {'case': 'stress_4_1_1', 'input': _hex_to_unicode('c0 af')},
    {'case': 'stress_4_1_2', 'input': _hex_to_unicode('e0 80 af')},
    {'case': 'stress_4_1_3', 'input': _hex_to_unicode('f0 80 80 af')},
    {'case': 'stress_4_1_4', 'input': _hex_to_unicode('f8 80 80 80 af')},
    {'case': 'stress_4_1_5', 'input': _hex_to_unicode('fc 80 80 80 80 af')},
    # 4.2 Maximum overlong sequences
    {'case': 'stress_4_2_1', 'input': _hex_to_unicode('c1 bf')},
    {'case': 'stress_4_2_2', 'input': _hex_to_unicode('e0 9f bf')},
    {'case': 'stress_4_2_3', 'input': _hex_to_unicode('f0 8f bf bf')},
    {'case': 'stress_4_2_4', 'input': _hex_to_unicode('f8 87 bf bf bf')},
    {'case': 'stress_4_2_5', 'input': _hex_to_unicode('fc 83 bf bf bf bf')},
    # 4.3  Overlong representation of the NUL character
    {'case': 'stress_4_3_1', 'input': _hex_to_unicode('c0 80')},
    {'case': 'stress_4_3_2', 'input': _hex_to_unicode('e0 80 80')},
    {'case': 'stress_4_3_3', 'input': _hex_to_unicode('f0 80 80 80')},
    {'case': 'stress_4_3_4', 'input': _hex_to_unicode('f8 80 80 80 80')},
    {'case': 'stress_4_3_5', 'input': _hex_to_unicode('fc 80 80 80 80 80')},
    # and some cheesy example from polish novel 'Pan Tadeusz'
    {'case': 'mr_t', 'input': 'Hajże na Soplicę!'},
    # it won't be complete without that one
    {'case': 'mr_b', 'input': 'Grzegorz Brzęczyszczykiewicz, '
                              'Chrząszczyżewoszyce, powiat Łękołody'},
    # great success, christmas time
    {'case': 'olaf', 'input': '☃'}
]

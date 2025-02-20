# Copyright 2020 The StackStorm Authors.
# Copyright 2019 Extreme Networks, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import

import os
import json
import logging
from unittest import TestCase

import six
import mock
import requests

from st2client import models
from st2client.client import Client

from tests import base


LOG = logging.getLogger(__name__)

NONRESOURCES = ["workflows"]


class TestClientEndpoints(TestCase):
    def tearDown(self):
        for var in [
            "ST2_BASE_URL",
            "ST2_API_URL",
            "ST2_STREAM_URL",
            "ST2_DATASTORE_URL",
            "ST2_AUTH_TOKEN",
        ]:
            if var in os.environ:
                del os.environ[var]

    def test_managers(self):
        property_names = [
            k for k, v in six.iteritems(Client.__dict__) if isinstance(v, property)
        ]

        client = Client()

        for property_name in property_names:
            manager = getattr(client, property_name, None)
            self.assertIsNotNone(manager)

            if property_name not in NONRESOURCES:
                self.assertIsInstance(manager, models.ResourceManager)

    def test_default(self):
        base_url = "http://127.0.0.1"
        api_url = "http://127.0.0.1:9101/v1"
        stream_url = "http://127.0.0.1:9102/v1"

        client = Client()
        endpoints = client.endpoints
        self.assertEqual(endpoints["base"], base_url)
        self.assertEqual(endpoints["api"], api_url)
        self.assertEqual(endpoints["stream"], stream_url)

    @mock.patch.object(
        requests,
        "get",
        mock.MagicMock(return_value=base.FakeResponse(json.dumps({}), 200, "OK")),
    )
    def test_basic_auth_option_success(self):
        client = Client(basic_auth="username:password")
        self.assertEqual(client.basic_auth, ("username", "password"))

        self.assertEqual(requests.get.call_count, 0)
        client.actions.get_all()
        self.assertEqual(requests.get.call_count, 1)

        requests.get.assert_called_with(
            "http://127.0.0.1:9101/v1/actions", auth=("username", "password"), params={}
        )

    @mock.patch.object(
        requests,
        "get",
        mock.MagicMock(return_value=base.FakeResponse(json.dumps({}), 200, "OK")),
    )
    def test_basic_auth_option_success_password_with_colon(self):
        client = Client(basic_auth="username:password:with:colon")
        self.assertEqual(client.basic_auth, ("username", "password:with:colon"))

        self.assertEqual(requests.get.call_count, 0)
        client.actions.get_all()
        self.assertEqual(requests.get.call_count, 1)

        requests.get.assert_called_with(
            "http://127.0.0.1:9101/v1/actions",
            auth=("username", "password:with:colon"),
            params={},
        )

    def test_basic_auth_option_invalid_notation(self):
        self.assertRaisesRegex(
            ValueError,
            "needs to be in the username:password notation",
            Client,
            basic_auth="username_password",
        )

    def test_env(self):
        base_url = "http://www.stackstorm.com"
        api_url = "http://www.st2.com:9101/v1"
        stream_url = "http://www.st2.com:9102/v1"

        os.environ["ST2_BASE_URL"] = base_url
        os.environ["ST2_API_URL"] = api_url
        os.environ["ST2_STREAM_URL"] = stream_url
        self.assertEqual(os.environ.get("ST2_BASE_URL"), base_url)
        self.assertEqual(os.environ.get("ST2_API_URL"), api_url)
        self.assertEqual(os.environ.get("ST2_STREAM_URL"), stream_url)

        client = Client()
        endpoints = client.endpoints
        self.assertEqual(endpoints["base"], base_url)
        self.assertEqual(endpoints["api"], api_url)
        self.assertEqual(endpoints["stream"], stream_url)

    def test_env_base_only(self):
        base_url = "http://www.stackstorm.com"
        api_url = "http://www.stackstorm.com:9101/v1"
        stream_url = "http://www.stackstorm.com:9102/v1"

        os.environ["ST2_BASE_URL"] = base_url
        self.assertEqual(os.environ.get("ST2_BASE_URL"), base_url)
        self.assertEqual(os.environ.get("ST2_API_URL"), None)
        self.assertEqual(os.environ.get("ST2_STREAM_URL"), None)

        client = Client()
        endpoints = client.endpoints
        self.assertEqual(endpoints["base"], base_url)
        self.assertEqual(endpoints["api"], api_url)
        self.assertEqual(endpoints["stream"], stream_url)

    def test_args(self):
        base_url = "http://www.stackstorm.com"
        api_url = "http://www.st2.com:9101/v1"
        stream_url = "http://www.st2.com:9102/v1"

        client = Client(base_url=base_url, api_url=api_url, stream_url=stream_url)
        endpoints = client.endpoints
        self.assertEqual(endpoints["base"], base_url)
        self.assertEqual(endpoints["api"], api_url)
        self.assertEqual(endpoints["stream"], stream_url)

    def test_cacert_arg(self):
        # Valid value, boolean True
        base_url = "http://www.stackstorm.com"
        api_url = "http://www.st2.com:9101/v1"
        stream_url = "http://www.st2.com:9102/v1"

        client = Client(
            base_url=base_url, api_url=api_url, stream_url=stream_url, cacert=True
        )
        self.assertEqual(client.cacert, True)

        # Valid value, boolean False
        base_url = "http://www.stackstorm.com"
        api_url = "http://www.st2.com:9101/v1"
        stream_url = "http://www.st2.com:9102/v1"

        client = Client(
            base_url=base_url, api_url=api_url, stream_url=stream_url, cacert=False
        )
        self.assertEqual(client.cacert, False)

        # Valid value, existing path to a CA bundle
        cacert = os.path.abspath(__file__)
        client = Client(
            base_url=base_url, api_url=api_url, stream_url=stream_url, cacert=cacert
        )
        self.assertEqual(client.cacert, cacert)

        # Invalid value, path to the bundle doesn't exist
        cacert = os.path.abspath(__file__)
        expected_msg = 'CA cert file "doesntexist" does not exist'
        self.assertRaisesRegexp(
            ValueError,
            expected_msg,
            Client,
            base_url=base_url,
            api_url=api_url,
            stream_url=stream_url,
            cacert="doesntexist",
        )

    def test_args_base_only(self):
        base_url = "http://www.stackstorm.com"
        api_url = "http://www.stackstorm.com:9101/v1"
        stream_url = "http://www.stackstorm.com:9102/v1"

        client = Client(base_url=base_url)
        endpoints = client.endpoints
        self.assertEqual(endpoints["base"], base_url)
        self.assertEqual(endpoints["api"], api_url)
        self.assertEqual(endpoints["stream"], stream_url)

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
from unittest import TestCase

from st2common.util import hash as hash_utils
from st2common.util import auth as auth_utils
from six.moves import range


class TestHashWithApiKeys(TestCase):
    def test_hash_repeatability(self):
        api_key = auth_utils.generate_api_key()
        hash1 = hash_utils.hash(api_key)
        hash2 = hash_utils.hash(api_key)
        self.assertEqual(hash1, hash2, "Expected a repeated hash.")

    def test_hash_uniqueness(self):
        count = 10000
        api_keys = [auth_utils.generate_api_key() for _ in range(count)]
        hashes = set([hash_utils.hash(api_key) for api_key in api_keys])
        self.assertEqual(len(hashes), count, "Expected all unique hashes.")

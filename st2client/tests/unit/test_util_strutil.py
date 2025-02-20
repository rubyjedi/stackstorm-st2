# -*- coding: utf-8 -*-

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

from st2client.utils import strutil


class StrUtilTestCase(TestCase):
    # See https://mail.python.org/pipermail/python-list/2006-January/411909.html

    def test_unescape(self):
        in_str = 'Action execution result double escape \\"stuffs\\".\\r\\n'
        expected = 'Action execution result double escape "stuffs".\r\n'
        out_str = strutil.unescape(in_str)
        self.assertEqual(out_str, expected)

    def test_unicode_string(self):
        in_str = "\u8c03\u7528CMS\u63a5\u53e3\u5220\u9664\u865a\u62df\u76ee\u5f55"
        out_str = strutil.unescape(in_str)
        self.assertEqual(out_str, in_str)

    def test_strip_carriage_returns(self):
        in_str = "Windows editors introduce\r\nlike a noob in 2017."
        out_str = strutil.strip_carriage_returns(in_str)
        exp_str = "Windows editors introduce\nlike a noob in 2017."
        self.assertEqual(out_str, exp_str)

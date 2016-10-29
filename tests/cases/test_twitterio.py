#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#  Copyright Kitware Inc. and Epidemico Inc.
#
#  Licensed under the Apache License, Version 2.0 ( the "License" );
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
###############################################################################
import json
import os
import unittest
from gaia_twitter.inputs import TwitterIO

testfile_path = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '../data')


class TestGaiaProcessors(unittest.TestCase):

    def test_twitter_process(self):
        """
        Test TwitterIO conversion of feed to geojson
        """
        with open(os.path.join(testfile_path,
                               'twitter_feed.json')) as mock_feed:
            twitterdata = json.load(mock_feed)
        twitterio = TwitterIO()
        twitterio.data = twitterio.convertToGeojson(twitterdata)
        with open(os.path.join(
                testfile_path,
                'twitter_process_results.json')) as exp:
            expected_json = json.load(exp)
        actual_json = json.loads(twitterio.read())
        self.assertEquals(len(expected_json['features']),
                          len(actual_json['features']))

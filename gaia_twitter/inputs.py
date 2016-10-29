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
import webbrowser
from gaia import types

import carmen

try:
    import osr
except ImportError:
    from osgeo import osr
import gaia.formats as formats

from gaia.inputs import FileIO
from rauth import OAuth1Service
from geopy.geocoders import Nominatim
from geopandas import GeoDataFrame

geolocator = Nominatim()


class TwitterIO(FileIO):
    """
    Converts a twitter data stream into GeoJSON
    """

    #: Data type (vector or raster)
    type = types.VECTOR

    #: Default output format
    default_output = formats.JSON

    def get_coordinates_from_tweet(self, tweet):
        """
        Get location from a tweet using Carmen and geolocator
        :param tweet: tweet to find coordinates for
        :return: coordinates
        """
        resolver = carmen.get_resolver()
        resolver.load_locations()
        location = resolver.resolve_tweet(tweet)
        if location is not None:
            for x in location:
                if x:
                    location_string = (x.country + ',' + x.state + ',' +
                                       x.county + ',' + x.city)
                    coord = geolocator.geocode(location_string)
            return coord

    def convertToGeojson(self, data):
        """
        Convert a raw twitter JSON feed into GeoJSON
        :param data: raw twitter JSON
        :return: GeoJSON object
        """
        if len(data) > 1:
            geojson = {
                "type": "FeatureCollection",
                "features": []
            }

            if type(data) is str:
                data = json.loads(data)

            for i, tweet in enumerate(data, 1):
                coord = self.get_coordinates_from_tweet(tweet)
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [coord.longitude, coord.latitude]
                    },
                    "properties": {

                    }
                }
                # Iterate over the tweet and create properties
                for property in tweet:
                    feature["properties"][property] = tweet[property]
                geojson['features'].append(feature)

        else:
            geojson = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": []
                },
                "properties": {}
            }

            for i, tweet in enumerate(data, 1):
                coord = self.get_coordinates_from_tweet(tweet)
                geojson["geometry"]["coordinates"] = [coord.longitude,
                                                      coord.latitude]
                # Iterate over the tweet and create properties
                for property in tweet:
                    geojson["properties"][property] = tweet[property]

        class geoEmptyClass:
            pass

        if geojson["type"] == "Feature":
            results = geoEmptyClass()
            results.__geo_interface__ = geojson
            self.data = GeoDataFrame.from_features([results])
            if format == formats.JSON:
                return self.data.to_json()
            else:
                return self.data
        else:
            self.data = GeoDataFrame.from_features(geojson["features"])

        return self.data.to_json()

    def read(self, uri=None, format=formats.JSON):
        """
        Connect to twitter API, get data, convert to GeoJSON
        :param uri: location of twitter config file w/twitter API parameters
        :param format: output format
        :return: data in output format
        """
        if not format:
            format = self.default_output
        if self.data is None:
            if not uri:
                uri = self.inputs[0].uri

            with open(uri) as config_file:
                config_json = json.load(config_file)

            twitter_config = config_json['data_inputs']
            twitter = OAuth1Service(
                consumer_key=twitter_config['consumer_key'],
                consumer_secret=twitter_config['consumer_secret'],
                request_token_url=twitter_config['request_token_url'],
                access_token_url=twitter_config['access_token_url'],
                authorize_url=twitter_config['authorize_url'],
                base_url=twitter_config['base_url']
            )

            request_token, request_token_secret = twitter.get_request_token()

            authorize_url = twitter.get_authorize_url(request_token)

            webbrowser.open(authorize_url)
            pincode = raw_input('Enter PIN from browser: ')

            session = twitter.get_auth_session(request_token,
                                               request_token_secret,
                                               method='POST',
                                               data={'oauth_verifier': pincode})

            # Include retweets
            params = {'include_rts': twitter_config['include_retweets'],
                      'count': twitter_config['count']}

            r = session.get('statuses/home_timeline.json',
                            params=params, verify=True)

            # Convert twitter data into geojson
            # Create Feature if one tweet was found,
            # otherwise create FeatureCollection
            self.convertToGeojson(r.json())
        if format == formats.JSON:
            return self.data.to_json()
        else:
            return self.data

PLUGIN_CLASS_EXPORTS = [
    TwitterIO
]

# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Module for recording API responses for the Mock Tests."""

import os
import json
import re
from googleapiclient.discovery_cache.base import Cache

import harness.machine_producers.gcp_producer as gp

# To use, each of these must be set as a string.
# PROJECT should be a valid project under your GCP account.
# KEY_PATH should be a downloaded API key as a json file from a service account with access to PROJECT.
PROJECT = ""
KEY_PATH = ""

DIR_PATH = os.path.dirname(__file__) + "/"
ZONE = "us-west1-b"
MACHINE_TYPE = "n1-standard-1"
IMAGE = "debian-9-nested"


class GCPMachineProducerCache(Cache):
    """Records responses from the GCPMachineProducer object's operations. This is
    an implementation of googleapiclient.discovery_cache.base
    See: http://googleapis.github.io/google-api-python-client/docs/epy/index.html

    Attributes:
        cache: list of recorded json responses as strings.
    """
    def __init__(self):
        self.cache = []

    def set(self, url: str, content: str):
        """Set method called when building the API (e.g.
        googleapiclient.discovery.build("compute", "v1")

        Required method to extend Cache.

        :param url: url string called. Thrown away as it is not used for recording.
        :param content: json response content from the API
        :return:
        """
        self.cache.append(content)

    def get(self, url: str):
        """Return the first content entry in the cache.

        Required method to extend Cache.

        :param url: Not useful for recording.
        :return:
        """
        return self.cache[0] if self.cache else None

    def pop(self):
        """Returns and removes the first cache element.

        :return: first cache element, which is removed.
        """
        return self.cache.pop(0)

    def set_json(self, content: dict):
        """Sets dictionary objects into the cache. After building the api,
        subsequent API call responses are all dictionaries.

        All user specific information is stripped before entering into the cache.

        :param content: a dictionary object response from a request.
        :return:
        """
        content = self._strip_content(content)
        self.cache.append(content)

    @staticmethod
    def _strip_content(content: dict) -> str:
        """Strips user, project, and key information from API responses.

        :param content: API response to be stripped.
        :return: a string of valid JSON.
        """
        try:
            content["user"] = "test"
        except KeyError:
            pass

        content = json.dumps(content, indent=4)
        project_regex = re.compile(re.escape(PROJECT))
        key_regex = re.compile(re.escape(KEY_PATH))
        content = re.sub(project_regex, r"test", content)
        content = re.sub(key_regex, r"test", content)
        return content


def write_out(filename, content):
    with open(DIR_PATH + filename, "w") as f:
        f.write(content)


# Run the scenario.
cache = GCPMachineProducerCache()
producer = \
        gp.GCPMachineProducer(project=PROJECT, zone=ZONE, machine_type=MACHINE_TYPE, api_key_path=KEY_PATH, cache=cache)
producer.set_image(IMAGE)
machines = producer.get_machines(1)
producer.release_machines(machines)

# First should be the API.
write_out("compute_api_discover_mock.json", cache.pop())

# Then a call to get the image link.
write_out("get_image_link_mock.json", cache.pop())

# Then several operations of type 'insert'. Get the last completed one.
res = cache.pop()
decoded = json.loads(res)
while decoded["operationType"] == "insert" and decoded["status"] != "DONE":
    res = cache.pop()
    decoded = json.loads(res)

if decoded["operationType"] != "insert":
    raise ValueError("Invalid recording. Expected a insert opration. Got:\n {res}".format(res=res))
write_out("create_instance_mock.json", res)

# Next a call to get_instance.
write_out("get_instance_mock.json", cache.pop())

# Lastly a delete operation.
write_out("delete_instance_mock.json", cache.pop())




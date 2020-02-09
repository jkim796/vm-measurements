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

"""Tests for GCPMachineProducer"""

import os
from googleapiclient.http import HttpMockSequence

import harness.machine_producers.gcp_producer as gp

ZONE = "us-west1-b"
PROJECT = "test"
MACHINE_TYPE = "n1-standard-1"
STATUS_200 = {'status': '200'}
MOCKS_DIR = os.path.dirname(os.path.abspath(__file__)) + "/test_data/"

MOCK_COMPUTE_API_DISCOVERY = (STATUS_200, open(MOCKS_DIR + "compute_api_discover_mock.json").read())
MOCK_IMAGE_LIST = (STATUS_200, open(MOCKS_DIR + "get_image_link_mock.json").read())
MOCK_CREATE_INSTANCE = (STATUS_200, open(MOCKS_DIR + "create_instance_mock.json").read())
MOCK_REQUEST_DONE = (STATUS_200, open(MOCKS_DIR + "request_done_mock.json").read())
MOCK_GET_INSTANCE = (STATUS_200, open(MOCKS_DIR + "get_instance_mock.json").read())
MOCK_DELETE = (STATUS_200, open(MOCKS_DIR + "delete_instance_mock.json").read())


def test_add_api():
    """Test to build API with Mock HTTP Server.

    :return:
    """
    http = HttpMockSequence([
        MOCK_COMPUTE_API_DISCOVERY
    ])

    producer = \
        gp.GCPMachineProducer(project=PROJECT, zone=ZONE, machine_type=MACHINE_TYPE, http=http)
    assert producer.compute is not None


def test_set_image():
    """Test to set image used with Mock HTTP Server

    :return:
    """
    image = "debian-9-nested"

    http = HttpMockSequence([
        MOCK_COMPUTE_API_DISCOVERY,
        MOCK_IMAGE_LIST
    ])
    producer = \
        gp.GCPMachineProducer(project=PROJECT, zone=ZONE, machine_type=MACHINE_TYPE, http=http)
    producer.set_image(image)
    assert image in producer.image


def test_get_release_machines():
    """Test of get/release of machines using Mock HTTP Server.

    :return:
    """
    http = HttpMockSequence([
        MOCK_COMPUTE_API_DISCOVERY,
        MOCK_IMAGE_LIST,
        MOCK_CREATE_INSTANCE,
        MOCK_REQUEST_DONE,
        MOCK_GET_INSTANCE,
        MOCK_DELETE
    ])
    producer = \
        gp.GCPMachineProducer(project=PROJECT, zone=ZONE, machine_type=MACHINE_TYPE, http=http)
    producer.set_image("test_image")
    machines = producer.get_machines(1)
    assert len(machines) == 1
    producer.release_machines(machines)
